"""
Institution lock — Rowad Nahda Private — Tiznit
================================================
Double session :
  Matin      08:00 → 12:00   retard après 08:15
  Après-midi 14:00 → 18:00   retard après 14:15

Seul **appdev** peut modifier GPS + horaires.
"""

LOCKED_SCHOOL = {
    "school_name": "Rowad Nahda Private - Tiznit",
    "school_lat": "29.6974",
    "school_lng": "-9.7316",
    "school_radius_m": "200",
    "morning_start": "08:00",
    "morning_end": "12:00",
    "morning_late": "08:15",
    "afternoon_start": "14:00",
    "afternoon_end": "18:00",
    "afternoon_late": "14:15",
    "school_start": "08:00",
    "school_end": "18:00",
    "late_after": "08:15",
}

LOCKED_KEYS = frozenset(LOCKED_SCHOOL.keys())


def is_appdev(role: str) -> bool:
    return (role or "").strip().lower() == "appdev"


def apply_lock(get_setting, set_setting, role: str):
    if is_appdev(role):
        return
    for k, v in LOCKED_SCHOOL.items():
        if get_setting(k, "") != v:
            set_setting(k, v)


def filter_settings_update(form_dict, role: str) -> dict:
    out = {}
    for k, v in form_dict.items():
        if k in LOCKED_KEYS and not is_appdev(role):
            continue
        out[k] = v
    return out
