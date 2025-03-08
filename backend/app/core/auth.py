"""
Compatibility module to re-export authentication functions from security.py.
This is needed for modules that try to import from app.core.auth.
"""

from app.core.security import (
    get_current_user,
    get_current_active_user,
    check_admin_privileges,
    check_parent_or_admin_privileges,
    create_access_token,
    get_password_hash,
    verify_password
)

# Re-export all authentication related functions
__all__ = [
    "get_current_user",
    "get_current_active_user",
    "check_admin_privileges",
    "check_parent_or_admin_privileges",
    "create_access_token",
    "get_password_hash",
    "verify_password"
]
