from flask_login import login_user, logout_user

from app.api.helpers.auth import AuthManager
from app.models.user import User
from tests.all.integration.auth_helper import create_user


def test_load_user(db):
    """Method to test the registered user details"""
    user = create_user(email='authtest@gmail.com', password='password')
    assert user == db.session.query(User).get(user.id)


def test_verified_user(db):
    """Method to test if user is verified"""

    user = create_user(email='authtest@gmail.com', password='password')
    user.is_verified = False
    login_user(user)
    assert AuthManager.is_verified_user() == False


def test_is_accessible(db):
    """Method to test if user is accessible(authenticated)"""

    user = create_user(email='test@test.com', password='password')
    login_user(user)
    logout_user()
    assert AuthManager.is_accessible() == False


def test_check_auth_admin(db):
    """Method to test proper authentication & admin rights for a user"""

    user = create_user(email='authtest1@gmail.com', password='password')
    user.is_admin = True
    status = AuthManager.check_auth_admin('authtest1@gmail.com', 'password')
    assert True == status

    user = create_user(email='authtest2@gmail.com', password='password')
    user.is_admin = False
    status = AuthManager.check_auth_admin('authtest2@gmail.com', 'password')
    assert False == status
