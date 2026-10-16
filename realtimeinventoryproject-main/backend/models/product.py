from backend.db import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True, index=True)
    unit = db.Column(db.String(20), default='pcs')
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stock_movements = db.relationship('StockMovement', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Uncategorized',
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else 'None',
            'unit': self.unit,
            'price': float(self.price),
            'quantity': self.quantity,
            'reorder_level': self.reorder_level,
            'is_low_stock': self.is_low_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
