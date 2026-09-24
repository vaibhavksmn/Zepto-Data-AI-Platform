# Zepto Support Assistant (`/support_assistant`)

A deterministic, offline-capable GenAI support service powered by LangGraph, ChromaDB, Sentence-Transformers, and FastAPI.

---

## 1. RAG Architecture & Data Flow
[User Query]
│
▼
[Stage 1: Intent Routing] ──── (Node: classify_intent)
│
├── "general_question" ──► [Node: direct_answer] ──► [Final Response]
│
└── "policy_question"
│
▼
[Stage 2: Retrieval] ──────── (ChromaDB + all-MiniLM-L6-v2)
│
▼
[Stage 3: Generation] ─────── (Node: retrieve_and_answer) ──► [Final Response]


### Pipeline Breakdown:
1. **Ingestion (`app/db.py`):** The 8 canonical policy text documents in `docs/` (`doc_01.txt` to `doc_08.txt`) are ingested into memory at startup.
2. **Embedding (`app/db.py`):** Embeddings are computed locally using `sentence-transformers/all-MiniLM-L6-v2`. Vectors are indexed in an in-memory ChromaDB collection (`zepto_policy_docs`) using cosine distance.
3. **Retrieval (`app/graph.py` -> `retrieve_and_answer_node`):** When a query is routed to retrieval, ChromaDB computes cosine similarity to fetch the top-3 matching chunks. This step runs for real in both mock and real-LLM modes.
4. **Generation (`app/graph.py`):** The final node generates an answer conforming to the Pydantic JSON schema (`answer`, `sources`, `confidence`).

### `MOCK_LLM` Toggle Behavior:
The service is controlled via the `MOCK_LLM` environment variable (default: `1` / True):
* **Default Mode (`MOCK_LLM=1`):**
  * **`classify_intent`:** Uses a deterministic keyword heuristic scanning for: `delivery`, `return`, `refund`, `membership`, `tracking`, `cancel`, `gift card`, `support hours`. No external network calls are made.
  * **`retrieve_and_answer`:** Retains real vector retrieval, but generates a deterministic answer using the canned format: `f"Based on the retrieved context: {top_chunk_snippet}"` with `confidence=1.0`.
  * **`direct_answer`:** Returns a fixed canned response: `"I can only answer questions about Zepto policies right now."` with `sources=[]` and `confidence=1.0`.
* **Real-LLM Mode (`MOCK_LLM=0`):**
  * Evaluates intent and executes generation by calling the Groq API (or specified LLM backend) with the structured template in `app/prompts.py`. If structured JSON validation fails, it retries up to 2 times before falling back to a structured error state.

---

## 2. Structured Prompt Template

The prompt implemented in `app/prompts.py` adheres strictly to the **Role-Context-Task-Format-Length** skeleton:

```text
[ROLE]
You are Zepto's Customer Support Assistant, specializing in delivering clear, accurate policy guidance to quick-commerce customers.

[CONTEXT]
{context}

[TASK]
Answer the user's question accurately using ONLY the provided policy context above.

[NEGATIVE CONSTRAINTS]
1. Do not answer using information, assumptions, or prior world knowledge that is not present in the provided context.
2. If the context does not contain sufficient details to answer the question, state: "I'm sorry, but that information is not available in Zepto's policy documentation."
3. Do not invent fees, timings, or conditions.

[FORMAT]
Respond STRICTLY with a valid JSON object matching this schema:
{
  "answer": "string",
  "sources": ["list of document IDs used, e.g. doc_01.txt"],
  "confidence": float between 0.0 and 1.0
}

[LENGTH]
Provide concise answers between 1 to 3 sentences.

[FEW-SHOT EXAMPLES]
Example 1:
Context: [doc_08.txt]: Zepto customer support is available via in-app chat 24 hours a day, 7 days a week. Phone support is not offered.
User Query: Can I call customer care on the phone?
JSON Output:
{
  "answer": "Phone support is not offered by Zepto. However, customer support is accessible via in-app chat 24/7.",
  "sources": ["doc_08.txt"],
  "confidence": 0.95
}