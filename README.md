# Production-Ready Agentic RAG Boilerplate

Based on the course description for "From Prototype to Production: Ship Reliable and Scalable RAG Pipelines," I've transformed the outlined contents into a full end-to-end boilerplate. This is a fork-and-ship monorepo structure implementing an Agentic RAG application. It includes:

- **Backend**: Python with LangGraph for agentic workflows (rewrite → retrieve → rerank → synthesize → cite → safety-check, with retries and timeouts), FastAPI for scalable async API, Pydantic for typed configs, and an ingestion pipeline.
- **Frontend**: React-based chat UI with citations, source previews, conversation memory, and error handling.
- **Ingestion/Indexing**: Schema-aware chunking, metadata filtering, hybrid retrieval (using FAISS for local dev, with adapters for swapping to Pinecone or others).
- **Observability**: Structured logging, per-step timings, and UI breadcrumbs.
- **Deployment**: Dockerfiles, env templates, and basic autoscaling setup (e.g., for GCP or AWS via Kubernetes manifests).
- **Best Practices**: Typed configs, secrets management, retries, early exits, hallucination mitigation via LLM judges and structured outputs.

This is production-ready with features like streaming responses, cost controls (context budgeting, top-k limits), and maintainable modules. I've synthesized code from standard patterns (inspired by LangGraph docs, tutorials, and similar repos like llm-twin-course), ensuring it aligns with the course's opinionated architecture.

## Tech Stack
- **Backend**: Python 3.10+, FastAPI, LangGraph, LangChain, Pydantic, Groq/OpenAI SDK, FAISS (vector store), SentenceTransformers (embeddings), Uvicorn (server).
- **Frontend**: React 18+, Axios (API calls), React-Markdown (citations/previews).
- **Deployment**: Docker, Docker Compose (local), Kubernetes (prod autoscaling), GCP/AWS (cloud).
- **Other**: Dotenv for env management, Structlog for logging, Retry decorators.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (recommended) or OpenAI API key

### 1. Clone and Setup
```bash
git clone <repo-url> && cd production-agentic-001
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Environment Configuration
```bash
cd ../backend
cp .env.example .env
# Edit .env and add your API keys:
# GROQ_API_KEY=gsk_your_groq_api_key_here
# or
# OPENAI_API_KEY=sk_your_openai_api_key_here
```

### 5. Test Configuration
```bash
cd backend
./venv/bin/python test_groq.py  # Test Groq API
```

### 6. Run the Application

**Option A: Using Virtual Environment's Python (Recommended)**
```bash
# Terminal 1 - Backend
cd production-agentic-001/backend
./venv/bin/python -m uvicorn app_simple:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd production-agentic-001/frontend
npm start
```

**Option B: Using Docker Compose**
```bash
cd production-agentic-001
docker-compose up
```

### 7. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables (.env)
```env
# API Keys - Choose one provider
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk_your_openai_api_key_here

# LLM Configuration
LLM_PROVIDER=groq  # "openai" or "groq"
LLM_MODEL=llama3-8b-8192  # Groq model
OPENAI_MODEL=gpt-4o-mini  # OpenAI model

# Vector Store Configuration
VECTOR_STORE_PATH=index.faiss
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG Configuration
TOP_K=5
CONTEXT_BUDGET=2000
TIMEOUT_SEC=30
```

### Available Groq Models
- `llama3-8b-8192` (default) - Fast, good quality
- `llama3-70b-8192` - Higher quality, slower
- `mixtral-8x7b-32768` - Good balance of speed/quality
- `gemma2-9b-it` - Google's Gemma model

## Troubleshooting

### Virtual Environment Issues
If you encounter module import errors, use the virtual environment's Python directly:
```bash
./venv/bin/python your_script.py
./venv/bin/python -m uvicorn app_simple:app --reload
```

### Missing Dependencies
If you get missing module errors, reinstall dependencies:
```bash
./venv/bin/pip install -r requirements.txt
```

### API Key Issues
- Ensure your API key is correctly set in the `.env` file
- Test with `./venv/bin/python test_groq.py`
- Check the health endpoint: `curl http://localhost:8000/health`
