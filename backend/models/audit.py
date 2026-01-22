from db import db
from datetime import datetime
from bson import ObjectId

def log_action(action, actor, details="", target_user=None, return_id=None):
    """
    Records a security-relevant action in the audit logs.
    
    Args:
        action: Type of action (LOGIN, LOGOUT, RETURN_CREATED, RETURN_APPROVED, etc.)
        actor: User ID who performed the action
        details: Additional details about the action
        target_user: User ID affected by the action (optional)
        return_id: Return request ID affected (optional)
    """
    audit_entry = {
        "action": action,
        "actor": actor,
        "details": details,
        "timestamp": datetime.utcnow(),
        "target_user": target_user,
        "return_id": return_id
    }
    
    db.audit_logs.insert_one(audit_entry)
    print(f"[AUDIT] {action} by {actor}: {details}")


def get_audit_logs(limit=100, skip=0, action_filter=None, actor_filter=None):
    """
    Retrieve audit logs with optional filtering
    
    Args:
        limit: Maximum number of logs to return
        skip: Number of logs to skip (for pagination)
        action_filter: Filter by action type
        actor_filter: Filter by actor user ID
    """
    query = {}
    
    if action_filter:
        query['action'] = action_filter
    
    if actor_filter:
        query['actor'] = actor_filter
    
    logs = db.audit_logs.find(query).sort('timestamp', -1).skip(skip).limit(limit)
    
    return [{
        '_id': str(log['_id']),
        'action': log['action'],
        'actor': log['actor'],
        'details': log['details'],
        'timestamp': log['timestamp'].isoformat() if log['timestamp'] else None,
        'target_user': log.get('target_user'),
        'return_id': log.get('return_id')
    } for log in logs]


def get_user_activity_summary(user_id, days=30):
    """
    Get summary of user activity for suspicious behavior detection
    
    Args:
        user_id: User ID to analyze
        days: Number of days to look back
    """
    from datetime import timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Count different action types
    pipeline = [
        {
            '$match': {
                'actor': user_id,
                'timestamp': {'$gte': cutoff_date}
            }
        },
        {
            '$group': {
                '_id': '$action',
                'count': {'$sum': 1}
            }
        }
    ]
    
    results = list(db.audit_logs.aggregate(pipeline))
    
    summary = {result['_id']: result['count'] for result in results}
    
    # Flag suspicious behavior
    flags = []
    
    if summary.get('RETURN_CREATED', 0) > 10:
        flags.append(f"High return volume: {summary['RETURN_CREATED']} returns in {days} days")
    
    if summary.get('LOGIN_FAILED', 0) > 5:
        flags.append(f"Multiple failed logins: {summary['LOGIN_FAILED']} attempts")
    
    return {
        'user_id': user_id,
        'period_days': days,
        'activity_summary': summary,
        'flags': flags,
        'is_suspicious': len(flags) > 0
    }


def get_system_stats():
    """
    Get overall system statistics
    """
    total_users = db.users.count_documents({})
    total_returns = db.returns.count_documents({})
    pending_returns = db.returns.count_documents({'status': 'Pending'})
    approved_returns = db.returns.count_documents({'status': 'Approved'})
    rejected_returns = db.returns.count_documents({'status': 'Rejected'})
    
    # Get recent activity count (last 24 hours)
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(hours=24)
    
    recent_returns = db.returns.count_documents({
        'created_at': {'$gte': yesterday}
    })
    
    recent_logins = db.audit_logs.count_documents({
        'action': 'LOGIN_SUCCESS',
        'timestamp': {'$gte': yesterday}
    })
    
    return {
        'total_users': total_users,
        'total_returns': total_returns,
        'pending_returns': pending_returns,
        'approved_returns': approved_returns,
        'rejected_returns': rejected_returns,
        'returns_last_24h': recent_returns,
        'logins_last_24h': recent_logins
    }


def get_suspicious_users(threshold=5):
    """
    Identify users with suspicious return patterns
    
    Args:
        threshold: Minimum number of returns to be flagged as suspicious
    """
    from datetime import timedelta
    last_30_days = datetime.utcnow() - timedelta(days=30)
    
    pipeline = [
        {
            '$match': {
                'created_at': {'$gte': last_30_days}
            }
        },
        {
            '$group': {
                '_id': '$user_id',
                'return_count': {'$sum': 1},
                'orders': {'$addToSet': '$order_id'}
            }
        },
        {
            '$match': {
                'return_count': {'$gte': threshold}
            }
        },
        {
            '$sort': {'return_count': -1}
        }
    ]
    
    results = list(db.returns.aggregate(pipeline))
    
    suspicious_users = []
    for result in results:
        user = db.users.find_one({'_id': ObjectId(result['_id'])})
        if user:
            suspicious_users.append({
                'user_id': result['_id'],
                'username': user.get('username'),
                'name': user.get('name'),
                'return_count': result['return_count'],
                'unique_orders': len(result['orders']),
                'risk_level': 'HIGH' if result['return_count'] > 10 else 'MEDIUM'
            })
    
    return suspicious_users