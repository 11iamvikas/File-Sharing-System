from fastapi import FastAPI
from app.routers import auth, file_ops, client_file

app = FastAPI()

# Routers will be included here later 
app.include_router(auth.router)
app.include_router(file_ops.router)
app.include_router(client_file.router) 