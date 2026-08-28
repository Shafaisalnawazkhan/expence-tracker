from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class PinIn(BaseModel):
    pin: str = Field(pattern=r"^\d{4,8}$")

class ProfileIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr

class PasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


def token_pair(user: User):
    return {"access_token": create_token(user.id, "access"), "refresh_token": create_token(user.id, "refresh"), "token_type": "bearer", "user": {"id": user.id, "name": user.name, "email": user.email, "app_lock_enabled": bool(user.app_lock_hash)}}


@router.post("/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())):
        raise HTTPException(409, "Email is already registered")
    user = User(name=data.name.strip(), email=data.email.lower(), password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"message": "Account created successfully. Please sign in.", "email": user.email}


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return token_pair(user)


@router.post("/refresh")
def refresh(data: RefreshIn, db: Session = Depends(get_db)):
    try: user_id = decode_token(data.refresh_token, "refresh")
    except ValueError: raise HTTPException(401, "Invalid or expired refresh token")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "User not found")
    return token_pair(user)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "app_lock_enabled": bool(user.app_lock_hash)}

@router.put("/me")
def update_profile(data:ProfileIn,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    email=data.email.lower()
    if db.scalar(select(User).where(User.email==email,User.id!=user.id)): raise HTTPException(409,"Email is already registered")
    user.name=data.name.strip();user.email=email;db.commit();db.refresh(user)
    return {"id":user.id,"name":user.name,"email":user.email,"app_lock_enabled":bool(user.app_lock_hash)}

@router.put("/password")
def update_password(data:PasswordIn,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if not verify_password(data.current_password,user.password_hash): raise HTTPException(401,"Current password is incorrect")
    user.password_hash=hash_password(data.new_password);db.commit();return {"updated":True}


@router.post("/app-lock/setup")
def setup_app_lock(data: PinIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.app_lock_hash = hash_password(data.pin); db.commit()
    return {"enabled": True}


@router.post("/app-lock/verify")
def verify_app_lock(data: PinIn, user: User = Depends(get_current_user)):
    if not user.app_lock_hash or not verify_password(data.pin, user.app_lock_hash):
        raise HTTPException(401, "Incorrect app-lock PIN")
    return {"verified": True}


@router.delete("/app-lock")
def disable_app_lock(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.app_lock_hash = None; db.commit(); return {"enabled": False}
