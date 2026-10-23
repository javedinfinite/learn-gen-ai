From the repository root, sync that project’s dependencies without trying to build the local package (the package layout currently causes a build error):

```
uv sync --project projects/rag-assistant/python-service --no-install-project
```

Then run Uvicorn using that project’s environment:

Be in python service folder and run below command 

```
uv run --no-sync python -m uvicorn ex2.finance:app --reload --port 8000

```

If you are in root folder i.e. learn-gen-ai then run below command 

```
uv run --project projects/rag-assistant/python-service --no-sync \
  uvicorn --app-dir projects/rag-assistant/python-service \
  ex2.finance:app --reload --port 8000
```

The sync may take a while because it installs the service’s dependencies.


Prompts to Test Each Capability
Here is a progression of prompts to test the tool-calling behavior in your terminal:

1. Populate the Ledger (write operations)
"Log an expense of 450 INR for Groceries."

"Add an expense of 120 EUR under Hotel."

"Record 80 EUR for Dinner in the Food category."

2. Query the Ledger (read operations with get_expenses)
List everything:"Can you show me all my recorded expenses so far?"

Filter by category:"How much have I spent on Food?"

Filter by currency:"Show me all the expenses I paid in EUR."

3. Chained / Multi-tool reasoning
Read + Currency Conversion:"What is the total of my EUR expenses, and how much is that in INR?" (The assistant should retrieve the expenses, then use convert_currency for the amount.)

Read + Bill Split:"Look up my Hotel expense and tell me how much each person pays if we split it between 3 people."