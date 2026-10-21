# Lesson 10 — Embeddings and Semantic Search

## 1. Concept

**Embeddings are numerical representations of data that capture useful aspects of its meaning.**

In RAG, we commonly convert text into a vector of numbers so that the system can search for text with a similar meaning.

Imagine your knowledge base contains this sentence:

    Employees can return a product within 30 days of purchase.

A user asks:

    How long do I have to send something back?

The words are different, but the meanings are related.

A traditional keyword search might struggle because the query does not contain the words “return” or “purchase.” Semantic search can identify the relationship in meaning using embeddings.

The basic process is:

    Text → Embedding Model → Vector → Similarity Search → Relevant Text

Embeddings help the system find relevant information even when the query and document use different words.

## 2. Why Do Embeddings Exist?

Consider three documents:

- Document A: “Employees receive 20 days of annual leave.”
- Document B: “Staff members are entitled to 20 vacation days per year.”
- Document C: “The office kitchen closes at 6 PM.”

A user asks:

    How much vacation time do employees get?

A keyword-based system may find Document A easily because it shares the word “employees.” But Document B may also be highly relevant even though it uses “staff members” and “vacation days.”

Embeddings help represent the meaning of the text so that A and B can be recognized as semantically related to the question.

They are useful for:

- Semantic search
- RAG retrieval
- Document clustering
- Recommendation systems
- Duplicate or near-duplicate detection
- Finding related content

In our RAG pipeline, embeddings help determine **which pieces of information are worth giving to the LLM**.

## 3. How Embeddings Work

An embedding model takes input text and produces a vector.

For illustration, imagine these vectors have only three dimensions:

    "I love programming"  → [0.8, 0.7, 0.1]
    "I enjoy coding"     → [0.79, 0.69, 0.12]
    "The weather is hot" → [0.1, 0.2, 0.9]

The first two vectors are close to each other, while the third is farther away.

Real embedding vectors commonly have hundreds or thousands of dimensions, depending on the model.

Each dimension is a numerical feature learned by the model. You generally cannot interpret one dimension as a simple human concept such as “happiness” or “programming.”

The important idea is that the model learns a representation in which useful semantic relationships can be measured.

**Important:** An embedding is not a summary or a translation of the sentence. It is a numerical representation designed for tasks such as comparing and retrieving text.

## 4. What Is Semantic Search?

Semantic search retrieves items based on similarity between their representations.

A typical RAG ingestion pipeline looks like this:

    Document
       ↓
    Chunking
       ↓
    Embedding Model
       ↓
    Store chunk text + vector + metadata

At query time:

    User question
       ↓
    Same embedding model
       ↓
    Query vector
       ↓
    Search stored vectors
       ↓
    Retrieve relevant chunks
       ↓
    Send chunks to the LLM

For example, suppose the database contains a chunk:

    Expense claims must be submitted within 30 days.

The user asks:

    What is the deadline for claiming my expenses?

The system embeds the question, searches for similar vectors, and may retrieve the chunk containing the deadline.

The LLM then uses that retrieved text to formulate an answer.

Notice the division of responsibilities:

- **Embedding model:** Represents text as vectors.
- **Vector search:** Finds nearby vectors.
- **Retrieved chunks:** Supply the actual evidence.
- **LLM:** Generates the answer from the evidence and other context.

The embedding model does not answer the user's question by itself.

## 5. How Do We Measure Similarity?

To compare vectors, systems commonly use cosine similarity, dot product, or Euclidean distance.

### A. Cosine similarity

Cosine similarity measures the angle between two vectors.

A useful intuition:

- Similar direction → high similarity.
- Perpendicular directions → similarity around zero.
- Opposite directions → negative similarity.

The formula is:

\[
\operatorname{cosine}(A,B)=
\frac{A\cdot B}{\|A\|\|B\|}
\]

Here:

- \(A\cdot B\) is the dot product.
- \(\|A\|\) is the magnitude, or length, of vector \(A\).
- \(\|B\|\) is the magnitude of vector \(B\).

For nonzero vectors, cosine similarity is between -1 and 1.

A value closer to 1 indicates a smaller angle and a more similar direction. It does not mean the texts are that percentage similar or that the result is that percentage correct.

### B. Dot product

The dot product measures both alignment and vector magnitude.

For normalized vectors—vectors scaled to length 1—the dot product equals cosine similarity.

### C. Euclidean distance

Euclidean distance measures the straight-line distance between two vectors.

A smaller distance means the vectors are closer under this metric.

### Which should we use?

It depends on the embedding model, how its vectors are trained, and the model's recommendations. Some systems normalize embeddings and use cosine similarity; others use dot product or distance-based metrics.

Do not assume one metric is always best.

## 6. Why the Same Embedding Model Matters

Suppose you store document embeddings using Model A, but generate query embeddings using an unrelated Model B.

The resulting vectors may belong to different learned representation spaces. Comparing them may produce meaningless retrieval results.

Therefore, the usual approach is:

1. Choose an embedding model.
2. Embed document chunks using that model.
3. Embed incoming queries using the compatible model.
4. Search the stored vectors using the configured similarity metric.

If you change the embedding model, you will generally need to regenerate the document embeddings and update the index.

Some models support specialized query and document encoders, so follow their compatibility requirements rather than assuming every model uses identical processing for both sides.

## 7. Embeddings Are Different from LLMs

| Embedding model | Generative LLM |
|---|---|
| Produces numerical vectors | Produces text or other supported outputs |
| Commonly used for semantic search | Commonly used for answering, reasoning, and generation |
| Helps find relevant information | Uses context to formulate a response |
| Often cheaper for retrieval workloads | Cost and latency vary with model and task |

A production RAG application may use both models:

    Document chunks
         ↓
    Embedding model
         ↓
    Vector database

    User question
         ↓
    Embedding model
         ↓
    Vector search
         ↓
    Relevant chunks
         ↓
    Generative LLM
         ↓
    Answer

The embedding model and generative LLM do not have to come from the same provider.

## 8. Semantic Search Is Not the Same as Keyword Search

Consider a document containing:

    HTTP 429 means the client has sent too many requests.

The user asks:

    Why is my API being rate limited?

Semantic search may identify the relationship between “rate limited” and “too many requests.”

Keyword search, on the other hand, looks for matching terms and can be very effective for exact identifiers, names, error codes, and technical terminology.

Neither approach wins in every situation.

For many production RAG systems, **hybrid search** combines keyword retrieval with semantic retrieval. We will explore that later in the syllabus.

Also, semantic similarity is not the same as factual correctness. Two passages can be semantically close while expressing different rules or even contradicting each other.

## 9. Practical Implementation

Imagine building a company-policy assistant.

During ingestion:

    chunks = [
        "Annual leave allowance is 20 days.",
        "Expense claims must be submitted within 30 days.",
        "Employees must use approved laptops."
    ]

    vectors = embedding_model.embed_documents(chunks)

    vector_database.store(
        texts=chunks,
        embeddings=vectors
    )

At query time:

    question = "How much annual vacation do I get?"

    query_vector = embedding_model.embed_query(question)

    results = vector_database.search(
        query_vector,
        top_k=3
    )

    answer = llm.generate(
        question=question,
        context=results
    )

This is conceptual pseudocode, not a specific provider's API.

The important detail is that documents are generally embedded during ingestion, not repeatedly every time a user asks a question. At query time, the system embeds the new question and searches the existing index.

For a production implementation, also consider metadata filters, authorization, score interpretation, retrieval thresholds, latency, and evaluation.

## 10. What Can Go Wrong?

### A. Semantically similar but incorrect results

A query about a 30-day refund period might retrieve a 30-day expense submission deadline. The numbers and language are similar, but the policies differ.

**Possible solution:** Improve chunk boundaries and metadata, use filters or hybrid search, and rerank candidates.

### B. Missing exact matches

A query containing an error code or product ID may not rank correctly through semantic search alone.

**Possible solution:** Combine semantic search with keyword search.

### C. Poor source text

If a PDF parser extracts scrambled text or destroys table relationships, the embedding model may represent incorrect or incomplete content.

**Possible solution:** Improve extraction and document processing before embedding.

### D. Wrong embedding configuration

Using incompatible models, dimensions, or distance metrics can undermine retrieval.

**Possible solution:** Keep the model configuration consistent and follow its documented requirements.

### E. Assuming a similarity score proves correctness

A high similarity score means the vectors are close under the chosen metric. It does not prove that the retrieved text answers the question.

**Possible solution:** Evaluate retrieval against real questions and known relevant documents.

## 11. Production Considerations

**Embedding cost:** Every document chunk needs an embedding when it is indexed. Reprocessing unchanged documents unnecessarily wastes time and money.

**Latency:** Query embedding and vector search add steps to the request. Measure their contribution to total response time.

**Indexing:** Large collections may need approximate nearest-neighbor search to avoid comparing a query against every vector.

**Versioning:** Track the embedding model and indexing configuration. Re-embedding after a model change should be treated as a controlled migration.

**Access control:** Apply authorization constraints to retrieval. Similarity search must not expose another user's private documents.

**Evaluation:** Measure whether relevant chunks are retrieved, not merely whether the final answer sounds convincing.

## 12. Interview Perspective

**Q: What is an embedding?**

An embedding is a numerical vector generated by a model to represent data in a learned space, allowing similarity-based operations such as semantic search.

**Q: Why do we need embeddings in RAG?**

They help retrieve relevant information based on meaning, including when a query uses different wording from the source document.

**Q: What is cosine similarity?**

It measures the cosine of the angle between two nonzero vectors and is commonly used to compare embedding directions.

**Q: Why not use an LLM to search all documents directly?**

Searching a large collection directly with a generative LLM is generally inefficient and costly. An embedding-based retrieval system can narrow the collection to relevant candidates before generation.

**Q: Does a higher similarity score guarantee a better answer?**

No. Similarity measures closeness under a particular representation and metric, not factual correctness or whether the passage fully answers the question.

**Q: What happens when we change the embedding model?**

The existing document vectors may no longer be compatible with the new query vectors. Typically, we regenerate embeddings and rebuild or migrate the index.

## 13. Summary

- Embeddings convert text into numerical vectors.
- Semantic search uses vector similarity to find relevant information.
- The embedding model represents text; the vector database stores and searches vectors; the LLM generates answers.
- Cosine similarity, dot product, and Euclidean distance are common comparison methods.
- Document and query embeddings must be compatible.
- Semantic search is useful for meaning-based retrieval, while keyword search remains valuable for exact terms.
- Similarity is not proof of relevance or correctness.
- Good retrieval requires good source data, appropriate chunking, compatible embeddings, and evaluation.

**Key mental model:** Embeddings help the system find *where the answer might be*. Retrieved text provides the evidence, and the LLM uses that evidence to produce the answer.

**Next lesson — Lesson 11: Vector Databases.** We will explore how vectors are stored, indexed, searched efficiently, and combined with metadata in a real RAG application.