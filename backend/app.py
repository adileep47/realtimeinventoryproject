import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.db import init_db

def create_app():
    frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
    
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize Database & seed initial records
    init_db(app)

    # Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.category_routes import category_bp
    from backend.routes.supplier_routes import supplier_bp
    from backend.routes.product_routes import product_bp
    from backend.routes.stock_routes import stock_bp
    from backend.routes.report_routes import report_bp
    from backend.routes.activity_routes import activity_bp
    from backend.routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(supplier_bp, url_prefix='/api/suppliers')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(activity_bp, url_prefix='/api/activity-log')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    # Serve static frontend pages
    @app.route('/')
    def serve_frontend():
        return send_from_directory(frontend_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(frontend_folder, path)):
            return send_from_directory(frontend_folder, path)
        return send_from_directory(frontend_folder, 'index.html')

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
