"""Maxsus exception klasslar."""
from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self, detail: str = "Yaroqsiz token yoki ma'lumotlar"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundException(HTTPException):
    def __init__(self, resource: str = "Ma'lumot"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} topilmadi",
        )


class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "Bu amalga ruxsat yo'q"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Ma'lumotlar konflikti"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
