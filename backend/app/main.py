from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api import auth, users, quizzes, categories, challenges, progress, admin, test
from app.core.config import settings
from app.db.session import engine, get_db
from app.models import base

# Create database tables
base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quiz App API",
    description="API per l'applicazione di quiz educativi",
    version="0.1.0",
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(quizzes.router, prefix=f"{settings.API_V1_STR}/quizzes", tags=["Quizzes"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["Categories"])
app.include_router(challenges.router, prefix=f"{settings.API_V1_STR}/challenges", tags=["Challenges"])
app.include_router(progress.router, prefix=f"{settings.API_V1_STR}/progress", tags=["Progress"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])
app.include_router(test.router, prefix=f"{settings.API_V1_STR}/test", tags=["Test"])

@app.get("/")
def read_root():
    return {"message": "Benvenuto nell'API di Quiz App"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
