from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    anon_id: Optional[str] = None
    username: str = "anonymous"
    role: str = "anonymous"
