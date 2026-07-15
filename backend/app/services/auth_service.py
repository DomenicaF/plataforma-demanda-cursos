"""Servicio de autenticación (RNF-06)."""
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def authenticate(self, email: str, password: str):
        user = self.repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    def login(self, email: str, password: str) -> dict | None:
        user = self.authenticate(email, password)
        if user is None:
            return None
        token = create_access_token(subject=user.email, role=user.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role,
            "full_name": user.full_name,
            "email": user.email,
        }
