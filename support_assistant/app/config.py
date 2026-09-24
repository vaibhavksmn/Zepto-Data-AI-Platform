import os

# Default MOCK_LLM to 1 (True) for the required offline/mock path
MOCK_LLM = os.getenv("MOCK_LLM", "1").strip().lower() in ("1", "true", "yes")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
COLLECTION_NAME = "zepto_policy_docs"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"