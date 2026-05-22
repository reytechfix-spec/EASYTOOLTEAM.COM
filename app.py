from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

# ============ HII NDIO ROUTE MUHIMU ============
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')
# =============================================

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "version": "0.02",
        "message": "EASY TOOL by briana"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
