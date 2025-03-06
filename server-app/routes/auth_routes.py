from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from middleware.auth_middleware import require_auth

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.get_json()
        user = auth_service.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.get_json()
        auth_data = auth_service.authenticate_user(
            email=data['email'],
            password=data['password']
        )
        return jsonify(auth_data), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        user_id = get_jwt_identity()
        access_token = auth_service.refresh_token(user_id)
        return jsonify({'access_token': access_token}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = UserRepository.get_user_by_id(user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user = auth_service.update_user_profile(user_id, **data)
        return jsonify(user.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
