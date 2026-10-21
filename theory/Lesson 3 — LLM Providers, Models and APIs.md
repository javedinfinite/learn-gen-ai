# Lesson 3 — LLM Providers, Models and APIs

## 1. Concept

An LLM application usually does not contain the LLM itself.

Instead, your application communicates with a model through an API.

The basic architecture is:

    Your Application
          ↓
       LLM API
          ↓
        Model
          ↓
       Response

For example:

    React
      ↓
    Your Backend
      ↓
    LLM Provider API
      ↓
    Model
      ↓
    Response
      ↓
    Your Backend
      ↓
    React

The LLM provider manages things such as:

- model infrastructure
- GPUs
- model serving
- scaling
- availability
- inference

Your application consumes the model as a service.

This is conceptually similar to using:

    PostgreSQL as a database service
    AWS S3 as object storage
    Stripe as a payment service

except the API you're consuming is an AI model.

---

# 2. Model providers

There are several major categories of providers.

## Hosted model providers

Examples include:

- OpenAI
- Anthropic
- Google
- Azure AI
- AWS Bedrock
- Cohere
- Mistral

Your application sends requests to their infrastructure.

Conceptually:

    Your Server
         ↓
    Provider API
         ↓
    GPU infrastructure
         ↓
    LLM

---

# 3. Open-weight / self-hosted models

You can also run models yourself.

For example:

    Your Application
          ↓
       Model Server
          ↓
        LLM
          ↓
       GPU/CPU

The model might be obtained from ecosystems such as Hugging Face.

You could run it using infrastructure such as:

    Ollama
    vLLM
    TensorRT-LLM
    etc.

This gives you more control but also creates more infrastructure responsibility.

You now need to worry about:

- GPU availability
- memory
- inference performance
- scaling
- model deployment
- upgrades
- monitoring
- availability
- cost

We'll study self-hosted inference later.

---

# 4. Why are there so many models?

There is no single "best LLM".

Different models optimize for different things.

For example:

    Model A
    → best reasoning

    Model B
    → cheaper

    Model C
    → faster

    Model D
    → better coding

    Model E
    → better vision

    Model F
    → can run locally

So model selection becomes an engineering decision.

You may need to balance:

    Quality
       ↕
    Cost
       ↕
    Latency
       ↕
    Context size
       ↕
    Availability
       ↕
    Privacy
       ↕
    Capability

---

# 5. The model is not the API

This distinction is important.

You might have:

    Provider
      ↓
    API
      ↓
    Model

These are different concepts.

For example:

    Provider:
    OpenAI

    API:
    Responses API

    Model:
    a particular GPT model

Similarly:

    Provider:
    Anthropic

    API:
    Anthropic API

    Model:
    a particular Claude model

Your application talks to an API.

The API routes your request to a particular model.

---

# 6. Basic LLM API request

Conceptually, an application might do:

    const response = await llm.generate({
        model: "some-model",
        input: "Explain RAG simply"
    });

The provider receives:

    model
    +
    input
    +
    configuration

and returns a response.

Conceptually:

    {
        text: "RAG stands for..."
    }

Real APIs expose much more information, such as:

- output
- usage
- model
- request identifiers
- finish information
- tool calls
- metadata

The exact API structure varies between providers.

---

# 7. Messages and roles

LLM APIs commonly represent conversations using different message roles.

Conceptually:

    system
    user
    assistant
    tool

For example:

    system:
    You are a helpful assistant.

    user:
    Explain RAG.

The model processes these messages as context.

A conversation might look like:

    system
      ↓
    user
      ↓
    assistant
      ↓
    user
      ↓
    assistant

The model does not magically remember previous messages.

Your application generally needs to provide the relevant conversation history or stored state.

---

# 8. System instructions

System instructions define high-level behavior.

For example:

    You are an assistant for an HR application.

    Answer using company policy.

    Never reveal confidential employee information.

These instructions become part of the model's context.

A useful mental model is:

    System instructions
            +
    User request
            +
    Retrieved context
            +
    Tool results
            ↓
           LLM
            ↓
         Response

System instructions are powerful, but they are **not a replacement for security controls**.

For example:

    "Never access another user's data."

is not sufficient security.

Your backend must enforce:

    user → authorization → allowed data

---

# 9. User message

The user message represents the current request.

For example:

    "What is our leave policy?"

But in a real application, the user message may be accompanied by additional context:

    System instructions
    +
    Conversation history
    +
    Retrieved documents
    +
    User request

This is why modern LLM engineering is increasingly about **context construction**, not just writing prompts.

---

# 10. Assistant message

The assistant message is the model's generated output.

For example:

    User:
    What is RAG?

    Assistant:
    RAG stands for Retrieval-Augmented Generation...

But an assistant response doesn't necessarily contain plain text.

It could contain:

    Text

or:

    Structured JSON

or:

    Tool call

or:

    Multiple output items

This becomes very important for application development.

---

# 11. Tool messages

Suppose the user asks:

    "What's the weather in Delhi?"

The model might decide:

    Call:
    getWeather({
        city: "Delhi"
    })

Your application executes the tool.

The result might be:

    {
        "temperature": 31,
        "condition": "Sunny"
    }

That result is then provided back to the model.

The flow becomes:

    User
      ↓
    LLM
      ↓
    Tool call
      ↓
    Application
      ↓
    Weather API
      ↓
    Tool result
      ↓
    LLM
      ↓
    Final answer

This is the foundation of tool calling.

---

# 12. The LLM doesn't execute your function

This is one of the most important concepts.

Suppose your application defines:

    getUserBalance(userId)

The model cannot magically execute your JavaScript function.

Instead, the model produces something conceptually like:

    {
        "tool": "getUserBalance",
        "arguments": {
            "userId": "123"
        }
    }

Your application receives that request.

Then your application decides:

    Is this tool allowed?

    Are these arguments valid?

    Does this user have permission?

Then it executes:

    getUserBalance("123")

The result is sent back to the model.

So:

    LLM
    → decides/request tool

    Application
    → executes tool

This distinction becomes extremely important when we discuss agents and MCP.

---

# 13. Structured output

Plain text isn't always useful for software.

Suppose you ask:

    "Extract the user's information."

You don't want:

    "The user is John, age 32, and lives in Delhi."

Your backend might prefer:

    {
        "name": "John",
        "age": 32,
        "city": "Delhi"
    }

This is **structured output**.

It allows LLM output to become application data.

The architecture becomes:

    User
      ↓
    LLM
      ↓
    Structured output
      ↓
    Schema validation
      ↓
    Application logic

This is much safer than trying to parse arbitrary natural language.

---

# 14. Why schema validation matters

Even if the model is instructed to produce JSON, you should not blindly trust it.

Suppose you expect:

    {
        "amount": number,
        "currency": string
    }

The model might produce:

    {
        "amount": "five hundred",
        "currency": "USD"
    }

Your application should validate the result.

Conceptually:

    LLM output
        ↓
    Schema validation
        ↓
    Valid?
      /   \
    Yes    No
     ↓      ↓
    Use    Retry / reject / repair

This pattern will become important later for reliable AI pipelines.

---

# 15. Streaming

Traditional API:

    Request
      ↓
    Wait
      ↓
    Complete response
      ↓
    Display

For LLMs, responses can take several seconds.

Instead, we can stream tokens/output as they become available.

Conceptually:

    Request
      ↓
    LLM
      ↓
    "The"
      ↓
    "answer"
      ↓
    "is"
      ↓
    "..."

The frontend can display:

    The answer is...

while the model is still generating.

This improves perceived latency.

---

# 16. Streaming architecture

A common architecture is:

    React
      ↕
    Streaming connection
      ↕
    Backend
      ↕
    LLM API
      ↓
    Model

The backend receives model output incrementally and forwards it to the frontend.

Common technologies include:

- Server-Sent Events
- WebSockets
- streaming HTTP responses

The choice depends on the application.

For normal chat generation, SSE-style streaming is often a natural fit because the server primarily sends events to the client.

---

# 17. Tokens

LLMs don't fundamentally process text as human-readable words.

They process **tokens**.

For example:

    "Hello world"

may be represented internally as several tokens depending on the tokenizer.

A token can be:

- part of a word
- a complete word
- punctuation
- whitespace-related pieces

Therefore:

    Characters ≠ tokens
    Words ≠ tokens

The exact tokenization depends on the model/tokenizer.

---

# 18. Why tokens matter to engineers

Tokens affect:

### Cost

Many providers price based partly on token usage.

### Context size

Models have limits on how much input/output they can process.

### Latency

More tokens generally means more work.

### RAG

Retrieved documents consume context.

### Conversation history

Long conversations consume context.

### Caching

Repeated context can sometimes be optimized.

Therefore:

> **Token management is an engineering concern, not merely an AI concept.**

---

# 19. Context window

A model has a maximum amount of context it can process in one request.

Conceptually:

    ┌─────────────────────────────┐
    │       Context Window       │
    │                             │
    │ System instructions         │
    │ Conversation                │
    │ Retrieved documents         │
    │ Tool results                │
    │ User request                │
    │                             │
    │ Generated output            │
    └─────────────────────────────┘

If your application keeps adding information:

    conversation
    +
    documents
    +
    tool results
    +
    more conversation

eventually you can hit the model's context limit.

Even when you don't hit the hard limit, very large context can increase cost and latency.

This is why **context engineering** becomes important.

---

# 20. Model parameters

LLM APIs expose various parameters.

One commonly discussed parameter is:

    temperature

Conceptually:

    Lower temperature
    → more predictable / conservative output

    Higher temperature
    → more variation / creativity

But don't think of temperature as:

    "intelligence"

It doesn't make the model smarter.

It influences the randomness of token selection.

For production applications where predictable output matters, you often want relatively controlled generation.

---

# 21. Other model configuration concerns

Depending on the provider/model, you may encounter settings related to:

- maximum output tokens
- temperature
- top-p
- stop sequences
- reasoning configuration
- structured output
- tool choice
- response format

Not every model supports every parameter.

Therefore:

> **Don't build your architecture around parameters that are specific to one provider unless you intentionally accept provider lock-in.**

---

# 22. Model selection

Suppose you're building an AI customer-support system.

You could choose:

    Huge expensive model

or:

    Smaller cheaper model

The correct answer depends on requirements.

Imagine:

    1 million requests/day

A tiny difference in cost per request can become significant.

You therefore evaluate:

    Quality
    Cost
    Latency
    Throughput
    Context requirements
    Tool calling
    Structured output
    Safety
    Availability

A useful engineering process is:

    Define task
       ↓
    Define quality requirement
       ↓
    Select candidate models
       ↓
    Build evaluation dataset
       ↓
    Benchmark
       ↓
    Compare cost / latency / quality
       ↓
    Choose model

Don't choose a model merely because it is currently popular.

---

# 23. Model routing

Production systems don't necessarily use one model for everything.

For example:

    Simple classification
        ↓
    Small / cheap model

    Complex reasoning
        ↓
    Stronger model

    Embeddings
        ↓
    Embedding model

    Image understanding
        ↓
    Vision model

This is called **model routing**.

Conceptually:

    Request
       ↓
    Router
      / \
     /   \
    ↓     ↓
    Small  Large
    Model  Model

This can significantly reduce cost.

We'll study this later in the scaling/cost section.

---

# 24. Provider abstraction

Suppose your code directly depends everywhere on one provider:

    openai.responses.create(...)

Now switching providers may require changing many parts of your application.

A common architecture is:

    Application
        ↓
    AI Service Interface
        ↓
    Provider Adapter
       / \
      /   \
    Provider A
    Provider B

For example, conceptually:

    interface LLMService {
        generate(request)
    }

Then:

    OpenAIService
    AnthropicService
    LocalModelService

implement the interface.

This can make provider switching easier.

However, don't over-engineer this too early.

Provider abstraction is useful when you actually need portability, routing, fallback, or multi-provider support.

---

# 25. Fallback models

Imagine your primary model provider is temporarily unavailable.

You might have:

    Primary Model
          ↓
       failure
          ↓
    Fallback Model
          ↓
       response

But fallback isn't always trivial.

Different models may have different:

- capabilities
- context limits
- tool behavior
- structured-output support
- quality

So production fallback strategies need testing.

---

# 26. Hosted vs self-hosted

Let's compare conceptually.

## Hosted

    Your App
       ↓
    Provider API
       ↓
    Provider GPU

Advantages:

- simple
- fast to start
- provider manages infrastructure
- easy scaling

Disadvantages:

- ongoing API cost
- provider dependency
- data/privacy considerations
- rate limits
- less infrastructure control

## Self-hosted

    Your App
       ↓
    Your Model Server
       ↓
    Your GPU

Advantages:

- more control
- potentially useful for high-volume workloads
- privacy/control
- customization

Disadvantages:

- infrastructure complexity
- GPU costs
- deployment
- scaling
- monitoring
- model optimization

Neither is universally better.

---

# 27. API gateway / AI gateway

As systems become more complex, you may introduce an AI gateway.

Conceptually:

    Application
         ↓
     AI Gateway
      /   |   \
     /    |    \
    ↓     ↓     ↓
    Model Model Model
     A     B     C

The gateway may provide:

- routing
- rate limiting
- authentication
- logging
- caching
- retries
- provider abstraction
- cost tracking
- fallback

This becomes particularly useful in enterprise systems.

---

# 28. Practical architecture

A production application might eventually look like:

    React
      ↓
    API Gateway
      ↓
    Backend
      ↓
    AI Orchestrator
      ↓
    AI Gateway
      ↓
    ┌───────────────┬───────────────┐
    │               │
    LLM             Embedding Model
    │               │
    │               ↓
    │           Vector DB
    │
    ↓
    Tool Calling
      ↓
    External Systems

Around it:

    Auth
    Guardrails
    Evaluation
    Observability
    Caching
    Rate limiting
    Cost management

This is the foundation we'll keep expanding.

---

# 29. Important terminology

### Model Provider

A company/service providing access to models.

### Model

The actual trained AI model used for inference.

### API

The interface your application uses to communicate with the model.

### Inference

Running the trained model to generate an output.

### Token

A unit of text representation processed by the model.

### Context Window

The amount of input/output context a model can handle in a request.

### Structured Output

Model output constrained to a machine-readable structure.

### Tool Calling

The model generates a request for your application to execute a defined tool.

### Streaming

Receiving generated output incrementally instead of waiting for the complete response.

### Model Routing

Choosing different models based on the task.

### Model Serving

Infrastructure responsible for making a model available for inference.

---

# 30. Practical understanding

When you build a GenAI feature, don't start with:

    "Which LLM should I use?"

Start with:

    What does the application need to do?

Then:

    What information does it need?

    What actions does it need?

    What quality is required?

    How much latency is acceptable?

    How much can we spend?

    What data/privacy constraints exist?

Then select:

    Model
    +
    RAG
    +
    Tools
    +
    Architecture

This is the difference between **using an LLM** and **engineering an LLM-powered system**.

---

# 31. Interview questions

## Q1. What is inference?

Inference is the process of running a trained model to generate predictions or outputs for new input.

For an LLM:

    Input/context
         ↓
       Model
         ↓
    Generated output

---

## Q2. What is the difference between a model and a model provider?

A model is the AI model itself.

A provider offers infrastructure/API access to one or more models.

---

## Q3. Why do tokens matter?

They influence:

- cost
- context capacity
- latency
- throughput
- RAG design
- conversation history management

---

## Q4. Why is structured output useful?

Because application code can consume validated structured data more reliably than arbitrary natural language.

---

## Q5. Does streaming make the model faster?

Not necessarily.

The total generation time may be similar.

Streaming primarily improves **time-to-first-output** and perceived responsiveness.

---

## Q6. Why might we use multiple models?

Different models may optimize for different:

- quality
- cost
- latency
- capabilities

Routing allows us to use the appropriate model for each task.

---

## Q7. Why would a company self-host an LLM?

Potential reasons include:

- privacy
- control
- customization
- predictable high-volume economics
- infrastructure requirements

But self-hosting introduces significant operational complexity.

---

# 32. The key mental model

Think of the model as an external compute capability:

    Your Application
          ↓
    ┌───────────────────┐
    │   AI Interface    │
    └─────────┬─────────┘
              ↓
         Model API
              ↓
            Model
              ↓
           Output

The application controls:

    Context
    Instructions
    Tools
    Validation
    Security
    Business logic

The model provides:

    Language understanding
    Generation
    Reasoning capabilities
    Structured decisions
    Tool selection

That boundary is fundamental.

---

# 33. Summary

The most important concepts from this lesson are:

    1. LLM ≠ application

    2. Your application communicates with models through APIs.

    3. Providers manage model infrastructure when using hosted models.

    4. Models differ in quality, cost, latency and capabilities.

    5. LLMs work with tokens and context windows.

    6. Structured output allows LLMs to produce application-friendly data.

    7. Tool calling allows models to request actions without directly executing them.

    8. Streaming improves responsiveness.

    9. Model routing can optimize cost and performance.

    10. Hosted and self-hosted models have different engineering trade-offs.

    11. Production systems may use an AI gateway for routing, logging,
        caching, rate limiting and provider management.

Most importantly:

> **As a GenAI engineer, your job isn't just to call a model. Your job is to design the system around the model.**

---

# Next Lesson

## Lesson 4 — Tokens, Context Windows, Temperature and Model Parameters

We'll go deeper into the model request itself:

    Text
      ↓
    Tokenization
      ↓
    Context
      ↓
    Model inference
      ↓
    Token generation
      ↓
    Decoding
      ↓
    Final output

We'll especially focus on **tokens and context windows**, because those concepts directly affect RAG, prompt engineering, cost, latency, memory, and scaling.