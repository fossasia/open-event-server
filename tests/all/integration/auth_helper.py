from app.api.helpers.db import save_to_db
from app.models.user import User


def create_user(email, password, is_verified=True):
    """
    Registers the user but not logs in
    """
    user = User(email=email,
                password=password,
                is_verified=is_verified)
    save_to_db(user, "User created")
    return user


def create_super_admin(email, password):
    user = create_user(email, password, is_verified=True)
    user.is_super_admin = True
    user.is_admin = True
    save_to_db(user, "User updated")
    return user
