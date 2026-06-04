"""
Web UI for testing RAG pipeline - No Discord needed
Usage: python web_ui.py
Then open http://localhost:5000
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from flask import Flask, render_template_string, request, jsonify
from rag_pipeline import RAGPipeline
from prompts import build_context_prompt

app = Flask(__name__)
pipeline = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClassBot - RAG Test UI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #36393f; color: #dcddde; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; color: #5865f2; margin-bottom: 20px; }
        .chat-box { background: #2f3136; border-radius: 8px; padding: 20px; min-height: 400px; max-height: 600px; overflow-y: auto; margin-bottom: 20px; }
        .message { margin-bottom: 16px; display: flex; gap: 12px; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
        .user-avatar { background: #5865f2; }
        .bot-avatar { background: #57f287; }
        .message-content { flex: 1; }
        .author { font-weight: 600; margin-bottom: 4px; }
        .user-name { color: #5865f2; }
        .bot-name { color: #57f287; }
        .text { line-height: 1.5; }
        .meta { font-size: 12px; color: #72767d; margin-top: 8px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .badge-happy { background: #57f287; color: #000; }
        .badge-low { background: #fee75c; color: #000; }
        .badge-fail { background: #ed4245; color: #fff; }
        .input-area { display: flex; gap: 12px; }
        input[type="text"] { flex: 1; padding: 12px 16px; border-radius: 8px; border: none; background: #40444b; color: #dcddde; font-size: 16px; }
        input[type="text"]:focus { outline: 2px solid #5865f2; }
        button { padding: 12px 24px; border-radius: 8px; border: none; background: #5865f2; color: #fff; font-size: 16px; font-weight: 600; cursor: pointer; }
        button:hover { background: #4752c4; }
        .source { background: #2f3136; border-left: 3px solid #5865f2; padding: 8px 12px; margin-top: 8px; border-radius: 0 4px 4px 0; }
        .score { color: #fee75c; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 ClassBot - RAG Test UI</h1>
        <div class="chat-box" id="chatBox">
            <div class="message">
                <div class="avatar bot-avatar">🤖</div>
                <div class="message-content">
                    <div class="author bot-name">ClassBot</div>
                    <div class="text">Xin chào! Tôi là ClassBot. Hãy hỏi tôi về nội dung buổi học. Ví dụ: "Bài tập CNN là gì?"</div>
                </div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="queryInput" placeholder="Nhập câu hỏi..." onkeypress="if(event.key==='Enter') sendQuery()">
            <button onclick="sendQuery()">Gửi</button>
        </div>
    </div>
    <script>
        function sendQuery() {
            const input = document.getElementById('queryInput');
            const query = input.value.trim();
            if (!query) return;
            
            // Add user message
            addMessage('user', query);
            input.value = '';
            
            // Send to API
            fetch('/api/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            })
            .then(r => r.json())
            .then(data => {
                addMessage('bot', data);
            })
            .catch(err => {
                addMessage('bot', {type: 'error', answer: 'Lỗi kết nối: ' + err});
            });
        }
        
        function addMessage(type, data) {
            const chatBox = document.getElementById('chatBox');
            const div = document.createElement('div');
            div.className = 'message';
            
            if (type === 'user') {
                div.innerHTML = `
                    <div class="avatar user-avatar">👤</div>
                    <div class="message-content">
                        <div class="author user-name">Bạn</div>
                        <div class="text">${data}</div>
                    </div>
                `;
            } else {
                let badge = '';
                if (data.type === 'happy') badge = '<span class="badge badge-happy">✅ Tìm thấy</span>';
                else if (data.type === 'low_confidence') badge = '<span class="badge badge-low">⚠️ Ít kết quả</span>';
                else badge = '<span class="badge badge-fail">❌ Không tìm thấy</span>';
                
                let sources = '';
                if (data.documents && data.documents.length > 0) {
                    sources = '<div class="source"><strong>Nguồn:</strong><br>';
                    data.documents.forEach((doc, i) => {
                        sources += `${i+1}. <span class="score">[${data.scores[i].toFixed(2)}]</span> ${doc.author}: ${doc.content.substring(0, 80)}...<br>`;
                    });
                    sources += '</div>';
                }
                
                div.innerHTML = `
                    <div class="avatar bot-avatar">🤖</div>
                    <div class="message-content">
                        <div class="author bot-name">ClassBot ${badge}</div>
                        <div class="text">${data.answer || 'Không tìm thấy thông tin.'}</div>
                        ${sources}
                        <div class="meta">Confidence: ${(data.confidence * 100).toFixed(0)}% | Documents: ${data.documents ? data.documents.length : 0}</div>
                    </div>
                `;
            }
            
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query', '')
    
    if not query_text:
        return jsonify({'type': 'error', 'answer': 'Câu hỏi trống'})
    
    result = pipeline.query(query_text)
    
    # Build context for LLM (without actual LLM call for testing)
    if result['type'] == 'failure':
        answer = f'Không tìm thấy thông tin về "{query_text}" trong lịch sử chat. Thử hỏi trực tiếp giảng viên.'
    elif result['type'] == 'low_confidence':
        answer = f'Chỉ tìm thấy ít thông tin về "{query_text}". '
        if result['documents']:
            answer += f'{result["documents"][0]["author"]} nói: {result["documents"][0]["content"][:100]}...'
    else:
        if result['documents']:
            doc = result['documents'][0]
            answer = f'{doc["author"]} nói: {doc["content"][:200]}'
        else:
            answer = 'Không tìm thấy thông tin.'
    
    return jsonify({
        'type': result['type'],
        'answer': answer,
        'confidence': result['confidence'],
        'documents': result['documents'][:3],
        'scores': result['scores'][:3]
    })

@app.route('/api/stats')
def stats():
    return jsonify(pipeline.get_stats())

def main():
    global pipeline
    
    print("=" * 60)
    print("   CLASSBOT - WEB TEST UI")
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
    print(f"    -> Đã ingest {num_chunks} chunks")
    
    print(f"\n[3] Khởi động web server...")
    print(f"    -> Mở trình duyệt: http://localhost:5000")
    print(f"    -> Hoặc: http://127.0.0.1:5000")
    print(f"\n    Nhấn Ctrl+C để thoát")
    
    app.run(debug=False, port=5000)

if __name__ == "__main__":
    main()
