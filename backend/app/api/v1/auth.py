"""Auth endpointlari."""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_oltp_db
from app.models.oltp.user import User
from app.schemas.auth import TokenRefresh, TokenResponse, UserRegister, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_oltp_db)) -> User:
    """Yangi foydalanuvchini ro'yxatga olish."""
    return auth_service.register_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_oltp_db),
) -> TokenResponse:
    """Login va JWT token olish."""
    user = auth_service.authenticate_user(db, form.username, form.password)
    return auth_service.build_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: TokenRefresh, db: Session = Depends(get_oltp_db)) -> TokenResponse:
    """Refresh token orqali yangi tokenlar olish."""
    return auth_service.refresh_access_token(db, payload.refresh_token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Joriy login qilgan foydalanuvchi haqida ma'lumot."""
    return current_user
