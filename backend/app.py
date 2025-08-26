from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from .graph import graph
from .config import settings
import asyncio
import structlog

# Configure structured logging
logger = structlog.get_logger()

app = FastAPI(
    title="Agentic RAG API",
    description="Production-ready Agentic RAG system with streaming responses",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    version: str = "1.0.0"

async def stream_response(query: str):
    """Stream response using the full LangGraph workflow"""
    try:
        # Initialize state for the workflow
        state = {
            "messages": [HumanMessage(content=query)], 
            "query": query,
            "context": ""
        }
        
        # Stream events from the LangGraph workflow
        async for event in graph.astream_events(state, version="v2"):
            if event["event"] == "on_chain_end" and "messages" in event["data"]:
                # Get the final response
                final_message = event["data"]["messages"][-1]
                yield f"data: {final_message.content}\n\n"
                break
            elif event["event"] == "on_chain_start":
                logger.info("Starting RAG workflow", query=query)
            elif event["event"] == "on_chain_error":
                error_msg = event["data"].get("error", "Unknown error")
                logger.error("Workflow error", error=error_msg)
                yield f"data: Error: {error_msg}\n\n"
                break
                
    except Exception as e:
        logger.error("Streaming error", error=str(e))
        yield f"data: Error: {str(e)}\n\n"

@app.post("/chat")
async def chat(query: Query):
    """
    Streaming chat endpoint with full RAG workflow
    
    This endpoint processes queries through the complete agentic RAG pipeline:
    1. Query rewriting for better retrieval
    2. Document retrieval and reranking
    3. Answer synthesis with citations
    4. Safety validation
    """
    try:
        logger.info("Chat request received", message=query.message[:100])
        return StreamingResponse(
            stream_response(query.message), 
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error("Chat endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Agentic RAG API is running!",
        "provider": settings.llm_provider,
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint for monitoring and load balancers
    
    Returns the current status of the API and configuration.
    """
    return HealthResponse(
        status="healthy",
        llm_provider=settings.llm_provider
    )

@app.get("/config")
async def get_config():
    """
    Configuration endpoint (non-sensitive information only)
    
    Returns current configuration without exposing API keys.
    """
    return {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "top_k": settings.top_k,
        "context_budget": settings.context_budget,
        "timeout_sec": settings.timeout_sec,
        "embedding_model": settings.embedding_model
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
