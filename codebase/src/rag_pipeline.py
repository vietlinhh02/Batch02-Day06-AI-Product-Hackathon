"""
RAG Pipeline for Discord Class Bot
Handles: text chunking, embedding, vector store, retrieval
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import chromadb
from chromadb.config import Settings
from openai import OpenAI

from config import (
    OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_EMBEDDING_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, SIMILARITY_THRESHOLD,
    CHROMA_DIR, DATA_DIR, MAX_CONTEXT_LENGTH
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextChunker:
    """Split text into overlapping chunks for embedding."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_message(self, message: Dict) -> List[Dict]:
        """Chunk a single message into smaller pieces if needed."""
        content = message["content"]
        
        # If message is short enough, return as single chunk
        if len(content.split()) <= self.chunk_size:
            return [{
                "content": content,
                "author": message["author"],
                "user_id": message.get("user_id", ""),
                "role": message.get("role", "member"),
                "timestamp": message["timestamp"],
                "message_id": message["id"],
                "channel": message.get("channel", "general"),
                "reply_to": message.get("reply_to"),
                "message_link": message.get("message_link", self._generate_link(message))
            }]
        
        # Split long message into chunks
        words = content.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "content": chunk_text,
                "author": message["author"],
                "user_id": message.get("user_id", ""),
                "role": message.get("role", "member"),
                "timestamp": message["timestamp"],
                "message_id": message["id"],
                "channel": message.get("channel", "general"),
                "reply_to": message.get("reply_to"),
                "message_link": message.get("message_link", self._generate_link(message))
            })
        
        return chunks
    
    def _generate_link(self, message: Dict) -> str:
        """Return empty if no message_link provided — links come from Discord API."""
        return ""
    
    def chunk_messages(self, messages: List[Dict]) -> List[Dict]:
        """Chunk all messages."""
        all_chunks = []
        for msg in messages:
            chunks = self.chunk_message(msg)
            all_chunks.extend(chunks)
        return all_chunks


class EmbeddingEngine:
    """Generate embeddings using OpenRouter."""
    
    def __init__(self, api_key: str = OPENAI_API_KEY, base_url: str = OPENAI_BASE_URL, model: str = OPENAI_EMBEDDING_MODEL):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        return all_embeddings


class VectorStore:
    """ChromaDB vector store for message retrieval."""
    
    def __init__(self, persist_directory: str = str(CHROMA_DIR)):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="discord_messages",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Add documents with embeddings to vector store."""
        import time
        timestamp = int(time.time() * 1000)
        ids = [f"msg_{timestamp}_{i}" for i in range(len(chunks))]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [{
            "author": chunk["author"],
            "user_id": chunk.get("user_id", ""),
            "role": chunk["role"],
            "timestamp": chunk["timestamp"],
            "message_id": chunk["message_id"],
            "channel": chunk["channel"],
            "message_link": chunk.get("message_link", "")
        } for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Added {len(chunks)} documents to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = TOP_K) -> Tuple[List[Dict], List[float]]:
        """Search for similar documents."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Convert distances to similarity scores (cosine)
        # ChromaDB returns distances, lower is better
        # We convert to similarity: 1 - distance
        documents = []
        scores = []
        
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity = 1 - dist  # Convert distance to similarity
                if similarity >= SIMILARITY_THRESHOLD:
                    documents.append({
                        "content": doc,
                        "author": meta["author"],
                        "user_id": meta.get("user_id", ""),
                        "role": meta["role"],
                        "timestamp": meta["timestamp"],
                        "message_id": meta["message_id"],
                        "channel": meta["channel"],
                        "message_link": meta.get("message_link", "")
                    })
                    scores.append(similarity)
        
        return documents, scores
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics."""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name
        }
    
    def search_by_user(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Search for messages by a specific user with pagination support."""
        results = self.collection.get(
            where={"user_id": user_id},
            limit=limit,
            offset=offset,
            include=["documents", "metadatas"]
        )
        
        documents = []
        if results["documents"]:
            for doc, meta in zip(results["documents"], results["metadatas"]):
                documents.append({
                    "content": doc,
                    "author": meta["author"],
                    "user_id": meta.get("user_id", ""),
                    "role": meta["role"],
                    "timestamp": meta["timestamp"],
                    "message_id": meta["message_id"],
                    "channel": meta["channel"],
                    "message_link": meta.get("message_link", "")
                })
        
        return documents


class RAGPipeline:
    """Complete RAG pipeline for Discord Class Bot."""
    
    def __init__(self):
        self.chunker = TextChunker()
        self.embedder = EmbeddingEngine()
        self.vector_store = VectorStore()
    
    def ingest_messages(self, messages_file: str):
        """Ingest messages from JSON file into vector store."""
        logger.info(f"Loading messages from {messages_file}")
        
        with open(messages_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data["messages"]
        logger.info(f"Loaded {len(messages)} messages")
        
        # Chunk messages
        chunks = self.chunker.chunk_messages(messages)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedder.embed_batch(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store in vector DB
        self.vector_store.add_documents(chunks, embeddings)
        logger.info("Ingestion complete!")
        
        return len(chunks)
    
    def query(self, question: str) -> Dict:
        """Query the RAG system."""
        logger.info(f"Processing query: {question}")
        
        # Generate query embedding
        query_embedding = self.embedder.embed_text(question)
        
        # Search vector store
        documents, scores = self.vector_store.search(query_embedding)
        
        # Build response
        if not documents:
            return {
                "type": "failure",
                "question": question,
                "answer": None,
                "documents": [],
                "scores": [],
                "confidence": 0
            }
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if len(scores) == 1 and scores[0] < 0.4:
            return {
                "type": "low_confidence",
                "question": question,
                "answer": None,
                "documents": documents,
                "scores": scores,
                "confidence": avg_score
            }
        
        return {
            "type": "happy",
            "question": question,
            "answer": None,  # Will be generated by LLM
            "documents": documents,
            "scores": scores,
            "confidence": avg_score
        }
    
    def query_user_messages(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Query messages from a specific user with pagination support."""
        return self.vector_store.search_by_user(user_id, limit, offset)
    
    def get_stats(self) -> Dict:
        """Get pipeline statistics."""
        return {
            "vector_store": self.vector_store.get_collection_stats(),
            "config": {
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "top_k": TOP_K,
                "similarity_threshold": SIMILARITY_THRESHOLD
            }
        }


def main():
    """Test the RAG pipeline."""
    pipeline = RAGPipeline()
    
    # Ingest sample data
    sample_file = DATA_DIR / "sample_messages.json"
    if sample_file.exists():
        num_chunks = pipeline.ingest_messages(str(sample_file))
        print(f"Ingested {num_chunks} chunks")
        
        # Test queries
        test_queries = [
            "Tối qua có bài tập gì không?",
            "Thầy nói gì về overfitting?",
            "Deadline môn này là khi nào?",
            "Learning rate bao nhiêu là phù hợp?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"Query: {query}")
            result = pipeline.query(query)
            print(f"Type: {result['type']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Documents found: {len(result['documents'])}")
            if result['documents']:
                print(f"Top result: {result['documents'][0]['content'][:100]}...")
    else:
        print(f"Sample file not found: {sample_file}")


if __name__ == "__main__":
    main()
