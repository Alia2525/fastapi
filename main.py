"""
Вам надано FastAPI-додаток із наступною функціональністю:
•  Реєстрація користувача (/register) з валідацією через Pydantic
•  Логін (/login) з генерацією JWT access-токена
•  Зміна пароля (/change-password) — захищений ендпоїнт
•  Перегляд профілю (/profile) — захищений ендпоїнт
•  Хешування паролів через bcrypt (passlib)
"""
from fastapi import FastAPI, HTTPException, Depends, status
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

# =====================
# FAKE DB
# =====================
fake_users_db: Dict[str, dict] = {}

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

class UserLogin(BaseModel):
    username: str
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str


# =====================
# UTILS
# =====================
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return fake_users_db[username]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
        "hashed_password": hash_password(user.password)
    }

    return {"message": "User registered successfully"}


# LOGIN
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


# PROFILE (protected)
@app.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"]
    }


# CHANGE PASSWORD (protected)
@app.post("/change-password")
def change_password(data: ChangePassword, current_user: dict = Depends(get_current_user)):
    username = current_user["username"]

    if not verify_password(data.old_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    fake_users_db[username]["hashed_password"] = hash_password(data.new_password)

    return {"message": "Password updated successfully"}
