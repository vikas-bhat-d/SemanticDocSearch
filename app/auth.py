from dataclasses import dataclass
from typing import Optional
from fastapi import Request, Header, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import get_config, verify_secret


@dataclass
class AuthContext:
    auth_type: str  # "session" | "api_key"


def verify_api_key(x_api_key: str, db: Session) -> bool:
    if not x_api_key:
        return False
    config = get_config(db)
    if not config.api_key_hash:
        return False
    return verify_secret(x_api_key, config.api_key_hash)


def verify_session(request: Request) -> bool:
    return bool(request.session.get("authenticated"))


async def require_auth(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> AuthContext:
    # 1. Check API Key header
    if x_api_key and verify_api_key(x_api_key, db):
        return AuthContext(auth_type="api_key")

    # 2. Check Session Cookie
    if verify_session(request):
        return AuthContext(auth_type="session")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Valid session cookie or X-API-Key header required"
    )


async def require_session_ui(request: Request):
    if not verify_session(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return True


async def require_session_api(request: Request):
    if not verify_session(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session login required"
        )
    return True
