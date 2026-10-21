# Lesson 2 — Anatomy of a Production GenAI Application

## 1. Concept

A production GenAI application is usually a combination of:

```
Traditional Software
+
AI Components
+
Data
+
External Tools
+
Safety / Reliability Infrastructure
```

A useful mental model is:

```
User
  ↓
Frontend
  ↓
Backend API
  ↓
AI Orchestrator
  ↓
┌──────────────┬──────────────┐
│              │              │
Knowledge     Actions        Memory
│              │              │
RAG           Tools          DB
Vector DB     MCP
│              │
└──────────────┴──────┐
                      ↓
                     LLM
                      ↓
                Validation
                      ↓
                   Response
```

Around this pipeline:

```
Authentication
Authorization
Guardrails
Evaluation
Observability
Caching
Rate limiting
Cost control
```

The key idea is:

> **An AI application is an orchestration system around one or more models.**

---

# 2. Why do we need an orchestration layer?

Consider a simple application.

```
User
  ↓
Backend
  ↓
LLM
  ↓
Response
```

This works for:

```
"Explain recursion."
```

But imagine:

```
"Read my company's leave policy,
 tell me how many days I have left,
 and submit leave for next Monday."
```

Now the backend may need to:

```
1. Understand the request
2. Retrieve company policy
3. Query the employee database
4. Determine available leave
5. Decide whether submission is allowed
6. Ask for confirmation
7. Submit the request
8. Return the result
```

This logic belongs somewhere.

That "somewhere" is often called:

```
AI Orchestration Layer
```

It coordinates:

```
LLM
Retrieval
Tools
Agents
Memory
Validation
Business logic
```

---

# 3. A complete request lifecycle

Let's follow one request from beginning to end.

User asks:

```
"Can I take leave next Monday?
 If yes, submit it."
```

The request might flow like this:

```
React
  ↓
POST /api/assistant
  ↓
Authentication
  ↓
Authorization
  ↓
AI Orchestrator
  ↓
Retrieve relevant policy
  ↓
LLM
  ↓
Tool selection
  ↓
Check leave balance
  ↓
Business rules
  ↓
Confirmation / approval
  ↓
Submit leave
  ↓
LLM
  ↓
Response
  ↓
React
```

Notice something important.

The LLM isn't necessarily involved in every step.

For example:

```
Authentication
Authorization
Leave balance
Leave creation
Database transaction
```

should normally be handled by deterministic software.

The LLM should handle tasks where language understanding or reasoning is useful.

---

# 4. Deterministic vs probabilistic components

This distinction is extremely important.

## Deterministic software

Traditional code behaves predictably.

For example:

```
if (leaveBalance >= requestedDays) {
    approve();
}
```

Given the same state, the result is predictable.

## Probabilistic AI

An LLM may produce different outputs for the same request.

For example:

```
"Should this employee take leave?"
```

The model might interpret the request differently depending on context.

Therefore:

> **Use AI for tasks where flexibility and language understanding are valuable. Use deterministic code for rules that must be guaranteed.**

This principle will appear repeatedly throughout the course.

---

# 5. What should the LLM do?

Good candidates for the LLM:

* Understand natural language
* Extract information
* Summarize
* Classify
* Generate text
* Reason over provided context
* Select tools
* Transform information
* Produce structured output

For example:

```
User:
"I need two days off next Thursday and Friday."
```

LLM can convert this into:

```
{
  "startDate": "...",
  "endDate": "...",
  "days": 2
}
```

But the backend should validate the result.

---

# 6. What should traditional code do?

Good candidates for deterministic code:

* Authentication
* Authorization
* Database transactions
* Financial calculations
* Permission checks
* Rate limiting
* Security policies
* Data validation
* Business rules
* Tool execution
* Resource access

For example:

```
LLM:
"The user should be allowed to delete the account."
```

Your backend should NOT simply execute:

```
deleteAccount()
```

Instead:

```
LLM decision
    ↓
Backend authorization
    ↓
Check actual user permissions
    ↓
Execute operation if allowed
```

The LLM can recommend an action.

Your application decides whether that action is permitted.

---

# 7. The AI Orchestrator

Think of the orchestrator as the coordinator.

For example:

```
async function handleRequest(request) {

    authenticateUser();

    const intent = await understandRequest(request);

    const context = await retrieveContext(intent);

    const decision = await llm({
        request,
        context
    });

    if (decision.requiresTool) {
        const result = await executeTool(decision.tool);

        return await generateResponse(result);
    }

    return decision.response;
}
```

This is simplified, but the architectural idea is important.

The orchestrator coordinates multiple components.

---

# 8. A better architecture

A production application may look like:

```
┌───────────────────────────────┐
│           Frontend            │
│             React             │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          API Gateway          │
│ Auth / Rate Limit / Routing   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       AI Orchestration        │
│                               │
│  Prompt / Context / Workflow  │
└───────┬───────────┬───────────┘
        │           │
        ▼           ▼
    Retrieval      Tools
        │           │
        ▼           ▼
    Vector DB    External APIs
        │
        └──────┬────┘
               ▼
              LLM
               │
               ▼
         Validation
               │
               ▼
            Response
```

And around everything:

```
Observability
Evaluation
Security
Caching
Logging
```

---

# 9. Request context

One of the most important concepts in GenAI applications is:

**Context**

The LLM does not automatically know everything your application knows.

You have to provide the relevant information.

For example:

```
User asks:

"What is our refund policy?"
```

The model needs:

```
System instructions
+
User question
+
Retrieved company policy
+
Conversation context
```

Conceptually:

```
┌───────────────────────┐
│ System Instructions   │
├───────────────────────┤
│ Conversation History  │
├───────────────────────┤
│ Retrieved Context     │
├───────────────────────┤
│ Tool Results          │
├───────────────────────┤
│ Current User Request  │
└───────────────────────┘
            ↓
           LLM
            ↓
         Response
```

This entire collection becomes the model's **context**.

We'll study context engineering in much greater depth later.

---

# 10. Context is not the same as memory

This distinction is important.

Suppose a user says:

```
"My name is Rahul."
```

The current request may contain:

```
User:
My name is Rahul.
```

That is context.

If the application stores:

```
user.name = "Rahul"
```

and retrieves it in future conversations, that's application memory.

So:

```
Context
=
Information supplied to the model for the current interaction.

Memory
=
Information stored and retrieved across interactions.
```

We'll revisit this when discussing agents and state.

---

# 11. RAG fits into the context pipeline

Suppose the user asks:

```
"What's our remote work policy?"
```

The application doesn't want to send every company document to the LLM.

Instead:

```
User question
      ↓
Embedding / retrieval
      ↓
Relevant documents
      ↓
Context
      ↓
LLM
      ↓
Answer
```

So RAG is essentially a **context construction mechanism**.

This is a useful mental model.

Instead of thinking:

> RAG = vector database

think:

> **RAG = retrieving useful external information and putting it into the model's context.**

A vector database is only one possible component used to achieve that.

---

# 12. Tools fit into the context pipeline too

Consider:

```
User:
"What's my current bank balance?"
```

The LLM doesn't know.

The application provides a tool:

```
getBankBalance()
```

Flow:

```
User
  ↓
LLM
  ↓
Tool request
  ↓
Backend
  ↓
Bank API
  ↓
Tool result
  ↓
LLM
  ↓
Response
```

The tool result becomes new context for the LLM.

So both RAG and tools provide the model with additional information.

The difference is:

```
RAG
→ retrieves information

Tool
→ performs an action or retrieves live information
```

---

# 13. Workflow vs Agent

This distinction is very important for your future interviews.

Suppose we have:

```
User
  ↓
Retrieve policy
  ↓
Check balance
  ↓
Submit leave
  ↓
Respond
```

This is a predefined workflow.

The application knows the steps.

A workflow can be represented as:

```
A → B → C → D
```

Now consider:

```
User:
"Plan my business trip to Delhi."
```

The system may need to:

```
Search flights
Search hotels
Check calendar
Compare options
Ask questions
Re-search
Book something
```

The next step may depend on what happened previously.

That's more agent-like:

```
A
↓
Decide
↓
B
↓
Observe
↓
Decide
↓
C
↓
...
```

So:

> **Workflow = predefined execution path.**

> **Agent = dynamically chooses the next action based on state/context/results.**

This distinction will become extremely important when we study agents.

---

# 14. Where MCP fits

MCP doesn't replace the orchestrator.

Instead, it can standardize how external capabilities are exposed.

For example:

```
AI Application
      ↓
   MCP Client
      ↓
┌─────┼────────┐
↓     ↓        ↓
GitHub Slack  Database
MCP    MCP      MCP
Server Server   Server
```

The orchestration layer still decides:

```
"Should I use this tool?"
```

MCP provides a standardized way to expose and interact with those capabilities.

---

# 15. Where guardrails fit

Guardrails can exist at multiple points.

For example:

```
User
  ↓
Input Guardrail
  ↓
AI Orchestrator
  ↓
LLM
  ↓
Output Guardrail
  ↓
Tool Authorization
  ↓
Tool
  ↓
Response
```

There isn't necessarily one single "guardrail".

There can be multiple controls.

For example:

```
Input:
Detect malicious prompt

Output:
Validate structured response

Tool:
Check permissions

Data:
Prevent sensitive information leakage
```

---

# 16. Production concerns

A prototype might look like:

```
User → Backend → LLM → Response
```

A production system must answer much harder questions.

### Reliability

What happens if the LLM API fails?

### Latency

What if the request takes 10 seconds?

### Cost

What if one user generates thousands of requests?

### Security

What if a retrieved document contains a malicious prompt?

### Scale

What if 10,000 users call the system simultaneously?

### Observability

How do we know why a request failed?

### Evaluation

How do we know the model got better after changing the prompt?

### Versioning

What happens when we change the model?

These concerns are what turn a GenAI demo into an actual software engineering problem.

---

# 17. A production request example

Let's combine everything.

User:

```
"Find our refund policy and
 refund my latest order if I'm eligible."
```

Possible flow:

```
1. React sends request

2. Backend authenticates user

3. AI orchestrator receives request

4. RAG retrieves refund policy

5. LLM determines required information

6. Tool retrieves latest order

7. Backend checks authorization

8. Backend checks deterministic refund rules

9. If refund is allowed:
       request confirmation

10. User confirms

11. Backend executes refund

12. LLM generates explanation

13. Response streamed to frontend

14. Observability records:
       - latency
       - tokens
       - retrieval
       - tool calls
       - errors
       - cost
```

Notice the division of responsibilities.

### LLM

```
Understand
Reason
Generate
Select tools
```

### Application

```
Authenticate
Authorize
Validate
Execute
Enforce business rules
```

### RAG

```
Provide knowledge
```

### Tools

```
Access external systems
```

### Guardrails

```
Control AI behavior
```

### Observability

```
Tell us what happened
```

---

# 18. Important architectural principle

A very important principle for senior engineers:

> **Don't put business logic inside the prompt when it should be enforced by code.**

Bad:

```
System prompt:

"Never allow refunds above $500."
```

This is only an instruction to a probabilistic model.

Better:

```
LLM
  ↓
"Refund requested: $750"
  ↓
Backend business rule
  ↓
if amount > 500
    reject
```

The prompt can tell the LLM how to behave.

But critical rules should be enforced by deterministic systems.

---

# 19. Another important principle

> **Use the simplest architecture that solves the problem.**

Don't automatically build an agent.

For example:

```
User asks:
"Summarize this PDF."
```

You probably don't need:

```
Agent
+ 8 tools
+ MCP
+ multi-agent system
+ vector DB
```

A simple pipeline is enough:

```
PDF
  ↓
Extract text
  ↓
LLM
  ↓
Summary
```

But:

```
"Research competitors, search multiple sources,
 compare findings, generate a report, and cite sources"
```

may benefit from more complex orchestration.

The complexity should come from the problem, not from the excitement around AI.

---

# 20. Interview perspective

## Question: What is an AI orchestration layer?

A strong answer:

> It is the application layer responsible for coordinating LLM calls with retrieval, tools, memory, workflows, agents, validation, and business logic. It controls how information and actions flow through the AI system rather than treating the LLM as the entire application.

---

## Question: What should not be delegated to an LLM?

Things such as:

* authorization
* security enforcement
* financial calculations
* critical business rules
* database transactions
* permission checks

These should be enforced deterministically by application code.

---

## Question: What is the difference between RAG and a tool?

A useful distinction:

```
RAG
→ retrieve relevant knowledge

Tool
→ retrieve live information or perform an action
```

For example:

```
"What is our vacation policy?"
→ RAG

"How many vacation days do I have?"
→ Tool / database query

"Apply for vacation."
→ Tool / business API
```

---

## Question: Workflow vs Agent?

```
Workflow:
predefined steps

Agent:
dynamically decides what to do next
```

Don't use an agent when a deterministic workflow is sufficient.

---

# 21. Practical mental model

When designing a GenAI feature, ask these questions in order:

### 1. Does the model need to understand natural language?

If no, don't use an LLM.

### 2. Does it need external/private knowledge?

If yes, consider RAG.

### 3. Does it need live information or actions?

If yes, consider tools.

### 4. Does it need to dynamically decide which actions to take?

If yes, consider an agent.

### 5. Does it need access to external AI-compatible capabilities?

Consider MCP.

### 6. Could the model produce dangerous or invalid behavior?

Add guardrails and deterministic authorization.

### 7. How will we know whether it works?

Build evaluation.

### 8. How will we debug it in production?

Add observability.

### 9. How will it handle high traffic?

Design for scaling, caching, queues, rate limits, and model capacity.

This decision-making framework will be useful throughout the course.

---

# 22. Summary

A production GenAI application is not:

```
Frontend
  ↓
LLM
  ↓
Response
```

It is closer to:

```
Frontend
   ↓
Backend
   ↓
Authentication
   ↓
AI Orchestration
   ↓
┌──────────┬──────────┬──────────┐
│          │          │
RAG       Tools      Agents
│          │          │
Vector DB  APIs       MCP
│          │          │
└──────────┴──────────┘
            ↓
           LLM
            ↓
       Validation
            ↓
         Response
```

With:

```
Guardrails
Evaluation
Observability
Caching
Security
Scaling
Deployment
```

around the system.

The most important takeaway:

> **GenAI engineering is primarily about designing reliable software systems around probabilistic models.**

Your existing full-stack experience is therefore highly relevant. You are not starting software engineering from zero—you are learning the **AI layer that plugs into the software systems you already understand.**

---

# Next Lesson

**Lesson 3 — LLM Providers, Models and APIs**

We will move from architecture into the actual model layer:

```
OpenAI / Anthropic / Google / open-source models
↓
Model APIs
↓
Requests / responses
↓
System + user messages
↓
Structured output
↓
Streaming
↓
Model selection
```

The goal will be to understand **what actually happens when your backend makes an LLM API call**, rather than treating `llm.generate()` as a black box.
