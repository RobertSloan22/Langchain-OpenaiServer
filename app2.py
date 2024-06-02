from flask import Flask, request, jsonify
from query_and_summarize import summarize_data

app = Flask(__name__)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    query = data.get('query')
    model = data.get('model')
    
    if not query or not model:
        return jsonify({"error": "query and model are required fields"}), 400
    
    try:
        summary = summarize_data(model, query)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
