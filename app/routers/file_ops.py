from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.utils.security import decode_access_token
from app.services.file_service import save_file
from app.schemas.file import FileUploadResponse
from app.models.user import OperationUser
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()
security = HTTPBearer()

def get_current_ops_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or payload.get('role') != 'ops':
        raise HTTPException(status_code=403, detail='Not authorized')
    user = db.query(OperationUser).filter(OperationUser.id == payload['user_id']).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user

@router.post('/ops/upload', response_model=FileUploadResponse)
def upload_file(file: UploadFile = File(...), current_user: OperationUser = Depends(get_current_ops_user), db: Session = Depends(get_db)):
    uploaded_file = save_file(file, current_user.id, db)
    return uploaded_file 