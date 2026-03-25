from flask import Blueprint, request, jsonify
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_httpauth import HTTPBasicAuth

auth_bp = Blueprint('auth', __name__)
mongo = None
basic_auth = HTTPBasicAuth()

def init_auth_routes(mongo_instance):
    global mongo
    mongo = mongo_instance

@basic_auth.verify_password
def verify_password(email, password):
    user = mongo.db.users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

# ─── REGISTER ──────────────────────────────────────────────────────────────────
@auth_bp.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"error": "Name, email and password are required"}), 400
    if mongo.db.users.find_one({"email": data['email']}):
        return jsonify({"error": "Email already registered"}), 400
    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    new_user = {
        "_id": "USR-" + data['name'][:3].upper(),
        "name": data['name'],
        "email": data['email'],
        "password": hashed_pw.decode('utf-8'),
        "role": data.get('role', 'user')
    }
    mongo.db.users.insert_one(new_user)
    return jsonify({"message": "User registered successfully"}), 201

# ─── LOGIN (Basic Auth) ────────────────────────────────────────────────────────
@auth_bp.route('/users/login', methods=['POST'])
@basic_auth.login_required
def login():
    user = basic_auth.current_user()
    token = create_access_token(
        identity=user['_id'],
        additional_claims={"role": user['role']}
    )
    refresh_token = create_refresh_token(identity=user['_id'])
    return jsonify({
        "token": token,
        "refresh_token": refresh_token,
        "role": user['role']
    }), 200

# ─── REFRESH TOKEN ─────────────────────────────────────────────────────────────
@auth_bp.route('/users/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": current_user})
    new_token = create_access_token(
        identity=current_user,
        additional_claims={"role": user['role']}
    )
    return jsonify({"token": new_token}), 200

# ─── GET ALL USERS (admin only) ────────────────────────────────────────────────
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    users = list(mongo.db.users.find({}, {"_id": 0, "password": 0}))
    return jsonify({"data": users, "total": len(users)}), 200

# ─── GET ONE USER ──────────────────────────────────────────────────────────────
@auth_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if current_user != user_id and claims.get('role') != 'admin':
        return jsonify({"error": "Unauthorised"}), 403
    user = mongo.db.users.find_one({"_id": user_id}, {"_id": 0, "password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"data": user}), 200

# ─── UPDATE USER ───────────────────────────────────────────────────────────────
@auth_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    data = request.get_json()
    if current_user != user_id and claims.get('role') != 'admin':
        return jsonify({"error": "Unauthorised"}), 403
    user = mongo.db.users.find_one({"_id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    data.pop('password', None)
    data.pop('role', None)
    data.pop('_id', None)
    mongo.db.users.update_one({"_id": user_id}, {"$set": data})
    return jsonify({"message": "User updated successfully"}), 200

# ─── DELETE USER ───────────────────────────────────────────────────────────────
@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    claims = get_jwt()
    if current_user != user_id and claims.get('role') != 'admin':
        return jsonify({"error": "Unauthorised"}), 403
    user = mongo.db.users.find_one({"_id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    mongo.db.users.delete_one({"_id": user_id})
    return jsonify({"message": "User deleted successfully"}), 200