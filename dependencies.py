from fastapi import Depends, Request

from schema.user import User
from utils import decode_token, create_anonymous_token


async def get_current_user(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if payload:
            if "user_id" in payload:
                return User(id=payload["user_id"], username=payload.get("username", "user"), role="user")
            if "anon_id" in payload:
                return User(anon_id=payload["anon_id"])
    # 没有 token → 自动创建匿名用户
    anon_token = create_anonymous_token()
    return User(anon_id=decode_token(anon_token)["anon_id"])
