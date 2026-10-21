from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama  # 🦙 Ollama integration
from langchain_core.prompts import ChatPromptTemplate

# ⑤ Open the same vector store we built in step 1
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db       = Chroma(persist_directory="./chroma_db", embedding_function=embedder)

# 🦙 REPLACE OPENAI WITH OLLAMA
model    = ChatOllama(model="qwen2.5-coder:3b", temperature=0)

# ⑥ The prompt: instructions + chunks + question
prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the context below. If the context doesn't contain
the answer, say "I don't know." Be concise and quote facts directly.

Context:
{context}

Question: {question}
""")

def rag_answer(question):
    chunks = db.similarity_search(question, k=3)         # ⑦ retrieve top 3
    context = "\n\n".join(c.page_content for c in chunks)
    chain = prompt | model                                # ⑧ chain trick
    return chain.invoke({"context": context, "question": question}).content

print(rag_answer("How long do I have to return something?"))