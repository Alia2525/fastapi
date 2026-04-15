task4
# FastAPI Auth API

## Опис
API для роботи з користувачами з використанням:
- реєстрації
- JWT авторизації (access і refresh токени)
- зміни пароля
- ролей (user/admin)
- logout (blacklist)
- видалення акаунта

## Встановлення та запуск
### 1. Створення віртуального середовища
python -m venv venv  
venv\Scripts\activate  

### 2. Встановлення залежностей
pip install -r requirements.txt  

### 3. Запуск сервера
uvicorn main:app --reload  

### 4. Swagger UI
http://127.0.0.1:8000/docs  

## Залежності
fastapi  
uvicorn  
python-jose  
passlib[bcrypt]  
python-multipart  
email-validator  
pytest  
httpx  

## Авторизація
У Swagger натисни Authorize і встав:
Bearer <access_token>

## Ендпоїнти

### POST /register
Опис: Реєстрація нового користувача  
Запит:
{
  "username": "test",
  "email": "test@example.com",
  "password": "123456"
}
Відповідь:
{
  "message": "User registered"
}
Помилки:
400 — User already exists  
422 — Validation error  

### POST /login
Опис: Логін користувача  
Тип: form-data  
Запит:
username: test  
password: 123456  
Відповідь:
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
Помилки:
401 — Incorrect username or password  

### POST /refresh
Опис: Отримати новий access token  
Запит:
{
  "refresh_token": "string"
}
Відповідь:
{
  "access_token": "string"
}
Помилки:
401 — Invalid refresh token  

### POST /logout
Опис: Вихід (додає токен у blacklist)  
Header:
Authorization: Bearer <token>  
Відповідь:
{
  "message": "Logged out"
}

### GET /profile
Опис: Отримати дані користувача  
Відповідь:
{
  "username": "test",
  "email": "test@example.com",
  "role": "user"
}
Помилки:
401 — Unauthorized  

### POST /change-password
Опис: Зміна пароля  
Запит:
{
  "old_password": "123456",
  "new_password": "newpass"
}
Відповідь:
{
  "message": "Password changed"
}

### DELETE /profile
Опис: Видалення акаунта  
Запит:
{
  "password": "123456"
}
Відповідь:
{
  "message": "Account deleted"
}

### GET /admin/users
Опис: Список усіх користувачів (тільки admin)  
Відповідь:
[
  {
    "username": "test",
    "email": "test@example.com",
    "role": "user"
  }
]
Помилки:
403 — Access denied  

## Коди помилок
200 — OK  
400 — Bad Request  
401 — Unauthorized  
403 — Forbidden  
422 — Validation Error  
500 — Internal Server Error  

## Примітки
- Дані зберігаються в пам’яті (fake DB)
- після перезапуску сервера всі користувачі зникають
- JWT використовується для авторизації
- refresh token має більший час життя (7 днів)