from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
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
import base64
import mimetypes

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
    password_hash: str
    role: str = "parent"  # admin, staff, parent
    status: str = "active"  # active, disabled
    name: str
    phone: str
    household_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    last_login_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    email_verified: bool = False

class Parent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    phone: str
    email: str
    branch: str  # kinder, junior, middle
    household_token: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: str
    name: str
    grade: str
    birthdate: Optional[str] = None
    notes: Optional[str] = None

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_user_id: str
    action: str  # RESET_PW, DISABLE, ENABLE, EXPORT, NOTIFY
    target_type: str  # User, Parent, Student
    target_id: str
    meta: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ip: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    name: str  # parent name
    student_name: str
    password: str
    terms_accepted: bool
    branch: str  # kinder, junior, middle

class ParentCreate(BaseModel):
    name: str
    phone: str
    email: str
    branch: str

class StudentCreate(BaseModel):
    name: str
    grade: str
    birthdate: Optional[str] = None
    notes: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str
    name: str
    phone: str
    household_token: str
    last_login_at: Optional[datetime]
    created_at: datetime
    email_verified: bool

class ParentResponse(BaseModel):
    id: str
    user_id: str
    name: str
    phone: str
    email: str
    branch: str
    household_token: str
    created_at: datetime

class StudentResponse(BaseModel):
    id: str
    parent_id: str
    name: str
    grade: str
    birthdate: Optional[str]
    notes: Optional[str]

class MemberListResponse(BaseModel):
    id: str
    parent_name: str
    phone: str
    email: str
    students: List[Dict[str, str]]
    branch: str
    household_token: str
    joined_at: datetime
    last_login: Optional[datetime]
    status: str

class MemberDetailResponse(BaseModel):
    user: UserResponse
    parent: ParentResponse
    students: List[StudentResponse]
    admission_data: Optional[Dict[str, Any]]
    exam_reservations: List[Dict[str, Any]]
    consent_status: Optional[str]
    forms_status: Optional[str]
    guides_status: Optional[str]
    checklist_status: Optional[str]

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

class ExamReservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    household_token: str
    user_id: str
    brchType: str  # junior, middle, kinder
    campus: str
    slot_id: str
    slot_start: datetime
    slot_end: datetime
    level_track: Optional[str] = None
    notes: Optional[str] = None
    status: str = "requested"  # requested, confirmed, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExamReservationCreate(BaseModel):
    brchType: str
    campus: str
    slot_id: str
    slot_start: str  # ISO string
    slot_end: str    # ISO string
    level_track: Optional[str] = None
    notes: Optional[str] = None

# Admin Models
class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    password_hash: str
    role: str = "admin"  # admin, super_admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

class AdminCreate(BaseModel):
    username: str
    email: str
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime
    last_login: Optional[datetime]

# News Models
class NewsArticle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: str  # 개강소식, 공지사항, 뉴스
    image_url: Optional[str] = None
    featured: bool = False
    published: bool = True
    created_by: str  # admin_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NewsArticleCreate(BaseModel):
    title: str
    content: str
    category: str
    image_url: Optional[str] = None
    featured: bool = False
    published: bool = True

class NewsArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    featured: Optional[bool] = None
    published: Optional[bool] = None

class NewsResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    image_url: Optional[str]
    featured: bool
    published: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

class BulkNotifyRequest(BaseModel):
    user_ids: List[str]
    message: str

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

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        admin_id = payload.get('admin_id')
        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid admin token")
        
        admin = await db.admins.find_one({"id": admin_id})
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        
        return AdminResponse(**admin)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_admin_jwt_token(admin_id: str, username: str) -> str:
    payload = {
        'admin_id': admin_id,
        'username': username,
        'exp': datetime.now(timezone.utc).timestamp() + (24 * 60 * 60)  # 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

async def log_audit(actor_user_id: str, action: str, target_type: str, target_id: str, meta: Optional[Dict] = None, ip: Optional[str] = None):
    """Log admin actions for audit trail"""
    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        meta=meta or {},
        ip=ip
    )
    
    audit_dict = audit_log.dict()
    audit_dict['created_at'] = audit_dict['created_at'].isoformat()
    
    await db.audit_logs.insert_one(audit_dict)

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
        name=user_data.name,
        password_hash=hash_password(user_data.password)
    )
    
    # Insert user
    user_dict = user.dict()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    await db.users.insert_one(user_dict)
    
    # Create parent record
    parent = Parent(
        user_id=user.id,
        name=user_data.name,
        phone=user_data.phone,
        email=user_data.email,
        branch=user_data.branch,
        household_token=user.household_token
    )
    
    parent_dict = parent.dict()
    parent_dict['created_at'] = parent_dict['created_at'].isoformat()
    await db.parents.insert_one(parent_dict)
    
    # Create student record
    student = Student(
        parent_id=parent.id,
        name=user_data.student_name,
        grade="1"  # Default grade, can be updated later
    )
    
    await db.students.insert_one(student.dict())
    
    # Create admission data
    admission = AdmissionData(household_token=user.household_token)
    admission_dict = admission.dict()
    admission_dict['updated_at'] = admission_dict['updated_at'].isoformat()
    await db.admission_data.insert_one(admission_dict)
    
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
    
    # Check if user is active
    if user.get('status') == 'disabled':
        raise HTTPException(status_code=401, detail="Account is disabled")
    
    # Update last login
    await db.users.update_one(
        {"id": user['id']},
        {"$set": {"last_login_at": datetime.now(timezone.utc).isoformat()}}
    )
    
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
    
    # Get user info for signature
    user = await db.users.find_one({"household_token": token})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get parent info for signature
    parent = await db.parents.find_one({"user_id": user['id']})
    student = await db.students.find_one({"parent_id": parent['id'] if parent else ""})
    
    # Add signature information
    consent_with_signature = consent_data.dict()
    consent_with_signature.update({
        "parent_signature": user['name'],
        "student_name": student['name'] if student else "",
        "signed_at": datetime.now(timezone.utc).isoformat()
    })
    
    update_data = {
        "consent_data": consent_with_signature,
        "consent_status": "completed",
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.admission_data.update_one(
        {"household_token": token},
        {"$set": update_data}
    )
    
    return {"message": "Consent updated successfully", "signature_info": {
        "parent_name": user['name'],
        "student_name": student['name'] if student else "",
        "signed_at": consent_with_signature["signed_at"]
    }}

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

@api_router.post("/exam/reservation")
async def create_exam_reservation(reservation_data: ExamReservationCreate, current_user: UserResponse = Depends(get_current_user)):
    # Create exam reservation record
    reservation = ExamReservation(
        household_token=current_user.household_token,
        user_id=current_user.id,
        brchType=reservation_data.brchType,
        campus=reservation_data.campus,
        slot_id=reservation_data.slot_id,
        slot_start=datetime.fromisoformat(reservation_data.slot_start.replace('Z', '+00:00')),
        slot_end=datetime.fromisoformat(reservation_data.slot_end.replace('Z', '+00:00')),
        level_track=reservation_data.level_track,
        notes=reservation_data.notes
    )
    
    # Save to database
    reservation_dict = reservation.dict()
    reservation_dict['slot_start'] = reservation_dict['slot_start'].isoformat()
    reservation_dict['slot_end'] = reservation_dict['slot_end'].isoformat()
    reservation_dict['created_at'] = reservation_dict['created_at'].isoformat()
    
    await db.exam_reservations.insert_one(reservation_dict)
    
    # TODO: Trigger webhook for Google Sheets logging
    # TODO: Send Kakao AlimTalk notification
    
    return {
        "message": "Exam reservation created successfully",
        "reservation_id": reservation.id,
        "status": reservation.status
    }

@api_router.get("/exam/reservations")
async def get_user_reservations(current_user: UserResponse = Depends(get_current_user)):
    reservations = await db.exam_reservations.find({
        "household_token": current_user.household_token
    }).to_list(100)
    
    return {"reservations": reservations}

@api_router.get("/admin/audit")
async def get_audit_logs(
    current_admin: AdminResponse = Depends(get_current_admin),
    targetId: str = None,
    type: str = None,
    page: int = 1,
    limit: int = 50
):
    query = {}
    if targetId:
        query["target_id"] = targetId
    if type:
        query["action"] = type
    
    skip = (page - 1) * limit
    
    audit_logs = await db.audit_logs.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total_count = await db.audit_logs.count_documents(query)
    
    # Clean audit logs and add actor names
    for log in audit_logs:
        if '_id' in log:
            del log['_id']
        
        actor = await db.admins.find_one({"id": log["actor_user_id"]})
        if actor:
            log["actor_name"] = actor.get("username", "Unknown")
        else:
            log["actor_name"] = "System"
    
    return {
        "audit_logs": audit_logs,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "totalPages": (total_count + limit - 1) // limit
        }
    }

@api_router.get("/exam/available-slots")
async def get_available_exam_slots(brchType: str, campus: str = None):
    # Mock available slots for demo
    # In production, this would query actual availability
    mock_slots = [
        {
            "id": "slot_1",
            "date": "2025-02-10",
            "start_time": "10:00",
            "end_time": "11:30" if brchType == "middle" else "11:00",
            "campus": "강남캠퍼스",
            "available": True,
            "capacity": 12,
            "booked": 3
        },
        {
            "id": "slot_2", 
            "date": "2025-02-10",
            "start_time": "14:00",
            "end_time": "15:30" if brchType == "middle" else "15:00",
            "campus": "강남캠퍼스",
            "available": True,
            "capacity": 12,
            "booked": 7
        },
        {
            "id": "slot_3",
            "date": "2025-02-15",
            "start_time": "10:00", 
            "end_time": "11:30" if brchType == "middle" else "11:00",
            "campus": "서초캠퍼스",
            "available": False,
            "capacity": 8,
            "booked": 8
        }
    ]
    
    if campus:
        mock_slots = [slot for slot in mock_slots if slot["campus"] == campus]
    
    return {"available_slots": mock_slots}

# Admin Routes
@api_router.post("/admin/signup")
async def create_admin(admin_data: AdminCreate):
    # Check if admin already exists
    existing_admin = await db.admins.find_one({"$or": [{"username": admin_data.username}, {"email": admin_data.email}]})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    # Create admin
    admin = Admin(
        username=admin_data.username,
        email=admin_data.email,
        password_hash=hash_password(admin_data.password)
    )
    
    # Insert admin
    await db.admins.insert_one(admin.dict())
    
    # Create JWT token
    token = create_admin_jwt_token(admin.id, admin.username)
    
    return {
        "message": "Admin created successfully",
        "token": token,
        "admin": AdminResponse(**admin.dict())
    }

@api_router.post("/admin/login")
async def admin_login(login_data: AdminLogin):
    admin = await db.admins.find_one({"username": login_data.username})
    if not admin or not verify_password(login_data.password, admin['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    await db.admins.update_one(
        {"id": admin['id']},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    
    token = create_admin_jwt_token(admin['id'], admin['username'])
    
    return {
        "message": "Login successful",
        "token": token,
        "admin": AdminResponse(**admin)
    }

@api_router.get("/admin/profile")
async def get_admin_profile(current_admin: AdminResponse = Depends(get_current_admin)):
    return current_admin

# News Management Routes
@api_router.get("/news")
async def get_news_articles(category: Optional[str] = None, published: bool = True, skip: int = 0, limit: int = 10):
    query = {"published": published} if published else {}
    if category and category != "전체":
        query["category"] = category
    
    articles = await db.news_articles.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"articles": articles}

@api_router.get("/news/{article_id}")
async def get_news_article(article_id: str):
    article = await db.news_articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return NewsResponse(**article)

@api_router.post("/admin/news")
async def create_news_article(article_data: NewsArticleCreate, current_admin: AdminResponse = Depends(get_current_admin)):
    article = NewsArticle(
        **article_data.dict(),
        created_by=current_admin.id
    )
    
    article_dict = article.dict()
    article_dict['created_at'] = article_dict['created_at'].isoformat()
    article_dict['updated_at'] = article_dict['updated_at'].isoformat()
    
    await db.news_articles.insert_one(article_dict)
    
    return {
        "message": "Article created successfully",
        "article_id": article.id
    }

@api_router.put("/admin/news/{article_id}")
async def update_news_article(article_id: str, article_data: NewsArticleUpdate, current_admin: AdminResponse = Depends(get_current_admin)):
    article = await db.news_articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    update_data = {k: v for k, v in article_data.dict().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.news_articles.update_one(
        {"id": article_id},
        {"$set": update_data}
    )
    
    return {"message": "Article updated successfully"}

@api_router.delete("/admin/news/{article_id}")
async def delete_news_article(article_id: str, current_admin: AdminResponse = Depends(get_current_admin)):
    result = await db.news_articles.delete_one({"id": article_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {"message": "Article deleted successfully"}

@api_router.get("/admin/news")
async def get_admin_news_articles(current_admin: AdminResponse = Depends(get_current_admin), category: Optional[str] = None, skip: int = 0, limit: int = 20):
    query = {}
    if category and category != "전체":
        query["category"] = category
    
    articles = await db.news_articles.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total_count = await db.news_articles.count_documents(query)
    
    return {
        "articles": articles,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

# File Upload Routes
@api_router.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...), current_admin: AdminResponse = Depends(get_current_admin)):
    # Check if file is an image
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size (limit to 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / unique_filename
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
    
    # Return the file URL
    file_url = f"/uploads/images/{unique_filename}"
    
    return {
        "message": "Image uploaded successfully",
        "file_url": file_url,
        "filename": unique_filename
    }

@api_router.post("/admin/upload-image-base64")
async def upload_image_base64(file: UploadFile = File(...), current_admin: AdminResponse = Depends(get_current_admin)):
    # Check if file is an image
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file contents
    contents = await file.read()
    
    # Check file size (limit to 5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Convert to base64
    base64_string = base64.b64encode(contents).decode('utf-8')
    data_url = f"data:{file.content_type};base64,{base64_string}"
    
    return {
        "message": "Image converted to base64 successfully",
        "data_url": data_url,
        "filename": file.filename,
        "size": len(contents)
    }

# Admin Member Management Routes
@api_router.get("/admin/members")
async def get_members(
    current_admin: AdminResponse = Depends(get_current_admin),
    query: str = None,
    branch: str = None,
    status: str = None,
    page: int = 1,
    pageSize: int = 50,
    sort: str = "joinedAt:desc"
):
    # Build MongoDB query
    mongo_query = {}
    
    # Text search across multiple fields
    if query:
        mongo_query["$or"] = [
            {"name": {"$regex": query, "$options": "i"}},
            {"phone": {"$regex": query, "$options": "i"}},
            {"email": {"$regex": query, "$options": "i"}}
        ]
    
    # Filter by status
    if status:
        mongo_query["status"] = status
    
    # Build parent query for branch filtering
    parent_query = {}
    if branch:
        parent_query["branch"] = branch
    
    # Parse sort parameter
    sort_field, sort_order = sort.split(":")
    sort_direction = -1 if sort_order == "desc" else 1
    
    # Map sort field names
    sort_mapping = {
        "joinedAt": "created_at",
        "lastLogin": "last_login_at",
        "name": "name"
    }
    sort_field = sort_mapping.get(sort_field, "created_at")
    
    # Calculate skip for pagination
    skip = (page - 1) * pageSize
    
    # Get users with parent information
    try:
        # For now, use simpler approach since aggregation might be complex
        users = await db.users.find(mongo_query).sort(sort_field, sort_direction).skip(skip).limit(pageSize).to_list(pageSize)
        
        members = []
        for user in users:
            # Clean user data
            if '_id' in user:
                del user['_id']
                
            # Get parent info
            parent = await db.parents.find_one({"user_id": user["id"]})
            if not parent:
                continue
                
            # Clean parent data
            if '_id' in parent:
                del parent['_id']
                
            # Apply branch filter
            if branch and parent.get("branch") != branch:
                continue
                
            # Get students
            students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
            
            # Clean student data
            for student in students:
                if '_id' in student:
                    del student['_id']
            
            # Get additional search match for students
            if query:
                student_match = any(
                    query.lower() in student.get("name", "").lower() 
                    for student in students
                )
                user_match = (
                    query.lower() in user.get("name", "").lower() or
                    query.lower() in user.get("phone", "").lower() or
                    query.lower() in user.get("email", "").lower()
                )
                if not (user_match or student_match):
                    continue
            
            member = MemberListResponse(
                id=user["id"],
                parent_name=user.get("name", ""),
                phone=user.get("phone", ""),
                email=user.get("email", ""),
                students=[{"name": s.get("name", ""), "grade": s.get("grade", "")} for s in students],
                branch=parent.get("branch", ""),
                household_token=user.get("household_token", ""),
                joined_at=user.get("created_at"),
                last_login=user.get("last_login_at"),
                status=user.get("status", "active")
            )
            members.append(member)
        
        # Get total count
        total_count = await db.users.count_documents(mongo_query)
        
        return {
            "members": [m.dict() for m in members],
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": total_count,
                "totalPages": (total_count + pageSize - 1) // pageSize
            }
        }
    except Exception as e:
        logging.error(f"Error in get_members: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/admin/members/{user_id}")
async def get_member_details(user_id: str, current_admin: AdminResponse = Depends(get_current_admin)):
    # Get user
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove password_hash and convert ObjectId fields
    if 'password_hash' in user:
        del user['password_hash']
    if '_id' in user:
        del user['_id']
    
    # Get parent info
    parent = await db.parents.find_one({"user_id": user_id})
    if not parent:
        raise HTTPException(status_code=404, detail="Parent info not found")
    
    # Clean parent data
    if '_id' in parent:
        del parent['_id']
    
    # Get students
    students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
    
    # Clean student data
    for student in students:
        if '_id' in student:
            del student['_id']
    
    # Get admission data
    admission_data = await db.admission_data.find_one({"household_token": user['household_token']})
    if admission_data and '_id' in admission_data:
        del admission_data['_id']
    
    # Get exam reservations
    exam_reservations = await db.exam_reservations.find({"household_token": user['household_token']}).to_list(10)
    
    # Clean exam reservation data
    for reservation in exam_reservations:
        if '_id' in reservation:
            del reservation['_id']
    
    return {
        "user": UserResponse(**user),
        "parent": ParentResponse(**parent),
        "students": [StudentResponse(**student) for student in students],
        "admission_data": admission_data,
        "exam_reservations": exam_reservations,
        "consent_status": admission_data.get("consent_status") if admission_data else None,
        "forms_status": admission_data.get("forms_status") if admission_data else None,
        "guides_status": admission_data.get("guides_status") if admission_data else None,
        "checklist_status": admission_data.get("checklist_status") if admission_data else None
    }

@api_router.post("/admin/members/bulk/export")
async def bulk_export_members(user_ids: List[str], current_admin: AdminResponse = Depends(get_current_admin)):
    import csv
    import io
    from datetime import datetime
    
    # Get member data
    members_data = []
    for user_id in user_ids:
        user = await db.users.find_one({"id": user_id})
        if not user:
            continue
            
        parent = await db.parents.find_one({"user_id": user_id})
        students = await db.students.find({"parent_id": parent["id"] if parent else ""}).to_list(10)
        
        members_data.append({
            "Parent Name": user.get("name", ""),
            "Email": user.get("email", ""),
            "Phone": user.get("phone", ""),
            "Branch": parent.get("branch", "") if parent else "",
            "Students": "; ".join([s.get("name", "") for s in students]),
            "Status": user.get("status", "active"),
            "Joined At": user.get("created_at", ""),
            "Last Login": user.get("last_login_at", "")
        })
    
    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Parent Name", "Email", "Phone", "Branch", "Students", "Status", "Joined At", "Last Login"])
    writer.writeheader()
    writer.writerows(members_data)
    
    csv_content = output.getvalue()
    output.close()
    
    # Log audit action
    await log_audit(
        actor_user_id=current_admin.id,
        action="EXPORT",
        target_type="User",
        target_id="bulk",
        meta={"admin_username": current_admin.username, "export_count": len(user_ids)}
    )
    
    return {
        "message": "Export completed successfully",
        "csv_content": csv_content,
        "filename": f"members_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    }

@api_router.post("/admin/members/bulk/notify")
async def bulk_notify_members(request: BulkNotifyRequest, current_admin: AdminResponse = Depends(get_current_admin)):
    # TODO: Implement AlimTalk integration
    # For now, just log the action
    
    # Log audit action
    await log_audit(
        actor_user_id=current_admin.id,
        action="NOTIFY",
        target_type="User",
        target_id="bulk",
        meta={
            "admin_username": current_admin.username,
            "notify_count": len(request.user_ids),
            "message_preview": request.message[:100]
        }
    )
    
    return {
        "message": f"Notification sent to {len(request.user_ids)} members",
        "status": "success"
    }

@api_router.post("/admin/members/{user_id}/reset-password")
async def reset_member_password(user_id: str, current_admin: AdminResponse = Depends(get_current_admin)):
    # Generate a temporary password
    import secrets
    import string
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    hashed_password = hash_password(temp_password)
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"password_hash": hashed_password}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log audit action
    await log_audit(
        actor_user_id=current_admin.id,
        action="RESET_PW",
        target_type="User",
        target_id=user_id,
        meta={"admin_username": current_admin.username}
    )
    
    # TODO: Send email with new password
    
    return {
        "message": "Password reset successfully",
        "temporary_password": temp_password  # In production, this should be sent via email
    }

@api_router.patch("/admin/members/{user_id}/status")
async def update_member_status(user_id: str, status_data: Dict[str, str], current_admin: AdminResponse = Depends(get_current_admin)):
    status = status_data.get("status")
    if status not in ["active", "disabled"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'active' or 'disabled'")
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log audit action
    action = "ENABLE" if status == "active" else "DISABLE"
    await log_audit(
        actor_user_id=current_admin.id,
        action=action,
        target_type="User",
        target_id=user_id,
        meta={"admin_username": current_admin.username, "new_status": status}
    )
    
    return {"message": f"User status updated to {status}"}

# Admin Admission Management Routes
@api_router.get("/admin/admissions")
async def get_admission_overview(current_admin: AdminResponse = Depends(get_current_admin)):
    # Get admission statistics
    total_admissions = await db.admission_data.count_documents({})
    
    consent_completed = await db.admission_data.count_documents({"consent_status": "completed"})
    forms_completed = await db.admission_data.count_documents({"forms_status": "completed"})
    guides_completed = await db.admission_data.count_documents({"guides_status": "completed"})
    checklist_completed = await db.admission_data.count_documents({"checklist_status": "completed"})
    
    # Get recent admissions
    recent_admissions = await db.admission_data.find({}).sort("updated_at", -1).limit(10).to_list(10)
    
    # Add user info to admissions
    for admission in recent_admissions:
        user = await db.users.find_one({"household_token": admission["household_token"]})
        if user:
            admission["user_info"] = {
                "parent_name": user.get("name", ""),
                "email": user.get("email", "")
            }
    
    return {
        "statistics": {
            "total_admissions": total_admissions,
            "consent_completed": consent_completed,
            "forms_completed": forms_completed,
            "guides_completed": guides_completed,
            "checklist_completed": checklist_completed,
            "completion_rate": round((consent_completed / total_admissions * 100) if total_admissions > 0 else 0, 1)
        },
        "recent_admissions": recent_admissions
    }

# Admin Exam Management Routes
@api_router.get("/admin/exam-reservations")
async def get_exam_reservations(current_admin: AdminResponse = Depends(get_current_admin), status: str = None, brchType: str = None):
    query = {}
    if status:
        query["status"] = status
    if brchType:
        query["brchType"] = brchType
    
    reservations = await db.exam_reservations.find(query).sort("created_at", -1).to_list(100)
    
    # Add user info
    for reservation in reservations:
        user = await db.users.find_one({"household_token": reservation["household_token"]})
        if user:
            reservation["user_info"] = {
                "parent_name": user.get("name", ""),
                "email": user.get("email", ""),
                "phone": user.get("phone", "")
            }
    
    return {"reservations": reservations}

@api_router.put("/admin/exam-reservation/{reservation_id}/status")
async def update_reservation_status(reservation_id: str, status: str, current_admin: AdminResponse = Depends(get_current_admin)):
    if status not in ["requested", "confirmed", "cancelled", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.exam_reservations.update_one(
        {"id": reservation_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat(), "updated_by": current_admin.id}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # TODO: Send notification to parent
    
    return {"message": f"Reservation status updated to {status}"}

@api_router.get("/admin/dashboard-stats")
async def get_dashboard_stats(current_admin: AdminResponse = Depends(get_current_admin)):
    # Users stats
    total_users = await db.users.count_documents({})
    users_today = await db.users.count_documents({
        "created_at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()}
    })
    
    # News stats
    total_news = await db.news_articles.count_documents({})
    published_news = await db.news_articles.count_documents({"published": True})
    
    # Exam reservations stats
    total_reservations = await db.exam_reservations.count_documents({})
    pending_reservations = await db.exam_reservations.count_documents({"status": "requested"})
    confirmed_reservations = await db.exam_reservations.count_documents({"status": "confirmed"})
    
    # Admission progress stats
    total_admissions = await db.admission_data.count_documents({})
    completed_admissions = await db.admission_data.count_documents({
        "consent_status": "completed",
        "forms_status": "completed", 
        "guides_status": "completed",
        "checklist_status": "completed"
    })
    
    return {
        "users": {
            "total": total_users,
            "today": users_today,
            "growth": "+12.5%"  # Mock data
        },
        "news": {
            "total": total_news,
            "published": published_news,
            "draft": total_news - published_news
        },
        "exam_reservations": {
            "total": total_reservations,
            "pending": pending_reservations,
            "confirmed": confirmed_reservations
        },
        "admissions": {
            "total": total_admissions,
            "completed": completed_admissions,
            "completion_rate": round((completed_admissions / total_admissions * 100) if total_admissions > 0 else 0, 1)
        }
    }

# Include the router in the main app
app.include_router(api_router)

# Mount static files for uploads
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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