from fastapi import APIRouter, Depends, HTTPException
from db import fake_news_db
from security import get_author_or_admin

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/")
def list_news():
    """Отримати список усіх новин (публічно)"""
    return fake_news_db

@router.get("/{news_id}")
def get_one_news(news_id: int):
    """Отримати одну новину за ID (публічно)"""
    news = next((n for n in fake_news_db if n["id"] == news_id), None)
    if not news:
        raise HTTPException(status_code=404, detail="Новину не знайдено")
    return news

@router.post("/")
def create_news(title: str, content: str, user: dict = Depends(get_author_or_admin)):
    """Створити новину (тільки Author або Admin)"""
    new_item = {
        "id": len(fake_news_db) + 1,
        "title": title,
        "content": content,
        "author": user["username"]
    }
    fake_news_db.append(new_item)
    return {"message": "Новину створено", "news": new_item}