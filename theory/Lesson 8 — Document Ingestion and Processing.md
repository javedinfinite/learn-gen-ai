
# Lesson 8 — Document Ingestion and Processing

## 1. Concept

In the previous lesson, we learned that RAG retrieves relevant information from a knowledge base and supplies it to an LLM.

But before we can retrieve information, we must make the source documents usable.

Imagine building an AI assistant for a company that has:

- 2,000 PDF files
- 500 Word documents
- Thousands of internal knowledge-base articles
- Product documentation on a website
- Customer support records in a database

An LLM cannot automatically search all these sources just because they exist.

We need an **ingestion pipeline** that reads the source data, extracts useful information, prepares it, and makes it available for retrieval.

The basic flow is:

    Source documents
          ↓
    Load documents
          ↓
    Extract content
          ↓
    Clean and normalize
          ↓
    Preserve metadata
          ↓
    Prepare for chunking
          ↓
    Store for downstream indexing

Document ingestion is the process of turning raw source data into usable knowledge for an AI application.

**Important:** Ingestion and retrieval are separate operations. Ingestion prepares the knowledge base; retrieval searches it when a user asks a question.

---

## 2. Why Does Document Ingestion Exist?

Different sources store information in different formats.

A PDF might contain text, images, tables, headers, and footers. A webpage contains HTML. A database stores structured records. A scanned document may contain images of text rather than actual machine-readable text.

Before retrieval can work effectively, the system must understand what information is available and how to extract it.

Consider a PDF containing:

    Employee Leave Policy

    Employees receive 20 days of annual leave.

    Unused leave may be carried forward
    according to company policy.

If your application extracts the text correctly, the information can be chunked, indexed, retrieved, and used by an LLM.

But imagine the extraction produces:

    Employee Leave Policy
    Employees receive 20 days of annual
    leave Unused leave may be carried
    forward according to company policy

This might still be usable, but formatting and sentence boundaries have been damaged.

Now imagine a table gets extracted with its columns mixed together. The text exists, but its meaning may be lost.

**The quality of the final RAG answer depends partly on the quality of the content entering the pipeline.**

---

## 3. The Main Stages of Ingestion

A production ingestion pipeline commonly includes these stages:

    Source
      ↓
    Loading
      ↓
    Extraction
      ↓
    Cleaning and normalization
      ↓
    Metadata enrichment
      ↓
    Chunking
      ↓
    Embedding / indexing
      ↓
    Storage and availability

These stages are conceptually separate, even if a framework combines several of them.

Let's understand each one.

---

## 4. Loading: Getting the Source Data

The first step is connecting to the source.

Examples include:

| Source | Possible loading method |
|---|---|
| PDF files | File storage or upload API |
| Word documents | File storage or document repository |
| Websites | Web crawler or website API |
| Internal knowledge base | API or database query |
| Customer support tickets | Authorized database/API access |
| Cloud documents | Provider-specific connector |

For example, your backend might receive a PDF through an upload endpoint:

    POST /api/documents

After authentication and file validation, the backend stores the file and creates an ingestion job.

For large collections, ingestion usually runs asynchronously rather than making the user wait for every document to be processed.

A typical flow is:

    User uploads document
           ↓
    Backend validates file
           ↓
    Store original file
           ↓
    Create ingestion job
           ↓
    Queue / worker
           ↓
    Process document

This is a traditional backend engineering pattern applied to GenAI.

### Why keep the original document?

Keeping the original can help with:

- Reprocessing when extraction improves.
- Auditing where information came from.
- Rebuilding indexes.
- Investigating extraction errors.
- Supporting document updates.

Retention should still follow the application's security and data-retention requirements.

---

## 5. Extraction: Getting the Actual Content

The extraction method depends on the source format.

### Text-based PDFs

Some PDFs contain machine-readable text.

A PDF parser can extract the text directly.

### Scanned PDFs

A scanned PDF may contain only images of pages.

In this case, the pipeline may need OCR — Optical Character Recognition — to recognize text in those images.

### Word documents

A document parser can extract paragraphs, headings, tables, and other supported structures.

### Websites

A web extraction pipeline may need to remove navigation menus, advertisements, cookie banners, and other irrelevant page elements.

### Databases

Structured data can often be retrieved directly through SQL or APIs instead of being converted into a large block of text.

The important principle is:

**Choose an extraction strategy that matches the source and the information you need to preserve.**

---

## 6. OCR vs Document Parsing vs Vision Models

These technologies are related, but they solve different problems.

**Document parsing** extracts content and structure from a file, such as paragraphs, tables, or headings.

**OCR** recognizes text in images.

**Vision-language models** can interpret visual content, answer questions about images, and in supported cases understand relationships between text and visual layout.

For example, imagine a scanned invoice with a table:

| Item | Quantity | Amount |
|---|---:|---:|
| Chair | 2 | ₹8,000 |
| Table | 1 | ₹12,000 |

An OCR system might recognize the text and numbers. A layout-aware document parser may preserve which values belong to which columns. A vision-language model may help interpret the invoice's visual organization.

For high-accuracy financial extraction, you may combine these approaches and validate the extracted data against expected rules.

You do not automatically need a vision model for every PDF. If a normal parser extracts the information accurately, it may be simpler and cheaper.

---

## 7. Cleaning and Normalization

Extracted content often contains noise.

For example:

    Company Leave Policy

    Page 1 of 12

    Employees receive 20 days of annual leave.

    Page 2 of 12

    Employees may request leave through...

The page numbers and repeated headers may be unnecessary for retrieval.

Cleaning may involve:

- Removing repeated headers and footers.
- Fixing broken whitespace.
- Normalizing line breaks.
- Removing irrelevant boilerplate.
- Correcting extraction artifacts when reliable rules exist.
- Preserving paragraph and heading boundaries.
- Handling duplicate content.

However, **cleaning does not mean removing everything that looks unusual**.

A table heading, section number, or legal clause identifier might be essential to the meaning.

For example:

    Section 4.2 — Refund Exceptions

Removing the section title may make the following paragraph harder to interpret when it is retrieved independently.

A good pipeline removes noise while preserving meaningful structure.

---

## 8. Preserve Structure, Not Just Text

This is one of the most important practical lessons.

Suppose a document contains:

    Refund Policy

    Standard refunds must be requested
    within 30 days.

    Exceptions

    Damaged products may qualify for
    review outside the standard period.

If you flatten the document carelessly, you may lose the relationship between the "Exceptions" heading and the relevant paragraph.

A better representation preserves the structure:

    Section: Refund Policy
    Content: Standard refunds must be
    requested within 30 days.

    Section: Refund Policy > Exceptions
    Content: Damaged products may qualify
    for review outside the standard period.

When the second section is retrieved, the section path gives the LLM useful context.

Depending on the source, preserving structure may include:

- Document titles.
- Headings and subheadings.
- Table headers.
- Page numbers.
- Section identifiers.
- Paragraph boundaries.
- Timestamps for audio/video transcripts.
- Relationships between related records.

Not every application needs all these fields. Preserve the structure that matters for your expected queries.

---

## 9. Metadata

Metadata is information about a document or content chunk.

For example:

    {
      "document_id": "policy-101",
      "title": "Refund Policy",
      "department": "support",
      "version": "3",
      "updated_at": "2026-10-01",
      "access_level": "internal"
    }

This metadata is different from the document's actual content.

The content might say:

    Customers may request a refund
    within 30 days of purchase.

The metadata describes where that information came from, which version it belongs to, and how it should be handled.

### Why metadata matters

Metadata can support:

**Filtering**

Retrieve documents from the support department only.

**Freshness**

Prefer the current policy over an obsolete version.

**Access control**

Restrict retrieval to documents the current user is authorized to access.

**Source attribution**

Identify the document used to generate an answer.

**Lifecycle management**

Find all chunks belonging to a document that has been updated or deleted.

**Debugging**

Understand why a particular chunk appeared in a retrieval result.

Metadata design is therefore a data-modeling decision, not merely an optional field added for convenience.

---

## 10. Document Identity and Versioning

Suppose a company updates its refund policy.

The old version says:

    Refunds within 30 days.

The new version says:

    Refunds within 45 days.

If both versions remain searchable without proper version handling, the retrieval system might return both. The LLM could then give conflicting answers.

A robust ingestion system should identify which source version is current.

Conceptually:

    Document ID: refund-policy

    Version 1:
      Content: 30-day refund window
      Status: superseded

    Version 2:
      Content: 45-day refund window
      Status: current

When the new version is processed, the application should update the searchable representation and retire or clearly distinguish the old version.

The exact approach depends on whether the application needs historical document search.

For audit or legal use cases, historical versions may need to remain accessible under explicit rules rather than being deleted outright.

### A common production challenge

Updating a source document is not enough. The corresponding extracted text, chunks, embeddings, and search indexes must also be updated consistently.

Otherwise, your application may continue returning stale information.

---

## 11. Duplicate Documents

Imagine the same policy appears in three locations:

- An internal knowledge base.
- A PDF attachment.
- A shared folder.

If all three copies are ingested, retrieval might return several nearly identical chunks.

This can waste context and make ranking less effective.

Common approaches include:

- Stable document IDs.
- Content hashes to detect identical files.
- Duplicate detection across extracted text.
- Source-priority rules.
- Canonical versions of documents.

A content hash can help detect exact duplicates, but it does not reliably detect semantically equivalent documents with different wording.

More advanced deduplication may require additional processing.

Also, don't blindly discard duplicates: two similar passages can differ in version, jurisdiction, or permissions.

---

## 12. Large-Scale Ingestion: Why Background Jobs Matter

Suppose a company needs to ingest 100,000 documents.

Processing every document inside a single HTTP request is not a good design.

The request may time out, memory usage may grow too large, and one failure could interrupt the entire operation.

A more reliable architecture uses a queue and workers.

    Admin uploads documents
             ↓
    API stores files + job records
             ↓
    Queue ingestion jobs
             ↓
    Workers process documents
             ↓
    Extract and clean content
             ↓
    Chunk and generate embeddings
             ↓
    Update searchable index
             ↓
    Mark job status

Each document or processing unit can have a state such as:

    queued
      ↓
    processing
      ↓
    completed

Or, when processing fails:

    processing
      ↓
    failed
      ↓
    retry / manual review

The system should also support monitoring progress, handling retries, and identifying documents that permanently fail.

### Why this matters

Embedding generation and document parsing may involve external APIs, expensive computation, or substantial CPU and memory use.

A background pipeline lets you control concurrency, retry failures, and scale workers independently from your user-facing API.

---

## 13. Reliability: Retries, Idempotency, and Partial Failures

Real ingestion pipelines fail.

Possible causes include:

- Corrupt files.
- Unsupported formats.
- OCR failures.
- Provider rate limits.
- Network errors.
- Embedding API outages.
- Storage failures.
- Invalid metadata.

A production pipeline needs to handle these failures without creating inconsistent data.

### Retries

Retry transient failures, such as temporary network problems or rate limits, using bounded retries and appropriate backoff.

Do not endlessly retry permanently invalid files.

### Idempotency

An operation is idempotent when repeating it produces the same intended final state rather than duplicating its effects.

For example, processing the same document job twice should not create two independent sets of active chunks.

Stable document and chunk IDs, upserts, and version-aware updates can help.

### Atomicity and consistency

Consider a document update that produces 20 new chunks.

If only 12 are indexed before the job fails, users may see an incomplete representation of the document.

A safer design may prepare a new version separately and make it active only when processing completes successfully.

The exact implementation depends on the storage system, but the principle is to avoid exposing partially processed document versions as complete.

### Deletion

If a source document is deleted or access is revoked, its derived chunks and embeddings may also need to be removed or made inaccessible.

Removing the original file alone does not automatically remove its copies from a vector index or search system.

---

## 14. How Ingestion Connects to RAG

Let's connect the stages.

Suppose the source contains a refund policy.

**Ingestion time:**

    PDF
      ↓
    Extract text
      ↓
    Clean content
      ↓
    Preserve section metadata
      ↓
    Split into chunks
      ↓
    Generate embeddings
      ↓
    Store searchable chunks

**Query time:**

    "How long do I have to request a refund?"
      ↓
    Search the index
      ↓
    Retrieve the relevant chunk
      ↓
    Add chunk to LLM context
      ↓
    Generate answer
      ↓
    Return answer with source information

Notice that Lesson 8 focuses on preparing the source data. Lesson 9 will focus on how we split that prepared content into chunks.

---

## 15. Common Mistakes

**Mistake 1: Treating every PDF as plain text.**

Scanned PDFs, tables, and complex layouts may require specialized extraction.

**Mistake 2: Removing all formatting.**

Headings and table structure can be essential for interpreting content.

**Mistake 3: Ignoring metadata.**

Without source identity and version information, updates, access control, and citations become harder.

**Mistake 4: Re-ingesting everything for every small update.**

For large collections, incremental ingestion can save time and cost.

**Mistake 5: Assuming ingestion always succeeds.**

Track failures and provide retries or manual review.

**Mistake 6: Allowing partially processed versions to become active.**

Use a version-aware update strategy appropriate to the application.

**Mistake 7: Forgetting deletion and access revocation.**

Derived content in indexes and caches must follow the source's lifecycle and security rules.

**Mistake 8: Doing large ingestion work inside a user-facing request.**

Use background jobs when processing may be lengthy or resource-intensive.

---

## 16. Interview Perspective

**Q1. What is document ingestion in RAG?**

It is the process of loading source content, extracting and preparing it, preserving useful metadata, and making it searchable for later retrieval.

**Q2. What is the difference between ingestion and retrieval?**

Ingestion prepares and indexes the knowledge base. Retrieval searches it in response to a user query.

**Q3. When is OCR needed?**

When the source contains text in image form, such as a scanned PDF, and that text needs to be recognized.

**Q4. Why is metadata important?**

It enables filtering, source attribution, version management, lifecycle operations, and access-aware retrieval.

**Q5. How do you handle document updates?**

Identify the document and version, reprocess the affected content, update the index consistently, and ensure obsolete versions are handled according to the application's requirements.

**Q6. How do you make ingestion reliable at scale?**

Use background workers, bounded retries, idempotent operations, job tracking, monitoring, and version-aware indexing.

**Q7. Why keep the original document?**

It supports auditing, reprocessing, troubleshooting, and rebuilding derived indexes, subject to retention policies.

---

## 17. Summary

- Document ingestion prepares raw information for a RAG knowledge base.
- Loading, extraction, cleaning, metadata, chunking, and indexing are distinct stages.
- PDFs, scanned images, websites, and databases require different processing strategies.
- OCR recognizes text in images; document parsing can preserve document structure.
- Preserving headings, tables, and section relationships can improve retrieval quality.
- Metadata supports filtering, citations, security, versioning, and lifecycle management.
- Document updates must propagate to derived chunks and indexes.
- Background workers help process large collections reliably.
- Retries, idempotency, and consistent version activation prevent common ingestion failures.
- Deletion and access revocation must account for derived data, not just original files.

## One sentence to remember

**A RAG system is only as reliable as the knowledge it ingests: extract the right content, preserve its meaning and metadata, and keep the searchable representation consistent with the source.**

## Next lesson — Lesson 9: Chunking Strategies

We'll explore how to split documents into useful pieces, why chunk size and overlap matter, and how chunking decisions affect retrieval quality, context usage, and answer accuracy.