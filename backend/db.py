from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from backend.config import Config
import logging

db = SQLAlchemy()

def init_db(app):
    """
    Attempts to connect to MySQL database as configured in Config.
    If MySQL server is unavailable (e.g., local service not running),
    it gracefully falls back to SQLite so the application and test suites
    always run cleanly without crashes.
    """
    logger = logging.getLogger('inventory_db')
    target_uri = Config.SQLALCHEMY_DATABASE_URI
    
    try:
        engine = create_engine(target_uri)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        app.config['SQLALCHEMY_DATABASE_URI'] = target_uri
        logger.info(f"Connected successfully to primary database at {target_uri}")
    except Exception as e:
        logger.warning(f"Could not connect to primary database ({e}). Falling back to SQLite database.")
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLITE_DATABASE_URI

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_initial_data()

def seed_initial_data():
    from backend.models.user import User
    from backend.models.category import Category
    from backend.models.supplier import Supplier
    from backend.models.product import Product
    from backend.models.stock import StockMovement
    from backend.models.activity import ActivityLog
    from werkzeug.security import generate_password_hash

    # Seed Admin User if users table is empty
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@inventory.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        staff = User(
            username='staff',
            email='staff@inventory.com',
            password_hash=generate_password_hash('staff123'),
            role='staff'
        )
        db.session.add_all([admin, staff])
        db.session.commit()

        # Seed Categories
        c1 = Category(name='Electronics', description='Gadgets, components, and hardware accessories')
        c2 = Category(name='Office Supplies', description='Paper, pens, stationary, and desk items')
        c3 = Category(name='Furniture', description='Desks, chairs, cabinets, and office furniture')
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # Seed Suppliers
        s1 = Supplier(name='TechCorp Supplies', contact_name='Alice Johnson', email='contact@techcorp.com', phone='+1-555-0192', address='100 Innovation Way, Tech City')
        s2 = Supplier(name='Global Office Inc', contact_name='Bob Smith', email='sales@globaloffice.com', phone='+1-555-0183', address='45 Commercial Blvd, Metro City')
        db.session.add_all([s1, s2])
        db.session.commit()

        # Seed Products
        p1 = Product(sku='ELEC-LOGI-MX', name='Logitech MX Master 3S Wireless Mouse', category_id=c1.id, supplier_id=s1.id, unit='pcs', price=99.99, quantity=25, reorder_level=10)
        p2 = Product(sku='ELEC-DELL-U27', name='Dell UltraSharp 27" 4K Monitor', category_id=c1.id, supplier_id=s1.id, unit='pcs', price=450.00, quantity=5, reorder_level=8)
        p3 = Product(sku='OFF-PAPER-A4', name='A4 Printing Paper (Box of 5 Reams)', category_id=c2.id, supplier_id=s2.id, unit='box', price=35.50, quantity=40, reorder_level=15)
        p4 = Product(sku='FURN-ERGO-CHR', name='Ergonomic Executive Mesh Chair', category_id=c3.id, supplier_id=s2.id, unit='pcs', price=220.00, quantity=4, reorder_level=5)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # Seed Stock Movements
        m1 = StockMovement(product_id=p1.id, type='IN', quantity=25, reason='Initial stock import', user_id=admin.id)
        m2 = StockMovement(product_id=p2.id, type='IN', quantity=10, reason='Initial stock import', user_id=admin.id)
        m3 = StockMovement(product_id=p2.id, type='OUT', quantity=5, reason='Dispatched to Design Dept', user_id=staff.id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        # Seed Activity Logs
        a1 = ActivityLog(user_id=admin.id, action='CREATE', entity_type='USER', entity_id=admin.id, details='Admin user initialized')
        a2 = ActivityLog(user_id=admin.id, action='CREATE', entity_type='PRODUCT', entity_id=p1.id, details='Added product ELEC-LOGI-MX')
        a3 = ActivityLog(user_id=staff.id, action='STOCK_OUT', entity_type='PRODUCT', entity_id=p2.id, details='Deducted 5 units of Dell UltraSharp 27" 4K Monitor')
        db.session.add_all([a1, a2, a3])
        db.session.commit()
