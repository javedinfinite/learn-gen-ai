
# Lesson 5 — Streaming, Structured Output and Multimodal APIs

## 1. Concept

So far, we've learned how an LLM receives input, processes context, and generates a response.

Now we'll explore three capabilities that make LLM APIs useful in real applications:

1. **Streaming** — receive a response progressively instead of waiting for the entire answer.
2. **Structured output** — get responses in a predictable format, such as JSON, that your application can process.
3. **Multimodal APIs** — send and receive different types of content, such as text, images, audio, and video, depending on the model's capabilities.

These capabilities are especially important when building full-stack GenAI applications.

For example, imagine you're building an AI assistant using React and Node.js.

- Streaming makes the interface feel responsive.
- Structured output lets your backend process model responses reliably.
- Multimodal APIs allow users to upload images or speak instead of typing.

---

# 2. Streaming

## What problem does streaming solve?

Suppose a user asks:

    "Explain how RAG works."

Without streaming, the application typically waits for the complete response before displaying it.

    User sends request
          ↓
    LLM generates entire response
          ↓
    API returns complete response
          ↓
    UI displays answer

If the response takes 8 seconds to complete, the user might see nothing for those 8 seconds.

Streaming changes the experience.

    User sends request
          ↓
    LLM begins generating
          ↓
    "RAG stands for..."
          ↓
    "Retrieval-Augmented..."
          ↓
    "Generation..."
          ↓
    Remaining response arrives
          ↓
    Response completes

The user sees the answer progressively.

## How streaming works

The backend establishes a streaming response and forwards output as it becomes available.

Conceptually:

    React frontend
         │
         │ HTTP request
         ▼
    Node.js backend
         │
         │ Streaming request
         ▼
    LLM provider
         │
         │ Partial output events
         ▼
    Node.js backend
         │
         │ Stream chunks
         ▼
    React displays incrementally

The model may generate tokens internally, but your API usually exposes them through chunks or events. A chunk does not necessarily correspond to exactly one token.

## Streaming implementation example

Imagine an endpoint:

    POST /api/chat

Without streaming, your backend might conceptually do this:

    const response = await llm.generate({
      input: userMessage
    });

    return response.text;

The frontend receives the completed response.

With streaming, the backend requests a stream and forwards incremental output to the client.

Conceptually:

    const stream = await llm.stream({
      input: userMessage
    });

    for await (const event of stream) {
      // Forward each output event to the client.
    }

This is illustrative pseudocode; the exact method depends on the provider's SDK.

On the frontend, React updates the displayed answer as chunks arrive.

    let answer = "";

    // For every incoming text chunk:
    answer += chunk;
    setAnswer(answer);

In a real application, you'd also handle connection errors, cancellation, completion events, and non-text events.

## Streaming technologies

Common options include:

- **Server-Sent Events (SSE):** useful for sending a continuous stream of server-to-client events over HTTP.
- **Fetch streaming:** allows browser code to consume a response body progressively.
- **WebSockets:** useful when the application needs persistent, bidirectional communication.
- **Provider SDK streaming:** many LLM SDKs expose convenient streaming abstractions.

For a conventional text-generation interface, SSE or fetch streaming is often sufficient. Voice and real-time interactive systems may need different transport choices.

## Important distinction: latency

Streaming improves **time to first visible output** and perceived responsiveness.

It does not necessarily make the model generate the entire answer faster.

For example:

| Metric | Without streaming | With streaming |
|---|---|---|
| Time to first visible text | Usually after completion | As output arrives |
| Total generation time | Depends on model and request | May be similar |
| User experience | Can feel slow | Usually feels more responsive |

## Production considerations

When implementing streaming, remember to handle:

- Client disconnects and cancellation.
- Provider timeouts and errors.
- Partial responses when generation fails.
- Authentication and authorization before starting generation.
- Usage and cost tracking.
- Tool-call events versus ordinary text events.
- Reverse proxies and infrastructure that may buffer responses.
- Backpressure when a consumer cannot process data as quickly as it arrives.

**Important:** A streamed response is not automatically a safe response. If the application must validate the entire answer before showing it, you may need to buffer and validate it instead of displaying every chunk immediately.

---

# 3. Structured Output

## What problem does structured output solve?

LLMs are good at generating natural language, but production applications often need data in a specific format.

Suppose you're building a support-ticket classifier.

You want the model to identify:

- Category
- Priority
- Whether human intervention is required

A natural-language response might be:

    This appears to be a billing issue.
    It should be treated as high priority.
    A human should review it.

That is understandable to a person, but your backend would need to parse the text.

What if the model changes its wording or adds an explanation?

A better approach is to request structured output.

    {
      "category": "billing",
      "priority": "high",
      "requires_human": true
    }

Your application can now process the result as data.

## How structured output works

You define the expected shape of the response.

For example:

    TicketClassification:
      category: string
      priority: string
      requires_human: boolean

You then ask the model to return an object conforming to that schema.

The conceptual flow is:

    User's support ticket
            ↓
    LLM API + output schema
            ↓
    Structured response
            ↓
    Schema validation
            ↓
    Application logic
            ↓
    Save ticket / assign priority

The exact mechanism depends on the API. Some providers support constrained or schema-based generation, while others may rely more heavily on prompting and subsequent validation.

## Structured output versus ordinary JSON prompting

These are related, but not identical.

**Approach A: Prompting for JSON**

    "Return valid JSON with category and priority."

The model is instructed to produce JSON, but the instruction alone may not guarantee compliance.

**Approach B: Schema-constrained structured output**

You supply a supported schema or structured-output configuration through the API.

The API/model uses that configuration to constrain the output format where supported.

This generally provides stronger formatting guarantees than a prompt alone, but you must still account for API errors, refusals, incomplete responses, and application-level validation.

## Schema validation

Even when the model returns valid JSON, your application should validate it.

Consider this output:

    {
      "category": "billing",
      "priority": "extreme",
      "requires_human": "yes"
    }

It is valid JSON, but perhaps your application only permits:

    category: "billing" | "technical" | "account"
    priority: "low" | "medium" | "high"
    requires_human: boolean

The output violates the expected schema because:

- `"extreme"` is not an allowed priority.
- `"yes"` is a string, not a boolean.

This is why **valid JSON is not the same as valid application data**.

A reliable pipeline looks like:

    LLM output
        ↓
    Parse JSON
        ↓
    Validate schema
        ↓
    Apply business rules
        ↓
    Accept or reject

If validation fails, the application may retry, ask the model to repair the response, return an error, or use a fallback path. Retrying should be bounded so failures don't create an expensive loop.

## Example: extracting data from a support request

Input:

    "I was charged twice for my subscription.
    Please help me get a refund."

Desired output:

    {
      "category": "billing",
      "intent": "refund_request",
      "priority": "high"
    }

The backend can use the result to route the ticket.

However, classification must not automatically authorize a refund. The actual refund decision should follow your application's business rules and permissions.

## Where structured output is useful

- Data extraction from documents.
- Classification and routing.
- Generating UI components from known data structures.
- API response generation.
- Search-query construction.
- Tool arguments.
- Workflow decisions.
- Evaluations and scoring.
- Converting natural language into validated application inputs.

## Structured output versus tool calling

These are different concepts.

**Structured output** means the model returns data in a defined format.

**Tool calling** means the model requests that the application invoke a particular tool with particular arguments.

For example:

Structured output:

    {
      "intent": "check_order_status",
      "order_id": "ORD-123"
    }

Tool call:

    getOrderStatus({
      orderId: "ORD-123"
    })

The first is data describing an intent. The second is a request to invoke a capability through the API's tool-calling mechanism.

Even with tool calling, your backend must validate arguments and check authorization before executing the tool.

---

# 4. Multimodal APIs

## What does multimodal mean?

A text-only interaction looks like this:

    Text input → LLM → Text output

A multimodal interaction can involve multiple content types.

Depending on the model and API, a request might contain:

- Text
- Images
- Audio
- Video frames
- Other supported structured content

The response may also include text, generated images, audio, or other output types.

For example, a user might upload a photograph of a damaged product and ask:

    "What damage can you see in this image?"

A capable vision-language model can process the image alongside the question.

This is more than traditional text-only processing.

## Image understanding

A multimodal API may allow you to provide:

    User question:
    "Read the total amount from this receipt."

    Image:
    [Receipt photograph]

The model can use visual information to produce an answer.

Possible applications include:

- Receipt and invoice processing.
- Screenshot analysis.
- Document understanding.
- Product image analysis.
- Visual question answering.
- Chart interpretation.
- Image-based customer support.

### Is this always OCR followed by an LLM?

No.

Some document pipelines explicitly run OCR and then pass the extracted text to an LLM.

Other vision-language models can process image content directly and reason about visual information, including text in images.

A production system may combine both approaches. For example, OCR can provide searchable text, while a vision model can help interpret layout, tables, diagrams, or visual relationships.

The appropriate design depends on accuracy requirements, image complexity, cost, latency, and the model's capabilities.

## Audio understanding

Audio-enabled models may support:

- Speech recognition.
- Transcription.
- Understanding spoken requests.
- Audio classification.
- Speech translation.
- Audio conversation.

A conventional pipeline might be:

    User speaks
        ↓
    Speech-to-text
        ↓
    Text
        ↓
    LLM
        ↓
    Text response
        ↓
    Text-to-speech
        ↓
    Spoken response

Some modern APIs support more direct audio input and output, including real-time interaction, without requiring you to explicitly orchestrate every stage as a separate service.

We'll explore voice AI in a later phase.

## Video understanding

Video can be processed by extracting frames and analyzing them with a vision model, or through a model/API that explicitly supports video input.

A simplified pipeline might be:

    Video
      ↓
    Select relevant frames
      ↓
    Analyze frames + timestamps
      ↓
    Combine visual information
      ↓
    Answer the user's question

For example:

    "At what point does the person pick up the package?"

This may require visual analysis across multiple frames rather than interpreting a single image.

Some systems also incorporate audio and timestamps, depending on the task and available API.

## Multimodal does not mean every model supports everything

A provider may offer several models with different capabilities.

One model might support text and images, another audio input and output, and another only text.

Before selecting a model, check:

- Supported input types.
- Supported output types.
- File size and format limits.
- Context and output limits.
- Streaming support.
- Structured-output support.
- Tool-calling support.
- Pricing and latency.

Never assume that a feature supported by one model is supported by every model from the same provider.

---

# 5. A Practical Full-Stack Example

Imagine building an AI expense assistant.

A user uploads a receipt and asks:

    "Extract the merchant, date, total amount,
    and currency."

Your application could work like this:

    React frontend
        ↓
    Upload receipt
        ↓
    Node.js backend
        ↓
    Authentication + file validation
        ↓
    Multimodal LLM API
        ↓
    Structured output
        ↓
    Schema validation
        ↓
    Business validation
        ↓
    Save expense to database
        ↓
    Return result to React

The expected model output could be:

    {
      "merchant": "Example Store",
      "date": "2026-10-08",
      "total": 1250.50,
      "currency": "INR"
    }

Your application should then validate the date, currency, amount, and any required fields.

If the user is submitting a reimbursable expense, the model's extraction is only one step. Your application must still enforce authorization, expense policies, and approval workflows.

You might also stream progress updates to the frontend:

    "Uploading receipt..."
    "Reading receipt..."
    "Validating extracted data..."

These are application-generated status messages; they do not have to be streamed from the LLM itself.

This example combines three capabilities:

- Multimodal input for the receipt image.
- Structured output for the extracted data.
- Streaming or progress events for a responsive interface.

---

# 6. Choosing the Right Approach

| Requirement | Suitable approach |
|---|---|
| Display a long answer as it is generated | Streaming |
| Extract fields into a known schema | Structured output |
| Understand a photograph or screenshot | Vision-capable multimodal API |
| Transcribe spoken language | Speech-to-text or audio-capable model |
| Generate spoken answers | Text-to-speech or audio-capable model |
| Process video events | Video/frame analysis |
| Execute an external action | Tool calling + backend authorization |
| Return a validated API object | Structured output + application validation |

These capabilities can be combined in the same application.

---

# 7. Production Mistakes to Avoid

### Mistake 1: Treating streamed text as a completed response

A stream may end with an error or an incomplete result. Track completion and failure explicitly.

### Mistake 2: Assuming JSON is automatically trustworthy

Valid JSON can still contain incorrect values, fabricated data, or unauthorized requests.

Validate the schema and enforce business rules.

### Mistake 3: Executing model-generated instructions without authorization

A model might produce a valid tool call or a valid structured object. That does not mean the requested action is permitted.

### Mistake 4: Assuming every multimodal model accepts every media type

Verify capabilities and limits for the specific model/API.

### Mistake 5: Ignoring privacy when uploading media

Images, audio, and documents can contain personal or confidential information. Apply access controls, data-retention policies, and appropriate handling before sending data to an external provider.

### Mistake 6: Treating OCR output as ground truth

OCR and vision models can misread amounts, dates, names, and tables. Validate extracted values, especially when they affect financial or other important decisions.

---

# 8. Interview Perspective

**Q1. What is LLM streaming?**

Receiving generated output incrementally instead of waiting for the complete response. It primarily improves responsiveness and time to first output.

**Q2. Does streaming reduce total generation time?**

Not necessarily. It usually lets users see partial output sooner, even when total generation time remains similar.

**Q3. What is structured output?**

A way to obtain model responses in a predefined format or schema so an application can process the result more reliably.

**Q4. Is valid JSON enough for production?**

No. JSON parsing, schema validation, semantic validation, authorization, and business-rule checks may all be required.

**Q5. What is the difference between structured output and tool calling?**

Structured output returns data. Tool calling asks the application to invoke a capability. Tool execution must still be validated and authorized.

**Q6. What is a multimodal LLM?**

A model that can process or generate multiple modalities, such as text, images, audio, or video, depending on its supported capabilities.

**Q7. Does image understanding always require a separate OCR service?**

No. Vision-language models can directly process images, including text within them. Separate OCR can still be valuable for searchable text, precision, cost control, or specialized document workflows.

---

# 9. Summary

- **Streaming** delivers output progressively and improves perceived responsiveness.
- Streaming applications must handle partial output, cancellation, errors, and completion.
- **Structured output** provides responses in a known data format.
- Valid JSON does not guarantee correct or safe data.
- Schema validation and deterministic business rules remain essential.
- **Tool calling** is distinct from structured output because it requests application-side execution.
- **Multimodal APIs** support different combinations of text, images, audio, and video.
- OCR is one possible part of a document pipeline, not a universal requirement for image understanding.
- Always check the actual capabilities of the selected model.
- These capabilities can be combined to build reliable full-stack GenAI features.

## One sentence to remember

**Streaming controls how the response arrives, structured output controls its shape, and multimodal capabilities control the kinds of information the application can exchange with the model.**

## Next lesson — Lesson 6: Deterministic Workflows vs AI Workflows vs Agents

We'll learn when ordinary code is enough, when an LLM adds value, and when an agent is actually justified. This is a foundational architecture decision for production GenAI systems.