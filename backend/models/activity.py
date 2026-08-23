from backend.db import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = db.Column(db.String(50), nullable=False) # e.g. CREATE, UPDATE, DELETE, STOCK_IN, STOCK_OUT, LOGIN
    entity_type = db.Column(db.String(50), nullable=False) # e.g. PRODUCT, CATEGORY, SUPPLIER, USER
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref='activity_logs', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System',
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details or '',
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
