from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['return_refund_db']

def init_db():
    """Initialize database and create collections if they don't exist"""
    try:
        # Create collections
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
            print("✓ Created 'users' collection")
        
        if 'returns' not in db.list_collection_names():
            db.create_collection('returns')
            print("✓ Created 'returns' collection")
        
        if 'audit_logs' not in db.list_collection_names():
            db.create_collection('audit_logs')
            print("✓ Created 'audit_logs' collection")
        
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Error initializing database: {str(e)}")
        return False

def get_db():
    """Get database instance"""
    return db