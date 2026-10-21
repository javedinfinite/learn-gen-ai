from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ① load your documents (any text — for now, hardcoded)
docs = [
    "Our return policy allows refunds within 30 days of purchase.",
    "Shipping is free for orders above ₹999 across India.",
    "For corporate orders above 50 units, contact sales@example.com.",
    "Our office is in Indiranagar, Bangalore. Open Mon-Fri 10am-7pm.",
]

# ② split into chunks (small docs here, but production = thousands of pages)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.create_documents(docs)

# ③ pick an embedding model (free, runs locally, no API key)
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ④ build the vector store from chunks + embeddings (saves to disk)
db = Chroma.from_documents(chunks, embedder, persist_directory="./chroma_db")

print(f"Indexed {len(chunks)} chunks 🎉")