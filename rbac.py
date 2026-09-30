"""
RBAC — Rowad Nahda Campus Check-In
===================================
Roles: student, teacher, staff, host, admin, appdev

AppDev = full control (all features + GPS / hours lock).
Admin  = almost everything except school GPS / hours / name.
"""
from functools import wraps
from flask import session, redirect, url_for

ROLES = (
    "student", "teacher", "staff", "host", "admin", "appdev",
)

PERMISSIONS = {
    "checkin.self":      {"student", "teacher", "staff", "host", "admin", "appdev"},
    "history.self":      {"student", "teacher", "staff", "host", "admin", "appdev"},
    "history.all":       {"teacher", "staff", "host", "admin", "appdev"},
    "campus.board":      {"teacher", "staff", "host", "admin", "appdev"},
    "report.view":       {"teacher", "staff", "host", "admin", "appdev"},
    "checkin.manual":    {"teacher", "staff", "host", "admin", "appdev"},
    "announce.post":     {"teacher", "staff", "host", "admin", "appdev"},
    "announce.read":     {"student", "teacher", "staff", "host", "admin", "appdev"},
    "channel.create":    {"teacher", "admin", "appdev"},
    "channel.post":      {"teacher", "admin", "appdev"},
    "channel.read":      {"student", "teacher", "staff", "host", "admin", "appdev"},
    "channel.members":   {"teacher", "admin", "appdev"},
    "admin.users":       {"admin", "appdev"},
    "admin.export":      {"admin", "appdev"},
    "admin.force_out":   {"admin", "appdev"},
    "admin.settings":    {"admin", "appdev"},
    "admin.panel":       {"admin", "appdev"},
    "admin.roles":       {"admin", "appdev"},
    "admin.school_lock": {"appdev"},
    "system.full":       {"appdev"},
}


def current_role() -> str:
    return (session.get("role") or "").strip().lower()


def is_appdev_role(role: str = None) -> bool:
    r = (role if role is not None else current_role()) or ""
    return r.strip().lower() == "appdev"


def has_perm(permission: str) -> bool:
    role = current_role()
    if not role:
        return False
    if role == "appdev":
        return True
    if role == "admin":
        if permission in ("admin.school_lock", "system.full"):
            return False
        return permission in PERMISSIONS
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
                        f"Access denied. Required: {p} "
                        f"(current role: {current_role() or 'none'}).",
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
            if current_role() == "appdev":
                return f(*args, **kwargs)
            if not has_role(*roles):
                return f"Access denied. Allowed roles: {', '.join(roles)}", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator


def permissions_for_role(role: str) -> list:
    role = (role or "").lower()
    if role == "appdev":
        return sorted(set(PERMISSIONS.keys()) | {"* (full control)"})
    if role == "admin":
        return sorted(p for p in PERMISSIONS if p not in ("admin.school_lock", "system.full"))
    return sorted(p for p, roles in PERMISSIONS.items() if role in roles)


def can_access_admin_panel() -> bool:
    return has_perm("admin.panel") or has_perm("admin.settings") or current_role() == "appdev"
