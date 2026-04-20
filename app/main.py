# main.py
from fastapi import FastAPI
from routers import comments, auth, news

app = FastAPI()

app.include_router(comments.router)
# Підключіть інші роутери тут:
# app.include_router(auth.router)
# app.include_router(news.router)

@app.get("/")
def root():
    return {"message": "API is running. Check /docs for Swagger UI"}