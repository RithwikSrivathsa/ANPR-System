from fastapi import APIRouter, HTTPException

from app.core.security import create_access_token
from app.schemas import LoginRequest, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
    # Scaffold: replace with a users table or identity provider before production exposure.
    if not payload.username or not payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(payload.username))
