
# Lesson 7 — RAG: Why It Exists and How It Works

## 1. Concept

**RAG stands for Retrieval-Augmented Generation.**

It is a technique in which an application retrieves relevant information from an external knowledge source and supplies that information to an LLM so it can generate a better-informed response.

The basic flow is:

    User asks a question
            ↓
    Retrieve relevant information
            ↓
    Add retrieved information to the prompt
            ↓
    LLM generates an answer
            ↓
    Return the answer

For example, imagine you're building an AI assistant for a company.

An employee asks:

    "How many days of parental leave
    does our company provide?"

The answer exists in the company's internal HR policy document, but the LLM might never have seen that document during training.

With RAG, your application retrieves the relevant policy and gives it to the LLM.

The model can then answer using the supplied information.

**The central idea: instead of expecting the LLM to already know everything, retrieve the information it needs when answering.**

---

## 2. Why Does RAG Exist?

To understand RAG, we first need to understand the limitations of an LLM.

### Problem 1: The LLM may not know your private data

Suppose you have these documents:

    company/
      hr-policy.pdf
      refund-policy.pdf
      engineering-guidelines.pdf
      employee-handbook.pdf

A general-purpose LLM does not automatically have access to these files.

You could paste a document into the prompt manually, but that becomes impractical when you have thousands or millions of documents.

RAG allows your application to search the relevant information and provide only what is needed.

### Problem 2: Knowledge can become outdated

Imagine asking:

    "What is our current refund policy?"

Your policy might have changed last week.

An LLM's learned knowledge does not automatically update whenever your company changes a document.

RAG can retrieve the current policy from your knowledge source, assuming your ingestion and update pipeline keeps the indexed information up to date.

### Problem 3: You need answers grounded in specific sources

Imagine an AI assistant answering questions about a legal agreement or internal engineering documentation.

You don't just want a plausible answer. You want an answer based on the relevant source material.

RAG helps by supplying relevant documents that the model can use as evidence.

However, retrieval alone does not guarantee correctness. The model can still misinterpret the evidence, and the retrieval system can return irrelevant or outdated information.

### Problem 4: You cannot put your entire knowledge base in every prompt

Suppose a company has 500,000 documents.

Sending all of them to the LLM for every question would be expensive, slow, and potentially exceed the context window.

Instead, RAG searches the knowledge base and retrieves a small subset.

    500,000 documents
            ↓
    Search for relevant information
            ↓
    Retrieve a few useful passages
            ↓
    Send them to the LLM

This is much more practical.

---

## 3. What RAG Is — and What It Is Not

A common misconception is:

    RAG = Vector Database

That is incorrect.

A vector database can be one component of a RAG system, but RAG is the complete process of retrieving information and using it to generate a response.

A RAG system may include:

- Document storage.
- Document processing.
- Chunking.
- Embeddings.
- A search or retrieval system.
- A vector database, keyword index, or both.
- Retrieval and ranking logic.
- Prompt construction.
- An LLM.
- Response validation and source citations.

You can even build a basic RAG system without a vector database, using keyword search or a relational database.

We'll study each component separately in upcoming lessons.

---

## 4. The Complete RAG Architecture

There are two main processes:

1. **Ingestion:** Prepare documents so they can be searched.
2. **Query-time retrieval and generation:** Find relevant information when a user asks a question.

<text weight="medium" size="md">A. Ingestion pipeline — usually runs before the user asks a question</text>

    Documents
       ↓
    Extract text and useful metadata
       ↓
    Split content into chunks
       ↓
    Generate embeddings, if using semantic search
       ↓
    Store chunks and searchable representations
       ↓
    Knowledge base ready

<text weight="medium" size="md">B. Query pipeline — runs when the user asks a question</text>

    User question
          ↓
    Search the knowledge base
          ↓
    Retrieve relevant chunks
          ↓
    Build context for the LLM
          ↓
    Generate grounded answer
          ↓
    Return answer and, if appropriate, sources

Notice that the document preparation process is separate from answering a user's question.

You usually don't want to reprocess every company document whenever someone asks a question.

---

## 5. Understanding the Ingestion Pipeline

Let's use a practical example.

Suppose you have a PDF containing this text:

    Refund Policy

    Customers may request a refund within
    30 days of purchase.

    Products damaged during delivery are
    eligible for review outside this period.

Your application must prepare this information for retrieval.

### Step 1: Document ingestion

Your system receives the PDF and extracts its content.

The source might be:

- A PDF file.
- A Word document.
- A webpage.
- A database record.
- An internal knowledge-base article.

The extraction method depends on the source. Scanned PDFs, for example, may require OCR.

### Step 2: Chunking

Instead of always storing and retrieving the entire document, the system divides it into smaller sections called **chunks**.

For example:

    Chunk 1:
    Customers may request a refund within
    30 days of purchase.

    Chunk 2:
    Products damaged during delivery are
    eligible for review outside this period.

Why split the document?

Because a user might ask about the refund period without needing the entire document.

Smaller, meaningful passages can make retrieval more precise.

But chunks that are too small can lose important context. Chunking is a design decision, not simply a matter of splitting text after a fixed number of characters.

We'll cover this in Lesson 9.

### Step 3: Create searchable representations

One option is to generate an embedding for each chunk.

An embedding is a numerical representation designed to capture aspects of the chunk's meaning.

For example:

    "How long do I have to request a refund?"

could be semantically related to:

    "Customers may request a refund
    within 30 days of purchase."

The wording differs, but the meanings are related.

Embeddings make this kind of semantic retrieval possible.

We will study embeddings in Lesson 10.

### Step 4: Store the information

The system stores the chunk along with useful metadata and its searchable representation.

Conceptually:

    {
      "document_id": "refund-policy",
      "chunk_id": "chunk-1",
      "text": "Customers may request...",
      "embedding": [ ... ],
      "metadata": {
        "department": "support",
        "version": "current"
      }
    }

This is illustrative data, not a requirement to use this exact schema.

The storage could be a vector database, a relational database with vector-search support, a search engine, or a combination of systems.

---

## 6. Understanding the Query Pipeline

Now the knowledge base is ready.

A user asks:

    "How long do I have to request a refund?"

### Step 1: Receive the question

Your backend receives the user's question through an API.

For example:

    POST /api/assistant

The backend authenticates the user and applies any necessary access controls.

### Step 2: Retrieve relevant information

The retrieval system searches the indexed content and returns useful chunks.

For this question, it might return:

    "Customers may request a refund within
    30 days of purchase."

The retrieval method could use keyword search, semantic search, or a combination.

### Step 3: Build the LLM context

Your application constructs a prompt containing instructions, the retrieved content, and the user's question.

Conceptually:

    System instruction:
    Answer using the supplied policy.
    If the evidence is insufficient, say so.

    Retrieved context:
    Customers may request a refund within
    30 days of purchase.

    User question:
    How long do I have to request a refund?

### Step 4: Generate the answer

The LLM receives the context and generates:

    "You can request a refund within
    30 days of purchase."

### Step 5: Return the response

Your application returns the answer to the frontend.

If source citations are required, the backend should also retain the source metadata and associate the answer with the supporting passages.

A model-generated citation is not automatically trustworthy; the application should ensure that cited sources actually exist and correspond to the retrieved material.

---

## 7. Why Can't We Just Put the Documents in the Prompt?

This is an important architectural question.

For a small knowledge base, directly including the relevant content in a prompt may be perfectly reasonable.

RAG becomes more useful when:

- There are many documents.
- Documents change frequently.
- Different users have different access permissions.
- Queries concern different parts of the knowledge base.
- Cost and latency matter.
- Sources need to be tracked.
- The application must retrieve relevant evidence dynamically.

Compare the two approaches.

| Direct context | RAG |
|---|---|
| Supply known content directly | Retrieve relevant content dynamically |
| Simple for small inputs | Better suited to large knowledge collections |
| Can waste tokens with irrelevant documents | Can limit context to selected passages |
| Manual updates may be needed | Indexes can be updated through ingestion pipelines |
| No retrieval component required | Requires retrieval and indexing infrastructure |

RAG is not always the right answer. If the required information is already available in a small, known set of records, a normal database query or direct context may be simpler.

---

## 8. RAG vs Model Training vs Fine-Tuning

These approaches solve different problems.

### RAG

Provides external information at query time.

Example:

    Retrieve current company policy
              ↓
    Supply it to the LLM
              ↓
    Answer employee question

### Fine-tuning

Adjusts a model using training examples to change or improve its behavior for a task.

For example, you might fine-tune a model to produce a particular style of classification or output.

Fine-tuning is not usually the first choice for frequently changing company facts.

### Pretraining

The broad process used to train a model's underlying capabilities and learned representations using large training datasets.

It is different from retrieving information at request time.

### Quick comparison

| Requirement | Common approach |
|---|---|
| Answer questions about current company documents | RAG |
| Retrieve specific customer records | Database/API lookup |
| Produce outputs in a specialized style | Prompting or fine-tuning, depending on requirements |
| Teach a model a specialized behavior or task pattern | Fine-tuning may help |
| Improve a model's general capabilities | Training or model selection, depending on the problem |

You can combine RAG and fine-tuning, but they are not interchangeable.

---

## 9. Does RAG Eliminate Hallucinations?

No.

RAG can reduce some errors caused by missing or outdated knowledge by supplying relevant evidence. But it does not guarantee factual correctness.

There are several possible failure points:

1. **Retrieval failure:** The correct document isn't retrieved.
2. **Ranking failure:** The correct document is found but ranked too low or excluded.
3. **Context failure:** Relevant information is truncated or poorly presented.
4. **Generation failure:** The LLM misinterprets or ignores the supplied evidence.
5. **Source failure:** The indexed document is outdated or incorrect.
6. **Evaluation failure:** The system is deployed without adequately measuring its weaknesses.

For example, if the retrieved document says the refund window is 30 days but the model answers 60 days, RAG has not solved the problem.

A stronger system combines retrieval quality, source freshness, appropriate instructions, validation, evaluation, and monitoring.

This is why advanced RAG is an engineering discipline, not just a database integration.

---

## 10. Access Control in RAG

Consider an enterprise knowledge assistant with two employees.

Employee A can access:

    Public engineering documentation

Employee B can access:

    Public engineering documentation
    + Confidential HR documents

If both users search the same knowledge base, the application must prevent Employee A from retrieving confidential HR content.

A secure retrieval flow might be:

    User request
        ↓
    Authenticate user
        ↓
    Determine allowed data scope
        ↓
    Apply access controls during retrieval
        ↓
    Build context from authorized results
        ↓
    Generate answer
        ↓
    Return response

Filtering only after retrieval can be risky if unauthorized information has already entered model context or other logs.

Access restrictions should be enforced by trusted application logic and the retrieval/data layer—not merely by telling the LLM not to reveal confidential content.

This becomes especially important in multi-tenant applications, where data from one customer must never leak into another customer's answers.

---

## 11. RAG Is a Pipeline, Not a Single Model Call

Let's put the architecture into a full-stack perspective.

    ┌──────────────────────────┐
    │      React Frontend      │
    └────────────┬─────────────┘
                 ↓
    ┌──────────────────────────┐
    │    Backend API           │
    │ Authentication / Access  │
    └────────────┬─────────────┘
                 ↓
    ┌──────────────────────────┐
    │   Retrieval Orchestrator │
    └────────────┬─────────────┘
                 ↓
    ┌──────────────────────────┐
    │ Search / Vector Database │
    └────────────┬─────────────┘
                 ↓
    ┌──────────────────────────┐
    │ Relevant Document Chunks │
    └────────────┬─────────────┘
                 ↓
    ┌──────────────────────────┐
    │     LLM API              │
    └────────────┬─────────────┘
                 ↓
    ┌──────────────────────────┐
    │ Validation / Response    │
    └────────────┬─────────────┘
                 ↓
              Frontend

This is a simplified architecture. Real applications may also use keyword search, reranking, caches, background ingestion jobs, tracing, and evaluation systems.

The key point is that your backend controls the complete pipeline.

The LLM is only one component.

---

## 12. When Should You Use RAG?

RAG is a strong candidate when your application needs to answer questions using a sizable or changing knowledge base.

Examples include:

- Enterprise knowledge assistants.
- Customer support assistants.
- Product documentation chatbots.
- Legal document search.
- Research assistants.
- Internal engineering assistants.
- Question answering over manuals and reports.
- Search across company policies.

However, don't automatically use RAG for every data access problem.

For example, if a user asks:

    "What is my current account balance?"

A direct, authorized database or API lookup is generally more appropriate than searching a vector database.

If a user asks:

    "Explain why my spending increased
    compared with last month."

The application might retrieve transaction data through an API, calculate the comparison using code, and use an LLM to explain the result.

The best design depends on the information and operation required.

---

## 13. Common Mistakes

**Mistake 1: Thinking RAG is just a vector database.**

RAG includes ingestion, retrieval, context construction, generation, and often validation.

**Mistake 2: Assuming embeddings are mandatory.**

Embeddings are common for semantic retrieval, but keyword search and hybrid approaches can also be part of RAG.

**Mistake 3: Sending entire documents unnecessarily.**

Retrieve useful passages when the knowledge base is large.

**Mistake 4: Assuming retrieved information guarantees correctness.**

Retrieval and generation both need evaluation.

**Mistake 5: Ignoring document updates.**

An outdated index can produce outdated answers even when the source document has been corrected.

**Mistake 6: Relying on prompts for access control.**

Enforce authorization in application code and the data/retrieval layer.

**Mistake 7: Using RAG instead of ordinary database queries.**

Structured, exact data is often better retrieved through conventional queries and APIs.

---

## 14. Interview Perspective

**Q1. What is RAG?**

RAG is an architecture that retrieves relevant external information and supplies it to an LLM as context for generating a response.

**Q2. Why is RAG needed if an LLM is already trained?**

The LLM may lack access to private, current, or domain-specific information. RAG supplies relevant information at query time.

**Q3. What are the two major RAG pipelines?**

- Ingestion pipeline: processes, chunks, indexes, and stores documents.
- Query pipeline: retrieves relevant content, constructs context, and generates a response.

**Q4. Is a vector database required for RAG?**

No. It is one possible retrieval component. Keyword search, relational databases with search capabilities, and hybrid retrieval can also be used.

**Q5. Does RAG eliminate hallucinations?**

No. It can improve grounding, but retrieval failures, stale data, and generation errors can still occur.

**Q6. What is the difference between RAG and fine-tuning?**

RAG supplies external information at inference time. Fine-tuning changes model behavior by training on examples.

**Q7. How do you secure an enterprise RAG system?**

Authenticate users, enforce authorization during retrieval, isolate tenant data, protect sensitive context, and monitor access and data flows.

---

## 15. Summary

- RAG means **Retrieval-Augmented Generation**.
- It combines external knowledge retrieval with LLM generation.
- It is useful for private, current, and domain-specific knowledge.
- The ingestion pipeline prepares documents for retrieval.
- The query pipeline retrieves relevant information and passes it to the LLM.
- Chunking and embeddings are common components, but RAG is not limited to vector databases.
- RAG can improve grounding but does not eliminate hallucinations.
- Source freshness, retrieval quality, validation, and evaluation matter.
- Enterprise RAG requires proper authorization and data isolation.
- Use normal database queries when exact structured data retrieval is the better solution.

## One sentence to remember

**RAG lets an application retrieve the right external knowledge for a question and give it to an LLM at the time of answering, rather than expecting the model to already know everything.**

## Next lesson — Lesson 8: Document Ingestion and Processing

We'll examine how real-world files become searchable knowledge: extracting text, handling PDFs and scanned documents, preserving metadata, processing updates, and building a reliable ingestion pipeline.