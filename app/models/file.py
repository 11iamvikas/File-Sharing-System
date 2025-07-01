from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filetype = Column(String(50), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    uploader_id = Column(Integer, ForeignKey('operation_users.id'))
    uploader = relationship('OperationUser')
    path = Column(String(255), nullable=False) 