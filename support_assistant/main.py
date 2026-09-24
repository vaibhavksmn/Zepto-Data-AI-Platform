from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schemas import QueryRequest, SupportResponse
from app.graph import rag_graph
from app.db import get_chroma_collection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize ChromaDB on startup
    get_chroma_collection()
    yield

app = FastAPI(title="Zepto Support Assistant", lifespan=lifespan)

@app.post("/ask", response_model=SupportResponse)
async def ask_question(request: QueryRequest):
    initial_state = {
        "query": request.query,
        "intent": "",
        "retrieved_chunks": [],
        "final_response": {}
    }
    result = rag_graph.invoke(initial_state)
    return result["final_response"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)