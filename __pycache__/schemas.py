from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.sql.sqltypes import VARCHAR

class UserBase(BaseModel):
    email: VARCHAR

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
