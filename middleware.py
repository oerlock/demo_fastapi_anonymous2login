from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from schema.user import User
from utils import decode_token, create_anonymous_token


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        user = None
        new_token = None  # 如果生成新的匿名 token，需要返回给前端

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload:
                if "user_id" in payload:
                    user = User(id=payload["user_id"], username=payload.get("username", "user"), role="user")
                elif "anon_id" in payload:
                    user = User(anon_id=payload["anon_id"])
                else:
                    # token 无效 → 生成匿名
                    new_token = create_anonymous_token()
                    user = User(anon_id=decode_token(new_token)["anon_id"])
            else:
                # token 无效 → 生成匿名
                new_token = create_anonymous_token()
                user = User(anon_id=decode_token(new_token)["anon_id"])
        else:
            # 没有 token → 生成匿名
            new_token = create_anonymous_token()
            user = User(anon_id=decode_token(new_token)["anon_id"])

        request.state.user = user
        response: Response = await call_next(request)

        # 如果生成了新的匿名 token，则返回给前端
        if new_token:
            # 方式 1：放到 response header
            response.headers["X-Anonymous-Token"] = new_token
            # 方式 2：也可以放到 cookie
            # response.set_cookie("anon_token", new_token, httponly=True)

        return response
