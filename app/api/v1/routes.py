import os
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.schemas import SeniorityLevel

# Internal imports
from app.models.schemas import UserCreate, Token
from app.core.jwt_utils import get_password_hash, verify_password, create_access_token
from app.core.auth_dependency import get_current_user
from app.services.pdf_parser import pdf_parser
from app.services.question_generator import question_service

router = APIRouter()
logger = logging.getLogger(__name__)

# --- MONGODB SETUP ---
# Fetching from .env for security
MONGO_URL = os.getenv("MONGODB_URL")

if not MONGO_URL:
    logger.error("MONGODB_URL is not set in environment variables!")
    # In production, you might want to raise an error here
else:
    client = AsyncIOMotorClient(MONGO_URL)
    # Using 'interview_db' as your primary database
    db = client.interview_db
    users_collection = db.users
    logger.info("MongoDB connection initialized via Environment Variable")

@router.get("/health", tags=["System"])
async def health_check():
    """Verify backend and connectivity."""
    return {
        "status": "operational", 
        "database": "connected",
        "version": "1.1.0"
    }

@router.post("/auth/signup", tags=["Auth"])
async def signup(user: UserCreate):
    """Register a new user in MongoDB."""
    try:
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered")
        
        user_data = {
            "email": user.email,
            "password": get_password_hash(user.password)
        }
        await users_collection.insert_one(user_data)
        return {"message": "User successfully created"}
    except Exception as e:
        logger.error(f"MongoDB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )

@router.post("/auth/login", response_model=Token, tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Handles login for Swagger and Frontend."""
    user = await users_collection.find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/generate", tags=["Inference"])
async def generate_interview_questions(
    job_role: str = Form(...),
    seniority_level: SeniorityLevel = Form(...), # Use the Enum here
    job_description: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user)
):
    """Orchestrates PDF parsing and LLM generation."""
    resume_text = ""
    if resume_file:
        if not resume_file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF allowed")
        content = await resume_file.read()
        resume_text = pdf_parser.extract_text(content)

    questions = await question_service.create_questions(
        job_role=job_role,
        seniority_level=seniority_level,
        job_description=job_description,
        resume_text=resume_text
    )

    return {
        "user": current_user,
        "job_role": job_role,
        "questions": questions
    }