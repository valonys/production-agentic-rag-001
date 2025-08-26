from langchain_openai import ChatOpenAI as OpenAIChat
from langchain_groq import ChatGroq
from .config import settings

# Initialize LLM based on provider
def get_llm():
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required when using Groq provider")
        return ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.llm_model
        )
    elif settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return OpenAIChat(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

try:
    llm = get_llm()
except Exception as e:
    print(f"Warning: Could not initialize LLM: {e}")
    llm = None

def safety_check(answer: str, context: str) -> bool:
    if llm is None:
        return True  # Skip safety check if LLM not configured
        
    prompt = f"Is this answer faithful to the context? Answer: {answer}\nContext: {context}\nReply yes/no."
    try:
        response = llm.invoke(prompt).content.strip().lower()
        return response == "yes"
    except Exception as e:
        print(f"Safety check failed: {e}")
        return True  # Allow response if safety check fails
