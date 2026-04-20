from fastapi import APIRouter, HTTPException, status
from db import fake_users_db
from schemas import UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(data: UserLogin):
    # Шукаємо користувача в нашій імітаційній БД
    user = next((u for u in fake_users_db if u["username"] == data.username), None)

    if not user or data.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірне ім'я користувача або пароль"
        )

    # Повертаємо username як токен (спрощена схема для ДЗ)
    return {
        "access_token": user["username"],
        "token_type": "bearer",
        "role": user["role"]
    }


@router.get("/me")
def get_me(username: str):
    user = next((u for u in fake_users_db if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user