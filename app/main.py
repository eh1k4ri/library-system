from fastapi import FastAPI
from app.api.routers import users, books, healthcheck, loans, reservations, metrics, reports
from app.core.logger import configure_logging
from app.core.middlewares import log_requests, rate_limit, basic_auth, metrics as metrics_middleware

configure_logging()
app = FastAPI(
    title="Library System API",
    docs_url="/docs",
)
app.middleware("http")(basic_auth)
app.middleware("http")(metrics_middleware)
app.middleware("http")(rate_limit)
app.middleware("http")(log_requests)

app.include_router(healthcheck.router, prefix="", tags=["System"])

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])
app.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])
app.include_router(metrics.router, prefix="", tags=["System"])
app.include_router(reports.router, prefix="", tags=["Reports"])
