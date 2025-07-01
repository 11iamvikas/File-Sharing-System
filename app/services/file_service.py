import os
import shutil
from fastapi import UploadFile, HTTPException
from app.models.file import UploadedFile
from app.database import SessionLocal
from sqlalchemy.orm import Session
import mimetypes

ALLOWED_EXTENSIONS = {'.pptx', '.docx', '.xlsx'}
ALLOWED_MIME_TYPES = {
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}
UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploaded_files')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_file(file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail='Invalid file extension')
    mime_type, _ = mimetypes.guess_type(file.filename)
    if file.content_type not in ALLOWED_MIME_TYPES or mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail='Invalid file type')

def save_file(file: UploadFile, uploader_id: int, db: Session):
    validate_file(file)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    uploaded_file = UploadedFile(
        filename=file.filename,
        filetype=file.content_type,
        uploader_id=uploader_id,
        path=file_path
    )
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)
    return uploaded_file 