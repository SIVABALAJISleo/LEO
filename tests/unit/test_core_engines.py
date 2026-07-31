import pytest
from backend.routers.auth import hash_password, verify_password, create_jwt_token
from backend.core.database import User

class TestCoreAuthUnit:
    def test_password_hashing_and_verification(self):
        plain = "SuperSecretPassword123!"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_jwt_token_generation(self):
        user = User(
            uid="user_test_uid_123",
            email="test_jwt@leo.ai",
            tenant_id="tenant_123",
            tier="enterprise"
        )
        token = create_jwt_token(user)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
