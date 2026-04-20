# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db import fake_users_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # В реальному проєкті тут буде декодування JWT
    # Для прикладу повертаємо юзера, знайденого за "токеном" (ім'ям)
    for user in fake_users_db:
        if user["username"] == token:
            return user
    raise HTTPException(status_code=401, detail="Invalid token")

def get_author_or_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["author", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to perform this action"
        )
    return current_user