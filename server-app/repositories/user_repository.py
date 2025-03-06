from models.user import User
from extensions import db
from datetime import datetime

class UserRepository:
    @staticmethod
    def create_user(email, password, first_name=None, last_name=None):
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def update_last_login(user):
        user.last_login = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def update_user(user, **kwargs):
        if 'password' in kwargs:
            user.set_password(kwargs.pop('password'))
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user
