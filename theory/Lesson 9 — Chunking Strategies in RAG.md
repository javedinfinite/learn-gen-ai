# Lesson 9 — Chunking Strategies in RAG

## 1. Concept

**Chunking is the process of splitting a large document into smaller pieces so a RAG system can retrieve the most relevant information for a user's question.**

Imagine you have a 100-page employee handbook. A user asks:

> How many days do I have to request a refund for a business expense?

Sending the entire handbook to the LLM for every question is inefficient. Instead, we divide the handbook into chunks, retrieve the ones related to expense refunds, and provide those chunks to the LLM.

For example, a document might contain:

- Chunk 1: Leave policies
- Chunk 2: Expense reimbursement rules
- Chunk 3: Travel policies
- Chunk 4: Employee benefits

The system can retrieve Chunk 2 instead of processing the entire document.

**Important:** Chunking is not simply splitting text. We want each chunk to contain a meaningful, useful piece of information that can be retrieved independently.

## 2. Why Does Chunking Exist?

Chunking solves three important problems.

**Problem 1: Documents are too large**

A document may contain hundreds of pages, while the model has a limited context window. Sending everything is often expensive and unnecessary.

**Problem 2: Retrieval needs focused information**

If a document contains information about leave, salaries, expenses, and travel, a question about expenses should retrieve the relevant expense information rather than the entire document.

**Problem 3: Embeddings work best when the text represents a reasonably focused concept**

An embedding represents the meaning of a piece of text. If one chunk mixes unrelated topics, its embedding may not represent any single topic particularly well.

For example, a chunk containing both a leave policy and a laptop reimbursement policy may be less useful for retrieving either topic.

The goal is to create chunks that are **small enough to retrieve precisely but large enough to preserve the information needed to answer a question.**

## 3. How Chunking Works

A typical ingestion pipeline looks like this:

Document → Extracted text → Chunking → Embeddings → Vector database

Suppose the original document contains:

    Employees can request reimbursement for eligible expenses.
    Expense claims must be submitted within 30 days.
    Receipts are required for claims above ₹1,000.
    Managers must approve reimbursement requests.

A chunking system might produce:

**Chunk 1 — Expense submission**

    Employees can request reimbursement for eligible expenses.
    Expense claims must be submitted within 30 days.

**Chunk 2 — Receipt and approval requirements**

    Receipts are required for claims above ₹1,000.
    Managers must approve reimbursement requests.

Each chunk can be embedded and indexed separately.

When a question arrives, the retrieval system searches for relevant chunks rather than entire documents.

## 4. Common Chunking Strategies

### A. Fixed-size chunking

Split text after a specified number of tokens or characters.

For example, using a target of 500 tokens:

- Chunk 1: Tokens 1–500
- Chunk 2: Tokens 501–1,000
- Chunk 3: Tokens 1,001–1,500

In practice, implementations may split at nearby sentence or word boundaries to avoid cutting text awkwardly.

**Advantages**
- Simple to implement.
- Predictable chunk sizes.
- Easy to process large document collections.

**Disadvantages**
- Can split a sentence, paragraph, or important rule across chunks.
- May combine unrelated topics.

**When to use:** A reasonable baseline for ordinary text when you need a simple, scalable starting point.

### B. Overlapping chunking

Adjacent chunks share some text.

Suppose each chunk contains 500 tokens with an overlap of 100 tokens.

- Chunk 1: Tokens 1–500
- Chunk 2: Tokens 401–900
- Chunk 3: Tokens 801–1,300

Why overlap?

Imagine a policy says:

    Employees must submit expense claims within 30 days.
    Claims submitted after this period require special approval.

If a boundary separates these sentences, a chunk might contain only part of the rule. Overlap can help preserve context across boundaries.

However, overlap is not a universal solution. It increases storage, embedding costs, and duplicate retrieval. It also cannot fix every badly chosen boundary.

### C. Structure-aware chunking

Split documents using their natural structure, such as:

- Headings and sections
- Paragraphs
- Markdown headers
- HTML sections
- Pages or sections of a PDF
- Code functions or classes

For example:

    # Expense Policy

    ## Submission Deadline
    Claims must be submitted within 30 days.

    ## Receipt Requirements
    Receipts are required for claims above ₹1,000.

This approach creates chunks that align with the document's meaning.

**Advantages**
- Preserves relationships between content and headings.
- Often produces more meaningful chunks.
- Makes source attribution easier.

**Disadvantages**
- Requires document structure to be extracted correctly.
- Some sections may be extremely long or extremely short.

**When to use:** Policies, technical documentation, knowledge bases, Markdown files, and structured business documents.

### D. Semantic chunking

Split text based on changes in meaning rather than a fixed token count alone.

For example:

    The company provides 20 annual leave days.
    Employees can carry forward up to 5 unused days.

These sentences are closely related and should probably stay together.

    The company also reimburses approved travel expenses.

This sentence introduces another topic and might belong in a separate chunk.

Semantic chunking attempts to detect such topic changes. Implementations may use embeddings or other similarity techniques to help identify boundaries.

**Advantages**
- Can produce chunks that better reflect conceptual boundaries.
- Useful when document structure is inconsistent.

**Disadvantages**
- More computationally expensive and complex.
- Boundary selection depends on the method and thresholds.
- Does not automatically guarantee better retrieval.

**When to use:** Consider it when simpler approaches perform poorly on your actual documents and evaluation data.

## 5. Choosing Chunk Size and Overlap

There is no universally optimal chunk size.

| Smaller chunks | Larger chunks |
|---|---|
| More focused retrieval | More surrounding context |
| Can improve precision | Can preserve complete explanations |
| May omit necessary context | May mix unrelated topics |
| More chunks and index entries | Fewer, larger index entries |

Consider a question:

> What is the reimbursement deadline, and which receipts are required?

If the deadline and receipt requirements are stored in separate chunks, retrieving only one may produce an incomplete answer.

Larger chunks might preserve both rules, but excessively large chunks could introduce irrelevant content.

A practical starting experiment might use chunks around **300–800 tokens**, with modest overlap where appropriate. This is only a starting range, not a rule; the best choice depends on document type, questions, embedding model, retrieval method, and context budget.

Also distinguish three different limits:

- **Chunk size:** How much text each indexed chunk contains.
- **Retrieval count (`top-k`):** How many candidate chunks the search returns.
- **Context budget:** How much retrieved information is ultimately sent to the LLM.

These are related, but they are not the same setting.

## 6. Preserve Metadata and Context

A chunk should not necessarily be stored as plain text alone.

For example:

    {
      "document_id": "expense-policy-v3",
      "chunk_id": "expense-policy-v3-02",
      "section": "Expense Policy > Submission Deadline",
      "page": 12,
      "version": 3,
      "text": "Expense claims must be submitted within 30 days."
    }

This is an illustrative data structure.

Metadata helps the application:

- Identify the original source.
- Display citations or page references.
- Filter results by department, document type, or version.
- Enforce document-level access permissions.
- Update or delete chunks when a source document changes.

**Important:** Metadata filtering is not a replacement for authorization. The retrieval layer must enforce the current user's permissions.

Also preserve useful parent context. A sentence such as “This period can be extended with approval” may be unclear unless the system knows which period the sentence refers to.

Adding the section heading or retrieving the surrounding paragraph can help resolve that ambiguity.

## 7. Special Cases: Tables, Code, and Long Sections

Not all content should be chunked like ordinary prose.

**Tables:** Keep the column headers with the corresponding rows. Otherwise, a chunk containing `₹1,000` may lose the information explaining what that amount represents.

**Code:** Prefer splitting around functions, classes, or logical modules instead of arbitrary character boundaries. Include relevant class names or file paths when useful.

**Long sections:** A section may exceed the desired chunk size. Split it into smaller meaningful parts while retaining the section heading and other useful context.

**Very short sections:** Avoid splitting them unnecessarily. Sometimes combining related short sections creates a more useful chunk.

### Parent-child chunking

A more advanced approach stores smaller chunks for precise retrieval but keeps a relationship to a larger parent section.

For example:

- Parent: Full expense policy section.
- Child 1: Submission deadline.
- Child 2: Receipt requirements.
- Child 3: Approval rules.

The system searches using the smaller child chunks but can provide the relevant parent section, or a selected portion of it, to the LLM.

This can balance precise retrieval with sufficient context, although it adds implementation complexity.

## 8. Practical Implementation Strategy

For your first RAG application, do not start with an elaborate semantic chunking system.

Use this progression:

1. Extract text and preserve headings and useful metadata.
2. Split by document structure where possible.
3. Apply a maximum chunk size so individual sections do not become too large.
4. Add modest overlap only where it helps preserve context.
5. Generate and store embeddings for the resulting chunks.
6. Test retrieval using realistic user questions.
7. Adjust chunking based on observed failures.

For example, if a question consistently retrieves only the first half of a policy rule, inspect the chunk boundary. If results contain several unrelated topics, consider smaller or structure-aware chunks. If answers lack essential context, consider larger chunks or parent-child retrieval.

Do not assume that a more sophisticated chunking algorithm is automatically better.

## 9. How to Evaluate Chunking

Chunking is part of retrieval quality, so evaluate it using representative questions and expected evidence.

Ask:

- Did retrieval return the chunk containing the answer?
- Was the complete rule retrieved, or was relevant context missing?
- Were irrelevant chunks returned?
- Could the LLM answer correctly using the retrieved context?
- Were the correct source and document version used?

For a fair comparison, keep the evaluation questions consistent while testing different chunking strategies and sizes.

This helps distinguish a chunking problem from an embedding, ranking, or generation problem.

## 10. Common Mistakes

- Using one chunk size for every document type without evaluation.
- Splitting text at arbitrary boundaries and losing meaning.
- Setting excessive overlap, creating unnecessary duplicate content.
- Ignoring headings, table headers, and source metadata.
- Making chunks too small to contain complete answers.
- Making chunks so large that retrieval returns unrelated information.
- Assuming semantic chunking is always superior.
- Forgetting to update indexed chunks when documents change.
- Ignoring access permissions when retrieving chunks.
- Evaluating only the final answer without checking which chunks were retrieved.

## 11. Interview Perspective

**Q: Why is chunking necessary in RAG?**

Chunking makes large documents searchable at a useful level of granularity, allowing the system to retrieve relevant information without sending entire documents to the LLM.

**Q: What is the difference between fixed-size and semantic chunking?**

Fixed-size chunking uses a size-based boundary, while semantic chunking attempts to create boundaries based on changes in meaning.

**Q: Why use overlapping chunks?**

Overlap helps preserve context around boundaries, but increases storage and can introduce duplicate retrieval.

**Q: How would you choose the chunk size?**

Start with a reasonable baseline, build representative evaluation questions, compare retrieval quality and answer correctness, and tune chunk size, overlap, and retrieval count together.

**Q: What would you do if the correct document is retrieved but the answer is still wrong?**

Inspect the actual retrieved chunks. They may omit a critical sentence, lose table structure, contain ambiguous references, or provide insufficient context. If retrieval is adequate, investigate context construction and generation next.

## 12. Summary

- Chunking divides documents into meaningful, searchable pieces.
- Fixed-size chunking is simple; structure-aware chunking preserves natural document boundaries; semantic chunking attempts to follow changes in meaning.
- Overlap can preserve boundary context but adds duplication and cost.
- Chunk size should balance retrieval precision against the need for complete context.
- Metadata, document versions, headings, tables, and access permissions matter.
- Parent-child chunking can combine precise retrieval with richer context.
- Evaluate chunking using real questions instead of relying on assumptions.

**Key mental model:** Good chunking creates pieces that can be retrieved accurately while still containing enough context to answer the question.

**Next lesson — Lesson 10: Embeddings and Semantic Search.** We'll explore how text becomes vectors, how similarity search works, and why semantically related questions can retrieve relevant chunks even when they use different words.