from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class OperationUserLogin(BaseModel):
    email: EmailStr
    password: str

class ClientUserSignup(BaseModel):
    email: EmailStr
    password: str

class ClientUserLogin(BaseModel):
    email: EmailStr
    password: str

class ClientUserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime.datetime
    class Config:
        orm_mode = True 