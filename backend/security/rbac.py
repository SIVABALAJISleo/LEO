from enum import Enum
from typing import Dict
from fastapi import HTTPException, Depends
from backend.core.security import verify_token

class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    PRO = "pro"
    ADMIN = "admin"
    SERVICE = "service"

PERMISSIONS: Dict[Role, Dict[str, bool]] = {
    Role.GUEST:   {"orchestrate": False, "upload": False, "admin": False},
    Role.USER:    {"orchestrate": True,  "upload": False, "admin": False},
    Role.PRO:     {"orchestrate": True,  "upload": True,  "admin": False},
    Role.ADMIN:   {"orchestrate": True,  "upload": True,  "admin": True},
    Role.SERVICE: {"orchestrate": True,  "upload": True,  "admin": False},
}

def check_permission(user_role: Role, action: str) -> bool:
    return PERMISSIONS.get(user_role, {}).get(action, False)

def require_permission(user_role: Role, action: str):
    if not check_permission(user_role, action):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

class PermissionChecker:
    def __init__(self, action: str):
        self.action = action

    def __call__(self, token: dict = Depends(verify_token)):
        role_str = token.get("role", "guest")
        try:
            role = Role(role_str)
        except ValueError:
            role = Role.GUEST
        
        require_permission(role, self.action)
        return token
