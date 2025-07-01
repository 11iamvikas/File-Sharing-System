from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.utils.security import decode_access_token, encrypt_token, decrypt_token
from app.models.user import ClientUser
from app.models.file import UploadedFile
from app.schemas.file import FileListItem, DownloadLinkResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
import os

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()
security = HTTPBearer()

def get_current_client_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or payload.get('role') != 'client':
        raise HTTPException(status_code=403, detail='Not authorized')
    user = db.query(ClientUser).filter(ClientUser.id == payload['user_id']).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail='Not authorized')
    return user

@router.get('/client/files', response_model=list[FileListItem])
def list_files(current_user: ClientUser = Depends(get_current_client_user), db: Session = Depends(get_db)):
    files = db.query(UploadedFile).all()
    return files

@router.get('/client/download/{file_id}', response_model=DownloadLinkResponse)
def generate_download_link(file_id: int, current_user: ClientUser = Depends(get_current_client_user), db: Session = Depends(get_db)):
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail='File not found')
    token = encrypt_token(f"{file.id}:{current_user.id}")
    return {"download_link": f"/client/secure-download/{token}", "message": "success"}

@router.get('/client/secure-download/{token}')
def secure_download(token: str, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = decode_access_token(credentials.credentials)
    if not payload or payload.get('role') != 'client':
        raise HTTPException(status_code=403, detail='Not authorized')
    user_id = payload['user_id']
    data = decrypt_token(token)
    if not data:
        raise HTTPException(status_code=400, detail='Invalid or expired token')
    file_id, token_user_id = data.split(':')
    if int(token_user_id) != int(user_id):
        raise HTTPException(status_code=403, detail='Token does not match user')
    file = db.query(UploadedFile).filter(UploadedFile.id == int(file_id)).first()
    if not file:
        raise HTTPException(status_code=404, detail='File not found')
    if not os.path.exists(file.path):
        raise HTTPException(status_code=404, detail='File missing on server')
    return FileResponse(file.path, filename=file.filename) 