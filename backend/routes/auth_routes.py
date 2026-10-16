from flask import Blueprint, request, jsonify
from backend.db import db
from backend.models.user import User
from backend.utils.auth_middleware import generate_token, token_required
from backend.utils.logger import log_activity

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'staff').strip().lower()

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required fields.'}), 400

    if role not in ['admin', 'staff']:
        role = 'staff'

    if User.query.filter_by(username=username).first():
        return jsonify({'error': f'Username "{username}" is already taken.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': f'Email "{email}" is already registered.'}), 400

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    log_activity(new_user.id, 'REGISTER', 'USER', new_user.id, f'User registered as {role}')

    token = generate_token(new_user)
    return jsonify({
        'message': 'Registration successful.',
        'token': token,
        'user': new_user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username_or_email = data.get('username', '').strip()
    password = data.get('password', '')

    if not username_or_email or not password:
        return jsonify({'error': 'Username/email and password are required.'}), 400

    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username/email or password.'}), 401

    token = generate_token(user)
    log_activity(user.id, 'LOGIN', 'USER', user.id, 'User logged into application')

    return jsonify({
        'message': 'Login successful.',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({'user': current_user.to_dict()}), 200
