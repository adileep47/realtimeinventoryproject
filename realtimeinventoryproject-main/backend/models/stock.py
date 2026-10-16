from backend.db import db
from datetime import datetime

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False) # 'IN' or 'OUT'
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref='stock_movements', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_sku': self.product.sku if self.product else 'Unknown',
            'product_name': self.product.name if self.product else 'Deleted Product',
            'type': self.type,
            'quantity': self.quantity,
            'reason': self.reason or '',
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System',
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
