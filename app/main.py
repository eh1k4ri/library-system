from fastapi import FastAPI
from app.api.routers import users, books, healthcheck, loans
from app.core.logger import configure_logging
from app.core.middlewares import log_requests, rate_limit

configure_logging()
app = FastAPI(
    title="Library System API",
    docs_url="/docs",
)
app.middleware("http")(rate_limit)
app.middleware("http")(log_requests)
app.include_router(healthcheck.router, prefix="", tags=["System"])

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])
