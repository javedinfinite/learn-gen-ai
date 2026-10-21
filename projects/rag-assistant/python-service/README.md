Run the service
From your src/python_service directory, run:
uv add fastapi "uvicorn[standard]"
uv run uvicorn main:app --reload --port 8000
Test these endpoints:
- Health check
- Interactive API documentation
In /docs, open POST /search, click Try it out, and submit:
{
  "query": "refund within 30 days"
}
You should see the Refund Policy document in the results.
This is our first working retrieval implementation. It uses simple keyword matching; we'll improve it with semantic search and embeddings later.

to create vector index for RAG
```
uv run python ex1/index.py
```

to run RAG and LLM
```
uv run python ex1/rag.py
```