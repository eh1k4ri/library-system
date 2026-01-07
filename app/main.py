from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.routers import (
    users,
    books,
    healthcheck,
    loans,
    reservations,
    metrics,
    reports,
)
from app.core.logger import configure_logging
from app.core.constants import APP_NAME
from app.core.middlewares import (
    log_requests,
    rate_limit,
    basic_auth,
    metrics as metrics_middleware,
)

configure_logging()

app = FastAPI(
    title=APP_NAME,
    docs_url="/docs",
    description="Library System API - Use Local Auth (default: admin/password123)",
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=APP_NAME,
        version="1.0.0",
        description="Library System API - Use Local Auth (default: admin/password123)",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "basicAuth": {"type": "http", "scheme": "basic"}
    }
    openapi_schema["security"] = [{"basicAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.middleware("http")(basic_auth)
app.middleware("http")(metrics_middleware)
app.middleware("http")(rate_limit)
app.middleware("http")(log_requests)

app.include_router(healthcheck.router, prefix="", tags=["System"])

app.include_router(users.router, prefix="/user", tags=["Users"])
app.include_router(books.router, prefix="/book", tags=["Books"])
app.include_router(loans.router, prefix="/loan", tags=["Loans"])
app.include_router(reservations.router, prefix="/reservation", tags=["Reservations"])
app.include_router(metrics.router, prefix="", tags=["System"])
app.include_router(reports.router, prefix="", tags=["Reports"])
