from pydantic import BaseModel
import datetime

class FileUploadResponse(BaseModel):
    id: int
    filename: str
    filetype: str
    uploaded_at: datetime.datetime
    class Config:
        orm_mode = True

class FileListItem(BaseModel):
    id: int
    filename: str
    filetype: str
    uploaded_at: datetime.datetime
    class Config:
        orm_mode = True

class DownloadLinkResponse(BaseModel):
    download_link: str
    message: str 