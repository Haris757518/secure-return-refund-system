from flask import Blueprint, request, jsonify, session
from db import db
from models.audit import (
    get_system_stats,
    get_suspicious_users,
    get_user_activity_summary
)

admin_bp = Blueprint('admin', __name__)

def require_admin():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return None


@admin_bp.route('/admin/audit-logs', methods=['GET'])
def get_audit():
    auth_error = require_admin()
    if auth_error:
        return auth_error

    try:
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        order = request.args.get('order', 'desc')  # asc | desc

        sort_order = -1 if order == 'desc' else 1

        logs = (
            db.audit_logs
            .find({})
            .sort('timestamp', sort_order)
            .skip(skip)
            .limit(limit)
        )

        result = []
        for log in logs:
            result.append({
                '_id': str(log['_id']),
                'action': log['action'],
                'actor': log['actor'],
                'details': log['details'],
                'timestamp': log['timestamp'].isoformat()
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/admin/stats', methods=['GET'])
def get_stats():
    auth_error = require_admin()
    if auth_error:
        return auth_error
    return jsonify(get_system_stats()), 200


@admin_bp.route('/admin/suspicious-users', methods=['GET'])
def get_suspicious():
    auth_error = require_admin()
    if auth_error:
        return auth_error
    threshold = int(request.args.get('threshold', 5))
    return jsonify(get_suspicious_users(threshold)), 200


@admin_bp.route('/admin/user-activity/<user_id>', methods=['GET'])
def get_user_activity(user_id):
    auth_error = require_admin()
    if auth_error:
        return auth_error
    days = int(request.args.get('days', 30))
    return jsonify(get_user_activity_summary(user_id, days)), 200
