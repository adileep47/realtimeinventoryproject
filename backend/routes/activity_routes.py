from flask import Blueprint, request, jsonify
from backend.models.activity import ActivityLog
from backend.utils.auth_middleware import token_required

activity_bp = Blueprint('activity_bp', __name__)

@activity_bp.route('', methods=['GET'])
@token_required
def get_activity_log(current_user):
    entity_type = request.args.get('entity_type', '').strip().upper()
    action = request.args.get('action', '').strip().upper()
    limit = request.args.get('limit', default=100, type=int)

    query = ActivityLog.query
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if action:
        query = query.filter(ActivityLog.action == action)

    logs = query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()

    return jsonify({'activities': [a.to_dict() for a in logs]}), 200
