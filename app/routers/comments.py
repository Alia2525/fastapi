# routers/comments.py
from fastapi import APIRouter, Depends, HTTPException
from security import get_author_or_admin
from db import fake_comments_db
from schemas import CommentCreate
from datetime import datetime

router = APIRouter(prefix="/comments", tags=["comments"])

# Публічний GET
@router.get("/news/{news_id}/comments")
def get_comments(news_id: int):
    return [c for c in fake_comments_db if c["news_id"] == news_id]

# POST, PUT, DELETE (Захищені)
@router.post("/news/{news_id}/comments")
def create_comment(news_id: int, comment: CommentCreate, user: dict = Depends(get_author_or_admin)):
    new_comment = {
        "id": len(fake_comments_db) + 1,
        "news_id": news_id,
        "author_username": user["username"],
        "text": comment.text,
        "created_at": datetime.now()
    }
    fake_comments_db.append(new_comment)
    return new_comment

@router.put("/{comment_id}")
def update_comment(comment_id: int, comment_data: CommentCreate, user: dict = Depends(get_author_or_admin)):
    for comment in fake_comments_db:
        if comment["id"] == comment_id:
            comment["text"] = comment_data.text
            return comment
    raise HTTPException(status_code=404, detail="Comment not found")

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, user: dict = Depends(get_author_or_admin)):
    global fake_comments_db
    # Фільтруємо список, залишаючи все, крім видаленого
    fake_comments_db = [c for c in fake_comments_db if c["id"] != comment_id]
    return {"message": "Comment deleted"}