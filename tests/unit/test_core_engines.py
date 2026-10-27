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

    def test_pbkdf2_fallback_verification(self):
        import hashlib
        import os
        salt = os.urandom(16)
        pwd = "TestFallbackPassword456$"
        kdf_hash = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt, 10_000)
        formatted = f"pbkdf2_sha256$10000${salt.hex()}${kdf_hash.hex()}"
        assert verify_password(pwd, formatted) is True
        assert verify_password("IncorrectPassword", formatted) is False

    def test_password_verification_edge_cases(self):
        assert verify_password("", "some_hash") is False
        assert verify_password("password", "") is False
        assert verify_password("", "") is False
        assert verify_password("password", "invalid_format_string") is False
        assert verify_password("password", "pbkdf2_sha256$invalid$salt$hash") is False

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

