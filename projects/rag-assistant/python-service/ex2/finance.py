import json
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

load_dotenv()

app = FastAPI(title="Expense & Currency Intelligence Service (Ollama)")

# ---------------------------------------------------------
# State / Ledger
# ---------------------------------------------------------
EXPENSE_LEDGER: List[Dict[str, Any]] = []

FX_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "INR": 83.5,
    "GBP": 0.79,
    "JPY": 155.0,
}

# ---------------------------------------------------------
# Step 1: Define Tools with LangChain Core
# ---------------------------------------------------------
def _exchange_rate(from_currency: str, to_currency: str) -> float:
    from_c = from_currency.strip().upper()
    to_c = to_currency.strip().upper()
    if from_c not in FX_RATES or to_c not in FX_RATES:
        raise ValueError(
            f"Unsupported currency. Available: {list(FX_RATES.keys())}"
        )

    return FX_RATES[to_c] / FX_RATES[from_c]


@tool
def get_live_fx_rate(from_curr: str, to_curr: str) -> str:
    """Get the exchange rate between currencies. Use convert_currency to convert an amount."""
    try:
        rate = _exchange_rate(from_curr, to_curr)
    except ValueError as error:
        return json.dumps({"error": str(error)})

    return json.dumps({
        "from": from_curr.strip().upper(),
        "to": to_curr.strip().upper(),
        "rate": round(rate, 4),
    })


@tool
def log_expense(amount: float, category: str, currency: str) -> str:
    """Records an itemized expense entry into the tracking ledger."""
    entry = {
        "id": len(EXPENSE_LEDGER) + 1,
        "amount": round(amount, 2),
        "category": category.strip().capitalize(),
        "currency": currency.upper(),
    }
    EXPENSE_LEDGER.append(entry)
    return json.dumps({
        "status": "success",
        "entry": entry,
        "total_logged_entries": len(EXPENSE_LEDGER),
    })


@tool
def get_expenses(category: Optional[str] = None, currency: Optional[str] = None) -> str:
    """Retrieve recorded expenses from the ledger. Can optionally filter by category or currency."""
    results = EXPENSE_LEDGER

    if category:
        results = [e for e in results if e["category"].lower() == category.strip().lower()]

    if currency:
        results = [e for e in results if e["currency"].upper() == currency.strip().upper()]

    total_amount = sum(e["amount"] for e in results)

    return json.dumps({
        "count": len(results),
        "total_amount": round(total_amount, 2),
        "entries": results,
    })


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert a numeric amount between currencies. Use after retrieving an expense if needed."""
    try:
        rate = _exchange_rate(from_currency, to_currency)
    except ValueError as error:
        return json.dumps({"error": str(error)})

    return json.dumps({
        "amount": round(amount, 2),
        "from": from_currency.strip().upper(),
        "to": to_currency.strip().upper(),
        "rate": round(rate, 4),
        "converted_amount": round(amount * rate, 2),
    })


@tool
def calculate_split(total: float, num_people: int, tip_pct: float = 0.0) -> str:
    """Calculates bill splitting among multiple individuals with optional tip percentage."""
    try:
        # Cast inputs in case the model supplied them as strings
        total_num = float(total)
        people_count = int(num_people)
        tip_percent = float(tip_pct) if tip_pct is not None else 0.0
    except (ValueError, TypeError) as err:
        return json.dumps({
            "error": f"Invalid numerical argument received: {err}"
        })

    if people_count <= 0:
        return json.dumps({"error": "num_people must be at least 1."})

    tip_amount = total_num * (tip_percent / 100.0)
    grand_total = total_num + tip_amount
    per_person = grand_total / people_count

    return json.dumps({
        "subtotal": round(total_num, 2),
        "tip_percentage": tip_percent,
        "tip_amount": round(tip_amount, 2),
        "grand_total": round(grand_total, 2),
        "num_people": people_count,
        "per_person_share": round(per_person, 2),
    })


TOOLS = [
    get_live_fx_rate,
    convert_currency,
    log_expense,
    get_expenses,
    calculate_split,
]
TOOL_MAP = {t.name: t for t in TOOLS}

# ---------------------------------------------------------
# Step 2: Initialize Ollama Model with Bound Tools
# ---------------------------------------------------------
llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0,
)

llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are an expense and currency assistant. "
        "Always invoke the provided tools for recording expenses, checking or reading logged expenses, "
        "currency conversions, and bill splits. For currency conversions, use convert_currency; "
        "for bill splits, use calculate_split. Never guess or compute mental math when a tool is available. "
        "When one tool needs another tool's result, call the first tool and wait for its result before "
        "calling the dependent tool. Do not return JSON that describes a tool call as your final answer."
    )
)


def _parse_text_tool_call(content: Any) -> Optional[tuple[str, Dict[str, Any]]]:
    if not isinstance(content, str):
        return None

    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict) or not isinstance(payload.get("name"), str):
        return None

    arguments = payload.get("parameters", payload.get("arguments"))
    if not isinstance(arguments, dict):
        return None

    tool_name = payload["name"]
    if tool_name not in TOOL_MAP:
        return None

    return tool_name, arguments


# ---------------------------------------------------------
# Step 3: Tool-Calling Loop with Console Prints
# ---------------------------------------------------------
def process_user_query(query: str) -> str:
    messages = [SYSTEM_PROMPT, HumanMessage(content=query)]
    max_tool_rounds = 8

    print(f"\n" + "=" * 50)
    print(f"📩 [USER QUERY]: {query}")
    print("=" * 50)

    for _ in range(max_tool_rounds):
        ai_response: AIMessage = llm_with_tools.invoke(messages)
        messages.append(ai_response)

        if not ai_response.tool_calls:
            text_tool_call = _parse_text_tool_call(ai_response.content)
            if text_tool_call is not None:
                tool_name, tool_args = text_tool_call
                print(f"⚙️  Model returned a text-form tool call: `{tool_name}`")
                try:
                    tool_output = TOOL_MAP[tool_name].invoke(tool_args)
                except Exception as error:
                    tool_output = json.dumps({
                        "error": f"{type(error).__name__}: {error}"
                    })
                    print(f"      Tool error: {tool_output}")

                print(f"      Result: {tool_output}")
                messages.append(HumanMessage(
                    content=(
                        f"Your previous message described a tool call instead of answering. "
                        f"The `{tool_name}` tool returned: {tool_output}. "
                        "Use this result to answer the user's original request."
                    )
                ))
                continue

            print(f"🤖 [FINAL RESPONSE]:\n{ai_response.content}")
            print("=" * 50 + "\n")
            return str(ai_response.content)

        print(f"⚙️  Model requested {len(ai_response.tool_calls)} tool call(s):")
        for idx, tool_call in enumerate(ai_response.tool_calls, start=1):
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call.get("id") or f"call_{tool_name}_{idx}"

            print(f"\n  [{idx}] Invoking Tool: 🛠️  `{tool_name}`")
            print(f"      Arguments: {json.dumps(tool_args)}")

            selected_tool = TOOL_MAP.get(tool_name)
            if selected_tool:
                try:
                    tool_output = selected_tool.invoke(tool_args)
                except Exception as error:
                    tool_output = json.dumps({
                        "error": f"{type(error).__name__}: {error}"
                    })
                    print(f"      Tool error: {tool_output}")
            else:
                tool_output = json.dumps({"error": f"Tool '{tool_name}' not found."})

            print(f"      Result: {tool_output}")

            messages.append(
                ToolMessage(content=str(tool_output), tool_call_id=tool_id)
            )

        print("\n🔄 Sending tool results back to Ollama...")

    raise RuntimeError(
        f"Model exceeded the maximum of {max_tool_rounds} tool-call rounds."
    )

# ---------------------------------------------------------
# Step 4: FastAPI Endpoints
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    ledger_count: int

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    try:
        reply = process_user_query(payload.query)
        return ChatResponse(response=reply, ledger_count=len(EXPENSE_LEDGER))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ledger")
def get_ledger():
    return {"entries": EXPENSE_LEDGER}

def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()