# Lesson 4 — Tokens, Context Windows, Temperature and Model Parameters

## 1. Concept

When we send a request to an LLM, we don't actually send "words" directly to the model.

The basic flow is:

    Text
      ↓
    Tokenization
      ↓
    Token IDs
      ↓
    Context
      ↓
    Model inference
      ↓
    Token generation
      ↓
    Final text

Four concepts are especially important when building GenAI applications:

- **Tokens** — how the model represents text
- **Context window** — how much information the model can consider in one request
- **Temperature / sampling** — how the model chooses the next token
- **Model parameters** — controls that influence generation behavior

These aren't just ML concepts.

They directly affect:

- RAG
- prompt design
- cost
- latency
- application performance
- conversation history
- chunking
- agent behavior
- scaling

---

# 2. Tokens

## What is a token?

A token is a piece of text that the model processes.

A token can be:

- part of a word
- a complete word
- punctuation
- whitespace
- special characters

For example, conceptually:

    "I love programming."

might become something like:

    ["I", " love", " programming", "."]

The exact tokenization depends on the model's tokenizer.

So:

    1 word ≠ 1 token

and:

    1 character ≠ 1 token

Different languages and different types of text can have very different tokenization behavior.

---

# 3. Why Do Tokens Matter?

Tokens matter because they are the basic unit used for several important limits and costs.

### 1. Context limits

The model can only process a limited number of tokens in one request.

### 2. Cost

LLM providers commonly charge based on input and output tokens.

### 3. Latency

More tokens generally mean more work for the model.

### 4. RAG

Retrieved documents consume context tokens.

### 5. Conversation history

A long conversation can consume a large portion of the available context.

### 6. Output size

A response containing thousands of tokens takes more generation work than a short response.

So as a GenAI engineer, you should think in terms of **token budgets**, not just characters or words.

---

# 4. Tokenization

Before an LLM processes text, a tokenizer converts the text into tokens.

Conceptually:

    "Build a RAG application"

becomes:

    ["Build", " a", " RAG", " application"]

which is then converted into token IDs:

    [...., ...., ...., ....]

The neural network works with these numerical IDs/representations rather than raw strings.

You normally don't need to implement tokenization yourself.

But you need to understand its consequences.

---

# 5. Token Budget

Suppose your application sends:

    System instructions       → 1,000 tokens
    Conversation history      → 3,000 tokens
    Retrieved documents       → 5,000 tokens
    User question             →   200 tokens
    -----------------------------------
    Input                     → 9,200 tokens

Then you ask the model to generate:

    Maximum output            → 1,000 tokens

Your request needs enough context capacity for both the input and the generated output, subject to the model/API's specific rules.

This is why blindly adding more documents to a RAG prompt is a bad idea.

More context is not automatically better.

---

# 6. Context Window

## What is a context window?

The **context window** is the amount of information a model can consider for a single inference request.

Think of it as the model's current working space.

For example:

    ┌─────────────────────────────────┐
    │          Context Window         │
    │                                 │
    │ System instructions             │
    │ Conversation history            │
    │ Retrieved documents             │
    │ Tool results                    │
    │ User request                    │
    │                                 │
    │        Available output         │
    └─────────────────────────────────┘

The exact maximum depends on the model.

Modern models can have very large context windows, but the important engineering principle remains:

> A larger context window does not mean you should put everything into it.

---

# 7. Context Is Not Memory

This distinction is extremely important.

Suppose the user says:

    My company uses PostgreSQL.

The LLM doesn't automatically remember that forever.

For a later request, your application may need to provide that information again.

So:

    Context = information supplied to the model for this request

while:

    Memory = information stored somewhere and retrieved when needed

Memory could be stored in:

- a database
- user profile
- conversation store
- vector database
- application state

The application decides what memory becomes part of the model's context.

---

# 8. What Goes Into Context?

A production request might look like:

    ┌───────────────────────────────┐
    │ System / developer instructions│
    ├───────────────────────────────┤
    │ Conversation history          │
    ├───────────────────────────────┤
    │ Retrieved RAG documents       │
    ├───────────────────────────────┤
    │ Tool results                  │
    ├───────────────────────────────┤
    │ Current user request          │
    ├───────────────────────────────┤
    │ Output budget                │
    └───────────────────────────────┘
                    ↓
                   LLM
                    ↓
                 Response

This is why context engineering becomes important later in this course.

The challenge isn't simply:

> "How much context can the model accept?"

The better question is:

> "What information should I give the model right now?"

---

# 9. Context Quality > Context Quantity

Imagine a user asks:

    "What is our company's refund policy?"

Your system retrieves 50 documents containing:

- refund policy
- employee handbook
- engineering documentation
- unrelated HR policies
- old versions of the refund policy
- marketing documents

Even if the model can technically fit all of them into its context, this is poor design.

A better system might retrieve:

    1. Current refund policy
    2. Relevant product-specific policy
    3. Important exception

The model now has less information but better information.

Therefore:

> More context ≠ better answer.

Good GenAI systems optimize **context relevance**.

---

# 10. The Context Budget Problem in RAG

This becomes especially important with RAG.

Suppose you have:

    100,000 documents

You obviously cannot put all documents into the prompt.

Instead:

    User Query
        ↓
    Retrieval
        ↓
    Top relevant documents
        ↓
    Context
        ↓
    LLM

For example:

    100,000 documents
          ↓
    retrieve 20 chunks
          ↓
    rerank
          ↓
    select 5 chunks
          ↓
    LLM

This is one of the reasons retrieval quality is so important.

We'll study this deeply in the RAG phase.

---

# 11. Context Management Strategies

When context becomes too large, production applications can use techniques such as:

### Truncation

Remove older or less important information.

### Sliding window

Keep only the most recent portion of conversation.

### Summarization

Compress older conversation into a summary.

For example:

    10,000 tokens of history
            ↓
        summary
            ↓
    1,000 tokens

### Retrieval

Instead of keeping everything in context, retrieve relevant information when needed.

### Selective tool results

Don't send unnecessary tool output back to the model.

### Context prioritization

Keep critical information and remove low-value information.

These techniques become increasingly important as applications become larger.

---

# 12. Temperature

Now we move from **what the model sees** to **how it generates the answer**.

Temperature controls how much randomness is used during token selection.

Conceptually, the model predicts probabilities for the next token:

    "The capital of France is..."

Possible next tokens might have probabilities like:

    Paris       0.95
    London      0.01
    Berlin      0.01
    Rome        0.01
    ...

With low randomness, the model strongly favors the highest-probability token.

With higher randomness, lower-probability candidates have a greater chance of being selected.

---

# 13. Low vs High Temperature

Conceptually:

    Low temperature
        ↓
    More predictable
    More consistent
    Less variation

versus:

    High temperature
        ↓
    More variation
    More creativity
    Less predictable

For example, for:

    "Give me three names for a coffee shop."

Low temperature might repeatedly produce conventional names.

Higher temperature might produce more unusual variations.

---

# 14. Temperature Does NOT Mean Intelligence

A common misunderstanding is:

> Higher temperature = smarter model

No.

Temperature doesn't increase the model's intelligence.

It changes the **sampling behavior during generation**.

Think:

    Model capability
          ≠
    Temperature

A powerful model with temperature 0 isn't necessarily less intelligent than the same model with temperature 1.

You're primarily changing how it chooses among possible outputs.

---

# 15. When Should You Use Lower Temperature?

Lower randomness is generally useful for tasks such as:

- structured extraction
- classification
- JSON generation
- tool arguments
- deterministic-ish transformations
- factual workflows
- code generation where consistency is valuable

For example:

    User
      ↓
    Extract:
      name
      age
      email
      phone
      ↓
    JSON

You generally don't want the model inventing wildly different structures each time.

---

# 16. When Can Higher Temperature Help?

Higher randomness can be useful for:

- brainstorming
- creative writing
- naming
- generating alternatives
- ideation
- creative marketing content

Example:

    "Give me 20 creative names for an AI startup."

Variation is useful here.

---

# 17. Important: Low Temperature Does Not Guarantee Determinism

Even if you use a very low temperature, you shouldn't automatically assume:

    Same input → exactly same output forever

Real production systems can still change because of:

- model updates
- provider infrastructure
- backend changes
- different sampling behavior
- tool results
- dynamic context
- nondeterministic execution

So don't build critical business logic around the assumption that an LLM will always produce exactly the same response.

Instead:

> Validate the output and enforce important rules in application code.

---

# 18. Top-p

Another generation parameter you will commonly encounter is **top-p**.

It is also called **nucleus sampling**.

Instead of considering every possible next token, the model considers a group of the most probable tokens whose cumulative probability reaches a threshold.

For example, suppose:

    A → 0.50
    B → 0.25
    C → 0.15
    D → 0.05
    E → 0.05

If:

    top-p = 0.90

the model might consider:

    A + B + C = 0.90

and sample from that probability mass.

The exact implementation can vary by model/provider.

---

# 19. Temperature vs Top-p

Both affect generation randomness, but they do it differently.

Conceptually:

    Temperature
        ↓
    Changes probability distribution

    Top-p
        ↓
    Limits the candidate probability mass

You usually don't need to aggressively tune every generation parameter.

A good engineering approach is:

1. Start with model defaults.
2. Change parameters only when you have a clear reason.
3. Evaluate the result.
4. Keep configuration consistent.
5. Version important configurations.

Different models/providers may expose different parameters, so always follow the model's API contract.

---

# 20. Maximum Output Tokens

Another important parameter is the maximum output token budget.

For example:

    max output = 500 tokens

This doesn't necessarily mean the model will generate exactly 500 tokens.

It means:

> The model cannot generate beyond that configured output limit, subject to the API/model's rules.

This protects your application against unnecessarily large responses.

It also affects:

- cost
- latency
- response size
- streaming duration

For example, an API endpoint that should return:

    { name, age, email }

probably doesn't need thousands of output tokens.

---

# 21. Stop Sequences

A stop sequence tells the generation system:

> Stop generating when this particular sequence is reached.

Conceptually:

    Generate:
    "Question: ...\nAnswer: ..."

If the application specifies an appropriate stop sequence, generation can terminate when it reaches it.

This can be useful for certain structured or legacy completion-style workflows.

Modern chat APIs often provide better structured-generation mechanisms, so stop sequences aren't always necessary.

---

# 22. Finish Reasons

LLM APIs commonly return information describing why generation stopped.

Conceptually, the reason might be:

    completed normally
    reached output limit
    tool call generated
    content policy interruption
    etc.

The exact values depend on the provider.

This is useful for production debugging.

For example:

    response stopped because output limit reached

is very different from:

    response completed normally

Your application can react differently to each situation.

---

# 23. Reasoning Models

Modern LLMs may also have models designed to spend additional computation on difficult reasoning tasks.

Conceptually:

    User request
         ↓
    Model reasoning/computation
         ↓
    Final answer

The important application-level point is:

> Reasoning capability can affect latency and cost, not just answer quality.

You generally shouldn't depend on receiving or exposing a model's private chain-of-thought.

Instead, design your application around:

    Input
      ↓
    Model computation
      ↓
    Final answer / structured output / tool call

The exact controls for reasoning effort vary by model and provider.

---

# 24. Putting Everything Together

Consider a RAG application:

    User:
    "What is our refund policy?"

The backend might construct:

    System instructions
        800 tokens

    Conversation history
        1,200 tokens

    Retrieved documents
        3,000 tokens

    User question
          20 tokens

    -----------------
    Input ≈ 5,020 tokens

Then configure:

    Output budget
        500 tokens

    Temperature
        low

The flow becomes:

    User question
         ↓
    Retrieve relevant documents
         ↓
    Build context
         ↓
    Send context + question to LLM
         ↓
    Generate answer
         ↓
    Validate
         ↓
    Return answer

Every part of this affects production behavior.

---

# 25. A More Important Mental Model: Context Engineering

At this point, don't think of prompting as simply:

    "Write a good prompt."

Think of it as:

    Context Engineering

That means deciding:

- what information enters the context
- what information is removed
- how information is ordered
- which retrieved documents are included
- which conversation history matters
- which tool results matter
- how much output to allow
- which instructions have priority
- how context changes between steps

This becomes extremely important in:

- RAG
- agents
- tool calling
- long conversations
- enterprise assistants
- coding agents

We'll study context engineering explicitly later.

---

# 26. Production Example

Imagine an enterprise AI assistant.

A user asks:

    "Can I take leave next Friday?"

The application might need:

    System rules
    +
    User identity
    +
    Conversation context
    +
    Company leave policy
    +
    User's leave balance
    +
    Current date
    +
    User request

The LLM might determine:

    "The user wants to request leave."

But the application should NOT let the LLM decide:

    "The user is authorized to take leave."

That should be handled by deterministic business logic.

So:

    LLM
      ↓
    Understand request
      ↓
    Select tool
      ↓
    Application validates authorization
      ↓
    Application executes tool
      ↓
    Tool result
      ↓
    LLM generates response

This is the production mindset we established in the previous lessons.

---

# 27. Common Mistakes

## Mistake 1: Treating words as tokens

Don't assume:

    1 word = 1 token

Tokenization depends on the model and text.

---

## Mistake 2: Sending everything into context

More context isn't automatically better.

Irrelevant information can make the system:

- slower
- more expensive
- harder to reason over
- less reliable

---

## Mistake 3: Treating context as memory

The model only knows what your application provides for the current request.

---

## Mistake 4: Increasing temperature to make the model smarter

Temperature controls generation randomness, not intelligence.

---

## Mistake 5: Relying on temperature for correctness

If something must be correct:

    Validate it in code.

Don't rely on:

    temperature = 0

to guarantee correctness.

---

## Mistake 6: Ignoring output limits

Unlimited-looking generation can increase:

- cost
- latency
- resource usage

Set sensible output budgets.

---

## Mistake 7: Optimizing only the context window size

A huge context window doesn't solve poor retrieval.

Often:

    Better retrieval + smaller relevant context

is better than:

    Huge context + lots of irrelevant information.

---

# 28. Interview Perspective

### Q: What is a token?

A token is a unit of text representation processed by an LLM. It may represent part of a word, a word, punctuation, or other text fragments depending on the tokenizer.

### Q: Why do tokens matter?

They affect context capacity, cost, latency, RAG design, conversation history, and output size.

### Q: What is a context window?

The maximum amount of model-visible context that can be processed for a request, subject to the model/API's rules.

### Q: Is context the same as memory?

No.

Context is what is supplied to the model for the current request. Memory is persistent information that the application stores and retrieves when needed.

### Q: Does a larger context window mean better answers?

No.

The relevance and quality of context are often more important than simply increasing its size.

### Q: What does temperature control?

It controls the randomness of token sampling during generation.

### Q: Does higher temperature make a model smarter?

No. It generally increases output variation.

### Q: Should temperature be used to enforce business correctness?

No. Important business rules should be enforced by deterministic application code.

### Q: What is top-p?

A sampling technique that limits candidate tokens to a probability mass whose cumulative probability reaches a configured threshold.

---

# 29. The Core Mental Model

Remember this:

    TOKENS
       ↓
    How text is represented
       ↓
    CONTEXT
       ↓
    What information the model sees
       ↓
    MODEL INFERENCE
       ↓
    TEMPERATURE / SAMPLING
       ↓
    How the next tokens are selected
       ↓
    OUTPUT
       ↓
    VALIDATION
       ↓
    APPLICATION

And from an engineering perspective:

    Token management
        → controls cost and capacity

    Context management
        → controls what the model knows for this request

    Sampling configuration
        → controls output behavior

    Validation
        → controls application reliability

---

# 30. Summary

- **Token** = unit of text processed by the model.
- Tokens affect **cost, latency, context capacity, RAG, and output size**.
- **Context window** = the model's available working context for a request.
- Context is **not persistent memory**.
- A large context window doesn't mean you should send everything.
- **Context quality and relevance matter more than raw context size.**
- RAG helps select relevant information instead of putting an entire knowledge base into context.
- **Temperature controls randomness**, not intelligence.
- Lower temperature is generally useful for more consistent structured tasks.
- Higher temperature can be useful for creative variation.
- **Top-p** controls the probability mass from which candidate tokens are sampled.
- **Maximum output tokens** constrain generated output and help control cost/latency.
- Production systems should not rely on LLM randomness settings for correctness.
- Critical business rules should remain in deterministic application code.
- The next major concept is **streaming, structured output, and multimodal APIs**.

## One sentence to remember

> **Tokens determine what fits and what it costs; context determines what the model sees; sampling parameters influence how it responds; application code determines what is actually allowed to happen.**