import os
import glob
import chromadb
from chromadb.utils import embedding_functions
from app.config import COLLECTION_NAME, EMBEDDING_MODEL_NAME

_client = None
_collection = None

def get_chroma_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.Client()  # In-memory client
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )
    
    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Ingest 8 documents if empty
    if _collection.count() == 0:
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        doc_files = sorted(glob.glob(os.path.join(docs_dir, "doc_*.txt")))
        
        ids, documents, metadatas = [], [], []
        for file_path in doc_files:
            file_name = os.path.basename(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            ids.append(file_name)
            documents.append(content)
            metadatas.append({"source": file_name})
            
        _collection.add(ids=ids, documents=documents, metadatas=metadatas)
    
    return _collection