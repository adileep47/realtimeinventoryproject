from flask import Blueprint, request, send_file, jsonify
from backend.models.product import Product
from backend.models.stock import StockMovement
from backend.models.category import Category
from backend.utils.auth_middleware import token_required
from backend.utils.pdf_generator import generate_pdf_report
from sqlalchemy import func
from backend.db import db

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
    # Total valuation
    products = Product.query.all()
    total_products = len(products)
    total_valuation = sum(float(p.price) * p.quantity for p in products)
    low_stock_count = sum(1 for p in products if p.quantity <= p.reorder_level)

    # Category distribution
    categories = Category.query.all()
    category_data = []
    for c in categories:
        cat_prods = [p for p in products if p.category_id == c.id]
        category_data.append({
            'category_name': c.name,
            'count': len(cat_prods),
            'total_qty': sum(p.quantity for p in cat_prods)
        })

    # Most active products (by stock movement volume)
    top_moved = db.session.query(
        StockMovement.product_id,
        func.sum(StockMovement.quantity).label('total_volume')
    ).group_by(StockMovement.product_id).order_by(func.sum(StockMovement.quantity).desc()).limit(5).all()

    top_moved_list = []
    for pid, vol in top_moved:
        prod = db.session.get(Product, pid)
        if prod:
            top_moved_list.append({
                'id': prod.id,
                'sku': prod.sku,
                'name': prod.name,
                'total_volume': int(vol)
            })

    return jsonify({
        'summary': {
            'total_products': total_products,
            'total_valuation': round(total_valuation, 2),
            'low_stock_count': low_stock_count
        },
        'categories': category_data,
        'most_active_products': top_moved_list
    }), 200

@report_bp.route('/export-pdf', methods=['GET'])
@token_required
def export_pdf(current_user):
    report_type = request.args.get('type', 'products').strip().lower()

    if report_type == 'products':
        products = Product.query.order_by(Product.name.asc()).all()
        data = [p.to_dict() for p in products]
        filename = f"products_inventory_report.pdf"

    elif report_type == 'low_stock':
        products = Product.query.all()
        data = [p.to_dict() for p in products if p.quantity <= p.reorder_level]
        filename = f"low_stock_alerts_report.pdf"

    elif report_type == 'stock':
        movements = StockMovement.query.order_by(StockMovement.timestamp.desc()).limit(500).all()
        data = [m.to_dict() for m in movements]
        filename = f"stock_movement_report.pdf"

    else:
        return jsonify({'error': 'Invalid report type specified. Use products, stock, or low_stock.'}), 400

    pdf_buffer = generate_pdf_report(report_type, data)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
