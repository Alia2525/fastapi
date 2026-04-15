"""
Завдання 3: Тестування API
Напишіть тести для API, використовуючи pytest та httpx (або TestClient від FastAPI).
Покрийте тестами наступні сценарії:
•  Успішна реєстрація нового користувача
•  Реєстрація з дублікатом username повертає 400
•  Успішний логін та отримання токена
•  Логін з невірним паролем повертає 401
•  Доступ до /profile з валідним токеном
•  Доступ до /profile без токена повертає 401 (або 403)
•  Зміна пароля та подальший логін з новим паролем
•  Тест на expired токен (використайте мок або коротку тривалість)
Приклад структури тесту:
from fastapi.testclient import TestClient from main import app
client = TestClient(app)
def test_register_success():
    response = client.post("/register", json={         "username": "testuser",
        "email": "test@example.com",         "password": "securepass123"     })
    assert response.status_code == 201
"""
from fastapi.testclient import TestClient
from main import app, fake_users_db

client = TestClient(app)


#  очищаємо "базу" перед кожним тестом
def setup_function():
    fake_users_db.clear()


#  1. Успішна реєстрація
def test_register_success():
    response = client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    })
    assert response.status_code == 200
    assert response.json()["message"]


#  2. Дублікат username
def test_register_duplicate():
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    })

    response = client.post("/register", json={
        "username": "testuser",
        "email": "test2@example.com",
        "password": "123456"
    })

    assert response.status_code == 400


#  3. Успішний логін
def test_login_success():
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    })

    response = client.post("/login", data={
        "username": "testuser",
        "password": "123456"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


#  4. Невірний пароль
def test_login_wrong_password():
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    })

    response = client.post("/login", data={
        "username": "testuser",
        "password": "wrong"
    })

    assert response.status_code == 401


#  5. Доступ до profile з токеном
def test_profile_with_token():
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    })

    login = client.post("/login", data={
        "username": "testuser",
        "password": "123456"
    })

    token = login.json()["access_token"]

    response = client.get("/profile", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


# 6. Без токена
def test_profile_without_token():
    response = client.get("/profile")
    assert response.status_code in [401, 403]


# 7. Зміна пароля + новий логін
def test_change_password_and_login():
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    })

    login = client.post("/login", data={
        "username": "testuser",
        "password": "123456"
    })

    token = login.json()["access_token"]

    # змінюємо пароль
    response = client.post("/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": "123456",
            "new_password": "newpass"
        }
    )

    assert response.status_code == 200

    # логін з новим паролем
    login2 = client.post("/login", data={
        "username": "testuser",
        "password": "newpass"
    })

    assert login2.status_code == 200


#  8. expired token
def test_expired_token():
    from jose import jwt
    from main import SECRET_KEY, ALGORITHM
    from datetime import datetime, timedelta

    # створюємо прострочений токен
    expired_token = jwt.encode({
        "sub": "testuser",
        "exp": datetime.utcnow() - timedelta(minutes=1),
        "type": "access"
    }, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get("/profile", headers={
        "Authorization": f"Bearer {expired_token}"
    })

    assert response.status_code == 401