from flask import Blueprint, request, jsonify, session
from models.user import User
from models.audit import log_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        print("=== LOGIN REQUEST ===")
        data = request.get_json()
        username = data.get('username')
        
        print(f"Login attempt for username: {username}")
        
        user = User.authenticate(username, data['password'])
        
        if user:
            # Make session permanent
            session.permanent = True
            session['user_id'] = str(user._id)
            session['username'] = user.username
            session['role'] = user.role
            
            # Log successful login
            log_action(
                action='LOGIN_SUCCESS',
                actor=str(user._id),
                details=f'User {username} logged in successfully'
            )
            
            print(f"Login successful!")
            print(f"Session data: {dict(session)}")
            
            return jsonify({
                'user': {
                    '_id': str(user._id),
                    'username': user.username,
                    'name': user.name,
                    'role': user.role
                }
            }), 200
        else:
            # Log failed login attempt
            log_action(
                action='LOGIN_FAILED',
                actor=username or 'unknown',
                details=f'Failed login attempt for username: {username}'
            )
            
            print("Login failed: Invalid credentials")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        
        if user_id:
            # Log logout
            log_action(
                action='LOGOUT',
                actor=user_id,
                details=f'User {username} logged out'
            )
        
        print(f"Logout request for user: {username}")
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/check-session', methods=['GET', 'OPTIONS'])
def check_session():
    if request.method == 'OPTIONS':
        return '', 204
        
    print(f"=== CHECK SESSION ===")
    print(f"Session data: {dict(session)}")
    
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'user_id': session['user_id'],
                'username': session.get('username'),
                'role': session.get('role')
            }
        }), 200
    else:
        return jsonify({'logged_in': False}), 200