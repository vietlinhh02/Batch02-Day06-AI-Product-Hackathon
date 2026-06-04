"""
Quick test RAG + LLM response - No Discord needed
Usage: python test_full.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_pipeline import RAGPipeline
from prompts import build_context_prompt, SYSTEM_PROMPT
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

from openai import OpenAI


def generate_answer(question: str, documents: list, scores: list) -> str:
    """Generate answer using LLM via OpenRouter."""
    if not OPENAI_API_KEY:
        return "ERROR: OPENAI_API_KEY not set"

    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

    # Build context prompt
    context_prompt = build_context_prompt(question, documents, scores)

    # Call LLM
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context_prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content


def main():
    print("=" * 60)
    print("   CLASSBOT - FULL TEST (RAG + LLM)")
    print("=" * 60)

    # Initialize pipeline
    print("\n[1] Khởi tạo RAG Pipeline...")
    pipeline = RAGPipeline()

    # Ingest sample data
    sample_file = Path(__file__).parent / "data" / "sample_messages.json"
    print(f"[2] Đọc sample data...")
    num_chunks = pipeline.ingest_messages(str(sample_file))
    print(f"    -> Đã ingest {num_chunks} chunks")

    # Test cases
    test_cases = [
        "Tối qua có bài tập gì không?",
        "Thầy nói gì về overfitting?",
        "Learning rate bao nhiêu là phù hợp?",
        "Deadline môn này là khi nào?",
        "Quiz bao gồm những gì?"
    ]

    print("\n" + "=" * 60)
    print("   TEST CASES WITH LLM RESPONSE")
    print("=" * 60)

    for i, query in enumerate(test_cases, 1):
        print(f"\n{'─' * 60}")
        print(f"TEST {i}: {query}")
        print(f"{'─' * 60}")

        # RAG retrieval
        result = pipeline.query(query)
        print(f"Type: {result['type']} | Confidence: {result['confidence']:.2f} | Docs: {len(result['documents'])}")

        # LLM generation
        print("\n🤖 ClassBot trả lời:")
        try:
            answer = generate_answer(query, result['documents'], result['scores'])
            print(answer)
        except Exception as e:
            print(f"Lỗi: {e}")

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
            print(f"\nType: {result['type']} | Confidence: {result['confidence']:.2f}")

            print("\n🤖 ClassBot:")
            answer = generate_answer(query, result['documents'], result['scores'])
            print(answer)

        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"Lỗi: {e}")


if __name__ == "__main__":
    main()
