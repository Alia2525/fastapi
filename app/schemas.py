# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Схеми для Користувачів ---

class UserLogin(BaseModel):
    username: str
    password: str

# --- Схеми для Коментарів ---

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    # Використовуємо для POST запиту, де news_id передається в URL
    pass

class CommentResponse(CommentBase):
    id: int
    news_id: int
    author_username: str
    created_at: datetime

    class Config:
        # Дозволяє працювати з об'єктами (якщо вони будуть не лише словниками)
        from_attributes = True

# --- Схеми для Новин ---

class NewsBase(BaseModel):
    title: str
    content: str

class NewsResponse(NewsBase):
    id: int
    author: str