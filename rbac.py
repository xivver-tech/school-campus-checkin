"""
Role-Based Access Control for Rowad Nahda Campus Check-In
=========================================================
Roles: student, teacher, staff, busdriver, admin, host, appdev

Permissions are checked via @require("permission_name") or
require_any / require_role helpers.
"""
from functools import wraps
from flask import session, redirect, url_for

# ---- Roles ----
ROLES = (
    "student",
    "teacher",
    "staff",
    "busdriver",
    "host",
    "admin",
    "appdev",
)

# ---- Permission matrix ----
# True = allowed. Admin/appdev get everything via wildcard.
PERMISSIONS = {
    # Self check-in / out with GPS
    "checkin.self":        {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    # View own history
    "history.self":        {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    # View all users' history
    "history.all":         {"teacher", "staff", "host", "admin", "appdev"},
    # Live campus board (who's in/out)
    "campus.board":        {"teacher", "staff", "host", "admin", "appdev"},
    # Daily / week reports, absents
    "report.view":         {"teacher", "staff", "host", "admin", "appdev"},
    # Manual check-in for another person
    "checkin.manual":      {"teacher", "staff", "host", "admin", "appdev"},
    # School-wide announcements (post)
    "announce.post":       {"teacher", "staff", "host", "admin", "appdev"},
    # School-wide announcements (read)
    "announce.read":       {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    # Class channels: create / own
    "channel.create":      {"teacher", "admin", "appdev"},
    # Class channels: post to owned class
    "channel.post":        {"teacher", "admin", "appdev"},
    # Class channels: read (membership enforced separately)
    "channel.read":        {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    # Class channels: manage members
    "channel.members":     {"teacher", "admin", "appdev"},
    # Admin settings, users, export, force checkout
    "admin.settings":      {"admin", "appdev"},
    "admin.users":         {"admin", "appdev"},
    "admin.export":        {"admin", "appdev"},
    "admin.force_out":     {"admin", "appdev"},
}

def current_role() -> str:
    return (session.get("role") or "").strip().lower()

def has_perm(permission: str) -> bool:
    """Return True if current session role has the permission."""
    role = current_role()
    if not role:
        return False
    # Super roles
    if role in ("admin", "appdev"):
        return True
    allowed = PERMISSIONS.get(permission)
    if allowed is None:
        return False
    return role in allowed

def has_any(*permissions: str) -> bool:
    return any(has_perm(p) for p in permissions)

def has_role(*roles: str) -> bool:
    return current_role() in {r.lower() for r in roles}

def require(*permissions: str):
    """Decorator: user must have ALL listed permissions."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            for p in permissions:
                if not has_perm(p):
                    return (
                        f"Access denied. Need permission: {p} "
                        f"(your role: {current_role() or 'none'})",
                        403,
                    )
            return f(*args, **kwargs)
        return wrapped
    return decorator

def require_any(*permissions: str):
    """Decorator: user must have AT LEAST ONE permission."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if not has_any(*permissions):
                return (
                    f"Access denied. Need one of: {', '.join(permissions)} "
                    f"(your role: {current_role() or 'none'})",
                    403,
                )
            return f(*args, **kwargs)
        return wrapped
    return decorator

def require_role(*roles: str):
    """Decorator: user must have one of the listed roles."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if not has_role(*roles):
                return (
                    f"Access denied. Allowed roles: {', '.join(roles)} "
                    f"(your role: {current_role() or 'none'})",
                    403,
                )
            return f(*args, **kwargs)
        return wrapped
    return decorator

def permissions_for_role(role: str) -> list:
    """List all permissions a role has (for admin UI / debug)."""
    role = (role or "").lower()
    if role in ("admin", "appdev"):
        return sorted(PERMISSIONS.keys())
    return sorted(p for p, roles in PERMISSIONS.items() if role in roles)
