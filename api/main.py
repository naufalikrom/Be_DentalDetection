from fastapi import FastAPI
from .routers import auth



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

@app.get("/testing")
async def testing():
    return {"test": "its working"}

app.include_router(auth.router)
