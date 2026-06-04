"""
auth.py
-------
Local user registration and login for the CineGold dashboard.
Passwords are stored as PBKDF2-SHA256 hashes (never plain text).
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from styles import apply_auth_styles

USERS_PATH = Path(__file__).parent / "data" / "users.json"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _load_users() -> dict:
    if not USERS_PATH.exists():
        return {}
    try:
        return json.loads(USERS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict) -> None:
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    USERS_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return digest.hex()


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not EMAIL_RE.match(email):
        return False, "Please enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    users = _load_users()
    key = username.lower()
    if key in users:
        return False, "That username is already taken."
    if any(u.get("email") == email for u in users.values()):
        return False, "An account with this email already exists."

    salt = secrets.token_hex(16)
    users[key] = {
        "username": username,
        "email": email,
        "salt": salt,
        "password_hash": _hash_password(password, salt),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_users(users)
    return True, "Welcome to CineGold — your account is ready."


def authenticate(username: str, password: str) -> tuple[bool, str, str | None]:
    """Return (ok, message, display_username)."""
    key = username.strip().lower()
    users = _load_users()
    record = users.get(key)
    if not record:
        return False, "Invalid username or password.", None

    expected = record.get("password_hash", "")
    salt = record.get("salt", "")
    if _hash_password(password, salt) != expected:
        return False, "Invalid username or password.", None

    return True, "Signed in successfully.", record.get("username", username)


def init_session() -> None:
    defaults = {
        "authenticated": False,
        "username": None,
        "auth_mode": "Sign In",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout() -> None:
    st.session_state.authenticated = False
    st.session_state.username = None


def render_auth_page() -> None:
    """Full-screen login / sign-up gate."""
    apply_auth_styles()

    brand_col, form_col = st.columns([1.05, 0.95], gap="large")

    with brand_col:
        st.markdown(
            """
            <div class="auth-brand-panel">
                <h1>CineGold</h1>
                <p class="tagline">Where world cinema meets Kollywood elegance</p>
                <ul class="features">
                    <li>IMDb & TMDb top-rated films worldwide</li>
                    <li>Curated Tamil & Kollywood classics</li>
                    <li>Golden Index Score ranking system</li>
                    <li>Hidden Gems Detector</li>
                    <li>PDF & CSV export with analytics</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with form_col:
        st.markdown('<div class="auth-segment">', unsafe_allow_html=True)
        mode = st.segmented_control(
            "Mode",
            options=["Sign In", "Create Account"],
            default=st.session_state.get("auth_mode", "Sign In"),
            label_visibility="collapsed",
            key="auth_mode",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if mode == "Sign In":
            st.markdown(
                '<h2>Welcome back</h2><p class="sub">Enter your credentials to continue</p>',
                unsafe_allow_html=True,
            )
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="your_username", autocomplete="username")
                password = st.text_input("Password", type="password", placeholder="••••••••", autocomplete="current-password")
                submit = st.form_submit_button("Sign In →", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    ok, msg, display = authenticate(username, password)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.username = display
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.markdown(
                '<h2>Join CineGold</h2><p class="sub">Create your private cinema lounge</p>',
                unsafe_allow_html=True,
            )
            with st.form("signup_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Choose a unique name")
                email = st.text_input("Email", placeholder="you@example.com", autocomplete="email")
                password = st.text_input("Password", type="password", placeholder="Min. 8 characters", autocomplete="new-password")
                confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password", autocomplete="new-password")
                submit = st.form_submit_button("Create Account →", use_container_width=True)

            if submit:
                if password != confirm:
                    st.error("Passwords do not match.")
                elif not all([username, email, password]):
                    st.error("Please fill in all fields.")
                else:
                    ok, msg = register_user(username, email, password)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.username = username.strip()
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown(
            '<p class="auth-footer">Secured locally · Your credentials never leave this app</p>',
            unsafe_allow_html=True,
        )
