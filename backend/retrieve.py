from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import settings
from sentence_transformers import CrossEncoder

embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
vectorstore = FAISS.load_local(settings.vector_store_path, embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="hybrid", search_kwargs={"k": settings.top_k})  # Hybrid

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def retrieve_docs(query: str, top_k: int):
    return retriever.invoke(query)

def rerank_docs(docs, query: str):
    pairs = [[query, doc.page_content] for doc in docs]
    scores = reranker.predict(pairs)
    sorted_docs = [doc for _, doc in sorted(zip(scores, docs), reverse=True)]
    return sorted_docs[:settings.top_k]
