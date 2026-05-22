from flask import Flask, render_template, request, jsonify, session
import hashlib
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# File za kuhifadhi data
USERS_FILE = 'users.json'
PENDING_FILE = 'pending_users.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from file or create default admin"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                # Ensure admin exists
                if "REYTECHFX" not in users:
                    users["REYTECHFX"] = {
                        "password": hash_password("valentina241"),
                        "email": "reytechfix@gmail.com",
                        "role": "admin",
                        "is_active": True,
                        "created_at": datetime.now().isoformat()
                    }
                    save_users(users)
                return users
        except:
            pass
    
    # Default admin account
    return {
        "REYTECHFX": {
            "password": hash_password("valentina241"),
            "email": "reytechfix@gmail.com",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now().isoformat()
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

# ==================== ROUTES ====================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        
        if not username or len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'})
        
        if not password or len(password) < 4:
            return jsonify({'success': False, 'error': 'Password must be at least 4 characters'})
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Valid email is required'})
        
        users = load_users()
        pending = load_pending()
        
        if username in users:
            return jsonify({'success': False, 'error': 'Username already exists'})
        
        if username in pending:
            return jsonify({'success': False, 'error': 'Username already pending approval'})
        
        for user in users.values():
            if user.get('email') == email:
                return jsonify({'success': False, 'error': 'Email already registered'})
        
        pending[username] = {
            'password': hash_password(password),
            'email': email,
            'registered_at': datetime.now().isoformat()
        }
        save_pending(pending)
        
        return jsonify({'success': True, 'message': 'Registration successful! Awaiting admin approval.'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'})
        
        users = load_users()
        pending = load_pending()
        
        if username in pending:
            return jsonify({'success': False, 'error': 'Account pending admin approval'})
        
        if username not in users:
            return jsonify({'success': False, 'error': 'Invalid username or password'})
        
        user = users[username]
        
        if user['password'] != hash_password(password):
            return jsonify({'success': False, 'error': 'Invalid username or password'})
        
        if not user.get('is_active', True):
            return jsonify({'success': False, 'error': 'Account deactivated. Contact admin.'})
        
        session['username'] = username
        session['role'] = user.get('role', 'user')
        
        return jsonify({
            'success': True,
            'message': f'Welcome {username}!',
            'username': username,
            'role': session['role']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({
            'logged_in': True,
            'username': session['username'],
            'role': session.get('role', 'user')
        })
    return jsonify({'logged_in': False})

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/pending_users', methods=['GET'])
def get_pending_users():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    pending = load_pending()
    pending_list = []
    for username, data in pending.items():
        pending_list.append({
            'username': username,
            'email': data['email'],
            'registered_at': data['registered_at']
        })
    
    return jsonify({'success': True, 'users': pending_list})

@app.route('/api/admin/approve_user', methods=['POST'])
def approve_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    
    pending = load_pending()
    users = load_users()
    
    if username not in pending:
        return jsonify({'success': False, 'error': 'User not found'})
    
    user_data = pending[username]
    
    users[username] = {
        'password': user_data['password'],
        'email': user_data['email'],
        'role': 'user',
        'is_active': True,
        'created_at': user_data['registered_at'],
        'approved_by': session['username'],
        'approved_at': datetime.now().isoformat()
    }
    
    del pending[username]
    
    save_users(users)
    save_pending(pending)
    
    return jsonify({'success': True, 'message': f'User {username} approved!'})

@app.route('/api/admin/reject_user', methods=['POST'])
def reject_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    
    pending = load_pending()
    
    if username in pending:
        del pending[username]
        save_pending(pending)
    
    return jsonify({'success': True, 'message': f'User {username} rejected!'})

@app.route('/api/admin/all_users', methods=['GET'])
def get_all_users():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    users = load_users()
    user_list = []
    for username, data in users.items():
        user_list.append({
            'username': username,
            'email': data['email'],
            'role': data.get('role', 'user'),
            'is_active': data.get('is_active', True),
            'created_at': data.get('created_at', '')
        })
    
    return jsonify({'success': True, 'users': user_list})

@app.route('/api/admin/deactivate_user', methods=['POST'])
def deactivate_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.json
    username = data.get('username', '')
    action = data.get('action', 'deactivate')
    
    if username == 'REYTECHFX':
        return jsonify({'success': False, 'error': 'Cannot modify admin'})
    
    users = load_users()
    
    if username not in users:
        return jsonify({'success': False, 'error': 'User not found'})
    
    users[username]['is_active'] = (action == 'activate')
    save_users(users)
    
    status = 'activated' if action == 'activate' else 'deactivated'
    return jsonify({'success': True, 'message': f'User {username} {status}!'})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
