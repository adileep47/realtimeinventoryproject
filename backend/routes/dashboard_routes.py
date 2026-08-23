from flask import Blueprint, jsonify
from backend.models.product import Product
from backend.models.stock import StockMovement
from backend.models.category import Category
from backend.models.supplier import Supplier
from backend.models.activity import ActivityLog
from backend.utils.auth_middleware import token_required
from sqlalchemy import func
from backend.db import db
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    products = Product.query.all()
    total_products = len(products)
    total_categories = Category.query.count()
    total_suppliers = Supplier.query.count()
    low_stock_products = [p.to_dict() for p in products if p.quantity <= p.reorder_level]
    low_stock_count = len(low_stock_products)
    out_of_stock_count = sum(1 for p in products if p.quantity == 0)

    total_inventory_value = sum(float(p.price) * p.quantity for p in products)

    # Recent stock activity (latest 10)
    recent_stock = StockMovement.query.order_by(StockMovement.timestamp.desc()).limit(10).all()

    # Recent user audit activity (latest 10)
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()

    # Stock IN vs Stock OUT monthly trend (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    movements_trend = db.session.query(
        func.strftime('%Y-%m', StockMovement.timestamp).label('month') if db.engine.name == 'sqlite' else func.date_format(StockMovement.timestamp, '%Y-%m').label('month'),
        StockMovement.type,
        func.sum(StockMovement.quantity).label('total_qty')
    ).filter(StockMovement.timestamp >= six_months_ago)\
     .group_by('month', StockMovement.type)\
     .order_by('month').all()

    trend_months = sorted(list(set(m[0] for m in movements_trend if m[0])))
    stock_in_data = {m: 0 for m in trend_months}
    stock_out_data = {m: 0 for m in trend_months}

    for month, m_type, qty in movements_trend:
        if month:
            if m_type == 'IN':
                stock_in_data[month] = int(qty)
            elif m_type == 'OUT':
                stock_out_data[month] = int(qty)

    # Category product distribution
    categories = Category.query.all()
    cat_distribution = []
    for c in categories:
        count = sum(1 for p in products if p.category_id == c.id)
        cat_distribution.append({'category': c.name, 'count': count})

    return jsonify({
        'kpi': {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_suppliers': total_suppliers,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_inventory_value': round(total_inventory_value, 2)
        },
        'low_stock_items': low_stock_products,
        'recent_stock_activity': [m.to_dict() for m in recent_stock],
        'recent_system_activity': [a.to_dict() for a in recent_activities],
        'chart_stock_trend': {
            'labels': trend_months,
            'stock_in': [stock_in_data[m] for m in trend_months],
            'stock_out': [stock_out_data[m] for m in trend_months]
        },
        'chart_category_distribution': {
            'labels': [c['category'] for c in cat_distribution],
            'data': [c['count'] for c in cat_distribution]
        }
    }), 200
