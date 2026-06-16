from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    frequency: Optional[str] = None
    interval_value: Optional[str] = None
    is_completed: Optional[bool] = False
    telegram_enabled: Optional[bool] = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    frequency: Optional[str] = None
    interval_value: Optional[str] = None
    is_completed: Optional[bool] = None
    telegram_enabled: Optional[bool] = None

class TodoResponse(TodoBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserTelegramBase(BaseModel):
    telegram_chat_id: str
    is_active: Optional[bool] = True

class UserTelegramCreate(UserTelegramBase):
    pass

class UserTelegramUpdate(BaseModel):
    telegram_chat_id: Optional[str] = None
    is_active: Optional[bool] = None

class UserTelegramResponse(UserTelegramBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
