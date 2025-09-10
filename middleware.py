from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from schema.user import User
from utils import decode_token, create_anonymous_token, is_token_expiring, create_token


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        user = None
        new_token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload:
                if "user_id" in payload:
                    user = User(id=payload["user_id"], username=payload.get("username", "user"), role="user")
                elif "anon_id" in payload:
                    user = User(anon_id=payload["anon_id"])
                    if is_token_expiring(payload):
                        new_token = create_token({"anon_id": payload["anon_id"], "role": "anonymous"})
                else:
                    # token 无效 → 生成新的匿名
                    new_token = create_anonymous_token()
                    user = User(anon_id=decode_token(new_token)["anon_id"])
            else:
                # token 无效 → 生成新的匿名
                new_token = create_anonymous_token()
                user = User(anon_id=decode_token(new_token)["anon_id"])
        else:
            # 没有 token → 生成匿名
            new_token = create_anonymous_token()
            user = User(anon_id=decode_token(new_token)["anon_id"])

        request.state.user = user
        response: Response = await call_next(request)

        # 返回新的匿名 token
        if new_token:
            response.headers["X-Anonymous-Token"] = new_token

        return response
