import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.config import MOCK_LLM, GROQ_API_KEY
from app.schemas import SupportResponse
from app.db import get_chroma_collection
from app.prompts import SYSTEM_RAG_PROMPT

class GraphState(TypedDict):
    query: str
    intent: str
    retrieved_chunks: List[Dict[str, Any]]
    final_response: Dict[str, Any]

# Keyword list for deterministic mock classification
POLICY_KEYWORDS = [
    "delivery", "return", "refund", "membership", 
    "tracking", "cancel", "gift card", "support hours"
]

def classify_intent_node(state: GraphState) -> Dict[str, Any]:
    query_lower = state["query"].lower()
    
    if MOCK_LLM:
        if any(keyword in query_lower for keyword in POLICY_KEYWORDS):
            intent = "policy_question"
        else:
            intent = "general_question"
    else:
        # Optional real LLM intent classification (e.g. Groq)
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Classify the query as 'policy_question' (if asking about delivery, returns, refunds, membership, tracking, cancellations, gift cards, or support hours) or 'general_question'. Respond with ONLY the label."},
                    {"role": "user", "content": state["query"]}
                ],
                temperature=0.0
            )
            parsed = resp.choices[0].message.content.strip().lower()
            intent = "policy_question" if "policy" in parsed else "general_question"
        except Exception:
            intent = "policy_question" if any(k in query_lower for k in POLICY_KEYWORDS) else "general_question"

    return {"intent": intent}

def retrieve_and_answer_node(state: GraphState) -> Dict[str, Any]:
    collection = get_chroma_collection()
    query = state["query"]
    
    # Cosine similarity retrieval (runs for real in both modes)
    results = collection.query(query_texts=[query], n_results=3)
    
    chunks = []
    top_chunk_snippet = ""
    sources = []
    if results and results["documents"] and len(results["documents"][0]) > 0:
        docs = results["documents"][0]
        ids = results["ids"][0]
        sources = ids
        top_chunk_snippet = docs[0][:200]
        for doc_id, doc_text in zip(ids, docs):
            chunks.append({"id": doc_id, "text": doc_text})

    if MOCK_LLM:
        answer_text = f"Based on the retrieved context: {top_chunk_snippet}"
        validated = SupportResponse(
            answer=answer_text,
            sources=sources,
            confidence=1.0
        )
        return {"retrieved_chunks": chunks, "final_response": validated.model_dump()}
    else:
        # Real LLM call with retry mechanism (max 2 retries)
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        context_str = "\n\n".join([f"[{c['id']}]: {c['text']}" for c in chunks])
        prompt = SYSTEM_RAG_PROMPT.format(context=context_str)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                raw_json = json.loads(resp.choices[0].message.content)
                validated = SupportResponse(**raw_json)
                return {"retrieved_chunks": chunks, "final_response": validated.model_dump()}
            except Exception as e:
                if attempt < 2:
                    messages.append({"role": "user", "content": f"Formatting error: {str(e)}. Return pure JSON matching schema."})
                else:
                    return {
                        "retrieved_chunks": chunks,
                        "final_response": {
                            "answer": "Error: Failed to produce valid structured output.",
                            "sources": sources,
                            "confidence": 0.0
                        }
                    }

def direct_answer_node(state: GraphState) -> Dict[str, Any]:
    if MOCK_LLM:
        validated = SupportResponse(
            answer="I can only answer questions about Zepto policies right now.",
            sources=[],
            confidence=1.0
        )
        return {"final_response": validated.model_dump()}
    else:
        # Direct answer from LLM with no retrieval
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        try:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Keep it concise. Respond in JSON: {\"answer\": string, \"sources\": [], \"confidence\": 0.9}"},
                    {"role": "user", "content": state["query"]}
                ],
                response_format={"type": "json_object"}
            )
            raw = json.loads(resp.choices[0].message.content)
            validated = SupportResponse(**raw)
            return {"final_response": validated.model_dump()}
        except Exception:
            return {
                "final_response": {
                    "answer": "I can only assist with Zepto policy questions.",
                    "sources": [],
                    "confidence": 0.5
                }
            }

def route_intent(state: GraphState) -> str:
    return state["intent"]

# Build StateGraph
builder = StateGraph(GraphState)
builder.add_node("classify_intent", classify_intent_node)
builder.add_node("retrieve_and_answer", retrieve_and_answer_node)
builder.add_node("direct_answer", direct_answer_node)

builder.set_entry_point("classify_intent")
builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "policy_question": "retrieve_and_answer",
        "general_question": "direct_answer"
    }
)
builder.add_edge("retrieve_and_answer", END)
builder.add_edge("direct_answer", END)

rag_graph = builder.compile()