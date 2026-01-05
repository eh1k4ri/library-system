import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.session import Base, get_db
from app.main import app
from app.models import UserStatus, BookStatus, LoanStatus

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    db.add_all(
        [
            UserStatus(enumerator="active", translation="Ativo"),
            UserStatus(enumerator="suspended", translation="Suspenso"),
            UserStatus(enumerator="deactivated", translation="Desativado"),
            BookStatus(enumerator="available", translation="Disponível"),
            BookStatus(enumerator="loaned", translation="Emprestado"),
            LoanStatus(enumerator="active", translation="Ativo"),
            LoanStatus(enumerator="returned", translation="Devolvido"),
        ]
    )
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
