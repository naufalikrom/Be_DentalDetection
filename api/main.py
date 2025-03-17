from fastapi import FastAPI
from .routers import auth
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI(
    docs_url="/documentation",
    redoc_url = "/redocs",
    title="Dental_Detected",
    description="Dental_Detected API",
    version="1.0",
    contact={
        "name": "Dental_Detected",
        "website": "https://dental-detected.com",
        "email" : "naufalikrom69@gmail.com"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Sesuaikan dengan URL frontend
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua metode (GET, POST, OPTIONS, dll.)
    allow_headers=["*"],  # Mengizinkan semua header
)

@app.get("/api/testing")
async def testing():
    return {"test": "its working"}

@app.get("/api")
async def root():
    return {"message": "Awesome Dental Detection"}

app.include_router(auth.router)
