from flask import Flask, session, jsonify, request
from flask_cors import CORS
from db import init_db
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production-12345'

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CORS configuration
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    expose_headers=["Set-Cookie"],
    max_age=3600
)

# Initialize database
print("Initializing database...")
init_db()

# ✅ REGISTER ALL REQUIRED BLUEPRINTS
from routes.auth import auth_bp
from routes.returns import returns_bp
from routes.admin import admin_bp   # ✅ THIS LINE FIXES REJECT

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(returns_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')  # ✅ REQUIRED

# Debug middleware
@app.before_request
def log_request():
    print("\n" + "=" * 60)
    print(f"REQUEST: {request.method} {request.path}")
    print(f"Origin: {request.headers.get('Origin')}")
    print(f"Cookies: {request.cookies}")
    print(f"Session before: {dict(session)}")
    print("=" * 60 + "\n")

@app.after_request
def log_response(response):
    print("\n" + "=" * 60)
    print(f"RESPONSE: {response.status}")
    print(f"Session after: {dict(session)}")
    print(f"Set-Cookie: {response.headers.get('Set-Cookie')}")
    print("=" * 60 + "\n")
    return response

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200

# Root
@app.route('/')
def root():
    return jsonify({
        'message': 'Return & Refund API',
        'endpoints': {
            'health': '/api/health',
            'login': '/api/login',
            'logout': '/api/logout',
            'submit_return': '/api/returns',
            'my_returns': '/api/returns/my',
            'all_returns': '/api/returns/all (admin)'
        }
    }), 200

# Route list
@app.route('/api/routes', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify({'routes': routes}), 200

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Flask Backend Server")
    print("=" * 50)
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {rule} [{methods}]")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')
