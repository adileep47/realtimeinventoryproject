from flask import Blueprint, request, jsonify
from backend.db import db
from backend.models.category import Category
from backend.utils.auth_middleware import token_required, admin_required
from backend.utils.logger import log_activity

category_bp = Blueprint('category_bp', __name__)

@category_bp.route('', methods=['GET'])
@token_required
def get_categories(current_user):
    categories = Category.query.order_by(Category.name.asc()).all()
    return jsonify({'categories': [c.to_dict() for c in categories]}), 200

@category_bp.route('/<int:cat_id>', methods=['GET'])
@token_required
def get_category(current_user, cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({'error': 'Category not found.'}), 404
    return jsonify({'category': category.to_dict()}), 200

@category_bp.route('', methods=['POST'])
@token_required
def create_category(current_user):
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not name:
        return jsonify({'error': 'Category name is required.'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'error': f'Category with name "{name}" already exists.'}), 400

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    log_activity(current_user.id, 'CREATE', 'CATEGORY', category.id, f'Created category "{name}"')

    return jsonify({'message': 'Category created successfully.', 'category': category.to_dict()}), 201

@category_bp.route('/<int:cat_id>', methods=['PUT'])
@token_required
@admin_required
def update_category(current_user, cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({'error': 'Category not found.'}), 404

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if name and name != category.name:
        if Category.query.filter_by(name=name).first():
            return jsonify({'error': f'Category with name "{name}" already exists.'}), 400
        category.name = name

    if 'description' in data:
        category.description = description

    db.session.commit()
    log_activity(current_user.id, 'UPDATE', 'CATEGORY', category.id, f'Updated category "{category.name}"')

    return jsonify({'message': 'Category updated successfully.', 'category': category.to_dict()}), 200

@category_bp.route('/<int:cat_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_category(current_user, cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({'error': 'Category not found.'}), 404

    name = category.name
    db.session.delete(category)
    db.session.commit()

    log_activity(current_user.id, 'DELETE', 'CATEGORY', cat_id, f'Deleted category "{name}"')

    return jsonify({'message': f'Category "{name}" deleted successfully.'}), 200
