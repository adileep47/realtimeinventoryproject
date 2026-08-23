from backend.db import db
from backend.models.activity import ActivityLog

def log_activity(user_id, action, entity_type, entity_id=None, details=''):
    """
    Utility function to log user actions across the system.
    """
    try:
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error writing activity log: {e}")
