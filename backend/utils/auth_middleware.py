import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from backend.db import db
from backend.models.user import User

def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    secret = current_app.config.get('JWT_SECRET', 'inventory_jwt_secret_key_32bytes_long_signature_2026!')
    return jwt.encode(payload, secret, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({'error': 'Authorization token is missing!'}), 401

        try:
            secret = current_app.config.get('JWT_SECRET', 'inventory_jwt_secret_key_32bytes_long_signature_2026!')
            data = jwt.decode(token, secret, algorithms=['HS256'])
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                return jsonify({'error': 'User associated with token not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired! Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token provided!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin privilege required for this action!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated
