# db.py
fake_users_db = [
    {"username": "admin_user", "role": "admin", "password": "123"},
    {"username": "author_user", "role": "author", "password": "123"},
    {"username": "simple_user", "role": "user", "password": "123"},
]

# Ось цього рядка у тебе, ймовірно, не вистачає:
fake_news_db = [
    {"id": 1, "title": "Перша новина", "content": "Текст новини...", "author": "admin_user"}
]

fake_comments_db = []