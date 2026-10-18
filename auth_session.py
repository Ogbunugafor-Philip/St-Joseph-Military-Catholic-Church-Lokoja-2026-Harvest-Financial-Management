"""Framework-neutral session authorization helpers."""

from __future__ import annotations

from collections.abc import MutableMapping


AUTH_STATE_KEYS = (
    "app_ok",
    "admin_ok",
    "app_failed_attempts",
    "app_locked_until",
    "admin_failed_attempts",
    "admin_locked_until",
    "auth_last_activity",
)


def expire_inactive_session(state: MutableMapping, now: float, timeout_seconds: int) -> bool:
    """Clear authentication after inactivity and return whether expiry occurred."""
    if not state.get("app_ok", False):
        return False
    last_activity = float(state.get("auth_last_activity", now))
    if now - last_activity <= timeout_seconds:
        state["auth_last_activity"] = now
        return False
    clear_authentication(state)
    return True


def clear_authentication(state: MutableMapping) -> None:
    for key in AUTH_STATE_KEYS:
        state.pop(key, None)


def require_admin(state: MutableMapping) -> None:
    if not state.get("admin_ok", False):
        raise PermissionError("Administrator authorization is required.")
