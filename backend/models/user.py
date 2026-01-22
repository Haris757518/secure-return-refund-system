from db import db
from utils.auth import verify_password
from bson import ObjectId
from datetime import datetime

class User:
    def __init__(self, username, password, name, email, role='user', _id=None, created_at=None):
        self._id = _id
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.role = role
        self.created_at = created_at or datetime.utcnow()
    
    def save(self):
        """Save user to database"""
        user_data = {
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at
        }
        
        if self._id:
            db.users.update_one({'_id': ObjectId(self._id)}, {'$set': user_data})
        else:
            result = db.users.insert_one(user_data)
            self._id = result.inserted_id
        
        return self
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user"""
        user_data = db.users.find_one({'username': username})
        
        if user_data and verify_password(password, user_data['password']):
            return User(
                username=user_data['username'],
                password=user_data['password'],
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                _id=user_data['_id'],
                created_at=user_data.get('created_at')
            )
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        
        if user_data:
            return User(
                username=user_data['username'],
                password=user_data['password'],
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                _id=user_data['_id'],
                created_at=user_data.get('created_at')
            )
        return None


class Return:
    def __init__(
        self,
        user_id,
        order_id,
        reason,
        status='Pending',
        refund_status='Not Initiated',
        _id=None,
        created_at=None,
        updated_at=None
    ):
        self._id = _id
        self.user_id = user_id
        self.order_id = order_id
        self.reason = reason
        self.status = status
        self.refund_status = refund_status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    
    def save(self):
        """Save return request to database"""
        # Check for duplicate order_id for this user
        existing = db.returns.find_one({
            'user_id': self.user_id,
            'order_id': self.order_id,
            'status': {'$in': ['Pending', 'Approved']}
        })
        
        if existing:
            raise ValueError(f"A return request for order {self.order_id} already exists")
        
        return_data = {
            'user_id': self.user_id,
            'order_id': self.order_id,
            'reason': self.reason,
            'status': self.status,
            'refund_status': self.refund_status,
            'created_at': self.created_at,
            'updated_at': datetime.utcnow()
        }

        
        if self._id:
            db.returns.update_one({'_id': ObjectId(self._id)}, {'$set': return_data})
        else:
            result = db.returns.insert_one(return_data)
            self._id = result.inserted_id
        
        return self
    
    def approve(self, admin_id):
        """Approve return request"""
        from models.audit import log_action
        
        self.status = 'Approved'
        self.updated_at = datetime.utcnow()
        db.returns.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {'status': 'Approved', 'updated_at': self.updated_at}}
        )
        
        # Log the action
        log_action(
            action='RETURN_APPROVED',
            actor=admin_id,
            details=f'Approved return request {self._id} for order {self.order_id}',
            target_user=self.user_id,
            return_id=str(self._id)
        )
    
    def reject(self, admin_id):
        """Reject return request"""
        from models.audit import log_action
        
        self.status = 'Rejected'
        self.updated_at = datetime.utcnow()
        db.returns.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {'status': 'Rejected', 'updated_at': self.updated_at}}
        )
        
        # Log the action
        log_action(
            action='RETURN_REJECTED',
            actor=admin_id,
            details=f'Rejected return request {self._id} for order {self.order_id}',
            target_user=self.user_id,
            return_id=str(self._id)
        )
    
    @staticmethod
    def find_by_user(user_id):
        """Find all returns for a user"""
        returns = db.returns.find({'user_id': user_id}).sort('created_at', -1)
        return [Return(
            user_id=r['user_id'],
            order_id=r['order_id'],
            reason=r['reason'],
            status=r['status'],
            _id=r['_id'],
            created_at=r.get('created_at'),
            updated_at=r.get('updated_at')
        ) for r in returns]
    
    @staticmethod
    def find_all():
        """Find all return requests"""
        returns = db.returns.find().sort('created_at', -1)
        return [Return(
            user_id=r['user_id'],
            order_id=r['order_id'],
            reason=r['reason'],
            status=r['status'],
            _id=r['_id'],
            created_at=r.get('created_at'),
            updated_at=r.get('updated_at')
        ) for r in returns]
    
    @staticmethod
    def find_by_id(return_id):
        """Find return by ID"""
        return_data = db.returns.find_one({'_id': ObjectId(return_id)})
        
        if return_data:
            return Return(
                user_id=return_data['user_id'],
                order_id=return_data['order_id'],
                reason=return_data['reason'],
                status=return_data['status'],
                _id=return_data['_id'],
                created_at=return_data.get('created_at'),
                updated_at=return_data.get('updated_at')
            )
        return None
    
    @staticmethod
    def get_user_return_count(user_id, days=30):
        """Get count of returns submitted by user in last N days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = db.returns.count_documents({
            'user_id': user_id,
            'created_at': {'$gte': cutoff_date}
        })
        return count
    
    def to_dict(self):
        return {
        '_id': str(self._id),
        'user_id': self.user_id,
        'order_id': self.order_id,
        'reason': self.reason,
        'status': self.status,
        'refund_status': self.refund_status,
        'created_at': self.created_at.isoformat(),
        'updated_at': self.updated_at.isoformat()
    }
