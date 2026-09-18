"""
Role-Based Access Control for Rowad Nahda Campus Check-In
=========================================================
Roles: student, teacher, staff, busdriver, admin, host, appdev

School GPS + hours are locked: only **appdev** has admin.school_lock.
"""
from functools import wraps
from flask import session, redirect, url_for

ROLES = (
    "student", "teacher", "staff", "busdriver", "host", "admin", "appdev",
)

PERMISSIONS = {
    "checkin.self":        {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    "history.self":        {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    "history.all":         {"teacher", "staff", "host", "admin", "appdev"},
    "campus.board":        {"teacher", "staff", "host", "admin", "appdev"},
    "report.view":         {"teacher", "staff", "host", "admin", "appdev"},
    "checkin.manual":      {"teacher", "staff", "host", "admin", "appdev"},
    "announce.post":       {"teacher", "staff", "host", "admin", "appdev"},
    "announce.read":       {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    "channel.create":      {"teacher", "admin", "appdev"},
    "channel.post":        {"teacher", "admin", "appdev"},
    "channel.read":        {"student", "teacher", "staff", "busdriver", "host", "admin", "appdev"},
    "channel.members":     {"teacher", "admin", "appdev"},
    # Admin can manage users / force out / export — but NOT school GPS/hours
    "admin.users":         {"admin", "appdev"},
    "admin.export":        {"admin", "appdev"},
    "admin.force_out":     {"admin", "appdev"},
    "admin.settings":      {"admin", "appdev"},  # panel access
    # ONLY appdev can change school name, lat, lng, radius, hours
    "admin.school_lock":   {"appdev"},
}

def current_role() -> str:
    return (session.get("role") or "").strip().lower()

def has_perm(permission: str) -> bool:
    role = current_role()
    if not role:
        return False
    # appdev = full access including school_lock
    if role == "appdev":
        return True
    # admin gets everything EXCEPT school_lock
    if role == "admin":
        return permission != "admin.school_lock" and permission in PERMISSIONS
    allowed = PERMISSIONS.get(permission)
    if allowed is None:
        return False
    return role in allowed

def has_any(*permissions: str) -> bool:
    return any(has_perm(p) for p in permissions)

def has_role(*roles: str) -> bool:
    return current_role() in {r.lower() for r in roles}

def require(*permissions: str):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            for p in permissions:
                if not has_perm(p):
                    return (
                        f"Access denied. Need: {p} (role: {current_role() or 'none'}). "
                        f"School location/hours are locked to appdev only.",
                        403,
                    )
            return f(*args, **kwargs)
        return wrapped
    return decorator

def require_any(*permissions: str):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if not has_any(*permissions):
                return f"Access denied. Need one of: {', '.join(permissions)}", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

def require_role(*roles: str):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if not has_role(*roles):
                return f"Access denied. Roles: {', '.join(roles)}", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

def permissions_for_role(role: str) -> list:
    role = (role or "").lower()
    if role == "appdev":
        return sorted(PERMISSIONS.keys())
    if role == "admin":
        return sorted(p for p in PERMISSIONS if p != "admin.school_lock")
    return sorted(p for p, roles in PERMISSIONS.items() if role in roles)
