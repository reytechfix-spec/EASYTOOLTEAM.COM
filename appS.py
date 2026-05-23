from flask import Flask, render_template, request, jsonify, session
import hashlib
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

USERS_FILE = 'users.json'
PENDING_FILE = 'pending_users.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                if "REYTECHFX" not in users:
                    users["REYTECHFX"] = {
                        "password": hash_password("valentina241"),
                        "email": "reytechfix@gmail.com",
                        "role": "admin",
                        "is_active": True
                    }
                    save_users(users)
                return users
        except:
            pass
    return {
        "REYTECHFX": {
            "password": hash_password("valentina241"),
            "email": "reytechfix@gmail.com",
            "role": "admin",
            "is_active": True
        }
    }

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_pending():
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_pending(pending):
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        users = load_users()
        pending = load_pending()
        
        if username in pending:
            return jsonify({'success': False, 'error': 'Account pending admin approval'})
        if username not in users:
            return jsonify({'success': False, 'error': 'Invalid username or password'})
        
        user = users[username]
        if user['password'] != hash_password(password):
            return jsonify({'success': False, 'error': 'Invalid username or password'})
        
        session['username'] = username
        session['role'] = user.get('role', 'user')
        
        return jsonify({'success': True, 'username': username, 'role': session['role']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({'logged_in': True, 'username': session['username'], 'role': session.get('role', 'user')})
    return jsonify({'logged_in': False})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
