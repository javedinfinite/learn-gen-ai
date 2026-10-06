# Lesson 1 — Modern GenAI Application Stack

## 1. Concept

A modern GenAI application is not simply:

```
User → LLM → Answer
```

That is the simplest possible application.

A real production GenAI application usually looks more like:

```
User
  ↓
Frontend
  ↓
Backend / API
  ↓
AI Orchestration Layer
  ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │
RAG          Tools          Agents
│              │              │
Vector DB    APIs/DBs       MCP
│              │              │
└──────────────┴──────────────┘
               ↓
              LLM
               ↓
        Guardrails / Validation
               ↓
          Final Response
```

Around this entire pipeline we also have:

```
Evaluation
Observability
Security
Caching
Cost management
Scaling
Deployment
```

The important thing to understand is:

> **The LLM is only one component of a GenAI application.**

This is one of the most important mindset shifts for a software engineer entering GenAI.

---

# 2. Why does this architecture exist?

A raw LLM has limitations.

Suppose you call:

```
LLM("What is our company's vacation policy?")
```

The model may not know your company's policy.

Why?

Because the information is probably:

* private
* constantly changing
* not part of the model's training data

So we need **RAG**.

Now suppose you ask:

```
"Cancel my flight."
```

The LLM cannot actually cancel the flight by itself.

It needs access to a tool/API:

```
LLM
  ↓
cancelFlight()
  ↓
Airline API
```

So we need **tool calling**.

Now suppose the task requires several decisions:

```
"Find the cheapest flight to Delhi,
 check my calendar,
 make sure I have no meeting,
 and book it."
```

This may require multiple steps and tools.

That's where **agents** can become useful.

Now suppose the agent has access to powerful tools.

We need to prevent:

```
LLM → deleteDatabase()
```

when it shouldn't.

That's where **guardrails and authorization** come in.

Finally, once the system is running in production, we need to know:

* Did retrieval work?
* Did the model hallucinate?
* How many tokens did we use?
* Why did this request take 8 seconds?
* Which tool failed?
* How much did this request cost?

That's where **evaluation and observability** come in.

---

# 3. The major components

Let's understand the role of each component.

## 3.1 Frontend

This is the normal application layer you're already familiar with.

For example:

```
React
  ↓
Chat UI
  ↓
Backend API
```

The frontend might provide:

* chat interface
* file upload
* citations
* streaming responses
* tool execution status
* approval buttons
* conversation history

Nothing magical here.

The difference is that AI applications often need to represent **long-running and non-deterministic operations**.

---

# 3.2 Backend

The backend remains extremely important.

For example:

```
React
  ↓
Node.js / Python API
  ↓
AI services
```

The backend might handle:

* authentication
* authorization
* users
* conversations
* files
* database access
* AI orchestration
* tool permissions
* billing
* rate limiting

Your existing backend knowledge transfers directly here.

---

# 3.3 LLM

The LLM is the reasoning/generation engine.

Examples of things an LLM can do:

```
Input:
"Summarize this document."

Output:
Summary
```

Or:

```
Input:
"Which function should I call?"

Output:
Tool selection
```

Or:

```
Input:
"Generate SQL for this request."

Output:
SQL
```

The important distinction is:

> An LLM generates decisions/text/structured outputs, but your application is responsible for executing and enforcing those decisions.

For example:

```
LLM says:

{
  "tool": "getWeather",
  "city": "Delhi"
}
```

Your backend executes:

```
getWeather("Delhi")
```

The LLM did not actually call the weather API.

Your application did.

---

# 3.4 Embeddings

Embeddings convert information into vectors.

Conceptually:

```
"How do I reset my password?"
                 ↓
            Embedding Model
                 ↓
         [0.12, -0.43, 0.91, ...]
```

Another sentence:

```
"I forgot my password."
                 ↓
            Embedding Model
                 ↓
         [0.10, -0.40, 0.89, ...]
```

These vectors can be mathematically compared.

If their vectors are close, the meanings are likely similar.

This becomes extremely useful for **semantic search**.

And semantic search is one of the foundations of RAG.

---

# 3.5 Vector Database

A vector database stores embeddings and allows us to search for similar vectors.

Imagine we have:

```
Company documents

    ↓

Chunk documents

    ↓

Generate embeddings

    ↓

Store in Vector DB
```

Then the user asks:

```
"How many vacation days do employees get?"
```

We generate an embedding for that question.

Then:

```
Question embedding
      ↓
   Vector DB
      ↓
Relevant document chunks
```

Those chunks are given to the LLM.

This is the basic idea behind RAG.

---

# 3.6 RAG

RAG means:

**Retrieval-Augmented Generation**

Instead of:

```
User → LLM → Answer
```

we do:

```
User
  ↓
Retrieve relevant information
  ↓
Add information to context
  ↓
LLM
  ↓
Answer
```

Example:

```
User:
"What is our vacation policy?"

↓

Search company knowledge base

↓

Retrieve:
"Employees receive 25 annual vacation days..."

↓

Send to LLM:

Question:
What is our vacation policy?

Context:
Employees receive 25 annual vacation days...

↓

LLM

↓

Answer:
Employees receive 25 annual vacation days.
```

RAG allows an LLM to work with **external and current knowledge**.

---

# 3.7 Tools

Tools allow an LLM-powered application to interact with external systems.

Examples:

```
getWeather()
searchFlights()
createInvoice()
sendEmail()
queryDatabase()
createGitHubIssue()
```

The basic flow is:

```
User
  ↓
LLM
  ↓
"I need to call getWeather"
  ↓
Backend
  ↓
Weather API
  ↓
Result
  ↓
LLM
  ↓
Final answer
```

This is called **tool/function calling**.

---

# 3.8 Agents

An agent goes beyond a simple one-shot LLM call.

For example:

```
User:
"Find the cheapest flight to Delhi,
 check my calendar,
 and book it."
```

The system may need:

```
1. Search flights
2. Compare prices
3. Check calendar
4. Decide whether there is a conflict
5. Ask for approval
6. Book flight
```

This can become an agentic workflow.

Conceptually:

```
User
  ↓
Agent
  ↓
Think / decide next action
  ↓
Tool
  ↓
Result
  ↓
Agent
  ↓
Decide next action
  ↓
Tool
  ↓
...
  ↓
Final result
```

The key idea is **iteration**.

A normal LLM call is often:

```
Input → Output
```

An agent can be:

```
Input
  ↓
Decide
  ↓
Act
  ↓
Observe
  ↓
Decide
  ↓
Act
  ↓
...
  ↓
Result
```

---

# 3.9 MCP

MCP stands for:

**Model Context Protocol**

MCP provides a standardized way for AI applications to connect to external tools and data sources.

Instead of every AI application inventing its own integration mechanism:

```
AI App → Custom GitHub integration

AI App → Custom Slack integration

AI App → Custom Database integration
```

MCP aims to provide a common protocol:

```
AI Application
      ↓
     MCP
      ↓
┌─────┼─────┐
↓     ↓     ↓
GitHub Slack Database
```

Think of MCP as a standardized interface for exposing capabilities/data to AI systems.

We'll study this deeply later.

---

# 3.10 Guardrails

LLMs are probabilistic.

Your backend code usually isn't.

For example:

```
if (user.isAdmin) {
    deleteDatabase();
}
```

is deterministic.

But:

```
LLM:
"I think the user wants to delete the database."
```

is not something we should blindly trust.

Guardrails add boundaries around AI behavior.

Examples:

```
User Input
   ↓
Input Guardrail
   ↓
LLM
   ↓
Output Guardrail
   ↓
Application
```

We can also guard tools:

```
LLM
  ↓
Tool Request
  ↓
Authorization / Policy Check
  ↓
Tool
  ↓
External System
```

Important principle:

> **Never treat an LLM's decision as authorization.**

The application must enforce authorization.

---

# 3.11 Evaluation

Traditional software can often be tested like:

```
expected = 10
actual = calculate()

assert actual === expected
```

LLM applications are different.

Suppose the expected answer is:

```
"The company provides 25 vacation days."
```

The model might answer:

```
"Employees receive 25 days of annual vacation."
```

Is that correct?

Yes.

But an exact string comparison would fail.

Therefore, GenAI requires evaluation methods that can measure things like:

* correctness
* relevance
* groundedness
* retrieval quality
* hallucination
* safety

This becomes particularly important for RAG and agents.

---

# 3.12 Observability

When a production AI request takes 7 seconds, you want to know why.

Maybe:

```
LLM call       → 1.2 sec
Vector search  → 0.1 sec
Reranker       → 0.7 sec
Tool API       → 4.5 sec
Final LLM      → 0.5 sec
```

Without tracing, debugging this becomes difficult.

AI observability therefore tracks things such as:

* latency
* token usage
* model calls
* prompts
* responses
* retrieval
* tool calls
* errors
* cost

---

# 4. Putting everything together

Let's take a realistic example.

Imagine we're building:

**Company AI Assistant**

The user asks:

```
"What is our leave policy and
 create a leave request for next Monday."
```

The architecture could be:

```
React
  ↓
Backend API
  ↓
AI Orchestrator
  ↓
┌──────────────────────────┐
│                          │
│          RAG             │
│           ↓              │
│      Vector Database     │
│                          │
└──────────┬───────────────┘
           │
           ↓
          LLM
           │
           ↓
    Tool Selection
           │
           ↓
      Leave API
           │
           ↓
      Authorization
           │
           ↓
    Create Leave Request
           │
           ↓
         LLM
           │
           ↓
        Response
```

The system also has:

```
Guardrails
Evaluation
Observability
Caching
Rate limiting
```

Now you're no longer building "a chatbot".

You're building a **software system containing an LLM**.

That distinction is extremely important.

---

# 5. The most important mental model

Think about GenAI applications as four layers.

## Layer 1 — Intelligence

```
LLM
Embeddings
Multimodal models
```

This is where the model capabilities live.

## Layer 2 — Knowledge and Actions

```
RAG
Vector DB
Tools
MCP
External APIs
Databases
```

This gives the AI access to information and capabilities.

## Layer 3 — Control

```
Guardrails
Authentication
Authorization
Validation
Evaluation
```

This keeps the AI system reliable and safe.

## Layer 4 — Production Engineering

```
APIs
Queues
Caching
Observability
Scaling
Deployment
Cost optimization
```

This makes the system usable in the real world.

---

# 6. Important terminology

### LLM

Large Language Model.

Generates text, structured output, decisions, tool calls, etc.

### Embedding

A numerical representation of information that captures semantic relationships.

### Vector Database

A database optimized for storing and searching vectors.

### RAG

Retrieval-Augmented Generation.

Retrieve relevant external information and provide it to the LLM.

### Tool Calling

Allowing an LLM to request execution of predefined application functions.

### Agent

An AI system capable of iteratively deciding actions, using tools, observing results, and continuing toward a goal.

### MCP

Model Context Protocol.

A standardized protocol for connecting AI applications with external capabilities and data.

### Guardrail

A mechanism that constrains or validates AI inputs, outputs, actions, or tool usage.

### LLMOps

The engineering practices required to operate LLM applications in production.

---

# 7. Practical understanding

As a senior full-stack engineer, you should start thinking like this:

Traditional application:

```
User
  ↓
API
  ↓
Business Logic
  ↓
Database
  ↓
Response
```

GenAI application:

```
User
  ↓
API
  ↓
AI Orchestration
  ↓
┌───────────────┐
│               │
RAG           Tools
│               │
Vector DB    External APIs
│               │
└───────┬───────┘
        ↓
       LLM
        ↓
   Validation
        ↓
     Response
```

Production:

```
+ Authentication
+ Authorization
+ Guardrails
+ Evaluation
+ Observability
+ Caching
+ Rate limiting
+ Cost control
+ Scaling
+ Deployment
```

This is the mental model I want you to carry throughout the entire course.

---

# 8. Interview perspective

### Question

**"Is an LLM application just an API call to OpenAI/Anthropic/etc.?"**

A strong answer:

> No. An LLM is usually only one component of a production GenAI application. A real system may include retrieval, embeddings, vector databases, tool calling, agent orchestration, guardrails, evaluation, observability, caching, security, and scaling infrastructure around the model.

### Question

**"Why do we need RAG if LLMs already know a lot of information?"**

Because the model's knowledge may be:

* incomplete
* outdated
* unavailable for private company data
* difficult to reliably ground

RAG provides relevant external context at inference time.

### Question

**"Can an LLM directly execute a function?"**

Not by itself.

The LLM generates a structured tool request. The application executes the actual function and returns the result to the model.

### Question

**"Why can't we trust an agent to perform any action it decides?"**

Because LLM outputs are probabilistic. Authorization, permissions, validation, and business rules must remain enforced by deterministic application code.

---

# 9. What you should remember from Lesson 1

The most important idea is:

```
GenAI Application
=
LLM
+
Knowledge
+
Actions
+
Control
+
Production Engineering
```

Where:

```
Knowledge → RAG / Vector DB
Actions   → Tools / APIs / MCP
Control   → Guardrails / Security / Evaluation
Production → Scaling / Observability / Deployment
```

And:

> **The LLM is not the application. The LLM is one component inside the application.**

This distinction will make the rest of the syllabus much easier to understand.
