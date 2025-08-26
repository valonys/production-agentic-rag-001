from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys - use either OpenAI or Groq
    openai_api_key: str = ""
    groq_api_key: str = ""
    
    # Model Configuration
    llm_provider: str = "groq"  # "openai" or "groq"
    llm_model: str = "llama3-8b-8192"  # Groq model
    openai_model: str = "gpt-4o-mini"  # OpenAI model
    
    # Vector Store Configuration
    vector_store_path: str = "index.faiss"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG Configuration
    top_k: int = 5
    context_budget: int = 2000  # Tokens
    timeout_sec: int = 30

    class Config:
        env_prefix = ""

settings = Settings()
