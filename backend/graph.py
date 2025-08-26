from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI as OpenAIChat
from langchain_groq import ChatGroq
from typing import TypedDict, List
from .retrieve import retrieve_docs, rerank_docs
from .synthesize import synthesize_answer
from .safety import safety_check
from .utils import logger, retry_with_backoff
from .config import settings

class State(TypedDict):
    messages: List[AIMessage | HumanMessage]
    context: str
    query: str

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

@retry_with_backoff(retries=3, backoff_in_seconds=1)
def rewrite_query(state: State):
    if llm is None:
        state["query"] = state["messages"][-1].content
        return state
        
    query = state["messages"][-1].content
    prompt = f"Rewrite this query for better retrieval: {query}"
    response = llm.invoke(prompt)
    state["query"] = response.content
    logger.info(f"Rewritten query: {state['query']}")
    return state

def retrieve_node(state: State):
    docs = retrieve_docs(state["query"], top_k=settings.top_k)
    reranked = rerank_docs(docs, state["query"])
    state["context"] = "\n".join([doc.page_content for doc in reranked])
    logger.info(f"Retrieved {len(reranked)} docs")
    return state

def synthesize_node(state: State):
    answer = synthesize_answer(state["query"], state["context"])
    state["messages"].append(AIMessage(content=answer))
    return state

def safety_node(state: State):
    if not safety_check(state["messages"][-1].content, state["context"]):
        state["messages"].append(AIMessage(content="Unsafe response detected. Refusing."))
    return state

def decide_exit(state: State):
    if len(state["context"]) < 100:  # Early exit if poor context
        return "end"
    return "continue"

workflow = StateGraph(State)
workflow.add_node("rewrite", rewrite_query)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("synthesize", synthesize_node)
workflow.add_node("safety", safety_node)

workflow.add_edge(START, "rewrite")
workflow.add_edge("rewrite", "retrieve")
workflow.add_conditional_edges("retrieve", decide_exit, {"continue": "synthesize", "end": END})
workflow.add_edge("synthesize", "safety")
workflow.add_edge("safety", END)

graph = workflow.compile()
