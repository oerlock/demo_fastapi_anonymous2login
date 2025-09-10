import datetime

import jwt, uuid

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ANON_RENEW_THRESHOLD_MINUTES = 30  # 剩余小于30分钟就续期


def create_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + (
                expires_delta or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


def create_anonymous_token():
    return create_token({"anon_id": str(uuid.uuid4()), "role": "anonymous"})


def is_token_expiring(payload: dict, threshold_minutes=ANON_RENEW_THRESHOLD_MINUTES):
    exp = payload.get("exp")
    if not exp:
        return True
    remaining = datetime.datetime.fromtimestamp(exp, datetime.UTC) - datetime.datetime.now(datetime.UTC)
    return remaining < datetime.timedelta(minutes=threshold_minutes)
