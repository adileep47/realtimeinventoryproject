from flask import Blueprint, request, jsonify
from backend.db import db
from backend.models.product import Product
from backend.models.stock import StockMovement
from backend.utils.auth_middleware import token_required
from backend.utils.logger import log_activity

stock_bp = Blueprint('stock_bp', __name__)

@stock_bp.route('/movement', methods=['POST'])
@token_required
def record_movement(current_user):
    data = request.get_json() or {}
    product_id = data.get('product_id')
    movement_type = data.get('type', '').strip().upper() # 'IN' or 'OUT'
    quantity = data.get('quantity', 0)
    reason = data.get('reason', '').strip()

    if not product_id or movement_type not in ['IN', 'OUT'] or quantity <= 0:
        return jsonify({'error': 'Valid product_id, movement type (IN/OUT), and positive quantity are required.'}), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found.'}), 404

    if movement_type == 'OUT' and product.quantity < quantity:
        return jsonify({'error': f'Insufficient stock! Available: {product.quantity}, requested: {quantity}'}), 400

    # Auto-update product quantity
    if movement_type == 'IN':
        product.quantity += quantity
    else:
        product.quantity -= quantity

    movement = StockMovement(
        product_id=product.id,
        type=movement_type,
        quantity=quantity,
        reason=reason,
        user_id=current_user.id
    )

    db.session.add(movement)
    db.session.commit()

    action_label = 'STOCK_IN' if movement_type == 'IN' else 'STOCK_OUT'
    log_activity(current_user.id, action_label, 'PRODUCT', product.id,
                 f'Stock {movement_type}: {quantity} units for "{product.name}". New Total Qty: {product.quantity}')

    return jsonify({
        'message': f'Stock {movement_type} recorded successfully.',
        'movement': movement.to_dict(),
        'product': product.to_dict()
    }), 201

@stock_bp.route('/history', methods=['GET'])
@token_required
def get_stock_history(current_user):
    product_id = request.args.get('product_id', type=int)
    movement_type = request.args.get('type', '').strip().upper()
    limit = request.args.get('limit', default=100, type=int)

    query = StockMovement.query
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if movement_type in ['IN', 'OUT']:
        query = query.filter(StockMovement.type == movement_type)

    movements = query.order_by(StockMovement.timestamp.desc()).limit(limit).all()
    return jsonify({'movements': [m.to_dict() for m in movements]}), 200

@stock_bp.route('/low-stock', methods=['GET'])
@token_required
def get_low_stock_alerts(current_user):
    products = Product.query.all()
    low_stock_items = [p.to_dict() for p in products if p.quantity <= p.reorder_level]
    return jsonify({
        'low_stock_count': len(low_stock_items),
        'products': low_stock_items
    }), 200
