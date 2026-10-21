from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama  # 🦙 Ollama integration
from langchain_core.prompts import ChatPromptTemplate

# ⑤ Open the same vector store we built in step 1
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db       = Chroma(persist_directory="./chroma_db", embedding_function=embedder)

# 🦙 REPLACE OPENAI WITH OLLAMA
model    = ChatOllama(model="llama3.1:8b",base_url="http://localhost:11434",temperature=0)

# ⑥ The prompt: instructions + chunks + question
# Define the model's rules and placeholders for retrieved context and the question.
prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the context below. If the context doesn't contain
the answer, say "I don't know." Be concise and quote facts directly.

Context:
{context}

Question: {question}
""")

def rag_answer(question):
    # Convert the question to an embedding and retrieve the three closest chunks.
    chunks = db.similarity_search(question, k=3)         # ⑦ retrieve top 3

    # Combine the retrieved chunk text into one context block for the prompt.
    context = "\n\n".join(c.page_content for c in chunks)

    # Pipe the completed prompt into the chat model.
    chain = prompt | model                                # ⑧ chain trick

    # Run the chain and return only the model's text response.
    return chain.invoke({"context": context, "question": question}).content

# Ask an example question and print the grounded answer.
print(rag_answer("How long do I have to return something?"))
