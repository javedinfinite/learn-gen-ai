
# Lesson 6 — Deterministic Workflows vs AI Workflows vs Agents

## 1. Concept

When building a GenAI application, one of the most important architectural decisions is:

**Should I use traditional code, an LLM, or an AI agent?**

These are three different approaches to solving a problem.

- **Deterministic workflow:** Your code defines the steps and rules.
- **AI workflow:** An LLM performs tasks such as understanding language, extracting information, or generating responses within a predefined process.
- **AI agent:** An LLM-driven system can choose actions dynamically and continue working based on the results.

Let's understand them through an example.

Imagine you're building an AI-powered customer support application.

A customer asks:

    "Where is my order, and can you cancel it if it hasn't shipped?"

There are several ways to handle this request.

### Approach 1: Traditional code

    Receive order ID
        ↓
    Fetch order
        ↓
    Check shipping status
        ↓
    Apply cancellation rules
        ↓
    Return result

This works well when the input and business process are clearly defined.

### Approach 2: AI workflow

    Customer's natural-language request
                ↓
           LLM extracts intent
                ↓
        { intent, order_id }
                ↓
       Application validates data
                ↓
       Predefined workflow executes
                ↓
           Return result

The LLM helps interpret the customer's language, but the application controls the workflow.

### Approach 3: AI agent

    Customer's request
           ↓
          Agent
           ↓
    Choose an action
           ↓
    Inspect the result
           ↓
    Choose the next action
           ↓
    Continue until finished
           ↓
    Return result

The agent can decide dynamically whether it needs to look up an order, check its status, retrieve the cancellation policy, or ask the customer a follow-up question.

However, the application must still enforce permissions and cancellation rules.

**The key difference is not simply whether an LLM is present. It is how much control the system gives the LLM over the execution flow.**

---

## 2. Deterministic Workflows

### What are they?

A deterministic workflow is a process where the application defines the execution steps and decision rules.

For example:

    Input
      ↓
    Validate input
      ↓
    Fetch database record
      ↓
    Apply business rules
      ↓
    Update database
      ↓
    Return result

The program determines what happens next.

For the same inputs and state, a correctly designed deterministic workflow should generally produce the same behavior, assuming external dependencies and relevant environmental conditions remain unchanged.

### Why do they exist?

Traditional software is excellent at tasks with explicit rules.

Examples include:

- Calculating prices.
- Checking permissions.
- Processing payments.
- Updating database records.
- Applying refund policies.
- Validating user input.
- Enforcing rate limits.
- Managing transactions.

Consider a refund policy:

    If order is cancelled before shipment:
        Refund is allowed.

    Otherwise:
        Follow the post-shipment refund policy.

This should be implemented as application logic, not left to an LLM to interpret and enforce on its own.

### How they work

The workflow is defined before execution.

    Step A → Step B → Decision → Step C or Step D

The decision logic lives in code.

A simplified example in JavaScript:

    async function getOrderStatus(orderId, userId) {
      const order = await db.orders.findById(orderId);

      if (!order) {
        throw new Error("Order not found");
      }

      if (order.userId !== userId) {
        throw new Error("Access denied");
      }

      return {
        orderId: order.id,
        status: order.status
      };
    }

The application fetches the order, checks ownership, and returns the result.

No LLM is necessary.

### Advantages

- Predictable behavior.
- Easier testing.
- Clear security boundaries.
- Straightforward debugging.
- Usually lower cost and latency than adding an LLM.
- Strong control over business rules.

### Limitations

Traditional code becomes less convenient when inputs are ambiguous, unstructured, or expressed in many different ways.

For example, customers might say:

- "Where's my package?"
- "Has my order shipped?"
- "I haven't received my purchase yet."
- "Can you check when my delivery will arrive?"

A traditional application can handle these variations with explicit rules, but maintaining those rules can become cumbersome.

This is where an LLM may help.

---

## 3. AI Workflows

### What are they?

An AI workflow combines LLM capabilities with a process that your application largely defines in advance.

The LLM handles tasks that benefit from language understanding or generation, while ordinary code handles predictable execution.

For example:

    Customer message
          ↓
    LLM classifies intent
          ↓
    Application validates result
          ↓
    Predefined workflow
          ↓
    Database / external API
          ↓
    LLM generates response
          ↓
    Customer

The overall workflow remains controlled by your application.

### Why do AI workflows exist?

Many useful tasks are difficult to handle with rigid rules alone.

Consider these messages:

    "My package is taking forever."

    "The delivery was supposed to arrive yesterday."

    "Tracking says delivered, but nothing is here."

They might all concern an order, but they represent different situations.

An LLM can help classify the intent, extract relevant details, and understand the customer's actual request.

The backend can then execute the appropriate workflow.

### Example: Customer support

Suppose your application needs to categorize a message.

Input:

    "I was charged twice for my subscription."

The LLM returns:

    {
      "category": "billing",
      "intent": "duplicate_charge",
      "priority": "high"
    }

Your application validates the result and routes the ticket to the billing workflow.

The architecture is:

    Natural-language input
            ↓
    LLM classification
            ↓
    Structured output validation
            ↓
    Deterministic routing
            ↓
    Ticket creation
            ↓
    Response generation

Notice that the LLM doesn't control every step.

It performs the task where it adds value, while the application maintains control over the business process.

### Common AI workflow use cases

- Document extraction.
- Customer support classification.
- Summarization.
- Information extraction.
- Content generation.
- RAG question answering.
- Translation.
- Converting natural language into structured filters.
- Generating reports from retrieved data.

### Advantages

- Handles flexible language.
- Integrates naturally with existing software.
- Keeps business processes understandable.
- Easier to constrain than a fully dynamic agent.
- Can use LLMs without making every decision probabilistic.

### Limitations

- LLM outputs can be incorrect.
- Structured output can still contain semantically wrong values.
- The predefined workflow may not cover every situation.
- Additional model calls increase latency and cost.

The solution is not to remove the LLM. It is to place it inside a well-designed system with validation, fallbacks, and clear boundaries.

---

## 4. AI Agents

### What is an AI agent?

An AI agent is a system in which an LLM or another decision-making component selects actions based on the current task, available tools, and results from previous steps.

The exact definition of an agent varies across the industry, but the important characteristic for this course is **dynamic control flow**.

A traditional workflow says:

    Execute A → Execute B → Execute C

An agent can behave more like:

    Observe current state
          ↓
    Decide what to do next
          ↓
    Execute an action
          ↓
    Inspect the result
          ↓
    Decide again

The next step depends on what happened previously.

### Why do agents exist?

Some tasks cannot be fully specified as a short, fixed sequence of steps.

Consider this request:

    "Investigate why our production API
    became slow this morning and suggest
    how to fix it."

An agent might need to:

1. Inspect monitoring data.
2. Check recent deployments.
3. Examine error logs.
4. Compare latency across endpoints.
5. Investigate a suspected database bottleneck.
6. Gather more evidence.
7. Prepare a diagnosis and recommendations.

The next action depends on the findings.

If logs reveal database timeouts, the agent might investigate database performance. If the logs instead reveal repeated upstream failures, it might investigate the external service.

A fixed workflow can also implement these branches, but a dynamic investigation with many possible paths is one area where agents can be useful.

### How an agent works

A simplified agent loop:

    ┌─────────────────────────┐
    │ Receive goal and context│
    └────────────┬────────────┘
                 ↓
    ┌─────────────────────────┐
    │ Decide next action      │
    └────────────┬────────────┘
                 ↓
    ┌─────────────────────────┐
    │ Validate and execute    │
    │ selected tool           │
    └────────────┬────────────┘
                 ↓
    ┌─────────────────────────┐
    │ Observe tool result     │
    └────────────┬────────────┘
                 ↓
       Is the task complete?
           ↙           ↘
         No             Yes
          │               │
          └── Decide      ↓
             again     Respond

In practice, the model may produce a tool call rather than a normal text response. The orchestration layer executes the tool and sends the result back to the model.

The model then decides whether to call another tool, ask a question, or finish.

### Important distinction

The LLM does not automatically execute your application's functions.

Your application or agent runtime must:

- Expose available tools.
- Receive the model's requested action.
- Validate the arguments.
- Check authorization.
- Execute the tool.
- Return the result.
- Decide whether to continue or stop.

This separation is fundamental to secure agent design.

---

## 5. Comparing the Three Approaches

| Characteristic | Deterministic workflow | AI workflow | AI agent |
|---|---|---|---|
| Main controller | Application code | Application code | LLM-driven decisions within an application-controlled runtime |
| Execution path | Predetermined | Mostly predetermined | Can change dynamically |
| Uses an LLM | Not required | Yes | Usually yes |
| Handles flexible language | Requires explicit handling | Strong fit | Strong fit |
| Selects actions dynamically | Usually through coded rules | Usually limited | A central capability |
| Predictability | Generally high | Mixed | More variable |
| Typical cost | Low | Moderate | Often higher |
| Testing complexity | Usually lower | Higher | Often substantially higher |
| Best fit | Explicit rules | Known process with AI tasks | Open-ended, multi-step tasks |

These are general tendencies, not absolute rules. An agent can be constrained to a narrow path, and an AI workflow can contain many model-driven decisions.

---

## 6. The Most Important Architecture Decision

A common mistake is to assume:

    More AI = Better application

That is not true.

Suppose you're building an expense management system.

The system needs to:

- Extract receipt details.
- Calculate reimbursement amounts.
- Check company policy.
- Verify the employee's permissions.
- Request approval.
- Record the expense.

A sensible design might be:

| Task | Recommended approach |
|---|---|
| Extract merchant and amount from receipt | Multimodal LLM |
| Validate extracted fields | Schema validation in code |
| Calculate reimbursement | Deterministic code |
| Check employee authorization | Deterministic code |
| Retrieve relevant policy | RAG or database lookup |
| Interpret an ambiguous policy question | LLM |
| Request manager approval | Deterministic workflow |
| Investigate an unusual, multi-step expense issue | Potentially an agent |

The system doesn't need an agent for every step.

It needs the right combination of AI and ordinary software.

**Use AI where flexibility adds value. Use code where correctness and control matter most.**

---

## 7. Workflow vs Agent: A More Detailed Example

Imagine an AI research assistant.

The user asks:

    "Compare the latest approaches to RAG,
    identify their weaknesses, and prepare
    a report with supporting sources."

### Option A: Deterministic workflow

You define a fixed pipeline:

    Search sources
        ↓
    Retrieve documents
        ↓
    Summarize each document
        ↓
    Generate comparison
        ↓
    Generate report

This is suitable if the task is standardized and the pipeline reliably gathers enough evidence.

### Option B: AI workflow

The same fixed pipeline uses LLMs to summarize documents, extract comparison criteria, and generate the report.

The sequence is still predefined, but several steps use AI.

### Option C: Agent

The agent can decide that it needs more information.

For example:

    Search RAG approaches
          ↓
    Compare retrieved sources
          ↓
    Notice missing evaluation evidence
          ↓
    Search for benchmark studies
          ↓
    Compare evaluation methods
          ↓
    Check whether claims have support
          ↓
    Produce report

The agent adapts its actions to intermediate findings.

However, the agent can still fail: it may search poorly, repeat actions, miss important sources, or draw unsupported conclusions.

A production implementation needs limits, evidence checks, source tracking, and evaluation.

---

## 8. Reliability: Why Agents Need More Engineering

An ordinary function might look like this:

    calculateTax(income)

You define its behavior and test its inputs and outputs.

An agent is more complicated because it can make a sequence of decisions.

Potential failures include:

- Selecting the wrong tool.
- Passing invalid arguments.
- Repeating the same tool call.
- Misinterpreting tool results.
- Stopping too early.
- Continuing unnecessarily.
- Taking an action the user did not intend.
- Producing a confident but unsupported conclusion.

For example, an agent asked to cancel an order might repeatedly attempt cancellation after receiving an error.

A robust system should include:

- Maximum step or iteration limits.
- Tool timeouts.
- Retry limits.
- Argument validation.
- Authorization checks.
- Idempotency for operations that may be retried.
- Human approval for consequential actions.
- Logging and tracing.
- Evaluation of successful and failed runs.

An agent should not be allowed to loop indefinitely or execute arbitrary actions merely because the model requests them.

---

## 9. Human Approval and Consequential Actions

Consider an agent that can:

- Read emails.
- Draft replies.
- Send emails.
- Delete emails.

These tools have different levels of risk.

Reading an email is generally less consequential than sending a message or permanently deleting one.

You can design different permissions:

    Read email
        → Allowed after authorization

    Draft reply
        → Allowed

    Send reply
        → Require confirmation

    Permanently delete email
        → Stronger authorization or confirmation

The model may recommend an action, but the application determines whether the action is permitted.

This pattern is known as **human-in-the-loop control** when a person participates in reviewing or approving an operation.

It is especially important when agents can change external systems or perform irreversible actions.

---

## 10. A Practical Decision Framework

Before building an AI feature, ask these questions.

**Question 1: Can ordinary code solve the problem reliably?**

If yes, start with ordinary code.

**Question 2: Does the problem involve ambiguous language, unstructured documents, or flexible interpretation?**

If yes, consider adding an LLM.

**Question 3: Is the sequence of steps mostly known in advance?**

If yes, a predefined AI workflow is often a good fit.

**Question 4: Must the system choose among many possible next actions based on intermediate results?**

If yes, consider an agent.

**Question 5: Would an incorrect action cause significant harm or financial loss?**

If yes, strengthen validation, authorization, transaction handling, and human approval. An agent is not a replacement for these controls.

### Simple decision tree

    Can code solve the task?
          │
       Yes ─────→ Use code
          │
          No / AI adds value
          ↓
    Is the workflow mostly predefined?
          │
       Yes ─────→ AI workflow
          │
          No
          ↓
    Does it need dynamic,
    multi-step decision-making?
          │
       Yes ─────→ Consider an agent
          │
          No
          ↓
    Reconsider a simpler AI workflow

This is a starting point, not a strict rule. Sometimes a hybrid architecture is best.

---

## 11. Common Mistakes

### Mistake 1: Using an agent for a simple task

If a model can classify a ticket and your code can route it, you may not need an agent loop.

### Mistake 2: Putting business rules inside prompts

Instructions such as "never allow an unauthorized refund" are not sufficient security controls.

Enforce authorization and refund rules in code.

### Mistake 3: Confusing tool calling with an agent

A model can call a single tool in an otherwise fixed workflow.

**Tool calling alone does not make a system a sophisticated agent.** Dynamic, multi-step decision-making is the more important distinction in this lesson.

### Mistake 4: Assuming agents are always more intelligent

An agent can make more mistakes simply because it has more opportunities to choose incorrectly.

### Mistake 5: Giving an agent unrestricted permissions

Expose only the tools it needs, and enforce authorization independently of the model.

### Mistake 6: Ignoring cost and latency

An agent may need several model calls and tool executions to complete one user request.

Measure the full task, not just the latency of one model call.

### Mistake 7: Making everything deterministic

The opposite mistake also exists. Hard-coded rules can become unnecessarily complicated when the real task is interpreting flexible language or investigating an open-ended problem.

The objective is to choose the appropriate abstraction, not to avoid AI entirely.

---

## 12. Interview Perspective

**Q1. What is the difference between an AI workflow and an AI agent?**

An AI workflow generally follows a predefined execution process with AI used for selected tasks. An agent can dynamically choose its next action based on the goal, current state, and previous results.

**Q2. Does using an LLM make a workflow an agent?**

No. A fixed pipeline can use several LLM calls without being an agent.

**Q3. Is tool calling the same as agentic behavior?**

No. Tool calling is a capability. An agent can use tool calling as part of a dynamic, multi-step loop.

**Q4. Why not use agents for every GenAI application?**

Agents generally introduce additional latency, cost, nondeterminism, testing complexity, and failure modes. Many applications are better served by fixed workflows.

**Q5. How should an application secure an agent's tool calls?**

Validate tool arguments, enforce user and resource authorization, restrict available capabilities, apply limits, and require approval where appropriate. Never treat the model's decision as proof of permission.

**Q6. Can a production application combine all three approaches?**

Yes. A typical application uses deterministic code for business rules, AI workflows for language-related tasks, and agents for selected open-ended tasks.

---

## 13. Summary

- **Deterministic workflows** are best suited to explicit rules and predictable operations.
- **AI workflows** combine LLM capabilities with a mostly predefined process.
- **AI agents** can select actions dynamically and adapt to intermediate results.
- An LLM call does not automatically make an application agentic.
- Tool calling is a capability that workflows and agents can both use.
- Use deterministic code for authorization, calculations, database integrity, and critical business rules.
- Use LLMs for tasks such as language understanding, extraction, summarization, and flexible interpretation.
- Use agents when dynamic, multi-step decisions provide meaningful value.
- Agents need bounded execution, permissions, monitoring, testing, and failure handling.
- Human approval is valuable for consequential actions.

## One sentence to remember

**Use code to enforce rules, AI workflows to add intelligence to known processes, and agents when a task genuinely benefits from dynamically choosing its next steps.**

## Next lesson — Phase 2, Lesson 7: RAG — Why It Exists and How It Works

We'll begin Retrieval-Augmented Generation (RAG), one of the most important patterns in production GenAI. We'll understand why an LLM needs external knowledge, how retrieval works, and how the complete pipeline connects to a real application.