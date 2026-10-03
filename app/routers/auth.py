from typing import Optional
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import get_config, verify_secret
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    body: Optional[LoginRequest] = None,
    db: Session = Depends(get_db)
):
    user = username or (body.username if body else None)
    pwd = password or (body.password if body else None)

    if not user or not pwd:
        raise HTTPException(status_code=400, detail="Username and password required")

    config = get_config(db)

    if user == config.admin_username and verify_secret(pwd, config.admin_password_hash):
        request.session["authenticated"] = True
        request.session["username"] = user

        # Check if form request (redirects to /) or API JSON response
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

        return {"status": "success", "message": "Logged in successfully"}

    if "application/x-www-form-urlencoded" in request.headers.get("content-type", ""):
        return RedirectResponse(url="/login?error=Invalid+credentials", status_code=status.HTTP_303_SEE_OTHER)

    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"status": "success", "message": "Logged out"}
