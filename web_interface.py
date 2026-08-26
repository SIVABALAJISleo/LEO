"""
Simple Flask web interface for LEO.
Run this and open http://localhost:5000 in your browser.
"""

import json
from leo_engine import LEOv7_MemoryEfficient

try:
    from flask import Flask, render_template_string, request, jsonify
    app = Flask(__name__)
    leo = LEOv7_MemoryEfficient()
    leo.initialize_cache()

    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LEO v7 - Enterprise AI Assistant</title>
    <meta charset="utf-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #0f1117; color: #e1e7ec; }
        h1 { color: #22c55e; }
        input { width: 100%; box-sizing: border-box; padding: 12px 16px; font-size: 16px; background: #1a1d24; border: 1px solid #2e3440; color: #fff; border-radius: 6px; margin-bottom: 12px; }
        button { padding: 12px 24px; background: #22c55e; color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; }
        button:hover { background: #16a34a; }
        .response { margin-top: 24px; padding: 20px; background: #1a1d24; border: 1px solid #2e3440; border-radius: 8px; line-height: 1.6; }
        .meta { margin-top: 16px; font-size: 13px; color: #94a3b8; border-top: 1px solid #2e3440; pt: 10px; }
        .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
        .tag-cache { background: #14532d; color: #4ade80; }
        .tag-llm { background: #1e3a5f; color: #60a5fa; }
    </style>
</head>
<body>
    <h1>🤖 LEO v7 Enterprise AI</h1>
    <p>Ask an enterprise IT question. LEO searches pre-computed semantic cache first, then uses local on-demand AI if needed.</p>
    
    <input type="text" id="query" placeholder="e.g., How do I reset my password?" onkeydown="if(event.key==='Enter') askLEO()" />
    <button onclick="askLEO()">Ask LEO</button>
    
    <div id="response" class="response" style="display:none;"></div>
    
    <script>
        function askLEO() {
            let query = document.getElementById('query').value;
            if (!query.trim()) return;
            document.getElementById('response').innerHTML = "<em>Searching semantic cache...</em>";
            document.getElementById('response').style.display = 'block';

            fetch('/api/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            })
            .then(r => r.json())
            .then(data => {
                let badge = data.source === 'CACHE' ? '<span class="tag tag-cache">CACHE HIT ✅</span>' : '<span class="tag tag-llm">LLM FALLBACK ⚡</span>';
                let html = `
                    <strong>Answer:</strong><br>
                    <p>${data.response}</p>
                    <div class="meta">
                        <strong>Source:</strong> ${badge} &nbsp;|&nbsp;
                        <strong>Latency:</strong> ${data.latency_ms.toFixed(0)} ms &nbsp;|&nbsp;
                        <strong>Similarity:</strong> ${data.similarity ? (data.similarity * 100).toFixed(1) + '%' : 'N/A'}
                    </div>
                `;
                document.getElementById('response').innerHTML = html;
            })
            .catch(err => {
                document.getElementById('response').innerHTML = "<span style='color:#ef4444'>Error querying LEO backend.</span>";
            });
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
        data = request.json or {}
        text = data.get('query', '')
        result = leo.process_query(text)
        return jsonify(result)

    if __name__ == '__main__':
        print("🌐 LEO Web Interface starting...")
        print("📍 Open your browser to: http://localhost:5000")
        app.run(debug=False, host='127.0.0.1', port=5000)

except ImportError:
    print("Flask is not installed. To run web_interface.py, install it with: pip install flask")
