from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="RAG Assistant AI Service")

documents = [
    {
        "id": 1,
        "title": "Refund Policy",
        "content": (
            "Customers can request a refund within "
            "30 days of purchase. Products must be "
            "unused and in their original condition."
        ),
        "source": "refund-policy.txt",
    },
    {
        "id": 2,
        "title": "Shipping Policy",
        "content": (
            "Standard shipping usually takes 3 to 5 "
            "business days. Express shipping is also "
            "available for eligible orders."
        ),
        "source": "shipping-policy.txt",
    },
    {
        "id": 3,
        "title": "Warranty Policy",
        "content": (
            "Eligible products include a one-year "
            "warranty covering manufacturing defects."
        ),
        "source": "warranty-policy.txt",
    },
]


class SearchRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search")
def search(request: SearchRequest):
    query_words = set(request.query.lower().split())

    if not query_words:
        return {"results": []}

    results = []

    for document in documents:
        searchable_text = (
            document["title"] + " " + document["content"]
        ).lower()

        document_words = set(searchable_text.split())
        matched_words = query_words & document_words

        if matched_words:
            results.append({
                **document,
                "score": len(matched_words),
            })

    results.sort(
        key=lambda document: document["score"],
        reverse=True,
    )

    print('results: ', results, "\n" )
    print("results [:3]", results[:3])

    return {"results": results[:3]}