# Lesson 13 — Metadata Filtering and Hybrid Search

## 1. Concept

In our basic RAG pipeline, we converted a user's question into an embedding and searched a vector database for similar document chunks.

But **semantic similarity alone is not enough for reliable retrieval**.

Consider an employee asking:

> What is the reimbursement policy in India?

The database contains:

- India's expense reimbursement policy
- US expense reimbursement policy
- UK expense reimbursement policy
- India's employee leave policy

We need to find information that is both relevant to the question and appropriate for the user's requirements.

Two techniques help:

- **Metadata filtering:** Restricts the documents eligible for retrieval using attributes such as country, department, version, or access permissions.
- **Hybrid search:** Combines semantic vector search with keyword-based search.

These techniques solve different problems and are often used together.

## 2. Metadata Filtering

### What is metadata?

Metadata is information that describes a document or chunk rather than its main content.

For example:

    {
      "id": "expense-policy-india-v2",
      "text": "Expense claims must be submitted within 30 days.",
      "metadata": {
        "country": "India",
        "department": "Finance",
        "document_type": "Expense Policy",
        "version": 2,
        "status": "active"
      }
    }

The text contains the policy rule. The metadata tells us where and how that rule applies.

### Why do we need filtering?

Suppose the user asks about India's expense policy.

A vector search might retrieve a US policy because its wording is more semantically similar to the query. However, the US policy is not the correct source for this user.

We can apply filters such as:

    country = "India"
    document_type = "Expense Policy"
    status = "active"

The system then searches only the eligible documents.

### How filtering works

A simplified retrieval process is:

    User question
         ↓
    Determine applicable filters
         ↓
    Generate query embedding
         ↓
    Search eligible vectors
         ↓
    Return relevant chunks

Filters can be applied before or during vector search, depending on the database and its capabilities. Some systems also support filtering retrieved candidates afterward, but post-filtering can return too few relevant results and must not replace security enforcement.

### Common metadata fields

- `tenant_id`: Which customer or organization owns the document.
- `department`: Which department the content belongs to.
- `country`: Geographic applicability.
- `document_type`: Policy, handbook, technical documentation, etc.
- `version`: Document version.
- `status`: Whether a document is active or retired.
- `created_at` / `updated_at`: Document timestamps.
- `access_groups`: Which authorized groups can access the content.

Use only metadata fields that serve a clear retrieval, lifecycle, or security requirement.

## 3. Metadata Filtering Is Also a Security Concern

Imagine your SaaS application serves two companies: Company A and Company B.

Both companies have a document called `expense-policy.pdf`.

A user from Company A asks about expense reimbursement. Even if Company B's policy is a perfect semantic match, the application must not reveal it.

The application should derive the tenant identity from the authenticated session and enforce it in the retrieval layer.

    authenticated_tenant = auth.current_user.tenant_id

    results = vector_database.search(
        vector=query_vector,
        filter={
            "tenant_id": authenticated_tenant
        }
    )

This is conceptual pseudocode.

**Never trust a user-provided tenant ID as proof of authorization.** Also ensure that caches, citations, document downloads, and other retrieval paths enforce the same access boundaries.

Metadata filtering is a useful mechanism, but the application must ensure that its authorization model and filter implementation are correct.

## 4. The Limitation of Semantic Search

Embeddings are useful for meaning-based search, but they can miss important exact matches.

Suppose a developer asks:

> What does error `ERR_CONN_1042` mean?

A document contains:

    ERR_CONN_1042: Connection pool exhausted.

The exact identifier is highly important. Yet an embedding model may not reliably rank that document first because unusual identifiers often have limited semantic meaning.

Other examples include:

- Product codes
- Order IDs
- Error codes
- Legal clause numbers
- Exact names
- Version numbers
- Specialized technical terms

For these cases, keyword search can be valuable.

## 5. Keyword Search

Keyword search looks for matching words or terms in documents.

A simple implementation might search for the exact identifier:

    ERR_CONN_1042

Real search engines often use more sophisticated techniques, including tokenization, inverted indexes, term weighting, and relevance scoring.

One well-known ranking approach is BM25.

### What is BM25?

BM25 is a ranking algorithm commonly used in information retrieval. It estimates relevance using factors such as:

- How well query terms match a document.
- How frequently those terms occur.
- How long the document is relative to others.

It does not require generating embeddings.

For the error-code question, keyword search can retrieve the document containing `ERR_CONN_1042` directly.

However, keyword search has its own weakness. A query like “How do I fix a connection pool that has run out of available connections?” may not match a document that says only “connection pool exhausted” as effectively as semantic search does.

The two methods complement each other.

## 6. What Is Hybrid Search?

**Hybrid search combines keyword-based retrieval and vector-based semantic retrieval.**

Imagine a knowledge base containing:

    Document A:
    ERR_CONN_1042 means the connection pool is exhausted.

    Document B:
    A database connection pool manages reusable connections.

    Document C:
    HTTP 429 means too many requests.

Now compare two queries:

- “What does ERR_CONN_1042 mean?”
- “Why can't my application obtain a database connection?”

Keyword search is especially helpful for the first. Semantic search can be especially helpful for the second.

A hybrid retrieval system uses both to improve coverage.

### Architecture

    User query
         |
         +----------------------+
         |                      |
         v                      v
    Keyword search         Vector search
    (exact terms, BM25)    (embeddings, meaning)
         |                      |
         v                      v
    Keyword results        Vector results
         |                      |
         +----------+-----------+
                    |
                    v
             Combine rankings
                    |
                    v
            Relevant candidates
                    |
                    v
              LLM generates
                 an answer

The combined results can include documents found by either method.

## 7. How Are the Results Combined?

Keyword search and vector search generally produce different kinds of scores.

| Document | Keyword rank | Vector rank |
|---|---:|---:|
| A | 1 | 3 |
| B | 4 | 1 |
| C | 2 | 5 |

You should not automatically add raw scores together. A BM25 score and a cosine similarity score are not necessarily on comparable scales.

A common approach is **Reciprocal Rank Fusion (RRF)**.

RRF combines rankings rather than relying directly on the original score scales.

Its basic formula is:

\[
\operatorname{RRF}(d)=
\sum_{r\in R}\frac{1}{k+r(d)}
\]

Where:

- \(d\) is a document.
- \(R\) represents the ranked result lists.
- \(r(d)\) is the document's rank in one list.
- \(k\) is a constant that reduces the influence of very high ranks.

A document ranked highly by both search methods can receive a strong combined ranking.

You don't need to memorize the formula for implementation. Understand the main idea: **combine evidence from multiple ranked lists to produce a more useful candidate list.**

Other approaches use normalized scores, learned ranking models, or database-specific hybrid-search algorithms.

## 8. Practical Example: Company Knowledge Assistant

Suppose your application stores policies for several countries and departments.

The user asks:

> What is the deadline for submitting travel expenses in India?

### Step 1: Determine filters

The application identifies the applicable country and document type.

    filters = {
        "country": "India",
        "document_type": "Travel Policy",
        "status": "active"
    }

Security-sensitive filters must come from trusted application context and authorization logic.

### Step 2: Run keyword search

Search for terms such as:

    "travel expenses"
    "submission deadline"

This may retrieve documents that use the exact terminology.

### Step 3: Run vector search

Embed the question and search for semantically similar chunks within the eligible documents.

This may retrieve a chunk that says:

    Employees must submit business travel claims within 30 days of returning.

The wording differs, but the meaning is relevant.

### Step 4: Combine results

Merge the keyword and vector candidates using a suitable ranking method.

### Step 5: Optionally rerank

A reranker can assess which candidates most directly answer the question. We will study reranking in the next lesson.

### Step 6: Generate the answer

Provide the best evidence to the LLM, then return a grounded response with an appropriate source citation.

The system can now benefit from exact terminology, semantic similarity, and applicable document constraints.

## 9. Metadata Filtering vs Hybrid Search

| Aspect | Metadata filtering | Hybrid search |
|---|---|---|
| Main purpose | Restrict eligible documents | Improve retrieval relevance |
| Uses | Attributes and conditions | Keywords and semantic similarity |
| Example | Only active Indian policies | Find a document despite different wording |
| Security role | Can enforce retrieval boundaries when correctly implemented | Not an authorization mechanism |
| Commonly combined? | Yes | Yes |

They solve different problems, so they are often used in the same retrieval pipeline.

For example, you can run hybrid search across only the documents that the authenticated user is authorized to access.

## 10. Production Considerations

**Filter selectivity:** Very restrictive filters can leave too few eligible documents. Verify that filters represent the intended business rules.

**Search configuration:** Choose appropriate candidate counts for keyword and vector retrieval. If either search returns too few candidates, the combined list may miss useful evidence.

**Ranking quality:** Evaluate the final combined ranking rather than assuming that adding another search method always improves results.

**Latency:** Running two searches can increase latency. Parallel execution may help, but adds resource and operational considerations.

**Index consistency:** Keyword indexes and vector indexes must stay synchronized as documents are created, updated, or deleted.

**Access control:** Enforce permissions before results reach the LLM. Test for cross-tenant leakage, including through cached results and citations.

**Evaluation:** Test queries that need semantic matching, exact identifiers, or both. Compare retrieval quality against a baseline.

## 11. Common Mistakes

- Using semantic search alone for every query type.
- Assuming keyword search understands synonyms and paraphrases.
- Treating metadata filtering as optional for protected information.
- Trusting user-supplied security filters.
- Adding raw keyword and vector scores without considering their scales.
- Assuming hybrid search always improves relevance.
- Forgetting to synchronize indexes when documents change.
- Returning candidates that match the topic but not the specific question.
- Measuring only final answer quality without examining retrieval results.

## 12. Interview Perspective

**Q: Why combine vector search and keyword search?**

Vector search handles semantic similarity, while keyword search is effective for exact terms, identifiers, and specialized vocabulary. Hybrid search combines their strengths.

**Q: What is BM25?**

A traditional information-retrieval ranking algorithm that scores documents based on query-term matches, term frequency, and document length.

**Q: What is Reciprocal Rank Fusion?**

A technique that combines multiple ranked lists using each document's position in those lists.

**Q: What is the difference between filtering and ranking?**

Filtering determines which documents are eligible to appear. Ranking determines which eligible documents are most relevant to the query.

**Q: How would you secure a multi-tenant RAG system?**

Derive tenant identity from authenticated server-side context, enforce authorization at retrieval time, protect downstream access paths, and test isolation under adversarial conditions.

**Q: When would hybrid search be particularly useful?**

Technical documentation, enterprise knowledge bases, legal documents, and other collections where users may search using both natural-language descriptions and exact identifiers.

## 13. Summary

- Metadata filtering restricts retrieval to documents that meet specific conditions.
- Security-sensitive filters must be enforced by trusted application logic.
- Semantic search is good at finding meaning across different wording.
- Keyword search is valuable for exact terms and identifiers.
- Hybrid search combines both retrieval methods.
- BM25 is a common keyword-ranking algorithm; RRF is one way to merge rankings.
- Filtering and ranking solve different problems.
- Evaluate the complete retrieval pipeline using representative questions.

**Key mental model:** Metadata filtering determines *where the system is allowed to search*; hybrid search improves *how the system finds relevant information*.

**Next lesson — Lesson 14: Reranking and Retrieval Optimization.** We'll explore why the initial search results may not be the best results, how rerankers improve ordering, and how to measure whether retrieval is actually getting better.