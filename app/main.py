from fastapi import FastAPI
from app.api import users, books, healthcheck, loans

app = FastAPI(
    title="Library System API",
    docs_url="/docs",
)

app.include_router(healthcheck.router, prefix="", tags=["System"])

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])
