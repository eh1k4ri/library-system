from fastapi import FastAPI
from app.api import users, books, healthcheck

app = FastAPI(title="Library System API - Day 2")

app.include_router(healthcheck.router, prefix="", tags=["System"])

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(books.router, prefix="/books", tags=["Books"])
