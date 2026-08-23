from flask import Blueprint, request, jsonify
from backend.db import db
from backend.models.product import Product
from backend.models.category import Category
from backend.models.supplier import Supplier
from backend.utils.auth_middleware import token_required, admin_required
from backend.utils.logger import log_activity

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('', methods=['GET'])
@token_required
def get_products(current_user):
    query = Product.query

    # Search & Filter params
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    supplier_id = request.args.get('supplier_id', type=int)
    stock_status = request.args.get('status', '').strip().lower()

    if search:
        query = query.filter((Product.name.ilike(f'%{search}%')) | (Product.sku.ilike(f'%{search}%')))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)

    products = query.order_by(Product.name.asc()).all()

    if stock_status == 'low':
        products = [p for p in products if p.quantity <= p.reorder_level and p.quantity > 0]
    elif stock_status == 'out_of_stock':
        products = [p for p in products if p.quantity == 0]
    elif stock_status == 'normal':
        products = [p for p in products if p.quantity > p.reorder_level]

    return jsonify({'products': [p.to_dict() for p in products]}), 200

@product_bp.route('/<int:prod_id>', methods=['GET'])
@token_required
def get_product(current_user, prod_id):
    product = db.session.get(Product, prod_id)
    if not product:
        return jsonify({'error': 'Product not found.'}), 404
    return jsonify({'product': product.to_dict()}), 200

@product_bp.route('', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json() or {}
    sku = data.get('sku', '').strip().upper()
    name = data.get('name', '').strip()
    category_id = data.get('category_id')
    supplier_id = data.get('supplier_id')
    unit = data.get('unit', 'pcs').strip()
    price = data.get('price', 0.0)
    quantity = data.get('quantity', 0)
    reorder_level = data.get('reorder_level', 10)

    if not sku or not name:
        return jsonify({'error': 'SKU and Product Name are required fields.'}), 400

    if Product.query.filter_by(sku=sku).first():
        return jsonify({'error': f'Product with SKU "{sku}" already exists.'}), 400

    if category_id and not db.session.get(Category, category_id):
        category_id = None

    if supplier_id and not db.session.get(Supplier, supplier_id):
        supplier_id = None

    product = Product(
        sku=sku,
        name=name,
        category_id=category_id,
        supplier_id=supplier_id,
        unit=unit,
        price=price,
        quantity=quantity,
        reorder_level=reorder_level
    )

    db.session.add(product)
    db.session.commit()

    log_activity(current_user.id, 'CREATE', 'PRODUCT', product.id, f'Added product "{name}" ({sku}) with qty {quantity}')

    return jsonify({'message': 'Product created successfully.', 'product': product.to_dict()}), 201

@product_bp.route('/<int:prod_id>', methods=['PUT'])
@token_required
def update_product(current_user, prod_id):
    product = db.session.get(Product, prod_id)
    if not product:
        return jsonify({'error': 'Product not found.'}), 404

    data = request.get_json() or {}
    sku = data.get('sku', '').strip().upper()
    name = data.get('name', '').strip()

    if sku and sku != product.sku:
        if Product.query.filter_by(sku=sku).first():
            return jsonify({'error': f'SKU "{sku}" is already in use.'}), 400
        product.sku = sku

    if name:
        product.name = name

    if 'category_id' in data:
        cid = data['category_id']
        product.category_id = cid if cid and db.session.get(Category, cid) else None

    if 'supplier_id' in data:
        sid = data['supplier_id']
        product.supplier_id = sid if sid and db.session.get(Supplier, sid) else None

    if 'unit' in data: product.unit = data['unit'].strip()
    if 'price' in data: product.price = data['price']
    if 'quantity' in data: product.quantity = data['quantity']
    if 'reorder_level' in data: product.reorder_level = data['reorder_level']

    db.session.commit()
    log_activity(current_user.id, 'UPDATE', 'PRODUCT', product.id, f'Updated product "{product.name}" ({product.sku})')

    return jsonify({'message': 'Product updated successfully.', 'product': product.to_dict()}), 200

@product_bp.route('/<int:prod_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_product(current_user, prod_id):
    product = db.session.get(Product, prod_id)
    if not product:
        return jsonify({'error': 'Product not found.'}), 404

    sku = product.sku
    name = product.name
    db.session.delete(product)
    db.session.commit()

    log_activity(current_user.id, 'DELETE', 'PRODUCT', prod_id, f'Deleted product "{name}" ({sku})')

    return jsonify({'message': f'Product "{name}" deleted successfully.'}), 200
