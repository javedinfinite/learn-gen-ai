# Lesson 11 — Vector Databases

## 1. Concept

A **vector database** stores numerical vectors and lets us search for vectors that are similar to a given query vector.

In our previous lesson, we learned that an embedding model converts text into vectors. Now we need a system that stores those vectors and retrieves the most relevant document chunks efficiently.

Imagine a company has 1 million document chunks. Each chunk has:
- The original text
- An embedding vector
- Metadata such as document ID, section, version, and permissions

When a user asks a question, the application generates a query embedding and searches the database for relevant chunks.

The vector database returns matching records, including the original text or references to it.

**Important:** An embedding model creates vectors; a vector database stores and searches them. They perform different jobs.

## 2. Why Does a Vector Database Exist?

A normal relational database is excellent at queries such as:

    SELECT *
    FROM employees
    WHERE department = 'Engineering';

This finds records using exact conditions.

But consider this question:

    Which company policy explains how employees claim travel expenses?

The relevant document might use the words “business trip reimbursement” rather than “travel expenses.”

A conventional exact-match query may struggle to identify the relationship in meaning. Vector search can compare embeddings to find semantically related content.

A vector database helps with:

- Storing embeddings for large document collections.
- Finding similar vectors.
- Filtering search results using metadata.
- Retrieving relevant chunks for RAG.
- Supporting efficient search as collections grow.

You do not necessarily need a separate vector database product for every application. Some relational databases support vector search through extensions or built-in capabilities.

## 3. How a Vector Database Works

A typical RAG system has two pipelines.

### A. Ingestion pipeline

    Documents
       ↓
    Extract and clean text
       ↓
    Split into chunks
       ↓
    Generate embeddings
       ↓
    Store vectors + text + metadata
       ↓
    Build or update search index

### B. Query pipeline

    User question
       ↓
    Generate query embedding
       ↓
    Search vector index
       ↓
    Retrieve top matching chunks
       ↓
    Apply necessary filters and checks
       ↓
    Send context to LLM
       ↓
    Generate answer

For example, a stored record might look conceptually like this:

    {
      "id": "policy-101-chunk-3",
      "text": "Expense claims must be submitted within 30 days.",
      "embedding": [0.12, -0.08, 0.34, "..."],
      "metadata": {
        "department": "finance",
        "document_version": 2
      }
    }

The vector shown is illustrative, not a real embedding. Actual vectors contain a fixed number of numeric values determined by the embedding model.

The database searches using the vector, while the text and metadata help the application use the result.

## 4. What Is Vector Similarity Search?

Suppose the database contains 100,000 vectors. A simple search could calculate the distance between the query vector and every stored vector, then sort the results.

This is called **brute-force or exact nearest-neighbor search**.

Conceptually:

    for each stored_vector:
        calculate similarity(query_vector, stored_vector)

    sort results by similarity
    return top_k results

This approach can provide exact nearest neighbors, but becomes expensive for large collections and high request volumes.

For production workloads, vector systems often use **Approximate Nearest Neighbor (ANN)** search.

ANN finds vectors that are likely to be among the nearest neighbors without exhaustively comparing every vector.

It trades some search accuracy for improved performance.

## 5. How Does a Vector Database Search Efficiently?

Vector databases use specialized indexing techniques. Two important examples are HNSW and IVF.

### A. HNSW — Hierarchical Navigable Small World

HNSW builds a graph connecting nearby vectors.

Imagine a map where locations are connected by roads. Instead of examining every location, a search follows connections that lead progressively closer to the query.

HNSW uses multiple graph layers to help navigate efficiently.

**Advantages**
- Often offers fast, high-quality nearest-neighbor search.
- Useful for interactive retrieval workloads.

**Trade-offs**
- Uses additional memory for graph structures.
- Index construction and updates have costs.
- Search performance depends on configuration and workload.

### B. IVF — Inverted File Index

IVF groups vectors into clusters.

Instead of searching the entire collection, a query first identifies promising clusters and searches within selected clusters.

**Advantages**
- Can reduce the number of vectors examined.
- Useful for large collections when configured appropriately.

**Trade-offs**
- Searching too few clusters can miss relevant results.
- Searching more clusters improves recall but increases work.
- Requires suitable configuration and sometimes training the index.

You do not need to memorize the internal algorithms before building RAG applications. Understand the core trade-off:

**Exact search prioritizes exactness; approximate search aims to find highly relevant neighbors faster.**

## 6. What Does Top-k Mean?

Suppose a user asks:

    What is the expense reimbursement deadline?

The vector database may return the top three matches:

1. Expense claims must be submitted within 30 days.
2. Travel reimbursements require manager approval.
3. Employees must attach receipts to expense claims.

Here, `k = 3`.

Top-k specifies how many results to return, not how relevant they must be.

If `k` is too small, important evidence may be missed. If it is too large, irrelevant content can enter the LLM's context, increasing cost and potentially confusing the answer.

The best value depends on the documents, query type, retrieval strategy, and context budget.

Also distinguish:
- **Top-k:** Number of results requested.
- **Similarity threshold:** A rule that may reject results below a chosen score or above a chosen distance.
- **Reranking:** Reordering candidates using a more targeted relevance model.

A threshold must be calibrated to the model and metric. Similarity scores are not universally comparable across embedding models.

## 7. Metadata Filtering

Vector similarity alone may not be enough.

Suppose a company has separate policies for India, the US, and the UK. A user in India asks about reimbursement.

A vector search might retrieve a US policy because its wording is more similar to the query.

Metadata filtering can constrain the search:

    country = "India"
    document_type = "expense_policy"

The system then searches for relevant vectors within the permitted subset.

Metadata can represent:

- Document type
- Department
- Country or region
- Tenant or organization
- Version and status
- Creation or update date
- Access-control attributes

**Security warning:** Do not trust a country or tenant value supplied by the user as an authorization decision. Derive security-sensitive filters from authenticated identity and server-side authorization rules.

Filtering must be enforced by the application or trusted retrieval layer. A prompt instruction telling the LLM not to reveal unauthorized documents is not sufficient.

## 8. Vector Database vs Relational Database

| Capability | Relational database | Vector database |
|---|---|---|
| Exact filters and joins | Core strength | Often supported in some form, but varies |
| Structured business records | Excellent | Not usually the primary strength |
| Similarity search over embeddings | Depends on vector support | Core strength |
| Transactions and constraints | Mature support | Varies by product |
| Metadata filtering | Strong | Commonly supported |
| Full-text keyword search | Available in many systems | Varies by product |

These are general tendencies, not absolute boundaries.

For example, PostgreSQL with the `pgvector` extension can store relational records and embeddings together. This may be a good choice when you want one database and your search workload fits its performance characteristics.

Dedicated vector databases may be attractive when you need specialized indexing, large-scale vector workloads, or particular distributed-search features.

**Do not introduce a separate vector database merely because an application uses RAG.** Choose based on actual requirements.

## 9. Popular Vector Search Options

Examples include:

- **PostgreSQL + pgvector:** Vector search integrated with a relational database.
- **Pinecone:** Managed vector database service.
- **Qdrant:** Vector search with filtering and deployment options.
- **Weaviate:** Vector database with search and data-modeling capabilities.
- **Milvus:** Vector database designed for large-scale similarity search.
- **Elasticsearch / OpenSearch:** Search engines supporting keyword and vector retrieval.

Products differ in deployment model, indexing, filtering, scaling, operations, and pricing. Evaluate current capabilities against your workload rather than choosing based on popularity alone.

## 10. Practical Example: Building a Company Policy Search

Suppose you are implementing an internal assistant.

### Step 1: Store the chunks

Each record contains a unique ID, chunk text, embedding, and metadata.

    {
      "id": "expense-001",
      "text": "Expense claims must be submitted within 30 days.",
      "metadata": {
        "department": "finance",
        "country": "India"
      }
    }

The ingestion pipeline generates and stores the actual embedding.

### Step 2: Embed the user's question

    question = "When must I submit an expense claim?"

    query_vector = embedding_model.embed_query(question)

### Step 3: Search with filters

    results = vector_database.search(
        vector=query_vector,
        top_k=5,
        filter={
            "department": "finance",
            "country": "India"
        }
    )

This is conceptual pseudocode; actual APIs and filter syntax differ by product.

### Step 4: Use the results

The application checks permissions, assembles the relevant text, and sends it to the LLM with the user's question.

The model might answer:

    Expense claims must be submitted within 30 days.

The application can also provide the source document or section.

Notice that the database does not itself generate the answer. It retrieves candidate evidence for the rest of the RAG pipeline.

## 11. Production Considerations

### Index updates and deletion

When a document changes, its old chunks and vectors may need to be removed or replaced. Otherwise, the assistant can retrieve outdated information.

### Multi-tenancy

For a SaaS application, data from different customers must remain isolated. Use server-controlled tenant filters and enforce access at the retrieval boundary.

### Latency and throughput

Measure embedding time, vector-search latency, metadata-filtering overhead, and the effect of concurrent requests. Search speed alone does not determine total answer latency.

### Memory and storage

Vector dimensions, numeric precision, metadata, stored text, and index structures all affect resource usage.

### Recall and relevance

A fast search is not useful if it misses the right evidence. Tune approximate index settings using representative queries and measure retrieval quality.

### Reliability

Plan for index failures, unavailable dependencies, ingestion retries, and consistency between the source documents and indexed content.

## 12. Common Mistakes

- Assuming every RAG system requires a dedicated vector database.
- Thinking the database creates embeddings automatically in every architecture.
- Confusing vector similarity with factual correctness.
- Returning too many chunks without considering context quality.
- Choosing an approximate index without measuring recall.
- Ignoring metadata and authorization filters.
- Leaving outdated vectors after documents change.
- Using similarity thresholds without validating their behavior.
- Assuming a vector database replaces SQL, business logic, or normal API lookups.

## 13. Interview Perspective

**Q: What is a vector database?**

A system designed to store vectors and retrieve similar vectors efficiently, often using specialized nearest-neighbor indexes.

**Q: What is the difference between exact search and ANN?**

Exact search finds the true nearest neighbors under the selected metric by exhaustive comparison. ANN seeks close neighbors more efficiently, potentially sacrificing some recall.

**Q: What is HNSW?**

A graph-based approximate nearest-neighbor index that navigates connections between vectors using a hierarchical structure.

**Q: What is the difference between top-k and a similarity threshold?**

Top-k limits the number of returned candidates. A threshold determines whether a result meets a configured score or distance criterion.

**Q: When would you use pgvector instead of a dedicated vector database?**

When integrating vector search into an existing PostgreSQL system simplifies architecture and the workload meets performance, scaling, and operational requirements.

**Q: How do you prevent cross-tenant data leakage in vector search?**

Enforce tenant isolation and access-control filters using trusted server-side identity and authorization logic, and test those boundaries explicitly.

## 14. Summary

- A vector database stores embeddings and retrieves similar vectors.
- Embedding models generate vectors; vector indexes make similarity search efficient.
- Exact search is exhaustive; ANN trades some recall for speed.
- HNSW uses graph navigation; IVF searches selected clusters.
- Top-k controls result count, while thresholds control acceptance.
- Metadata filtering narrows results by attributes and supports secure retrieval when correctly enforced.
- Relational databases with vector extensions can be sufficient for many applications.
- Index maintenance, access control, latency, recall, and data freshness matter in production.

**Key mental model:** The embedding model represents meaning, the vector index searches for nearby representations, and the retrieved text provides evidence for the LLM.

**Next lesson — Lesson 12: Building a Basic RAG Pipeline.** We will connect document ingestion, chunking, embeddings, vector search, prompt construction, and answer generation into one working architecture.