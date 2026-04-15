from __future__ import annotations

from functools import wraps

from flask import abort, redirect, request, session, url_for


def is_authenticated() -> bool:
    return bool(session.get("authenticated"))


def current_user() -> dict:
    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role"),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if is_authenticated():
            return view(*args, **kwargs)
        return redirect(url_for("login_page", next=request.path))

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for("login_page", next=request.path))
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)

    return wrapped
