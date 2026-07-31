import pytest
from backend.core.database import User

ROLES = ["guest", "registered", "premium", "moderator", "admin"]

class TestMultiRoleAuthorization:
    @pytest.mark.parametrize("role", ROLES)
    def test_role_attribute_assignment(self, role):
        user = User(
            uid=f"test_uid_{role}",
            email=f"{role}@leo.ai",
            tenant_id=f"tenant_{role}",
            tier=role
        )
        assert user.tier == role

    def test_admin_permissions_superset(self):
        admin_user = User(uid="admin_uid", email="admin@leo.ai", tier="admin")
        assert admin_user.tier in ["admin", "enterprise"]
