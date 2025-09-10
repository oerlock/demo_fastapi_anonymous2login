from fastapi import FastAPI, Depends, HTTPException
from starlette.requests import Request

from dependencies import get_current_user
from middleware import UserMiddleware
from schema.user import User
from utils import decode_token, create_token

app = FastAPI()
app.add_middleware(UserMiddleware)


@app.get("/profile")
async def read_profile(request: Request):
    user: User = request.state.user
    return {"user": user.dict()}


@app.get("/only-registered")
async def only_registered(request: Request):
    user: User = request.state.user
    if user.role == "anonymous":
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Login required")
    return {"user": user.dict()}


@app.post("/login")
async def login(username: str, password: str, request: Request):
    # 1. 校验账号密码（略，假设 user_id = 123）
    user_id = 123

    # 2. 检查请求里是否有匿名 token
    auth_header = request.headers.get("Authorization")
    anon_id = None
    if auth_header and auth_header.startswith("Bearer "):
        payload = decode_token(auth_header.split(" ")[1])
        if payload and "anon_id" in payload:
            anon_id = payload["anon_id"]

    # 3. 如果有 anon_id → 合并匿名数据到 user_id
    if anon_id:
        # 示例：合并购物车/草稿（此处应替换为你的业务逻辑）
        # merge_anonymous_data(anon_id, user_id)
        pass
    # 4. 返回新的用户 token
    token = create_token({"user_id": user_id, "username": username, "role": "user"})
    return {"access_token": token, "token_type": "bearer"}
