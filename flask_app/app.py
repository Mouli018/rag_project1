from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import search_articles, concatenate_content, generate_answer
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Invalid request format"}), 400
            
        query = data['query'].strip()
        if not query:
            return jsonify({"error": "Empty query"}), 400
        
        print(f"[Backend] Processing query: '{query}'")
        
        # Step 1: Search
        articles = search_articles(query)
        if not articles:
            return jsonify({"error": "No relevant articles found"}), 404
        
        # Step 2: Process
        context = concatenate_content(articles)
        print(f"[Backend] Context length: {len(context)} characters")
        
        # Step 3: Generate
        answer = generate_answer(context, query)
        return jsonify({
            "answer": answer,
            "sources": [{'title': a.get('title'), 'url': a.get('link')} for a in articles]
        })
        
    except Exception as e:
        print(f"[Backend Error] {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)