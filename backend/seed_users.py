from db import db, init_db
from datetime import datetime
import hashlib

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_users():
    """Seed database with test users"""
    
    # Initialize database
    init_db()
    
    # Clear existing users (optional - remove this in production!)
    db.users.delete_many({})
    print("Cleared existing users")
    
    # Create test users
    users = [
        {
            'username': 'user1',
            'password': hash_password('user123'),
            'name': 'User One',
            'email': 'user1@example.com',
            'role': 'user',
            'created_at': datetime.utcnow()
        },
        {
            'username': 'admin1',
            'password': hash_password('admin123'),
            'name': 'Admin One',
            'email': 'admin1@example.com',
            'role': 'admin',
            'created_at': datetime.utcnow()
        },
        {
            'username': 'user2',
            'password': hash_password('user123'),
            'name': 'User Two',
            'email': 'user2@example.com',
            'role': 'user',
            'created_at': datetime.utcnow()
        }
    ]
    
    # Insert users
    result = db.users.insert_many(users)
    print(f"✓ Created {len(result.inserted_ids)} users")
    
    # Display created users
    print("\n=== Test Users ===")
    for user in users:
        print(f"Username: {user['username']}")
        print(f"Password: user123" if user['role'] == 'user' else f"Password: admin123")
        print(f"Role: {user['role']}")
        print(f"Name: {user['name']}")
        print("-" * 40)

if __name__ == '__main__':
    seed_users()