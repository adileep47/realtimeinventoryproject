from flask import Blueprint, request, jsonify
from backend.db import db
from backend.models.supplier import Supplier
from backend.utils.auth_middleware import token_required, admin_required
from backend.utils.logger import log_activity

supplier_bp = Blueprint('supplier_bp', __name__)

@supplier_bp.route('', methods=['GET'])
@token_required
def get_suppliers(current_user):
    suppliers = Supplier.query.order_by(Supplier.name.asc()).all()
    return jsonify({'suppliers': [s.to_dict() for s in suppliers]}), 200

@supplier_bp.route('/<int:sup_id>', methods=['GET'])
@token_required
def get_supplier(current_user, sup_id):
    supplier = db.session.get(Supplier, sup_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found.'}), 404
    return jsonify({'supplier': supplier.to_dict()}), 200

@supplier_bp.route('', methods=['POST'])
@token_required
def create_supplier(current_user):
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    contact_name = data.get('contact_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()

    if not name:
        return jsonify({'error': 'Supplier company name is required.'}), 400

    if Supplier.query.filter_by(name=name).first():
        return jsonify({'error': f'Supplier "{name}" already exists.'}), 400

    supplier = Supplier(
        name=name,
        contact_name=contact_name,
        email=email,
        phone=phone,
        address=address
    )
    db.session.add(supplier)
    db.session.commit()

    log_activity(current_user.id, 'CREATE', 'SUPPLIER', supplier.id, f'Added supplier "{name}"')

    return jsonify({'message': 'Supplier added successfully.', 'supplier': supplier.to_dict()}), 201

@supplier_bp.route('/<int:sup_id>', methods=['PUT'])
@token_required
@admin_required
def update_supplier(current_user, sup_id):
    supplier = db.session.get(Supplier, sup_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found.'}), 404

    data = request.get_json() or {}
    name = data.get('name', '').strip()

    if name and name != supplier.name:
        if Supplier.query.filter_by(name=name).first():
            return jsonify({'error': f'Supplier name "{name}" is already taken.'}), 400
        supplier.name = name

    if 'contact_name' in data: supplier.contact_name = data['contact_name'].strip()
    if 'email' in data: supplier.email = data['email'].strip()
    if 'phone' in data: supplier.phone = data['phone'].strip()
    if 'address' in data: supplier.address = data['address'].strip()

    db.session.commit()
    log_activity(current_user.id, 'UPDATE', 'SUPPLIER', supplier.id, f'Updated supplier "{supplier.name}"')

    return jsonify({'message': 'Supplier updated successfully.', 'supplier': supplier.to_dict()}), 200

@supplier_bp.route('/<int:sup_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_supplier(current_user, sup_id):
    supplier = db.session.get(Supplier, sup_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found.'}), 404

    name = supplier.name
    db.session.delete(supplier)
    db.session.commit()

    log_activity(current_user.id, 'DELETE', 'SUPPLIER', sup_id, f'Deleted supplier "{name}"')

    return jsonify({'message': f'Supplier "{name}" deleted successfully.'}), 200
