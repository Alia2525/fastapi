"""
2.1. Refresh Token
Додайте механізм refresh-токенів. Створіть ендпоїнт /refresh, який приймає refresh-токен і повертає новий access-токен. Refresh-токен повинен мати більший термін дії (наприклад, 7 днів).
 Підказка: Використовуйте різні значення у полі "type" payload для розрізнення access та refresh токенів.
2.2. Logout (інвалідація токена)
Реалізуйте ендпоїнт /logout, який додає поточний токен до "чорного списку" (blacklist). Модифікуйте verify_token(), щоб перевіряти чорний список.
 Підказка: Для blacklist можна використати простий set() у пам'яті.
2.3. Ролі користувачів (RBAC)
Додайте поле role до моделі користувача ("user" або "admin"). Створіть ендпоїнт /admin/users, який повертає список усіх користувачів (доступний лише для адмінів). Реалізуйте декоратор або dependency для перевірки ролі.
 Підказка: Створіть допоміжну функцію require_role(role: str) яка повертає Depends().
2.4. Видалення акаунта
Додайте ендпоїнт DELETE /profile для видалення власного акаунта. Користувач повинен підтвердити дію, передавши свій поточний пароль.

"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Dict

app = FastAPI()

# =====================
# CONFIG
# =====================
SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# =====================
# FAKE DB + BLACKLIST
# =====================
fake_users_db: Dict[str, dict] = {}
blacklist = set()

# =====================
# SECURITY
# =====================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =====================
# MODELS
# =====================
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class DeleteAccount(BaseModel):
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


# =====================
# UTILS
# =====================
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + expires_delta,
        "type": token_type
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    if token in blacklist:
        raise HTTPException(status_code=401, detail="Token revoked")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        if username not in fake_users_db:
            raise HTTPException(status_code=401, detail="User not found")

        return fake_users_db[username]

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =====================
# ROLE CHECK
# =====================
def require_role(role: str):
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return role_checker


# =====================
# ROUTES
# =====================

# REGISTER
@app.post("/register")
def register(user: UserRegister):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "role": "user"
    }

    return {"message": "User registered"}


# LOGIN (тепер повертає 2 токени)
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_token(
        {"sub": user["username"]},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "access"
    )

    refresh_token = create_token(
        {"sub": user["username"]},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
# REFRESH
@app.post("/refresh")
def refresh(data: RefreshTokenRequest):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        username = payload.get("sub")

        if username not in fake_users_db:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_token(
            {"sub": username},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "access"
        )

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# LOGOUT
@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    blacklist.add(token)
    return {"message": "Logged out"}


# PROFILE
@app.get("/profile")
def profile(user: dict = Depends(get_current_user)):
    return user


# CHANGE PASSWORD
@app.post("/change-password")
def change_password(data: ChangePassword, user: dict = Depends(get_current_user)):
    if not verify_password(data.old_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Wrong password")

    user["hashed_password"] = hash_password(data.new_password)
    return {"message": "Password changed"}


# DELETE ACCOUNT
@app.delete("/profile")
def delete_account(data: DeleteAccount, user: dict = Depends(get_current_user)):
    if not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Wrong password")

    del fake_users_db[user["username"]]
    return {"message": "Account deleted"}


# ADMIN ONLY
@app.get("/admin/users")
def get_all_users(admin: dict = Depends(require_role("admin"))):
    return list(fake_users_db.values())