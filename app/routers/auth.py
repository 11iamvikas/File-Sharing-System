from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import OperationUser, ClientUser
from app.schemas.user import OperationUserLogin, ClientUserSignup, ClientUserLogin, ClientUserOut
from app.utils.security import hash_password, verify_password, create_access_token, encrypt_token, decrypt_token
from app.services.email import send_email
from fastapi.responses import RedirectResponse
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/ops/login')
def ops_login(data: OperationUserLogin, db: Session = Depends(get_db)):
    user = db.query(OperationUser).filter(OperationUser.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_access_token({"sub": user.email, "role": "ops", "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post('/client/signup')
def client_signup(data: ClientUserSignup, db: Session = Depends(get_db)):
    if db.query(ClientUser).filter(ClientUser.email == data.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed = hash_password(data.password)
    user = ClientUser(email=data.email, hashed_password=hashed, is_active=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = encrypt_token(f"{user.id}:{user.email}")
    verify_url = f"http://localhost:8000/client/verify/{token}"
    send_email(user.email, "Verify your account", f"Click to verify: {verify_url}")
    return {"verify_url": verify_url}

@router.get('/client/verify/{token}')
def client_verify(token: str, db: Session = Depends(get_db)):
    data = decrypt_token(token)
    if not data:
        raise HTTPException(status_code=400, detail='Invalid or expired token')
    user_id, email = data.split(':')
    user = db.query(ClientUser).filter(ClientUser.id == int(user_id), ClientUser.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    user.is_active = True
    db.commit()
    return RedirectResponse(url='/client/verified-success')

@router.post('/client/login')
def client_login(data: ClientUserLogin, db: Session = Depends(get_db)):
    user = db.query(ClientUser).filter(ClientUser.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Account not verified')
    token = create_access_token({"sub": user.email, "role": "client", "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"} 