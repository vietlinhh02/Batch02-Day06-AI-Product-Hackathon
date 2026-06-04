"""
Test RAG pipeline directly via CLI - No Discord needed
Usage: python test_rag.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_pipeline import RAGPipeline
from prompts import build_context_prompt, RESPONSE_TEMPLATES


def main():
    print("=" * 60)
    print("   DISCORD CLASS BOT - RAG PIPELINE TEST")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n[1] Khởi tạo RAG Pipeline...")
    pipeline = RAGPipeline()
    
    # Ingest sample data
    sample_file = Path(__file__).parent / "data" / "sample_messages.json"
    print(f"[2] Đọc sample data từ: {sample_file}")
    
    if not sample_file.exists():
        print(f"ERROR: File không tồn tại: {sample_file}")
        return
    
    num_chunks = pipeline.ingest_messages(str(sample_file))
    print(f"    -> Đã ingest {num_chunks} chunks vào vector store")
    
    # Show stats
    stats = pipeline.get_stats()
    print(f"\n[3] Vector Store Stats:")
    print(f"    - Documents: {stats['vector_store']['total_documents']}")
    print(f"    - Chunk size: {stats['config']['chunk_size']}")
    print(f"    - Top-k: {stats['config']['top_k']}")
    print(f"    - Threshold: {stats['config']['similarity_threshold']}")
    
    # Test queries
    print("\n" + "=" * 60)
    print("   TEST CASES")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Happy Path - Tìm bài tập",
            "query": "Tối qua có bài tập gì không?"
        },
        {
            "name": "Happy Path - Tìm kiến thức",
            "query": "Thầy nói gì về overfitting?"
        },
        {
            "name": "Low Confidence - Tìm kiếm mơ hồ",
            "query": "Thầy nói gì về overfitting?"
        },
        {
            "name": "Failure - Không tìm thấy",
            "query": "Deadline môn này là khi nào?"
        },
        {
            "name": "Happy Path - Learning rate",
            "query": "Learning rate bao nhiêu là phù hợp?"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 60}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'─' * 60}")
        print(f"Query: {test['query']}")
        
        # Run RAG query
        result = pipeline.query(test['query'])
        
        print(f"\nResult Type: {result['type']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Documents Found: {len(result['documents'])}")
        
        if result['documents']:
            print(f"\nTop Results:")
            for j, (doc, score) in enumerate(zip(result['documents'][:3], result['scores'][:3]), 1):
                print(f"  {j}. [{score:.2f}] {doc['author']}: {doc['content'][:80]}...")
        
        # Build context prompt
        context_prompt = build_context_prompt(
            result['question'],
            result['documents'],
            result['scores']
        )
        
        print(f"\nContext Prompt (first 500 chars):")
        print(f"  {context_prompt[:500]}...")
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("   INTERACTIVE MODE")
    print("=" * 60)
    print("Nhập câu hỏi (hoặc 'quit' để thoát):")
    
    while True:
        try:
            query = input("\n> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                print("Tạm biệt!")
                break
            
            if not query:
                continue
            
            result = pipeline.query(query)
            
            print(f"\nType: {result['type']}")
            print(f"Confidence: {result['confidence']:.2f}")
            
            if result['documents']:
                print(f"\nTop Results:")
                for j, (doc, score) in enumerate(zip(result['documents'][:3], result['scores'][:3]), 1):
                    print(f"  {j}. [{score:.2f}] {doc['author']}: {doc['content'][:100]}")
                    if doc.get('message_link'):
                        print(f"     Link: {doc['message_link']}")
            else:
                print("Không tìm thấy kết quả.")
                
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"Lỗi: {e}")


if __name__ == "__main__":
    main()
