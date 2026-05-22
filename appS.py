from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "version": "0.02",
        "message": "EASY TOOL by briana",
        "creator": "briana",
        "contact": "254111457171"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
