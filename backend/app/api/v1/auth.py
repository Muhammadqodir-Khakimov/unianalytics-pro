"""Auth endpointlari."""
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.database import get_oltp_db
from app.models.oltp.user import User
from app.schemas.auth import TokenRefresh, TokenResponse, UserRegister, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: UserRegister, db: Session = Depends(get_oltp_db)) -> User:
    """Yangi foydalanuvchini ro'yxatga olish (5/min — spam protection)."""
    return auth_service.register_user(db, payload)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_oltp_db),
) -> TokenResponse:
    """Login va JWT token olish (10/min — brute-force protection)."""
    user = auth_service.authenticate_user(db, form.username, form.password)
    return auth_service.build_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
def refresh(request: Request, payload: TokenRefresh, db: Session = Depends(get_oltp_db)) -> TokenResponse:
    """Refresh token orqali yangi tokenlar olish."""
    return auth_service.refresh_access_token(db, payload.refresh_token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Joriy login qilgan foydalanuvchi haqida ma'lumot."""
    return current_user
