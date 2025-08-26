from langchain_openai import ChatOpenAI as OpenAIChat
from langchain_groq import ChatGroq
from .config import settings
from pydantic import BaseModel, Field

class StructuredAnswer(BaseModel):
    answer: str = Field(description="The final answer")
    citations: list[str] = Field(description="List of cited sources")

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

def synthesize_answer(query: str, context: str):
    if llm is None:
        return f"Error: LLM not configured. Query: {query}"
        
    prompt = f"Answer based on context: {context}\nQuery: {query}\nProvide citations."
    try:
        structured_llm = llm.with_structured_output(StructuredAnswer)
        response = structured_llm.invoke(prompt)
        return f"{response.answer} (Citations: {', '.join(response.citations)})"
    except Exception as e:
        # Fallback to simple response if structured output fails
        response = llm.invoke(prompt)
        return response.content
