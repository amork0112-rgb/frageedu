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
    branch: str  # kinder, junior, middle
    program_subtype: str = "regular"  # regular, kinder_single, transfer
    requires_exam: bool = True  # False for kinder_regular
    notes: Optional[str] = None

class ClassAssignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    class_id: str
    class_name: str
    teacher_name: str
    teacher_id: Optional[str] = None
    weekday: str  # "Monday,Wednesday,Friday"
    time_start: str  # "16:00"
    time_end: str  # "17:30"
    classroom: str
    level: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, completed, suspended
    materials: List[str] = []
    assigned_by: str  # admin_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExamResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    exam_reservation_id: Optional[str] = None
    score: Optional[int] = None  # 0-100
    level: Optional[str] = None  # Beginner, Elementary, Intermediate, Advanced
    passed: bool = False
    feedback: Optional[str] = None
    recommended_class: Optional[str] = None
    tested_at: datetime
    graded_by: Optional[str] = None  # admin/teacher_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Attendance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    class_assignment_id: str
    date: str  # "2025-08-30"
    status: str  # present, late, absent, excused
    arrival_time: Optional[str] = None  # "16:05"
    notes: Optional[str] = None
    marked_by: Optional[str] = None  # teacher_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Homework(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4))
    class_id: str
    class_assignment_id: str
    title: str
    description: Optional[str] = None
    due_date: datetime
    file_urls: List[str] = []  # Uploaded assignment files
    points: Optional[int] = None  # Total points possible
    created_by: str  # teacher_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HomeworkSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    homework_id: str
    student_id: str
    status: str = "pending"  # pending, submitted, graded, late
    submission_text: Optional[str] = None
    file_urls: List[str] = []
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[str] = None  # teacher_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Billing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    household_token: str
    billing_type: str  # tuition, materials, exam_fee, entrance_fee
    month: str  # "2025-08"
    amount: float
    currency: str = "KRW"
    due_date: datetime
    status: str = "pending"  # pending, paid, overdue, cancelled
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Notice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    notice_type: str  # general, urgent, maintenance, event
    target_audience: str = "all"  # all, branch:kinder, branch:junior, branch:middle
    priority: str = "normal"  # low, normal, high, urgent
    file_urls: List[str] = []
    published: bool = True
    publish_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None
    created_by: str  # admin_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NoticeAcknowledgment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    notice_id: str
    student_id: str
    household_token: str
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Guide(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    guide_type: str  # admission, orientation, curriculum, policy
    target_branch: str = "all"  # all, kinder, junior, middle
    file_url: Optional[str] = None
    content: Optional[str] = None  # Rich text content
    required_reading: bool = False
    order: int = 0  # Display order
    published: bool = True
    created_by: str  # admin_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GuideAcknowledgment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    guide_id: str
    student_id: str
    household_token: str
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_user_id: str
    action: str  # RESET_PW, DISABLE, ENABLE, EXPORT, NOTIFY, ENROLL, ASSIGN_CLASS
    target_type: str  # User, Parent, Student, ClassAssignment
    target_id: str
    meta: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ip: Optional[str] = None

# Frage Market Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str  # uniform, accessories, books, etc.
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    size_options: List[str] = []  # ["S", "M", "L", "XL"] or ["90", "95", "100"]
    color_options: List[str] = []  # ["Navy", "White", "Black"]
    images: List[str] = []  # Image URLs
    stock_quantity: int = 0
    is_available: bool = True
    is_featured: bool = False
    tags: List[str] = []
    specifications: Optional[Dict[str, str]] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    quantity: int
    selected_size: Optional[str] = None
    selected_color: Optional[str] = None
    price_at_time: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    order_number: str = Field(default_factory=lambda: f"FG{int(datetime.now().timestamp())}")
    items: List[Dict[str, Any]]  # Cart items with product details
    total_amount: float
    shipping_address: Dict[str, str]
    contact_info: Dict[str, str]
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
    payment_status: str = "pending"  # pending, paid, failed, refunded
    payment_method: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    name: str  # parent name
    student_name: str
    student_birthdate: str  # Added birthdate field
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

# Enrollment Flow Models
class EnrollmentFlow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    flow_key: str  # kinder_regular, kinder_transfer, junior, middle
    name: str
    description: str
    branch: str  # kinder, junior, middle
    program_type: str  # regular, transfer, single
    steps: List[Dict[str, Any]]  # [{"key": "seminar", "name": "설명회", "order": 1, "required": True}]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudentEnrollmentProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    household_token: str
    flow_key: str  # kinder_regular, kinder_transfer, junior, middle
    current_step: str  # seminar, form, payment, consent, placement
    completed_steps: List[str] = []  # ["seminar", "form"]
    step_data: Dict[str, Any] = {}  # Store data for each step
    status: str = "in_progress"  # in_progress, completed, on_hold
    enrollment_status: str = "new"  # new, consultation, exam_booked, enrolled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FlowEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    household_token: str
    event_type: str  # seminar.completed, form.submitted, payment.paid, consent.agreed, class.assigned
    step_key: str  # seminar, form, payment, consent, placement
    event_data: Dict[str, Any] = {}
    triggered_by: str  # system, admin, parent
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    household_token: str
    payment_type: str  # entrance, tuition, materials
    amount: float
    currency: str = "KRW"
    payment_method: Optional[str] = None
    payment_status: str = "pending"  # pending, paid, failed, refunded
    payment_date: Optional[datetime] = None
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClassPlacement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    class_name: str
    teacher_name: str
    schedule: str  # "Monday/Wednesday 4:00-5:30 PM"
    classroom: str
    level: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, completed, suspended
    assigned_by: str  # admin_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Parent Dashboard Models
# Dashboard Response Models
class StudentInfo(BaseModel):
    id: str
    name: str
    grade: str
    birthdate: Optional[str]
    branch: str
    program_subtype: str
    requires_exam: bool
    program_display: str  # "프라게 킨더 · 정규", "프라게 주니어 · 유치 단과"

class AdmissionProgressCard(BaseModel):
    current_step: str
    completed_steps: List[str]
    total_steps: int
    progress_percentage: float
    status: str
    enrollment_status: str
    next_action: Optional[str]
    flow_name: str

class ExamCard(BaseModel):
    show_card: bool
    has_reservation: bool
    reservation_date: Optional[str]
    reservation_time: Optional[str]
    has_result: bool
    score: Optional[int]
    level: Optional[str]
    passed: Optional[bool]
    next_action: Optional[str]

class TimetableCard(BaseModel):
    show_card: bool
    is_enrolled: bool
    class_name: Optional[str]
    teacher_name: Optional[str]
    schedule: Optional[str]  # "Monday/Wednesday 4:00-5:30 PM"
    classroom: Optional[str]
    level: Optional[str]
    start_date: Optional[str]

class HomeworkCard(BaseModel):
    show_card: bool
    total_assignments: int
    pending_count: int
    overdue_count: int
    recent_assignments: List[Dict[str, Any]]

class AttendanceCard(BaseModel):
    show_card: bool
    total_classes: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_rate: float
    recent_attendance: List[Dict[str, Any]]

class BillingCard(BaseModel):
    pending_payments: List[Dict[str, Any]]
    current_month_amount: Optional[float]
    due_date: Optional[str]
    payment_history_count: int
    overdue_count: int

class NoticesCard(BaseModel):
    unread_count: int
    urgent_count: int
    recent_notices: List[Dict[str, Any]]

class ResourcesCard(BaseModel):
    guides_total: int
    guides_unread: int
    required_guides_pending: int
    consent_pending: bool

class DashboardCardsResponse(BaseModel):
    student_info: StudentInfo
    admission_progress: AdmissionProgressCard
    exam: ExamCard
    timetable: TimetableCard
    homework: HomeworkCard
    attendance: AttendanceCard
    billing: BillingCard
    notices: NoticesCard
    resources: ResourcesCard

class ComprehensiveDashboardResponse(BaseModel):
    parent_info: Dict[str, Any]
    students: List[StudentInfo]  # For dropdown
    current_student: DashboardCardsResponse
    global_notifications: List[Dict[str, Any]]

# Exam Reservation Models
class ExamReservationRequest(BaseModel):
    student_id: str
    exam_date: str  # "2025-09-01"
    exam_time: str  # "14:00"
    branch_type: str
    notes: Optional[str] = None

class ExamReservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    household_token: str
    branch_type: str  # kinder, junior, middle
    exam_date: str
    exam_time: str
    status: str = "scheduled"  # scheduled, completed, cancelled, no_show
    notes: Optional[str] = None
    slot_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models
class HomeworkSubmissionRequest(BaseModel):
    submission_text: Optional[str] = None
    file_urls: List[str] = []

class NoticeAcknowledgmentRequest(BaseModel):
    notice_ids: List[str]

class GuideAcknowledgmentRequest(BaseModel):
    guide_id: str

class TestScheduleResponse(BaseModel):
    id: str
    student_name: str
    branch_type: str  # junior, middle, kinder
    scheduled_date: Optional[datetime]
    scheduled_time: Optional[str]
    location: str
    status: str  # scheduled, completed, cancelled
    notes: Optional[str]

class TestResultResponse(BaseModel):
    id: str
    student_name: str
    test_date: datetime
    score: Optional[int]
    level: Optional[str]
    status: str  # passed, failed, pending
    feedback: Optional[str]
    recommended_class: Optional[str]

class ClassAssignmentResponse(BaseModel):
    id: str
    student_name: str
    class_name: str
    teacher_name: str
    schedule: str  # e.g., "Monday/Wednesday 4:00-5:30 PM"
    classroom: str
    start_date: datetime
    end_date: Optional[datetime]
    status: str  # active, completed, suspended
    materials: List[str]

class ParentDashboardResponse(BaseModel):
    parent_info: Dict[str, Any]
    students: List[Dict[str, Any]]
    test_schedules: List[TestScheduleResponse]
    test_results: List[TestResultResponse]
    class_assignments: List[ClassAssignmentResponse]
    enrollment_status: str  # new, test_scheduled, test_taken, enrolled, active

# Flow Management Request/Response Models
class EnrollmentFlowResponse(BaseModel):
    id: str
    flow_key: str
    name: str
    description: str
    branch: str
    program_type: str
    steps: List[Dict[str, Any]]
    is_active: bool

class ProgressResponse(BaseModel):
    student_id: str
    student_name: str
    flow_key: str
    current_step: str
    completed_steps: List[str]
    total_steps: int
    progress_percentage: float
    status: str
    enrollment_status: str
    next_action: Optional[str]

class FlowEventRequest(BaseModel):
    event_type: str
    step_key: str
    event_data: Dict[str, Any] = {}

class PaymentRequest(BaseModel):
    payment_type: str
    amount: float
    payment_method: str
    reference_id: Optional[str] = None
    notes: Optional[str] = None

class ClassPlacementRequest(BaseModel):
    class_name: str
    teacher_name: str
    schedule: str
    classroom: str
    level: Optional[str] = None
    start_date: str  # ISO string

class DashboardSummaryResponse(BaseModel):
    student_info: Dict[str, Any]
    progress: ProgressResponse
    current_tasks: List[Dict[str, Any]]
    completed_tasks: List[Dict[str, Any]]
    pending_payments: List[Dict[str, Any]]
    class_assignments: List[Dict[str, Any]]
    announcements: List[Dict[str, Any]]

# Frage Market Request/Response Models
class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    subcategory: Optional[str]
    brand: Optional[str]
    size_options: List[str]
    color_options: List[str]
    images: List[str]
    stock_quantity: int
    is_available: bool
    is_featured: bool
    tags: List[str]
    specifications: Optional[Dict[str, str]]

class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = 1
    selected_size: Optional[str] = None
    selected_color: Optional[str] = None

class UpdateCartRequest(BaseModel):
    quantity: int
    selected_size: Optional[str] = None
    selected_color: Optional[str] = None

class CartResponse(BaseModel):
    items: List[Dict[str, Any]]
    total_items: int
    total_amount: float

class CreateOrderRequest(BaseModel):
    shipping_address: Dict[str, str]
    contact_info: Dict[str, str]
    payment_method: str
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    order_number: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime

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

# Flow Management Utility Functions
async def initialize_default_flows():
    """Initialize default enrollment flows"""
    default_flows = [
        {
            "flow_key": "kinder_regular",
            "name": "정규 킨더 정규입학",
            "description": "설명회 → 입학원서 → 입학금 납부 → 동의서/신청서 → 반배정",
            "branch": "kinder",
            "program_type": "regular",
            "steps": [
                {"key": "seminar", "name": "설명회", "order": 1, "required": True, "description": "입학 설명회 참석"},
                {"key": "form", "name": "입학원서", "order": 2, "required": True, "description": "입학원서 작성 및 제출"},
                {"key": "entrance_payment", "name": "입학금 납부", "order": 3, "required": True, "description": "입학금 납부"},
                {"key": "consent", "name": "동의서/신청서", "order": 4, "required": True, "description": "각종 동의서 및 신청서 작성"},
                {"key": "placement", "name": "반배정", "order": 5, "required": True, "description": "반 배정 완료"}
            ]
        },
        {
            "flow_key": "kinder_transfer",
            "name": "정규 킨더 편입",
            "description": "상담/테스트 → 입학원서 → 입학금 납부 → 동의서/신청서 → 반배정",
            "branch": "kinder",
            "program_type": "transfer",
            "steps": [
                {"key": "consultation", "name": "상담/테스트", "order": 1, "required": True, "description": "개별 상담 및 레벨 테스트"},
                {"key": "form", "name": "입학원서", "order": 2, "required": True, "description": "입학원서 작성 및 제출"},
                {"key": "entrance_payment", "name": "입학금 납부", "order": 3, "required": True, "description": "입학금 납부"},
                {"key": "consent", "name": "동의서/신청서", "order": 4, "required": True, "description": "각종 동의서 및 신청서 작성"},
                {"key": "placement", "name": "반배정", "order": 5, "required": True, "description": "반 배정 완료"}
            ]
        },
        {
            "flow_key": "junior",
            "name": "프라게 주니어",
            "description": "상담/테스트 → 반배정 → 수업료 납부 → 동의서/신청서 → 입학",
            "branch": "junior",
            "program_type": "regular",
            "steps": [
                {"key": "consultation", "name": "상담/테스트", "order": 1, "required": True, "description": "개별 상담 및 레벨 테스트"},
                {"key": "placement", "name": "반배정", "order": 2, "required": True, "description": "반 배정"},
                {"key": "tuition_payment", "name": "수업료 납부", "order": 3, "required": True, "description": "수업료 납부"},
                {"key": "consent", "name": "동의서/신청서", "order": 4, "required": True, "description": "각종 동의서 및 신청서 작성"},
                {"key": "enrollment", "name": "입학 완료", "order": 5, "required": True, "description": "입학 절차 완료"}
            ]
        },
        {
            "flow_key": "middle",
            "name": "프라디스 중등",
            "description": "상담/테스트 → 반배정 → 수업료 납부 → 동의서/신청서 → 입학",
            "branch": "middle",
            "program_type": "regular",
            "steps": [
                {"key": "consultation", "name": "상담/테스트", "order": 1, "required": True, "description": "개별 상담 및 레벨 테스트"},
                {"key": "placement", "name": "반배정", "order": 2, "required": True, "description": "반 배정"},
                {"key": "tuition_payment", "name": "수업료 납부", "order": 3, "required": True, "description": "수업료 납부"},
                {"key": "consent", "name": "동의서/신청서", "order": 4, "required": True, "description": "각종 동의서 및 신청서 작성"},
                {"key": "enrollment", "name": "입학 완료", "order": 5, "required": True, "description": "입학 절차 완료"}
            ]
        },
        {
            "flow_key": "junior_single",
            "name": "유치 단과",
            "description": "상담/테스트 → 반배정 → 수업료 납부 → 동의서/신청서 → 입학",
            "branch": "junior",
            "program_type": "single",
            "steps": [
                {"key": "consultation", "name": "상담/테스트", "order": 1, "required": True, "description": "개별 상담 및 레벨 테스트"},
                {"key": "placement", "name": "반배정", "order": 2, "required": True, "description": "반 배정"},
                {"key": "tuition_payment", "name": "수업료 납부", "order": 3, "required": True, "description": "수업료 납부"},
                {"key": "consent", "name": "동의서/신청서", "order": 4, "required": True, "description": "각종 동의서 및 신청서 작성"},
                {"key": "enrollment", "name": "입학 완료", "order": 5, "required": True, "description": "입학 절차 완료"}
            ]
        }
    ]
    
    # Check if flows already exist
    existing_flows = await db.enrollment_flows.count_documents({})
    if existing_flows > 0:
        return f"{existing_flows} flows already exist"
    
    # Insert flows
    for flow_data in default_flows:
        flow = EnrollmentFlow(**flow_data)
        flow_dict = flow.dict()
        flow_dict['created_at'] = flow_dict['created_at'].isoformat()
        flow_dict['updated_at'] = flow_dict['updated_at'].isoformat()
        await db.enrollment_flows.insert_one(flow_dict)
    
    return f"Successfully created {len(default_flows)} default flows"

async def get_student_progress(student_id: str) -> Optional[ProgressResponse]:
    """Get current progress for a student"""
    progress = await db.student_enrollment_progress.find_one({"student_id": student_id})
    if not progress:
        return None
    
    # Get flow definition
    flow = await db.enrollment_flows.find_one({"flow_key": progress["flow_key"]})
    if not flow:
        return None
    
    # Get student info
    student = await db.students.find_one({"id": student_id})
    student_name = student["name"] if student else "Unknown"
    
    total_steps = len(flow["steps"])
    completed_count = len(progress["completed_steps"])
    progress_percentage = (completed_count / total_steps) * 100 if total_steps > 0 else 0
    
    # Determine next action
    next_action = None
    if progress["current_step"] and progress["current_step"] not in progress["completed_steps"]:
        current_step_info = next((s for s in flow["steps"] if s["key"] == progress["current_step"]), None)
        if current_step_info:
            next_action = f"Complete: {current_step_info['name']}"
    
    return ProgressResponse(
        student_id=student_id,
        student_name=student_name,
        flow_key=progress["flow_key"],
        current_step=progress["current_step"],
        completed_steps=progress["completed_steps"],
        total_steps=total_steps,
        progress_percentage=progress_percentage,
        status=progress["status"],
        enrollment_status=progress["enrollment_status"],
        next_action=next_action
    )

async def trigger_flow_event(student_id: str, event_type: str, step_key: str, event_data: Dict = None, triggered_by: str = "system"):
    """Trigger a flow event and update progress"""
    try:
        # Get student and progress
        student = await db.students.find_one({"id": student_id})
        if not student:
            return {"error": "Student not found"}
        
        progress = await db.student_enrollment_progress.find_one({"student_id": student_id})
        if not progress:
            return {"error": "Progress record not found"}
        
        # Log the event
        event = FlowEvent(
            student_id=student_id,
            household_token=progress["household_token"],
            event_type=event_type,
            step_key=step_key,
            event_data=event_data or {},
            triggered_by=triggered_by
        )
        
        event_dict = event.dict()
        event_dict['created_at'] = event_dict['created_at'].isoformat()
        await db.flow_events.insert_one(event_dict)
        
        # Update progress based on event
        await update_progress_from_event(student_id, event_type, step_key, event_data)
        
        return {"success": True, "event_id": event.id}
        
    except Exception as e:
        return {"error": str(e)}

async def update_progress_from_event(student_id: str, event_type: str, step_key: str, event_data: Dict = None):
    """Update student progress based on triggered event"""
    progress = await db.student_enrollment_progress.find_one({"student_id": student_id})
    if not progress:
        return
    
    flow = await db.enrollment_flows.find_one({"flow_key": progress["flow_key"]})
    if not flow:
        return
    
    # Get flow steps ordered
    steps = sorted(flow["steps"], key=lambda x: x["order"])
    step_keys = [s["key"] for s in steps]
    
    updates = {
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Handle different event types
    if event_type.endswith(".completed"):
        # Mark step as completed
        if step_key not in progress["completed_steps"]:
            updates["$addToSet"] = {"completed_steps": step_key}
        
        # Update step data
        step_data = progress.get("step_data", {})
        step_data[step_key] = event_data or {}
        updates["step_data"] = step_data
        
        # Move to next step
        try:
            current_index = step_keys.index(step_key)
            if current_index + 1 < len(step_keys):
                updates["current_step"] = step_keys[current_index + 1]
            else:
                # All steps completed
                updates["status"] = "completed"
                updates["enrollment_status"] = "enrolled"
        except ValueError:
            pass
    
    elif event_type.startswith("payment.paid"):
        # Handle payment events
        if step_key in ["entrance_payment", "tuition_payment"]:
            if step_key not in progress["completed_steps"]:
                updates["$addToSet"] = {"completed_steps": step_key}
            
            # Update enrollment status
            if step_key == "entrance_payment":
                updates["enrollment_status"] = "payment_completed"
            elif step_key == "tuition_payment":
                updates["enrollment_status"] = "tuition_paid"
    
    elif event_type.startswith("class.assigned"):
        # Handle class placement
        if step_key == "placement":
            if step_key not in progress["completed_steps"]:
                updates["$addToSet"] = {"completed_steps": step_key}
            updates["enrollment_status"] = "enrolled"
    
    # Apply updates
    if "$addToSet" in updates:
        addToSet = updates.pop("$addToSet")
        await db.student_enrollment_progress.update_one(
            {"student_id": student_id},
            {"$set": updates, "$addToSet": addToSet}
        )
    else:
        await db.student_enrollment_progress.update_one(
            {"student_id": student_id},
            {"$set": updates}
        )

async def send_alimtalk_notification(student_id: str, template_type: str, data: Dict = None):
    """Send AlimTalk notification (placeholder for integration)"""
    # TODO: Integrate with Solapi AlimTalk API
    # For now, just log the notification
    
    student = await db.students.find_one({"id": student_id})
    if not student:
        return
    
    parent = await db.parents.find_one({"id": student["parent_id"]})
    if not parent:
        return
    
    notification_log = {
        "student_id": student_id,
        "parent_phone": parent.get("phone", ""),
        "template_type": template_type,
        "data": data or {},
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.notification_logs.insert_one(notification_log)
    
    print(f"AlimTalk notification queued: {template_type} to {parent.get('phone', 'N/A')} for student {student['name']}")

# Routes
@api_router.get("/")
async def root():
    return {"message": "Frage EDU API", "version": "1.0"}

# Enrollment Flow Management Routes
@api_router.post("/admin/init-flows")
async def init_enrollment_flows(current_admin: AdminResponse = Depends(get_current_admin)):
    """Initialize default enrollment flows"""
    try:
        result = await initialize_default_flows()
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing flows: {str(e)}")

@api_router.get("/admin/flows")
async def get_enrollment_flows(current_admin: AdminResponse = Depends(get_current_admin)):
    """Get all enrollment flows"""
    try:
        flows = await db.enrollment_flows.find({"is_active": True}).to_list(100)
        
        # Clean flows
        for flow in flows:
            if '_id' in flow:
                del flow['_id']
        
        return {"flows": [EnrollmentFlowResponse(**flow) for flow in flows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flows: {str(e)}")

@api_router.get("/flows/{flow_key}")
async def get_flow_by_key(flow_key: str):
    """Get specific enrollment flow"""
    try:
        flow = await db.enrollment_flows.find_one({"flow_key": flow_key, "is_active": True})
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        if '_id' in flow:
            del flow['_id']
        
        return EnrollmentFlowResponse(**flow)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching flow: {str(e)}")

@api_router.post("/admin/students/{student_id}/progress/init")
async def init_student_progress(
    student_id: str, 
    flow_key: str,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Initialize progress tracking for a student"""
    try:
        # Check if student exists
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get parent info for household_token
        parent = await db.parents.find_one({"id": student["parent_id"]})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")
        
        # Check if flow exists
        flow = await db.enrollment_flows.find_one({"flow_key": flow_key, "is_active": True})
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        # Check if progress already exists
        existing_progress = await db.student_enrollment_progress.find_one({"student_id": student_id})
        if existing_progress:
            raise HTTPException(status_code=400, detail="Progress already initialized")
        
        # Get first step
        first_step = min(flow["steps"], key=lambda x: x["order"])
        
        # Create progress record
        progress = StudentEnrollmentProgress(
            student_id=student_id,
            household_token=parent["household_token"],
            flow_key=flow_key,
            current_step=first_step["key"]
        )
        
        progress_dict = progress.dict()
        progress_dict['created_at'] = progress_dict['created_at'].isoformat()
        progress_dict['updated_at'] = progress_dict['updated_at'].isoformat()
        
        await db.student_enrollment_progress.insert_one(progress_dict)
        
        return {"message": "Progress initialized successfully", "progress_id": progress.id}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error initializing progress: {str(e)}")

@api_router.get("/parent/dashboard/enhanced")
async def get_enhanced_dashboard(
    studentId: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get enhanced parent dashboard with flow progress"""
    try:
        # Get parent info
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        # Get students
        students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        
        # If specific student requested, filter
        if studentId:
            students = [s for s in students if s["id"] == studentId]
            if not students:
                raise HTTPException(status_code=404, detail="Student not found")
        
        # Get progress for each student
        dashboard_data = []
        
        for student in students:
            # Get progress
            progress_response = await get_student_progress(student["id"])
            
            # Get current tasks (incomplete steps)
            current_tasks = []
            completed_tasks = []
            
            if progress_response:
                flow = await db.enrollment_flows.find_one({"flow_key": progress_response.flow_key})
                if flow:
                    for step in flow["steps"]:
                        task_info = {
                            "key": step["key"],
                            "name": step["name"],
                            "description": step.get("description", ""),
                            "order": step["order"],
                            "required": step.get("required", True)
                        }
                        
                        if step["key"] in progress_response.completed_steps:
                            completed_tasks.append(task_info)
                        elif step["key"] == progress_response.current_step:
                            task_info["is_current"] = True
                            current_tasks.append(task_info)
                        else:
                            current_tasks.append(task_info)
            
            # Get pending payments
            pending_payments = await db.payment_records.find({
                "student_id": student["id"],
                "payment_status": "pending"
            }).to_list(10)
            
            # Get class assignments
            class_assignments = await db.class_placements.find({
                "student_id": student["id"],
                "status": "active"
            }).to_list(10)
            
            # Clean data
            for payment in pending_payments:
                if '_id' in payment:
                    del payment['_id']
            
            for assignment in class_assignments:
                if '_id' in assignment:
                    del assignment['_id']
            
            student_dashboard = DashboardSummaryResponse(
                student_info={
                    "id": student["id"],
                    "name": student["name"],
                    "grade": student.get("grade", ""),
                    "birthdate": student.get("birthdate", "")
                },
                progress=progress_response if progress_response else ProgressResponse(
                    student_id=student["id"],
                    student_name=student["name"],
                    flow_key="",
                    current_step="",
                    completed_steps=[],
                    total_steps=0,
                    progress_percentage=0,
                    status="not_started",
                    enrollment_status="new"
                ),
                current_tasks=current_tasks,
                completed_tasks=completed_tasks,
                pending_payments=pending_payments,
                class_assignments=class_assignments,
                announcements=[]  # TODO: Add announcements
            )
            
            dashboard_data.append(student_dashboard)
        
        # If single student requested, return single object
        if studentId and len(dashboard_data) == 1:
            return dashboard_data[0]
        
        return {
            "parent_info": {
                "name": current_user.name,
                "email": current_user.email,
                "phone": current_user.phone,
                "branch": parent.get("branch", ""),
                "household_token": current_user.household_token
            },
            "students": dashboard_data
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard: {str(e)}")

@api_router.post("/parent/flow-event")
async def trigger_parent_flow_event(
    event_request: FlowEventRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Trigger a flow event from parent dashboard"""
    try:
        # Get parent and students
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        
        # For now, apply to first student (can be extended for multi-student)
        student = students[0]
        
        result = await trigger_flow_event(
            student["id"], 
            event_request.event_type, 
            event_request.step_key, 
            event_request.event_data,
            f"parent:{current_user.id}"
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {"message": "Event triggered successfully", "event_id": result["event_id"]}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error triggering event: {str(e)}")

@api_router.post("/admin/students/{student_id}/trigger-event")
async def admin_trigger_flow_event(
    student_id: str,
    event_request: FlowEventRequest,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Trigger a flow event from admin dashboard"""
    try:
        result = await trigger_flow_event(
            student_id, 
            event_request.event_type, 
            event_request.step_key, 
            event_request.event_data,
            f"admin:{current_admin.id}"
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Log admin action
        await log_audit(
            current_admin.id,
            f"TRIGGER_EVENT:{event_request.event_type}",
            "Student",
            student_id,
            event_request.event_data
        )
        
        return {"message": "Event triggered successfully", "event_id": result["event_id"]}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error triggering event: {str(e)}")

@api_router.get("/admin/students/{student_id}/progress")
async def get_student_progress_admin(
    student_id: str,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Get student progress (admin view)"""
    try:
        progress_response = await get_student_progress(student_id)
        if not progress_response:
            raise HTTPException(status_code=404, detail="Progress not found")
        
        # Get flow events history
        events = await db.flow_events.find({"student_id": student_id}).sort("created_at", -1).limit(50).to_list(50)
        
        # Clean events
        for event in events:
            if '_id' in event:
                del event['_id']
        
        return {
            "progress": progress_response,
            "events": events
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

@api_router.get("/admin/progress-report")
async def get_progress_report(
    current_admin: AdminResponse = Depends(get_current_admin),
    branch: Optional[str] = None,
    flow_key: Optional[str] = None,
    status: Optional[str] = None,
    enrollment_status: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    """Get progress report with filtering (admin view)"""
    try:
        # Build query
        query = {}
        if branch or flow_key or status or enrollment_status:
            if flow_key:
                query["flow_key"] = flow_key
            if status:
                query["status"] = status
            if enrollment_status:
                query["enrollment_status"] = enrollment_status
            
            # For branch filtering, we need to join with students/parents
            if branch:
                # Get students in the branch first
                parents_in_branch = await db.parents.find({"branch": branch}).to_list(1000)
                parent_ids = [p["id"] for p in parents_in_branch]
                students_in_branch = await db.students.find({"parent_id": {"$in": parent_ids}}).to_list(1000)
                student_ids = [s["id"] for s in students_in_branch]
                query["student_id"] = {"$in": student_ids}
        
        # Get progress records
        skip = (page - 1) * limit
        progress_records = await db.student_enrollment_progress.find(query).skip(skip).limit(limit).to_list(limit)
        total_count = await db.student_enrollment_progress.count_documents(query)
        
        # Enrich with student and parent info
        enriched_records = []
        for record in progress_records:
            if '_id' in record:
                del record['_id']
            
            # Get student info
            student = await db.students.find_one({"id": record["student_id"]})
            if student:
                if '_id' in student:
                    del student['_id']
                record["student_info"] = student
                
                # Get parent info
                parent = await db.parents.find_one({"id": student["parent_id"]})
                if parent:
                    if '_id' in parent:
                        del parent['_id']
                    record["parent_info"] = parent
            
            # Get flow info
            flow = await db.enrollment_flows.find_one({"flow_key": record["flow_key"]})
            if flow:
                if '_id' in flow:
                    del flow['_id']
                record["flow_info"] = {
                    "name": flow["name"],
                    "description": flow["description"],
                    "total_steps": len(flow["steps"])
                }
            
            enriched_records.append(record)
        
        # Calculate summary statistics
        all_records = await db.student_enrollment_progress.find({}).to_list(10000)
        stats = {
            "total_students": len(all_records),
            "by_status": {},
            "by_enrollment_status": {},
            "by_flow": {}
        }
        
        for record in all_records:
            # Count by status
            status = record.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by enrollment status
            enrollment_status = record.get("enrollment_status", "unknown")
            stats["by_enrollment_status"][enrollment_status] = stats["by_enrollment_status"].get(enrollment_status, 0) + 1
            
            # Count by flow
            flow_key = record.get("flow_key", "unknown")
            stats["by_flow"][flow_key] = stats["by_flow"].get(flow_key, 0) + 1
        
        return {
            "records": enriched_records,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit
            },
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress report: {str(e)}")

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
    user_dict['last_login_at'] = None  # Set to None initially
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
    
    # Create student record with birthdate
    student = Student(
        parent_id=parent.id,
        name=user_data.student_name,
        grade="1",  # Default grade, can be updated later
        birthdate=user_data.student_birthdate  # Add birthdate
    )
    
    await db.students.insert_one(student.dict())
    
    # Create admission data (legacy)
    admission = AdmissionData(household_token=user.household_token)
    admission_dict = admission.dict()
    admission_dict['updated_at'] = admission_dict['updated_at'].isoformat()
    await db.admission_data.insert_one(admission_dict)
    
    # Determine flow key based on branch
    flow_key_mapping = {
        "kinder": "kinder_regular",  # Default to regular, can be changed by admin
        "junior": "junior",
        "middle": "middle"
    }
    
    flow_key = flow_key_mapping.get(user_data.branch, "junior")
    
    # Initialize enrollment progress
    try:
        # Check if flow exists
        flow = await db.enrollment_flows.find_one({"flow_key": flow_key, "is_active": True})
        if flow:
            # Get first step
            first_step = min(flow["steps"], key=lambda x: x["order"])
            
            # Create progress record
            progress = StudentEnrollmentProgress(
                student_id=student.id,
                household_token=user.household_token,
                flow_key=flow_key,
                current_step=first_step["key"]
            )
            
            progress_dict = progress.dict()
            progress_dict['created_at'] = progress_dict['created_at'].isoformat()
            progress_dict['updated_at'] = progress_dict['updated_at'].isoformat()
            
            await db.student_enrollment_progress.insert_one(progress_dict)
    except Exception as e:
        # Don't fail signup if progress init fails, just log it
        print(f"Warning: Failed to initialize progress for student {student.id}: {str(e)}")
    
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

@api_router.get("/parent/dashboard")
async def get_parent_dashboard(current_user: UserResponse = Depends(get_current_user)):
    """Get comprehensive parent dashboard data"""
    try:
        # Get parent info
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        # Get students
        students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
        
        # Get admission data
        admission_data = await db.admission_data.find_one({"household_token": current_user.household_token})
        
        # Get exam reservations
        exam_reservations = await db.exam_reservations.find({"household_token": current_user.household_token}).to_list(10)
        
        # Determine enrollment status
        enrollment_status = "new"
        if exam_reservations:
            latest_reservation = max(exam_reservations, key=lambda x: x.get("created_at", ""))
            if latest_reservation.get("status") == "confirmed":
                enrollment_status = "test_scheduled"
            elif latest_reservation.get("status") == "completed":
                enrollment_status = "test_taken"
        
        # Check if enrolled in classes (mock data for now)
        # In production, this would check actual class enrollments
        if admission_data and admission_data.get("consent_status") == "completed" and admission_data.get("forms_status") == "completed":
            enrollment_status = "enrolled"
        
        # Note: Test schedules are now handled through the new dashboard cards system
        
        # Mock test results (in production, fetch from test_results table)
        test_results = []
        if enrollment_status in ["test_taken", "enrolled"]:
            for student in students:
                test_result = TestResultResponse(
                    id=f"result_{student.get('id', '')}",
                    student_name=student.get("name", ""),
                    test_date=datetime.now(timezone.utc),
                    score=85,  # Mock score
                    level="Intermediate",
                    status="passed",
                    feedback="Great potential! Recommended for regular classes.",
                    recommended_class=f"{parent.get('branch', 'Junior')} English A1"
                )
                test_results.append(test_result)
        
        # Mock class assignments (in production, fetch from class_enrollments table)
        class_assignments = []
        if enrollment_status == "enrolled":
            for student in students:
                class_assignment = ClassAssignmentResponse(
                    id=f"class_{student.get('id', '')}",
                    student_name=student.get("name", ""),
                    class_name=f"{parent.get('branch', 'Junior').title()} English A1",
                    teacher_name="Ms. Sarah Kim",
                    schedule="Monday/Wednesday 4:00-5:30 PM",
                    classroom="Room 201",
                    start_date=datetime.now(timezone.utc),
                    end_date=None,
                    status="active",
                    materials=["Student Workbook", "Online Platform Access", "Reading Materials"]
                )
                class_assignments.append(class_assignment)
        
        return ParentDashboardResponse(
            parent_info={
                "name": current_user.name,
                "email": current_user.email,
                "phone": current_user.phone,
                "branch": parent.get("branch", ""),
                "household_token": current_user.household_token
            },
            students=[{
                "id": s.get("id", ""),
                "name": s.get("name", ""),
                "grade": s.get("grade", ""),
                "birthdate": s.get("birthdate", "")
            } for s in students],
            test_results=test_results,
            class_assignments=class_assignments,
            enrollment_status=enrollment_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

@api_router.get("/parent/test-schedule")
async def get_test_schedule(current_user: UserResponse = Depends(get_current_user)):
    """Get test schedule for current user's child"""
    try:
        exam_reservations = await db.exam_reservations.find({
            "household_token": current_user.household_token
        }).to_list(10)
        
        # Get student info
        parent = await db.parents.find_one({"user_id": current_user.id})
        students = await db.students.find({"parent_id": parent["id"] if parent else ""}).to_list(10)
        student_name = students[0].get("name", "") if students else ""
        
        schedules = []
        for reservation in exam_reservations:
            schedule = {
                "id": reservation.get("id", ""),
                "student_name": student_name,
                "branch_type": reservation.get("brchType", ""),
                "date": reservation.get("slot_start", ""),
                "time": f"{reservation.get('slot_start', '')} - {reservation.get('slot_end', '')}",
                "location": reservation.get("campus", "Frage EDU Campus"),
                "status": reservation.get("status", "requested"),
                "notes": reservation.get("notes", "")
            }
            schedules.append(schedule)
        
        return {"test_schedules": schedules}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching test schedule: {str(e)}")

@api_router.get("/parent/test-results") 
async def get_test_results(current_user: UserResponse = Depends(get_current_user)):
    """Get test results for current user's child"""
    try:
        # Mock test results for now
        # In production, this would fetch from a test_results table
        parent = await db.parents.find_one({"user_id": current_user.id})
        students = await db.students.find({"parent_id": parent["id"] if parent else ""}).to_list(10)
        
        results = []
        for student in students:
            # Check if student has taken test (has exam reservation with completed status)
            exam_reservations = await db.exam_reservations.find({
                "household_token": current_user.household_token,
                "status": {"$in": ["completed", "confirmed"]}
            }).to_list(10)
            
            if exam_reservations:
                result = {
                    "id": f"result_{student.get('id', '')}",
                    "student_name": student.get("name", ""),
                    "test_date": datetime.now(timezone.utc).isoformat(),
                    "score": 85,  # Mock score
                    "level": "Intermediate",
                    "status": "passed",
                    "feedback": "Excellent performance! Your child shows great potential in English communication.",
                    "recommended_class": f"{parent.get('branch', 'Junior').title()} English A1"
                }
                results.append(result)
        
        return {"test_results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching test results: {str(e)}")

@api_router.get("/parent/class-assignments")
async def get_class_assignments(current_user: UserResponse = Depends(get_current_user)):
    """Get class assignments for enrolled students"""
    try:
        # Mock class assignments for now
        # In production, this would fetch from class_enrollments table
        parent = await db.parents.find_one({"user_id": current_user.id})
        students = await db.students.find({"parent_id": parent["id"] if parent else ""}).to_list(10)
        
        # Check if student is enrolled (completed admission process)
        admission_data = await db.admission_data.find_one({"household_token": current_user.household_token})
        is_enrolled = (
            admission_data and 
            admission_data.get("consent_status") == "completed" and 
            admission_data.get("forms_status") == "completed"
        )
        
        assignments = []
        if is_enrolled:
            for student in students:
                assignment = {
                    "id": f"class_{student.get('id', '')}",
                    "student_name": student.get("name", ""),
                    "class_name": f"{parent.get('branch', 'Junior').title()} English A1",
                    "teacher_name": "Ms. Sarah Kim",
                    "schedule": "Monday/Wednesday 4:00-5:30 PM",
                    "classroom": "Room 201",
                    "start_date": datetime.now(timezone.utc).isoformat(),
                    "status": "active",
                    "materials": [
                        "Student Workbook Level A1",
                        "Online Platform Access",
                        "Weekly Reading Materials",
                        "Homework Assignments"
                    ]
                }
                assignments.append(assignment)
        
        return {"class_assignments": assignments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching class assignments: {str(e)}")

# Frage Market API Routes
@api_router.get("/market/products")
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get products with filtering and pagination"""
    try:
        # Build query
        query = {"is_available": True}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search]}}
            ]
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Sort configuration
        sort_direction = -1 if sort_order == "desc" else 1
        
        # Get products
        products = await db.products.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit).to_list(limit)
        total_count = await db.products.count_documents(query)
        
        # Clean products
        for product in products:
            if '_id' in product:
                del product['_id']
        
        return {
            "products": [ProductResponse(**product) for product in products],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@api_router.get("/market/products/{product_id}")
async def get_product(product_id: str):
    """Get single product details"""
    try:
        product = await db.products.find_one({"id": product_id, "is_available": True})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if '_id' in product:
            del product['_id']
        
        return ProductResponse(**product)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

@api_router.get("/market/categories")
async def get_categories():
    """Get available product categories"""
    try:
        categories = await db.products.distinct("category", {"is_available": True})
        
        # Get category counts
        category_counts = {}
        for category in categories:
            count = await db.products.count_documents({"category": category, "is_available": True})
            category_counts[category] = count
        
        return {
            "categories": [
                {"name": cat, "count": category_counts[cat]} 
                for cat in categories
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@api_router.get("/market/featured")
async def get_featured_products(limit: int = 8):
    """Get featured products"""
    try:
        products = await db.products.find({
            "is_available": True, 
            "is_featured": True
        }).limit(limit).to_list(limit)
        
        # Clean products
        for product in products:
            if '_id' in product:
                del product['_id']
        
        return {"products": [ProductResponse(**product) for product in products]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching featured products: {str(e)}")

@api_router.post("/market/cart/add")
async def add_to_cart(cart_request: AddToCartRequest, current_user: UserResponse = Depends(get_current_user)):
    """Add item to cart"""
    try:
        # Check if product exists and is available
        product = await db.products.find_one({"id": cart_request.product_id, "is_available": True})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if item already exists in cart
        existing_item = await db.cart_items.find_one({
            "user_id": current_user.id,
            "product_id": cart_request.product_id,
            "selected_size": cart_request.selected_size,
            "selected_color": cart_request.selected_color
        })
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item["quantity"] + cart_request.quantity
            await db.cart_items.update_one(
                {"id": existing_item["id"]},
                {"$set": {"quantity": new_quantity}}
            )
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=cart_request.product_id,
                quantity=cart_request.quantity,
                selected_size=cart_request.selected_size,
                selected_color=cart_request.selected_color,
                price_at_time=product["price"]
            )
            
            cart_dict = cart_item.dict()
            cart_dict['created_at'] = cart_dict['created_at'].isoformat()
            await db.cart_items.insert_one(cart_dict)
        
        return {"message": "Item added to cart successfully"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error adding to cart: {str(e)}")

@api_router.get("/market/cart")
async def get_cart(current_user: UserResponse = Depends(get_current_user)):
    """Get user's cart"""
    try:
        cart_items = await db.cart_items.find({"user_id": current_user.id}).to_list(100)
        
        items = []
        total_amount = 0
        total_items = 0
        
        for cart_item in cart_items:
            # Get product details
            product = await db.products.find_one({"id": cart_item["product_id"]})
            if product and product.get("is_available", True):
                item_total = cart_item["price_at_time"] * cart_item["quantity"]
                total_amount += item_total
                total_items += cart_item["quantity"]
                
                items.append({
                    "cart_item_id": cart_item["id"],
                    "product": ProductResponse(**{k: v for k, v in product.items() if k != '_id'}),
                    "quantity": cart_item["quantity"],
                    "selected_size": cart_item.get("selected_size"),
                    "selected_color": cart_item.get("selected_color"),
                    "price_at_time": cart_item["price_at_time"],
                    "item_total": item_total
                })
        
        return CartResponse(
            items=items,
            total_items=total_items,
            total_amount=total_amount
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cart: {str(e)}")

@api_router.delete("/market/cart/{cart_item_id}")
async def remove_from_cart(cart_item_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Remove item from cart"""
    try:
        result = await db.cart_items.delete_one({
            "id": cart_item_id,
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        return {"message": "Item removed from cart"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error removing from cart: {str(e)}")

@api_router.post("/market/orders")
async def create_order(order_request: CreateOrderRequest, current_user: UserResponse = Depends(get_current_user)):
    """Create order from cart"""
    try:
        # Get cart items
        cart_items = await db.cart_items.find({"user_id": current_user.id}).to_list(100)
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Prepare order items
        order_items = []
        total_amount = 0
        
        for cart_item in cart_items:
            product = await db.products.find_one({"id": cart_item["product_id"]})
            if product and product.get("is_available", True):
                item_total = cart_item["price_at_time"] * cart_item["quantity"]
                total_amount += item_total
                
                order_items.append({
                    "product_id": cart_item["product_id"],
                    "product_name": product["name"],
                    "quantity": cart_item["quantity"],
                    "selected_size": cart_item.get("selected_size"),
                    "selected_color": cart_item.get("selected_color"),
                    "price_at_time": cart_item["price_at_time"],
                    "item_total": item_total
                })
        
        # Create order
        order = Order(
            user_id=current_user.id,
            items=order_items,
            total_amount=total_amount,
            shipping_address=order_request.shipping_address,
            contact_info=order_request.contact_info,
            payment_method=order_request.payment_method,
            notes=order_request.notes
        )
        
        order_dict = order.dict()
        order_dict['created_at'] = order_dict['created_at'].isoformat()
        order_dict['updated_at'] = order_dict['updated_at'].isoformat()
        await db.orders.insert_one(order_dict)
        
        # Clear cart
        await db.cart_items.delete_many({"user_id": current_user.id})
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            items=order_items,
            total_amount=total_amount,
            status=order.status,
            payment_status=order.payment_status,
            created_at=order.created_at
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@api_router.get("/market/orders")
async def get_orders(current_user: UserResponse = Depends(get_current_user)):
    """Get user's orders"""
    try:
        orders = await db.orders.find({"user_id": current_user.id}).sort("created_at", -1).to_list(50)
        
        # Clean orders
        for order in orders:
            if '_id' in order:
                del order['_id']
        
        return {"orders": orders}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

@api_router.post("/market/init-sample-data")
async def init_sample_data():
    """Initialize sample product data"""
    try:
        # Check if products already exist
        existing_products = await db.products.count_documents({})
        if existing_products > 0:
            return {"message": f"{existing_products} products already exist"}
        
        # Sample uniform products
        sample_products = [
            {
                "name": "프라게 EDU 정규 교복 상의 (남학생)",
                "description": "고급 원단으로 제작된 프라게 EDU 남학생 정규 교복 상의입니다. 편안한 착용감과 세련된 디자인이 특징입니다.",
                "price": 45000,
                "category": "uniform",
                "subcategory": "shirt",
                "brand": "Frage EDU",
                "size_options": ["90", "95", "100", "105", "110", "115"],
                "color_options": ["Navy", "White"],
                "images": ["https://via.placeholder.com/400x400/1f2937/ffffff?text=교복+상의"],
                "stock_quantity": 50,
                "is_available": True,
                "is_featured": True,
                "tags": ["교복", "상의", "남학생", "정규"],
                "specifications": {
                    "소재": "폴리에스터 70%, 면 30%",
                    "관리방법": "찬물 세탁, 건조기 사용 금지",
                    "제조사": "프라게 EDU"
                }
            },
            {
                "name": "프라게 EDU 정규 교복 하의 (남학생)",
                "description": "움직임이 편한 프라게 EDU 남학생 정규 교복 하의입니다. 내구성이 뛰어나고 관리가 쉽습니다.",
                "price": 42000,
                "category": "uniform",
                "subcategory": "pants",
                "brand": "Frage EDU",
                "size_options": ["90", "95", "100", "105", "110", "115"],
                "color_options": ["Navy", "Black"],
                "images": ["https://via.placeholder.com/400x400/374151/ffffff?text=교복+하의"],
                "stock_quantity": 45,
                "is_available": True,
                "is_featured": True,
                "tags": ["교복", "하의", "남학생", "정규"],
                "specifications": {
                    "소재": "폴리에스터 65%, 면 35%",
                    "관리방법": "30도 이하 찬물 세탁",
                    "제조사": "프라게 EDU"
                }
            },
            {
                "name": "프라게 EDU 정규 교복 상의 (여학생)",
                "description": "우아하고 단정한 디자인의 프라게 EDU 여학생 정규 교복 상의입니다.",
                "price": 47000,
                "category": "uniform",
                "subcategory": "blouse",
                "brand": "Frage EDU",
                "size_options": ["85", "90", "95", "100", "105", "110"],
                "color_options": ["White", "Light Blue"],
                "images": ["https://via.placeholder.com/400x400/e5e7eb/374151?text=여학생+상의"],
                "stock_quantity": 40,
                "is_available": True,
                "is_featured": True,
                "tags": ["교복", "상의", "여학생", "정규"],
                "specifications": {
                    "소재": "면 60%, 폴리에스터 40%",
                    "관리방법": "단독 세탁 권장",
                    "제조사": "프라게 EDU"
                }
            },
            {
                "name": "프라게 EDU 체육복 상하 세트",
                "description": "활동적인 체육 시간을 위한 프라게 EDU 체육복 세트입니다. 흡습 속건 기능이 있습니다.",
                "price": 38000,
                "category": "uniform",
                "subcategory": "sportswear",
                "brand": "Frage EDU",
                "size_options": ["S", "M", "L", "XL"],
                "color_options": ["Navy", "Gray"],
                "images": ["https://via.placeholder.com/400x400/6366f1/ffffff?text=체육복"],
                "stock_quantity": 60,
                "is_available": True,
                "is_featured": False,
                "tags": ["체육복", "세트", "운동복"],
                "specifications": {
                    "소재": "폴리에스터 100% (흡습속건)",
                    "관리방법": "찬물 세탁",
                    "제조사": "프라게 EDU"
                }
            },
            {
                "name": "프라게 EDU 학교 가방",
                "description": "튼튼하고 실용적인 프라게 EDU 공식 학교 가방입니다. 다양한 수납공간과 편안한 메는 끈이 특징입니다.",
                "price": 65000,
                "category": "accessories",
                "subcategory": "bag",
                "brand": "Frage EDU",
                "size_options": ["Standard"],
                "color_options": ["Navy", "Black"],
                "images": ["https://via.placeholder.com/400x400/1f2937/ffffff?text=학교가방"],
                "stock_quantity": 30,
                "is_available": True,
                "is_featured": True,
                "tags": ["가방", "학교", "백팩"],
                "specifications": {
                    "크기": "35 x 45 x 20 cm",
                    "소재": "나일론 원단 (발수 코팅)",
                    "용량": "약 30L",
                    "제조사": "프라게 EDU"
                }
            },
            {
                "name": "프라게 EDU 실내화",
                "description": "편안하고 위생적인 프라게 EDU 실내화입니다. 미끄럼 방지 솔창으로 안전합니다.",
                "price": 25000,
                "category": "accessories",
                "subcategory": "shoes",
                "brand": "Frage EDU",
                "size_options": ["220", "230", "240", "250", "260", "270"],
                "color_options": ["White", "Blue"],
                "images": ["https://via.placeholder.com/400x400/ddd6fe/374151?text=실내화"],
                "stock_quantity": 80,
                "is_available": True,
                "is_featured": False,
                "tags": ["실내화", "신발", "학교용품"],
                "specifications": {
                    "소재": "PVC + 면 안감",
                    "관리방법": "물세탁 가능",
                    "제조사": "프라게 EDU"
                }
            },
            {
                "name": "프라게 EDU 영어 교재 세트",
                "description": "체계적인 영어 학습을 위한 프라게 EDU 공식 교재 세트입니다. 단계별 학습이 가능합니다.",
                "price": 32000,
                "category": "books",
                "subcategory": "textbook",
                "brand": "Frage EDU",
                "size_options": ["Level 1", "Level 2", "Level 3"],
                "color_options": [],
                "images": ["https://via.placeholder.com/400x400/059669/ffffff?text=영어교재"],
                "stock_quantity": 100,
                "is_available": True,
                "is_featured": True,
                "tags": ["교재", "영어", "학습서"],
                "specifications": {
                    "구성": "메인북 + 워크북 + CD",
                    "페이지": "약 200페이지",
                    "출판사": "프라게 EDU Press"
                }
            },
            {
                "name": "프라게 EDU 문구 세트",
                "description": "학습에 필요한 기본 문구를 모은 프라게 EDU 문구 세트입니다.",
                "price": 18000,
                "category": "accessories",
                "subcategory": "stationery",
                "brand": "Frage EDU",
                "size_options": ["Basic Set", "Premium Set"],
                "color_options": ["Blue", "Pink", "Black"],
                "images": ["https://via.placeholder.com/400x400/f59e0b/ffffff?text=문구세트"],
                "stock_quantity": 120,
                "is_available": True,
                "is_featured": False,
                "tags": ["문구", "학용품", "세트"],
                "specifications": {
                    "구성": "연필, 지우개, 자, 필통, 노트",
                    "브랜드": "프라게 EDU Official"
                }
            }
        ]
        
        # Insert products
        for product_data in sample_products:
            product = Product(**product_data)
            product_dict = product.dict()
            product_dict['created_at'] = product_dict['created_at'].isoformat()
            product_dict['updated_at'] = product_dict['updated_at'].isoformat()
            await db.products.insert_one(product_dict)
        
        return {"message": f"Successfully created {len(sample_products)} sample products"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing sample data: {str(e)}")

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