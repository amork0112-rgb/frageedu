from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import bcrypt
import jwt
from email_validator import validate_email

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'frage-edu-secret-key-2025')

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    phone: str
    parent_name: str
    student_name: str
    password_hash: str
    household_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    email_verified: bool = False

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    parent_name: str
    student_name: str
    password: str
    terms_accepted: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    phone: str
    parent_name: str
    student_name: str
    household_token: str
    created_at: datetime
    email_verified: bool

class AdmissionData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    household_token: str
    consent_status: str = "pending"  # pending, completed
    forms_status: str = "pending"    # pending, completed
    guides_status: str = "pending"   # pending, completed
    checklist_status: str = "pending" # pending, completed
    consent_data: Optional[Dict[str, Any]] = {}
    forms_data: Optional[Dict[str, Any]] = {}
    guides_data: Optional[Dict[str, Any]] = {}
    checklist_data: Optional[Dict[str, Any]] = {}
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdmissionResponse(BaseModel):
    household_token: str
    consent_status: str
    forms_status: str
    guides_status: str
    checklist_status: str
    consent_data: Dict[str, Any]
    forms_data: Dict[str, Any]
    guides_data: Dict[str, Any]
    checklist_data: Dict[str, Any]
    updated_at: datetime

class ConsentUpdate(BaseModel):
    regulation_agreed: bool
    privacy_agreed: bool
    photo_consent: bool
    medical_consent: bool
    parent_signature: Optional[str] = None
    student_name: Optional[str] = None
    signed_at: Optional[datetime] = None

class FormsUpdate(BaseModel):
    student_name: str
    birth_date: str
    parent_name: str
    emergency_contact: str
    allergies: str
    milk_program: bool
    afterschool_program: str

class ChecklistUpdate(BaseModel):
    items: List[Dict[str, Any]]

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, household_token: str) -> str:
    payload = {
        'user_id': user_id,
        'household_token': household_token,
        'exp': datetime.now(timezone.utc).timestamp() + (24 * 60 * 60)  # 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return UserResponse(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@api_router.get("/")
async def root():
    return {"message": "Frage EDU API", "version": "1.0"}

@api_router.post("/signup")
async def signup(user_data: UserCreate):
    if not user_data.terms_accepted:
        raise HTTPException(status_code=400, detail="Terms must be accepted")
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password)
    )
    
    # Insert user
    await db.users.insert_one(user.dict())
    
    # Create admission data
    admission = AdmissionData(household_token=user.household_token)
    await db.admission_data.insert_one(admission.dict())
    
    # Create JWT token
    token = create_jwt_token(user.id, user.household_token)
    
    return {
        "message": "User created successfully",
        "token": token,
        "user": UserResponse(**user.dict()),
        "household_token": user.household_token
    }

@api_router.post("/login")
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user['id'], user['household_token'])
    
    return {
        "message": "Login successful",
        "token": token,
        "user": UserResponse(**user),
        "household_token": user['household_token']
    }

@api_router.get("/profile")
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@api_router.get("/admission/{token}")
async def get_admission_data(token: str):
    admission = await db.admission_data.find_one({"household_token": token})
    if not admission:
        raise HTTPException(status_code=404, detail="Admission data not found")
    
    return AdmissionResponse(**admission)

@api_router.put("/admission/{token}/consent")
async def update_consent(token: str, consent_data: ConsentUpdate):
    admission = await db.admission_data.find_one({"household_token": token})
    if not admission:
        raise HTTPException(status_code=404, detail="Admission data not found")
    
    update_data = {
        "consent_data": consent_data.dict(),
        "consent_status": "completed",
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.admission_data.update_one(
        {"household_token": token},
        {"$set": update_data}
    )
    
    return {"message": "Consent updated successfully"}

@api_router.put("/admission/{token}/forms")
async def update_forms(token: str, forms_data: FormsUpdate):
    admission = await db.admission_data.find_one({"household_token": token})
    if not admission:
        raise HTTPException(status_code=404, detail="Admission data not found")
    
    update_data = {
        "forms_data": forms_data.dict(),
        "forms_status": "completed",
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.admission_data.update_one(
        {"household_token": token},
        {"$set": update_data}
    )
    
    return {"message": "Forms updated successfully"}

@api_router.put("/admission/{token}/guides")
async def update_guides(token: str):
    admission = await db.admission_data.find_one({"household_token": token})
    if not admission:
        raise HTTPException(status_code=404, detail="Admission data not found")
    
    update_data = {
        "guides_status": "completed",
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.admission_data.update_one(
        {"household_token": token},
        {"$set": update_data}
    )
    
    return {"message": "Guides marked as viewed"}

@api_router.put("/admission/{token}/checklist")
async def update_checklist(token: str, checklist_data: ChecklistUpdate):
    admission = await db.admission_data.find_one({"household_token": token})
    if not admission:
        raise HTTPException(status_code=404, detail="Admission data not found")
    
    update_data = {
        "checklist_data": checklist_data.dict(),
        "checklist_status": "completed",
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.admission_data.update_one(
        {"household_token": token},
        {"$set": update_data}
    )
    
    return {"message": "Checklist updated successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()