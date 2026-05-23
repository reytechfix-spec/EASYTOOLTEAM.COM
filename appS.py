from flask import Flask, render_template, jsonify, request
import os
import hashlib
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "version": "0.02",
        "message": "EASY TOOL API is running!",
        "endpoints": {
            "/": "Home page",
            "/api/status": "API Status",
            "/api/login": "Login endpoint"
        }
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    # Demo login - admin account
    if username == 'REYTECHFX' and password == 'valentina241':
        return jsonify({
            "success": True,
            "username": username,
            "role": "admin",
            "message": "Login successful!"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid username or password"
        })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
