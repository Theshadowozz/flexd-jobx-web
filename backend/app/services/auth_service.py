from collections import OrderedDict
from threading import Lock
from time import monotonic

from sqlalchemy import select

from app.models.user import User
from app.utils.exceptions import AppError
from app.utils.security import create_token, hash_password, hasher, verify_password

_attempts = OrderedDict()
_lock = Lock()
_dummy = hash_password("not-a-real-account-password")


def check_rate_limit(client_ip):
    # Per-process bound; deployment must enforce a shared limit across workers.
    now = monotonic()
    with _lock:
        for key in list(_attempts):
            if _attempts[key][0] <= now - 60:
                del _attempts[key]
        start, count = _attempts.get(client_ip, (now, 0))
        if count >= 10:
            raise AppError(
                429,
                "rate_limit",
                {"login": "Terlalu banyak percobaan login"},
                headers={"Retry-After": str(max(1, int(60 - now + start)))},
            )
        _attempts[client_ip] = (start, count + 1)
        if len(_attempts) > 10000:
            _attempts.popitem(last=False)


def login(db, payload):
    user = db.scalar(select(User).where(User.email == str(payload.email)).with_for_update())
    valid = verify_password(
        payload.password.get_secret_value(), user.password_hash if user else _dummy
    )
    if not valid or user is None or user.account_status != "active":
        raise AppError(
            401,
            "authentication",
            {"credentials": "Email atau password salah"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token(user.id)
    if hasher.check_needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password.get_secret_value())
        db.commit()
    return user, token


def change_password(db, user, payload):
    user = db.scalar(
        select(User)
        .where(User.id == user.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if not verify_password(payload.current_password.get_secret_value(), user.password_hash):
        raise AppError(
            401,
            "authentication",
            {"credentials": "Password lama tidak sesuai"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.password_hash = hash_password(payload.new_password.get_secret_value())
    db.commit()
