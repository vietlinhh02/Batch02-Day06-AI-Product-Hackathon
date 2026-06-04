"""
Clear all data in vector store
Usage: python clear_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_pipeline import RAGPipeline

def main():
    print("Xóa dữ liệu trong vector store...")
    pipeline = RAGPipeline()
    
    # Delete collection
    try:
        pipeline.vector_store.client.delete_collection("discord_messages")
        print("✅ Đã xóa collection 'discord_messages'")
    except Exception as e:
        print(f"⚠️ Collection không tồn tại hoặc lỗi: {e}")
    
    # Recreate empty collection
    pipeline.vector_store.collection = pipeline.vector_store.client.get_or_create_collection(
        name="discord_messages",
        metadata={"hnsw:space": "cosine"}
    )
    print("✅ Đã tạo collection mới (trống)")
    
    # Verify
    stats = pipeline.get_stats()
    print(f"📊 Documents trong store: {stats['vector_store']['total_documents']}")

if __name__ == "__main__":
    main()
