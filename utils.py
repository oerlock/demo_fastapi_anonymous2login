import jwt, uuid
from datetime import datetime, timedelta

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ANON_RENEW_THRESHOLD_MINUTES = 30  # 剩余小于30分钟就续期


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
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
    remaining = datetime.utcfromtimestamp(exp) - datetime.utcnow()
    return remaining < timedelta(minutes=threshold_minutes)
