"""
Institution lock for Rowad Nahda Private — Tiznit
================================================
School identity, GPS geofence, and timetable are FROZEN for normal admins.
Only role **appdev** can change them.

This stops another school from cloning the app and pointing it at their campus.
"""

# Frozen for this deployment — change only as appdev in Admin
LOCKED_SCHOOL = {
    "school_name": "Rowad Nahda Private - Tiznit",
    "school_lat": "29.6974",
    "school_lng": "-9.7316",
    "school_radius_m": "200",
    "school_start": "08:00",
    "school_end": "16:00",
    "late_after": "08:15",
}

# Settings keys that require appdev
LOCKED_KEYS = frozenset(LOCKED_SCHOOL.keys())

def is_appdev(role: str) -> bool:
    return (role or "").strip().lower() == "appdev"

def apply_lock(get_setting, set_setting, role: str):
    """
    On every boot / request: force locked values unless caller is appdev.
    Non-appdev cannot persist different lat/lng/hours.
    """
    if is_appdev(role):
        return  # appdev may have customized DB values — leave them
    for k, v in LOCKED_SCHOOL.items():
        current = get_setting(k, "")
        if current != v:
            set_setting(k, v)

def filter_settings_update(form_dict, role: str) -> dict:
    """
    Strip locked keys from a settings form unless role is appdev.
    Returns only keys that are allowed to be written.
    """
    out = {}
    for k, v in form_dict.items():
        if k in LOCKED_KEYS and not is_appdev(role):
            continue  # ignore attempt to change school location/hours
        out[k] = v
    return out
