from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime
from repositories.user_repository import UserRepository
from werkzeug.security import generate_password_hash

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register_user(self, email, password, first_name=None, last_name=None):
        if self.user_repository.get_user_by_email(email):
            raise ValueError("Email already exists")
        
        return self.user_repository.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

    def authenticate_user(self, email, password):
        user = self.user_repository.get_user_by_email(email)
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("Account is deactivated")

        self.user_repository.update_last_login(user)
        
        return {
            'access_token': create_access_token(identity=user.id),
            'refresh_token': create_refresh_token(identity=user.id),
            'user': user.to_dict()
        }

    def refresh_token(self, user_id):
        user = self.user_repository.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Invalid user or inactive account")
        
        return create_access_token(identity=user_id)

    def update_user_profile(self, user_id, **kwargs):
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Password is handled directly by the model
        return self.user_repository.update_user(user, **kwargs)
