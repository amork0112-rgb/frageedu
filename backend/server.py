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
from datetime import datetime, timezone, timedelta
import bcrypt
import random
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
    program_subtype: str = "regular"  # kinder_regular, kinder_single, junior_regular, middle_regular
    status: str = "pending"  # pending, reserved_test, admitted_pending, enrolled, leave, withdrawn
    requires_exam: bool = True  # False for kinder_regular
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClassAssignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    class_id: str
    class_name: str
    homeroom_teacher: str  # Updated field name
    teacher_id: Optional[str] = None
    weekday: str  # "Monday,Wednesday,Friday"
    time_start: str  # "16:00"
    time_end: str  # "17:30"
    classroom: str
    level: Optional[str] = None
    effective_from: datetime  # Updated field name
    end_date: Optional[datetime] = None
    status: str = "active"  # active, completed, suspended
    materials: List[str] = []
    assigned_by: str  # admin_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Student Status Management Models
class StudentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class ClassAssignmentRequest(BaseModel):
    class_id: str
    class_name: str
    homeroom_teacher: str
    weekday: str
    time_start: str
    time_end: str
    classroom: str
    level: Optional[str] = None

class StudentApprovalRequest(BaseModel):
    notes: Optional[str] = None

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

class AdminCreateWithRole(BaseModel):
    username: str
    email: str
    password: str
    role: str = "admin"  # admin, super_admin, kinder_admin, junior_admin, middle_admin

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

# Extended RBAC Models
class Permission(BaseModel):
    code: str  # Primary key: "can_view_student", "can_edit_student"
    description: str
    category: str = "general"  # general, student, notice, payment, exam, class
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RolePermission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # super_admin, kinder_admin, junior_admin, middle_admin
    permission_code: str
    default_value: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminUserAllowedBranch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_user_id: str
    branch: str  # kinder, junior, middle, kinder_single
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminUserPermission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_user_id: str
    permission_code: str
    value: bool  # Override role default
    granted_by: str  # super_admin user_id who granted this
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    password_hash: str
    role: str = "kinder_admin"  # super_admin, kinder_admin, junior_admin, middle_admin
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Enhanced Student Model for Management
class StudentManagement(BaseModel):
    id: str
    name: str
    grade: str
    birthdate: Optional[str]
    branch: str
    program_subtype: str
    status: str = "active"  # active, inactive, graduated, suspended
    parent_name: str
    parent_phone: str
    parent_email: str
    class_name: Optional[str] = None
    teacher_name: Optional[str] = None
    attendance_rate: float = 0.0
    payment_status: str = "paid"  # paid, unpaid, overdue
    last_attendance: Optional[str] = None
    enrollment_progress: float = 0.0
    created_at: datetime

# Permission Response Models
class PermissionResponse(BaseModel):
    code: str
    description: str
    category: str
    has_permission: bool

class AdminUserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    allowed_branches: List[str]
    permissions: List[PermissionResponse]
    last_login: Optional[datetime]
    created_at: datetime

class StudentManagementResponse(BaseModel):
    students: List[StudentManagement]
    pagination: Dict[str, Any]
    allowed_branches: List[str]
    user_permissions: List[str]
class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    email: str
    reset_token: str
    new_password: str

class FindUsernameRequest(BaseModel):
    parent_name: str
    student_name: str
    student_birthdate: str  # YYYY-MM-DD format

class PasswordResetToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    reset_token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models for various actions
class HomeworkSubmissionRequest(BaseModel):
    submission_text: Optional[str] = None
    file_urls: List[str] = []

class NoticeAcknowledgmentRequest(BaseModel):
    notice_ids: List[str]

class GuideAcknowledgmentRequest(BaseModel):
    guide_id: str

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

# Dashboard Utility Functions
async def get_program_display_name(branch: str, program_subtype: str) -> str:
    """Generate program display name based on branch and subtype"""
    branch_names = {
        "kinder": "프라게 킨더",
        "junior": "프라게 주니어", 
        "middle": "프라디스 중등"
    }
    
    subtype_names = {
        "regular": "정규",
        "transfer": "편입",
        "kinder_single": "유치 단과"
    }
    
    branch_display = branch_names.get(branch, branch)
    subtype_display = subtype_names.get(program_subtype, program_subtype)
    
    return f"{branch_display} · {subtype_display}"

async def should_show_exam_card(student: Dict[str, Any]) -> bool:
    """Determine if exam card should be shown based on branch and program rules"""
    branch = student.get("branch")
    program_subtype = student.get("program_subtype", "regular")
    requires_exam = student.get("requires_exam", True)
    
    # Rule: Hide for kinder_regular, show for others
    if branch == "kinder" and program_subtype == "regular":
        return False
    elif branch in ["junior", "middle"]:
        return True
    elif branch == "junior" and program_subtype == "kinder_single" and requires_exam:
        return True
    
    return False

async def get_student_enrollment_status(student_id: str) -> str:
    """Get enrollment status based on class assignment"""
    assignment = await db.class_placements.find_one({"student_id": student_id, "status": "active"})
    return "enrolled" if assignment else "pre_enrollment"

async def build_admission_progress_card(student_id: str) -> AdmissionProgressCard:
    """Build admission progress card data"""
    progress = await get_student_progress(student_id)
    
    if not progress:
        return AdmissionProgressCard(
            current_step="",
            completed_steps=[],
            total_steps=0,
            progress_percentage=0,
            status="not_started",
            enrollment_status="new",
            next_action="Contact for consultation",
            flow_name=""
        )
    
    # Get flow info for display name
    flow = await db.enrollment_flows.find_one({"flow_key": progress.flow_key})
    flow_name = flow["name"] if flow else progress.flow_key
    
    return AdmissionProgressCard(
        current_step=progress.current_step,
        completed_steps=progress.completed_steps,
        total_steps=progress.total_steps,
        progress_percentage=progress.progress_percentage,
        status=progress.status,
        enrollment_status=progress.enrollment_status,
        next_action=progress.next_action,
        flow_name=flow_name
    )

async def build_exam_card(student_id: str, student: Dict[str, Any]) -> ExamCard:
    """Build exam card data"""
    show_card = await should_show_exam_card(student)
    
    if not show_card:
        return ExamCard(
            show_card=False,
            has_reservation=False,
            reservation_date=None,
            reservation_time=None,
            has_result=False,
            score=None,
            level=None,
            passed=None,
            next_action=None
        )
    
    # Get latest reservation
    reservation = await db.exam_reservations.find_one(
        {"student_id": student_id}, 
        sort=[("created_at", -1)]
    )
    
    # Get latest result
    result = await db.exam_results.find_one(
        {"student_id": student_id},
        sort=[("tested_at", -1)]
    )
    
    next_action = None
    if not reservation:
        next_action = "Schedule entrance exam"
    elif reservation and reservation["status"] == "scheduled":
        next_action = "Prepare for exam"
    elif result and not result.get("passed"):
        next_action = "Schedule retake exam"
    
    return ExamCard(
        show_card=True,
        has_reservation=bool(reservation),
        reservation_date=reservation.get("exam_date") if reservation else None,
        reservation_time=reservation.get("exam_time") if reservation else None,
        has_result=bool(result),
        score=result.get("score") if result else None,
        level=result.get("level") if result else None,
        passed=result.get("passed") if result else None,
        next_action=next_action
    )

async def build_timetable_card(student_id: str) -> TimetableCard:
    """Build timetable card data"""
    assignment = await db.class_placements.find_one({"student_id": student_id, "status": "active"})
    
    if not assignment:
        return TimetableCard(
            show_card=True,
            is_enrolled=False,
            class_name=None,
            teacher_name=None,
            schedule=None,
            classroom=None,
            level=None,
            start_date=None
        )
    
    # Format schedule string
    schedule = f"{assignment['weekday']} {assignment['time_start']}-{assignment['time_end']}"
    
    return TimetableCard(
        show_card=True,
        is_enrolled=True,
        class_name=assignment["class_name"],
        teacher_name=assignment["teacher_name"],
        schedule=schedule,
        classroom=assignment["classroom"],
        level=assignment.get("level"),
        start_date=assignment["start_date"].isoformat() if assignment.get("start_date") else None
    )

async def build_homework_card(student_id: str) -> HomeworkCard:
    """Build homework card data"""
    # Get class assignment
    assignment = await db.class_placements.find_one({"student_id": student_id, "status": "active"})
    
    if not assignment:
        return HomeworkCard(
            show_card=False,
            total_assignments=0,
            pending_count=0,
            overdue_count=0,
            recent_assignments=[]
        )
    
    # Get homework for this class
    homework_list = await db.homeworks.find({"class_assignment_id": assignment["id"]}).to_list(100)
    
    # Get submissions for this student
    submissions = await db.homework_submissions.find({"student_id": student_id}).to_list(100)
    submission_map = {sub["homework_id"]: sub for sub in submissions}
    
    pending_count = 0
    overdue_count = 0
    recent_assignments = []
    
    now = datetime.now(timezone.utc)
    
    for hw in homework_list[:5]:  # Recent 5
        submission = submission_map.get(hw["id"])
        is_submitted = submission and submission["status"] in ["submitted", "graded"]
        is_overdue = hw["due_date"] < now and not is_submitted
        
        if not is_submitted:
            pending_count += 1
        if is_overdue:
            overdue_count += 1
        
        recent_assignments.append({
            "id": hw["id"],
            "title": hw["title"],
            "due_date": hw["due_date"].isoformat(),
            "status": submission["status"] if submission else "not_started",
            "is_overdue": is_overdue
        })
    
    return HomeworkCard(
        show_card=True,
        total_assignments=len(homework_list),
        pending_count=pending_count,
        overdue_count=overdue_count,
        recent_assignments=recent_assignments
    )

async def build_attendance_card(student_id: str) -> AttendanceCard:
    """Build attendance card data"""
    # Get class assignment
    assignment = await db.class_placements.find_one({"student_id": student_id, "status": "active"})
    
    if not assignment:
        return AttendanceCard(
            show_card=False,
            total_classes=0,
            present_count=0,
            absent_count=0,
            late_count=0,
            attendance_rate=0.0,
            recent_attendance=[]
        )
    
    # Get attendance records
    attendance_records = await db.attendances.find({
        "student_id": student_id,
        "class_assignment_id": assignment["id"]
    }).sort("date", -1).to_list(100)
    
    present_count = len([a for a in attendance_records if a["status"] == "present"])
    late_count = len([a for a in attendance_records if a["status"] == "late"])
    absent_count = len([a for a in attendance_records if a["status"] in ["absent", "excused"]])
    total_classes = len(attendance_records)
    
    attendance_rate = (present_count + late_count) / total_classes * 100 if total_classes > 0 else 0
    
    recent_attendance = []
    for record in attendance_records[:10]:  # Recent 10
        recent_attendance.append({
            "date": record["date"],
            "status": record["status"],
            "arrival_time": record.get("arrival_time"),
            "notes": record.get("notes")
        })
    
    return AttendanceCard(
        show_card=True,
        total_classes=total_classes,
        present_count=present_count,
        absent_count=absent_count,
        late_count=late_count,
        attendance_rate=attendance_rate,
        recent_attendance=recent_attendance
    )

async def build_billing_card(student_id: str, household_token: str) -> BillingCard:
    """Build billing card data"""
    # Get pending payments
    pending_payments = await db.payment_records.find({
        "student_id": student_id,
        "payment_status": "pending"
    }).sort("due_date", 1).to_list(50)
    
    # Get current month billing
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    current_billing = await db.billings.find_one({
        "student_id": student_id,
        "month": current_month
    })
    
    # Count overdue payments
    now = datetime.now(timezone.utc)
    overdue_count = len([p for p in pending_payments if p.get("due_date") and p["due_date"] < now])
    
    # Get payment history count
    history_count = await db.payment_records.count_documents({"student_id": student_id})
    
    pending_list = []
    for payment in pending_payments:
        pending_list.append({
            "id": payment["id"],
            "type": payment["payment_type"],
            "amount": payment["amount"],
            "due_date": payment.get("due_date").isoformat() if payment.get("due_date") else None,
            "currency": payment.get("currency", "KRW")
        })
    
    return BillingCard(
        pending_payments=pending_list,
        current_month_amount=current_billing["amount"] if current_billing else None,
        due_date=current_billing["due_date"].isoformat() if current_billing and current_billing.get("due_date") else None,
        payment_history_count=history_count,
        overdue_count=overdue_count
    )

async def build_notices_card(student_id: str, student: Dict[str, Any]) -> NoticesCard:
    """Build notices card data"""
    branch = student.get("branch", "")
    
    # Build query for relevant notices
    query = {
        "published": True,
        "$or": [
            {"target_audience": "all"},
            {"target_audience": f"branch:{branch}"}
        ]
    }
    
    # Get notices
    notices = await db.notices.find(query).sort("created_at", -1).limit(20).to_list(20)
    
    # Get acknowledgments for this student
    ack_query = {"student_id": student_id}
    acknowledgments = await db.notice_acknowledgments.find(ack_query).to_list(100)
    ack_map = {ack["notice_id"]: ack for ack in acknowledgments}
    
    unread_count = 0
    urgent_count = 0
    recent_notices = []
    
    for notice in notices:
        is_acknowledged = notice["id"] in ack_map and ack_map[notice["id"]]["acknowledged"]
        is_urgent = notice.get("priority") in ["high", "urgent"]
        
        if not is_acknowledged:
            unread_count += 1
        if is_urgent and not is_acknowledged:
            urgent_count += 1
        
        recent_notices.append({
            "id": notice["id"],
            "title": notice["title"],
            "type": notice["notice_type"],
            "priority": notice.get("priority", "normal"),
            "published_date": notice.get("publish_date", notice["created_at"]).isoformat(),
            "is_read": is_acknowledged,
            "is_urgent": is_urgent
        })
    
    return NoticesCard(
        unread_count=unread_count,
        urgent_count=urgent_count,
        recent_notices=recent_notices[:5]  # Top 5
    )

async def build_resources_card(student_id: str, household_token: str, student: Dict[str, Any]) -> ResourcesCard:
    """Build resources card data"""
    branch = student.get("branch", "")
    
    # Get guides for this branch
    query = {
        "published": True,
        "$or": [
            {"target_branch": "all"},
            {"target_branch": branch}
        ]
    }
    
    guides = await db.guides.find(query).to_list(100)
    
    # Get guide acknowledgments
    guide_acks = await db.guide_acknowledgments.find({"student_id": student_id}).to_list(100)
    ack_map = {ack["guide_id"]: ack for ack in guide_acks}
    
    guides_unread = 0
    required_guides_pending = 0
    
    for guide in guides:
        is_acknowledged = guide["id"] in ack_map and ack_map[guide["id"]]["acknowledged"]
        is_required = guide.get("required_reading", False)
        
        if not is_acknowledged:
            guides_unread += 1
        if is_required and not is_acknowledged:
            required_guides_pending += 1
    
    # Check consent status (from existing admission_data or new consent system)
    admission_data = await db.admission_data.find_one({"household_token": household_token})
    consent_pending = admission_data and admission_data.get("consent_status") != "completed"
    
    return ResourcesCard(
        guides_total=len(guides),
        guides_unread=guides_unread,
        required_guides_pending=required_guides_pending,
        consent_pending=consent_pending
    )

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

@api_router.get("/parent/dashboard/comprehensive")
async def get_comprehensive_dashboard(
    studentId: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get comprehensive card-based parent dashboard"""
    try:
        # Get parent info
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        # Get all students for dropdown
        students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        
        # Determine target student
        target_student = None
        if studentId:
            target_student = next((s for s in students if s["id"] == studentId), None)
            if not target_student:
                raise HTTPException(status_code=404, detail="Student not found")
        else:
            target_student = students[0]  # Default to first student
        
        # Clean student data
        for student in students:
            if '_id' in student:
                del student['_id']
        
        if '_id' in target_student:
            del target_student['_id']
        
        # Build student info list for dropdown
        student_info_list = []
        for student in students:
            program_display = await get_program_display_name(
                student.get("branch", ""), 
                student.get("program_subtype", "regular")
            )
            
            student_info = StudentInfo(
                id=student["id"],
                name=student["name"],
                grade=student.get("grade", ""),
                birthdate=student.get("birthdate"),
                branch=student.get("branch", ""),
                program_subtype=student.get("program_subtype", "regular"),
                requires_exam=student.get("requires_exam", True),
                program_display=program_display
            )
            student_info_list.append(student_info)
        
        # Build comprehensive dashboard for target student
        target_student_info = next((s for s in student_info_list if s.id == target_student["id"]), student_info_list[0])
        
        # Build all dashboard cards
        admission_progress = await build_admission_progress_card(target_student["id"])
        exam_card = await build_exam_card(target_student["id"], target_student)
        timetable_card = await build_timetable_card(target_student["id"])
        homework_card = await build_homework_card(target_student["id"])
        attendance_card = await build_attendance_card(target_student["id"])
        billing_card = await build_billing_card(target_student["id"], parent["household_token"])
        notices_card = await build_notices_card(target_student["id"], target_student)
        resources_card = await build_resources_card(target_student["id"], parent["household_token"], target_student)
        
        # Build dashboard cards response
        dashboard_cards = DashboardCardsResponse(
            student_info=target_student_info,
            admission_progress=admission_progress,
            exam=exam_card,
            timetable=timetable_card,
            homework=homework_card,
            attendance=attendance_card,
            billing=billing_card,
            notices=notices_card,
            resources=resources_card
        )
        
        # Get global notifications (urgent notices, overdue items)
        global_notifications = []
        
        # Add urgent notices
        if notices_card.urgent_count > 0:
            global_notifications.append({
                "type": "urgent_notice",
                "message": f"{notices_card.urgent_count}개의 긴급 공지사항이 있습니다",
                "action": "view_notices",
                "priority": "high"
            })
        
        # Add overdue payments
        if billing_card.overdue_count > 0:
            global_notifications.append({
                "type": "overdue_payment",
                "message": f"{billing_card.overdue_count}개의 미납 결제가 있습니다",
                "action": "view_billing",
                "priority": "high"
            })
        
        # Add overdue homework
        if homework_card.overdue_count > 0:
            global_notifications.append({
                "type": "overdue_homework",
                "message": f"{homework_card.overdue_count}개의 미제출 과제가 있습니다",
                "action": "view_homework",
                "priority": "medium"
            })
        
        # Add required guides pending
        if resources_card.required_guides_pending > 0:
            global_notifications.append({
                "type": "required_guides",
                "message": f"{resources_card.required_guides_pending}개의 필독 가이드를 확인하세요",
                "action": "view_guides",
                "priority": "medium"
            })
        
        return ComprehensiveDashboardResponse(
            parent_info={
                "name": current_user.name,
                "email": current_user.email,
                "phone": current_user.phone,
                "branch": parent.get("branch", ""),
                "household_token": parent["household_token"]
            },
            students=student_info_list,
            current_student=dashboard_cards,
            global_notifications=global_notifications
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching comprehensive dashboard: {str(e)}")

@api_router.post("/parent/exam/reserve")
async def reserve_exam(
    reservation_request: ExamReservationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Reserve an exam slot for a student"""
    try:
        # Verify student belongs to parent
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        student = await db.students.find_one({"id": reservation_request.student_id, "parent_id": parent["id"]})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check if student should have exam
        if not await should_show_exam_card(student):
            raise HTTPException(status_code=400, detail="Exam not required for this student")
        
        # Check for existing reservation
        existing = await db.exam_reservations.find_one({
            "student_id": reservation_request.student_id,
            "status": "scheduled"
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Active reservation already exists")
        
        # Create reservation
        reservation = ExamReservation(
            student_id=reservation_request.student_id,
            household_token=parent["household_token"],
            branch_type=reservation_request.branch_type,
            exam_date=reservation_request.exam_date,
            exam_time=reservation_request.exam_time,
            notes=reservation_request.notes
        )
        
        reservation_dict = reservation.dict()
        reservation_dict['created_at'] = reservation_dict['created_at'].isoformat()
        reservation_dict['updated_at'] = reservation_dict['updated_at'].isoformat()
        
        await db.exam_reservations.insert_one(reservation_dict)
        
        # Trigger flow event
        await trigger_flow_event(
            reservation_request.student_id,
            "exam.scheduled",
            "consultation",
            {
                "exam_date": reservation_request.exam_date,
                "exam_time": reservation_request.exam_time,
                "branch_type": reservation_request.branch_type
            },
            f"parent:{current_user.id}"
        )
        
        return {"message": "Exam reservation successful", "reservation_id": reservation.id}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error creating reservation: {str(e)}")

@api_router.get("/parent/homework")
async def get_homework_list(
    current_user: UserResponse = Depends(get_current_user),
    student_id: Optional[str] = None,
    status: Optional[str] = None,  # pending, submitted, graded, overdue
    page: int = 1,
    limit: int = 20
):
    """Get homework list for student"""
    try:
        # Get parent and students
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        
        # Determine target student
        if student_id:
            target_student = next((s for s in students if s["id"] == student_id), None)
            if not target_student:
                raise HTTPException(status_code=404, detail="Student not found")
        else:
            target_student = students[0]
        
        # Get class assignment
        assignment = await db.class_placements.find_one({
            "student_id": target_student["id"], 
            "status": "active"
        })
        
        if not assignment:
            return {
                "homework_list": [],
                "pagination": {"page": page, "limit": limit, "total": 0, "total_pages": 0}
            }
        
        # Build query
        query = {"class_assignment_id": assignment["id"]}
        
        # Get homework
        skip = (page - 1) * limit
        homework_list = await db.homeworks.find(query).sort("due_date", -1).skip(skip).limit(limit).to_list(limit)
        total_count = await db.homeworks.count_documents(query)
        
        # Get submissions
        submission_query = {"student_id": target_student["id"]}
        submissions = await db.homework_submissions.find(submission_query).to_list(1000)
        submission_map = {sub["homework_id"]: sub for sub in submissions}
        
        # Build response
        homework_response = []
        now = datetime.now(timezone.utc)
        
        for hw in homework_list:
            if '_id' in hw:
                del hw['_id']
            
            submission = submission_map.get(hw["id"])
            hw_status = "not_started"
            is_overdue = False
            
            if submission:
                hw_status = submission["status"]
            
            if hw["due_date"] < now and hw_status not in ["submitted", "graded"]:
                is_overdue = True
                hw_status = "overdue"
            
            # Filter by status if requested
            if status and hw_status != status:
                continue
            
            homework_response.append({
                **hw,
                "status": hw_status,
                "is_overdue": is_overdue,
                "submission": submission,
                "due_date": hw["due_date"].isoformat(),
                "created_at": hw["created_at"].isoformat()
            })
        
        return {
            "homework_list": homework_response,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching homework: {str(e)}")

@api_router.post("/parent/homework/{homework_id}/submit")
async def submit_homework(
    homework_id: str,
    submission_request: HomeworkSubmissionRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Submit homework assignment"""
    try:
        # Verify homework exists
        homework = await db.homeworks.find_one({"id": homework_id})
        if not homework:
            raise HTTPException(status_code=404, detail="Homework not found")
        
        # Get parent and student
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        # Get class assignment to verify student
        assignment = await db.class_placements.find_one({"id": homework["class_assignment_id"]})
        if not assignment:
            raise HTTPException(status_code=404, detail="Class assignment not found")
        
        student = await db.students.find_one({
            "id": assignment["student_id"], 
            "parent_id": parent["id"]
        })
        if not student:
            raise HTTPException(status_code=403, detail="Not authorized for this homework")
        
        # Check if already submitted
        existing = await db.homework_submissions.find_one({
            "homework_id": homework_id,
            "student_id": student["id"],
            "status": {"$in": ["submitted", "graded"]}
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Homework already submitted")
        
        # Create or update submission
        now = datetime.now(timezone.utc)
        submission_data = {
            "homework_id": homework_id,
            "student_id": student["id"],
            "status": "submitted",
            "submission_text": submission_request.submission_text,
            "file_urls": submission_request.file_urls,
            "submitted_at": now,
            "updated_at": now
        }
        
        # Check if draft exists
        draft = await db.homework_submissions.find_one({
            "homework_id": homework_id,
            "student_id": student["id"],
            "status": "pending"
        })
        
        if draft:
            # Update existing draft
            await db.homework_submissions.update_one(
                {"id": draft["id"]},
                {"$set": submission_data}
            )
            submission_id = draft["id"]
        else:
            # Create new submission
            submission = HomeworkSubmission(**submission_data)
            submission_dict = submission.dict()
            submission_dict['created_at'] = submission_dict['created_at'].isoformat()
            submission_dict['submitted_at'] = submission_dict['submitted_at'].isoformat()
            submission_dict['updated_at'] = now.isoformat()
            
            await db.homework_submissions.insert_one(submission_dict)
            submission_id = submission.id
        
        return {"message": "Homework submitted successfully", "submission_id": submission_id}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error submitting homework: {str(e)}")

@api_router.post("/parent/notices/acknowledge")
async def acknowledge_notices(
    ack_request: NoticeAcknowledgmentRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark notices as read/acknowledged"""
    try:
        parent = await db.parents.find_one({"user_id": current_user.id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent info not found")
        
        students = await db.students.find({"parent_id": parent["id"]}).to_list(10)
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        
        # For now, acknowledge for first student (can be extended)
        student = students[0]
        
        acknowledged_count = 0
        now = datetime.now(timezone.utc)
        
        for notice_id in ack_request.notice_ids:
            # Check if already acknowledged
            existing = await db.notice_acknowledgments.find_one({
                "notice_id": notice_id,
                "student_id": student["id"]
            })
            
            if existing:
                # Update existing
                await db.notice_acknowledgments.update_one(
                    {"id": existing["id"]},
                    {
                        "$set": {
                            "acknowledged": True,
                            "acknowledged_at": now.isoformat()
                        }
                    }
                )
            else:
                # Create new acknowledgment
                ack = NoticeAcknowledgment(
                    notice_id=notice_id,
                    student_id=student["id"],
                    household_token=parent["household_token"],
                    acknowledged=True,
                    acknowledged_at=now
                )
                
                ack_dict = ack.dict()
                ack_dict['created_at'] = ack_dict['created_at'].isoformat()
                ack_dict['acknowledged_at'] = ack_dict['acknowledged_at'].isoformat()
                
                await db.notice_acknowledgments.insert_one(ack_dict)
            
            acknowledged_count += 1
        
        return {"message": f"Acknowledged {acknowledged_count} notices"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error acknowledging notices: {str(e)}")

@api_router.post("/admin/create-sample-data")
async def create_sample_student_data(current_admin: AdminResponse = Depends(get_current_admin)):
    """Create sample student data for testing (admin only)"""
    try:
        if current_admin.role not in ["admin", "super_admin", "kinder_admin", "junior_admin", "middle_admin"]:
            raise HTTPException(status_code=403, detail="Only admin can create sample data")
        
        # Check if we already have students
        existing_count = await db.students.count_documents({})
        if existing_count > 0:
            return {"message": f"Sample data not created - {existing_count} students already exist"}
        
        # Create sample parents and students
        sample_families = [
            {
                "parent": {
                    "name": "김영희", 
                    "email": "kim.younghee@example.com", 
                    "phone": "010-1234-5678",
                    "branch": "kinder"
                },
                "students": [
                    {"name": "김민수", "grade": "K1", "branch": "kinder", "program_subtype": "regular", "birthdate": "2019-03-15"}
                ]
            },
            {
                "parent": {
                    "name": "이철수", 
                    "email": "lee.chulsoo@example.com", 
                    "phone": "010-2345-6789",
                    "branch": "junior"
                },
                "students": [
                    {"name": "이소영", "grade": "G2", "branch": "junior", "program_subtype": "regular", "birthdate": "2015-07-22"}
                ]
            },
            {
                "parent": {
                    "name": "박지현", 
                    "email": "park.jihyun@example.com", 
                    "phone": "010-3456-7890",
                    "branch": "middle"
                },
                "students": [
                    {"name": "박준호", "grade": "G6", "branch": "middle", "program_subtype": "regular", "birthdate": "2012-11-08"}
                ]
            },
            {
                "parent": {
                    "name": "최미나", 
                    "email": "choi.mina@example.com", 
                    "phone": "010-4567-8901",
                    "branch": "kinder"
                },
                "students": [
                    {"name": "최하윤", "grade": "K2", "branch": "kinder", "program_subtype": "kinder_single", "birthdate": "2018-05-30"}
                ]
            }
        ]
        
        created_students = 0
        created_parents = 0
        
        for family in sample_families:
            # Create user
            user = User(
                email=family["parent"]["email"],
                phone=family["parent"]["phone"],
                name=family["parent"]["name"],
                password_hash=hash_password("Test123!")  # Default password for test data
            )
            user_dict = user.dict()
            user_dict['created_at'] = user_dict['created_at'].isoformat()
            user_dict['last_login_at'] = None
            await db.users.insert_one(user_dict)
            
            # Create parent
            parent = Parent(
                user_id=user.id,
                name=family["parent"]["name"],
                phone=family["parent"]["phone"],
                email=family["parent"]["email"],
                branch=family["parent"]["branch"],
                household_token=user.household_token
            )
            parent_dict = parent.dict()
            parent_dict['created_at'] = parent_dict['created_at'].isoformat()
            await db.parents.insert_one(parent_dict)
            created_parents += 1
            
            # Create students
            for student_data in family["students"]:
                student = Student(
                    parent_id=parent.id,
                    name=student_data["name"],
                    grade=student_data["grade"],
                    birthdate=student_data["birthdate"],
                    branch=student_data["branch"],
                    program_subtype=student_data["program_subtype"],
                    requires_exam=(student_data["branch"] != "kinder"),
                    notes=f"Sample student data created by admin {current_admin.username}"
                )
                student_dict = student.dict()
                await db.students.insert_one(student_dict)
                created_students += 1
        
        return {
            "message": f"Sample data created successfully", 
            "created_parents": created_parents,
            "created_students": created_students
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error creating sample data: {str(e)}")

@api_router.post("/admin/init-rbac")
async def init_rbac_system(current_admin: AdminResponse = Depends(get_current_admin)):
    """Initialize RBAC system with default permissions and roles"""
    try:
        # Allow admin or super_admin to initialize RBAC
        if current_admin.role not in ["admin", "super_admin", "kinder_admin", "junior_admin", "middle_admin"]:
            raise HTTPException(status_code=403, detail="Only admin or super admin can initialize RBAC system")
        
        result = await initialize_rbac_system()
        return {"message": result}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error initializing RBAC: {str(e)}")

@api_router.get("/admin/students")
async def get_students_for_admin(
    current_admin: AdminResponse = Depends(get_current_admin),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    branch_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    grade_filter: Optional[str] = None
):
    """Get students list with admin role-based filtering (alias for student-management)"""
    # This is essentially the same as the student-management endpoint
    # but with the expected naming convention
    try:
        # Check permission
        if not await has_permission(current_admin.id, current_admin.role, "can_view_student"):
            raise HTTPException(status_code=403, detail="Permission denied: cannot view students")
        
        # Get admin's allowed branches
        access_info = await filter_students_by_admin_access(current_admin.id, current_admin.role)
        allowed_branches = access_info["allowed_branches"]
        
        # Build query
        query = {}
        
        # Apply branch filtering based on admin access
        if branch_filter:
            if branch_filter in allowed_branches:
                query["branch"] = branch_filter
            else:
                # Admin requested a branch they don't have access to - return empty results
                query["branch"] = {"$in": []}  # This will return no results
        else:
            query["branch"] = {"$in": allowed_branches}
        
        # Apply additional filters
        if status_filter:
            query["status"] = status_filter
        if grade_filter:
            query["grade"] = grade_filter
        
        # Search functionality
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"id": {"$regex": search, "$options": "i"}}
            ]
        
        # Get students with pagination
        skip = (page - 1) * limit
        students = await db.students.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        total_count = await db.students.count_documents(query)
        
        # Enrich student data
        formatted_students = []
        for student in students:
            if '_id' in student:
                del student['_id']
            
            # Get parent info
            parent = await db.parents.find_one({"id": student["parent_id"]})
            
            # Get class info
            class_assignment = await db.class_placements.find_one({"student_id": student["id"], "status": "active"})
            
            # Get progress info
            progress = await db.student_enrollment_progress.find_one({"student_id": student["id"]})
            
            # Calculate enrollment progress
            if progress:
                completed_steps = len(progress.get("completed_steps", []))
                total_steps = 5  # Default flow steps
                progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            else:
                progress_percentage = 0.0
            
            formatted_student = StudentManagement(
                id=student["id"],
                name=student["name"],
                grade=student.get("grade", ""),
                birthdate=student.get("birthdate"),
                branch=student.get("branch", ""),
                program_subtype=student.get("program_subtype", "regular"),
                status=student.get("status", "active"),
                parent_name=parent["name"] if parent else "",
                parent_phone=parent["phone"] if parent else "",
                parent_email=parent["email"] if parent else "",
                class_name=class_assignment["class_name"] if class_assignment else None,
                teacher_name=class_assignment["teacher_name"] if class_assignment else None,
                attendance_rate=95.0,  # Placeholder
                payment_status="paid",  # Placeholder
                last_attendance=None,  # Placeholder
                enrollment_progress=progress_percentage,
                created_at=datetime.fromisoformat(student.get("created_at", datetime.now(timezone.utc).isoformat())) if isinstance(student.get("created_at"), str) else student.get("created_at", datetime.now(timezone.utc))
            )
            formatted_students.append(formatted_student)
        
        # Get user permissions for UI
        permission_codes = []
        user_permissions = await get_user_permissions(current_admin.id, current_admin.role)
        for perm in user_permissions:
            if perm.has_permission:
                permission_codes.append(perm.code)
        
        return StudentManagementResponse(
            students=formatted_students,
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit
            },
            allowed_branches=allowed_branches,
            user_permissions=permission_codes
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching students list: {str(e)}")

@api_router.get("/admin/student-management")
async def get_student_management_list(
    current_admin: AdminResponse = Depends(get_current_admin),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    branch_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    grade_filter: Optional[str] = None
):
    """Get students list with admin role-based filtering"""
    try:
        # Check permission
        if not await has_permission(current_admin.id, current_admin.role, "can_view_student"):
            raise HTTPException(status_code=403, detail="Permission denied: cannot view students")
        
        # Get admin's allowed branches
        access_info = await filter_students_by_admin_access(current_admin.id, current_admin.role)
        allowed_branches = access_info["allowed_branches"]
        
        # Build query
        query = {}
        
        # Apply branch filtering based on admin access
        if branch_filter:
            if branch_filter in allowed_branches:
                query["branch"] = branch_filter
            else:
                # Admin requested a branch they don't have access to - return empty results
                query["branch"] = {"$in": []}  # This will return no results
        else:
            query["branch"] = {"$in": allowed_branches}
        
        # Apply additional filters
        if status_filter:
            query["status"] = status_filter
        if grade_filter:
            query["grade"] = grade_filter
        
        # Search functionality
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"id": {"$regex": search, "$options": "i"}}
            ]
        
        # Get students with pagination
        skip = (page - 1) * limit
        students = await db.students.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        total_count = await db.students.count_documents(query)
        
        # Enrich student data
        formatted_students = []
        for student in students:
            if '_id' in student:
                del student['_id']
            
            # Get parent info
            parent = await db.parents.find_one({"id": student["parent_id"]})
            
            # Get class info
            class_assignment = await db.class_placements.find_one({"student_id": student["id"], "status": "active"})
            
            # Get progress info
            progress = await db.student_enrollment_progress.find_one({"student_id": student["id"]})
            
            # Calculate enrollment progress
            if progress:
                completed_steps = len(progress.get("completed_steps", []))
                total_steps = 5  # Default flow steps
                progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            else:
                progress_percentage = 0.0
            
            formatted_student = StudentManagement(
                id=student["id"],
                name=student["name"],
                grade=student.get("grade", ""),
                birthdate=student.get("birthdate"),
                branch=student.get("branch", ""),
                program_subtype=student.get("program_subtype", "regular"),
                status=student.get("status", "active"),
                parent_name=parent["name"] if parent else "",
                parent_phone=parent["phone"] if parent else "",
                parent_email=parent["email"] if parent else "",
                class_name=class_assignment["class_name"] if class_assignment else None,
                teacher_name=class_assignment["teacher_name"] if class_assignment else None,
                attendance_rate=95.0,  # Placeholder
                payment_status="paid",  # Placeholder
                last_attendance="2025-08-30",  # Placeholder
                enrollment_progress=progress_percentage,
                created_at=datetime.now(timezone.utc)
            )
            formatted_students.append(formatted_student)
        
        # Get user permissions
        user_permissions = await get_user_permissions(current_admin.id, current_admin.role)
        permission_codes = [p.code for p in user_permissions if p.has_permission]
        
        return StudentManagementResponse(
            students=formatted_students,
            pagination={
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": (total_count + limit - 1) // limit
            },
            allowed_branches=allowed_branches,
            user_permissions=permission_codes
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching student management list: {str(e)}")

@api_router.get("/admin/permissions/user/{admin_user_id}")
async def get_admin_user_permissions(
    admin_user_id: str,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Get permissions for specific admin user (super admin only)"""
    try:
        if current_admin.role != "admin":  # Will be super_admin later
            raise HTTPException(status_code=403, detail="Only super admin can view user permissions")
        
        # Get target admin user
        target_admin = await db.admins.find_one({"id": admin_user_id})
        if not target_admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        # Get permissions and branches
        permissions = await get_user_permissions(admin_user_id, target_admin["role"])
        allowed_branches = await get_allowed_branches(admin_user_id)
        
        return AdminUserResponse(
            id=target_admin["id"],
            username=target_admin["username"],
            email=target_admin["email"],
            role=target_admin["role"],
            is_active=target_admin.get("is_active", True),
            allowed_branches=allowed_branches,
            permissions=permissions,
            last_login=target_admin.get("last_login"),
            created_at=datetime.fromisoformat(target_admin["created_at"])
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching admin user permissions: {str(e)}")

@api_router.post("/admin/permissions/set-branches")
async def set_admin_user_branches(
    request: Dict[str, Any],
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Set allowed branches for an admin user (super admin only)"""
    try:
        if current_admin.role != "admin":  # Will be super_admin later
            raise HTTPException(status_code=403, detail="Only super admin can set user branches")
        
        admin_user_id = request.get("admin_user_id")
        branches = request.get("branches", [])
        
        if not admin_user_id:
            raise HTTPException(status_code=400, detail="admin_user_id is required")
        
        # Validate branches
        valid_branches = ["kinder", "junior", "middle", "kinder_single"]
        invalid_branches = [b for b in branches if b not in valid_branches]
        if invalid_branches:
            raise HTTPException(status_code=400, detail=f"Invalid branches: {invalid_branches}")
        
        await set_admin_branches(admin_user_id, branches, current_admin.id)
        
        return {"message": "Branches updated successfully", "branches": branches}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error setting admin branches: {str(e)}")

@api_router.post("/admin/permissions/set-permission")
async def set_admin_user_permission(
    request: Dict[str, Any],
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Set specific permission for an admin user (super admin only)"""
    try:
        if current_admin.role != "admin":  # Will be super_admin later
            raise HTTPException(status_code=403, detail="Only super admin can set user permissions")
        
        admin_user_id = request.get("admin_user_id")
        permission_code = request.get("permission_code")
        value = request.get("value")
        
        if not all([admin_user_id, permission_code, value is not None]):
            raise HTTPException(status_code=400, detail="admin_user_id, permission_code, and value are required")
        
        # Validate permission exists
        permission = await db.permissions.find_one({"code": permission_code})
        if not permission:
            raise HTTPException(status_code=400, detail=f"Permission not found: {permission_code}")
        
        await set_admin_permission(admin_user_id, permission_code, value, current_admin.id)
        
        return {"message": "Permission updated successfully", "permission": permission_code, "value": value}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error setting admin permission: {str(e)}")

@api_router.post("/admin/students/{student_id}/update-status")
async def update_student_enrollment_status(
    student_id: str,
    status_update: Dict[str, Any],
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Admin endpoint to update student enrollment status and trigger flow events"""
    try:
        # Verify student exists
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        new_enrollment_status = status_update.get("enrollment_status")
        new_flow_step = status_update.get("flow_step") 
        notes = status_update.get("notes", "")
        
        # Update progress if enrollment status provided
        if new_enrollment_status:
            progress = await db.student_enrollment_progress.find_one({"student_id": student_id})
            if progress:
                await db.student_enrollment_progress.update_one(
                    {"student_id": student_id},
                    {
                        "$set": {
                            "enrollment_status": new_enrollment_status,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
        
        # Trigger flow event if step provided  
        if new_flow_step:
            event_type = f"{new_flow_step}.completed"
            result = await trigger_flow_event(
                student_id,
                event_type,
                new_flow_step,
                {
                    "updated_by": f"admin:{current_admin.id}",
                    "notes": notes,
                    "manual_update": True
                },
                f"admin:{current_admin.id}"
            )
            
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
        
        # Create class assignment if enrolling
        if new_enrollment_status == "enrolled" and status_update.get("class_assignment"):
            class_data = status_update["class_assignment"]
            
            # Check if assignment already exists
            existing = await db.class_placements.find_one({
                "student_id": student_id,
                "status": "active"
            })
            
            if not existing:
                assignment = ClassAssignment(
                    student_id=student_id,
                    class_id=class_data.get("class_id", f"class_{student_id}"),
                    class_name=class_data["class_name"],
                    teacher_name=class_data["teacher_name"],
                    teacher_id=class_data.get("teacher_id"),
                    weekday=class_data["weekday"],
                    time_start=class_data["time_start"],
                    time_end=class_data["time_end"], 
                    classroom=class_data["classroom"],
                    level=class_data.get("level"),
                    start_date=datetime.fromisoformat(class_data["start_date"]),
                    assigned_by=current_admin.id
                )
                
                assignment_dict = assignment.dict()
                assignment_dict['created_at'] = assignment_dict['created_at'].isoformat()
                assignment_dict['start_date'] = assignment_dict['start_date'].isoformat()
                
                await db.class_placements.insert_one(assignment_dict)
                
                # Trigger placement event
                await trigger_flow_event(
                    student_id,
                    "class.assigned",
                    "placement",
                    {
                        "class_name": class_data["class_name"],
                        "teacher": class_data["teacher_name"],
                        "assigned_by": f"admin:{current_admin.id}"
                    },
                    f"admin:{current_admin.id}"
                )
        
        # Log admin action
        await log_audit(
            current_admin.id,
            f"UPDATE_STATUS:{new_enrollment_status or new_flow_step}",
            "Student", 
            student_id,
            status_update
        )
        
        # Send notification (if configured)
        await send_alimtalk_notification(
            student_id,
            "status_update",
            {
                "new_status": new_enrollment_status,
                "updated_by": current_admin.username,
                "notes": notes
            }
        )
        
        return {
            "message": "Student status updated successfully",
            "student_id": student_id,
            "new_status": new_enrollment_status,
            "flow_step": new_flow_step
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error updating student status: {str(e)}")

@api_router.post("/admin/students/{student_id}/assign-class")
async def assign_student_to_class(
    student_id: str,
    assignment_request: ClassAssignmentRequest,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Admin endpoint to assign student to class and transition to enrolled status"""
    try:
        # Check permissions
        if not await has_permission(current_admin.id, current_admin.role, "can_edit_class"):
            raise HTTPException(status_code=403, detail="Permission denied: cannot assign classes")
        
        # Verify student exists and is in admitted_pending status
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        if student.get("status") != "admitted_pending":
            raise HTTPException(
                status_code=400, 
                detail=f"Student must be in 'admitted_pending' status to assign class. Current status: {student.get('status')}"
            )
        
        # Check admin branch access
        if not await can_access_branch(current_admin.id, current_admin.role, student.get("branch")):
            raise HTTPException(status_code=403, detail="Access denied: cannot manage this student's branch")
        
        # Check if assignment already exists
        existing = await db.class_assignments.find_one({
            "student_id": student_id,
            "status": "active"
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Student already assigned to active class")
        
        # START TRANSACTION - Create assignment and update student status
        # Create assignment
        assignment = ClassAssignment(
            student_id=student_id,
            class_id=assignment_request.class_id,
            class_name=assignment_request.class_name,
            homeroom_teacher=assignment_request.homeroom_teacher,
            weekday=assignment_request.weekday,
            time_start=assignment_request.time_start,
            time_end=assignment_request.time_end,
            classroom=assignment_request.classroom,
            level=assignment_request.level,
            effective_from=datetime.now(timezone.utc),
            assigned_by=current_admin.id
        )
        
        assignment_dict = assignment.dict()
        assignment_dict['created_at'] = assignment_dict['created_at'].isoformat()
        assignment_dict['effective_from'] = assignment_dict['effective_from'].isoformat()
        
        await db.class_assignments.insert_one(assignment_dict)
        
        # Update student status to enrolled
        prev_status = student.get("status")
        await db.students.update_one(
            {"id": student_id},
            {
                "$set": {
                    "status": "enrolled",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Log audit trail
        await log_audit(
            current_admin.id,
            "ASSIGN_CLASS",
            "Student",
            student_id,
            {
                "class_name": assignment_request.class_name,
                "homeroom_teacher": assignment_request.homeroom_teacher,
                "prev_status": prev_status,
                "new_status": "enrolled"
            }
        )
        
        # Send notification (placeholder)
        await send_status_change_notification(student_id, "class_assigned", {
            "class_name": assignment_request.class_name,
            "teacher": assignment_request.homeroom_teacher
        })
        
        return {
            "message": "Class assigned successfully and student enrolled",
            "student_id": student_id,
            "class_assignment_id": assignment.id,
            "previous_status": prev_status,
            "current_status": "enrolled"
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error assigning class: {str(e)}")

@api_router.post("/admin/students/{student_id}/approve")
async def approve_student_admission(
    student_id: str,
    approval_request: StudentApprovalRequest,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Admin endpoint to approve student admission (pending -> admitted_pending)"""
    try:
        # Check permissions
        if not await has_permission(current_admin.id, current_admin.role, "can_edit_student"):
            raise HTTPException(status_code=403, detail="Permission denied: cannot approve students")
        
        # Verify student exists and is in correct status
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        current_status = student.get("status")
        if current_status not in ["pending", "reserved_test"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Student must be in 'pending' or 'reserved_test' status to approve. Current status: {current_status}"
            )
        
        # Check admin branch access
        if not await can_access_branch(current_admin.id, current_admin.role, student.get("branch")):
            raise HTTPException(status_code=403, detail="Access denied: cannot manage this student's branch")
        
        # Update student status to admitted_pending
        await db.students.update_one(
            {"id": student_id},
            {
                "$set": {
                    "status": "admitted_pending",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Log audit trail
        await log_audit(
            current_admin.id,
            "APPROVE_ADMISSION",
            "Student",
            student_id,
            {
                "prev_status": current_status,
                "new_status": "admitted_pending",
                "notes": approval_request.notes
            }
        )
        
        # Send notification (placeholder)
        await send_status_change_notification(student_id, "admission_approved", {
            "notes": approval_request.notes
        })
        
        return {
            "message": "Student admission approved successfully",
            "student_id": student_id,
            "previous_status": current_status,
            "current_status": "admitted_pending"
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error approving admission: {str(e)}")

@api_router.patch("/admin/students/{student_id}/status")
async def update_student_status(
    student_id: str,
    status_update: StudentStatusUpdate,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Admin endpoint to update student status (leave, withdrawn, etc.)"""
    try:
        # Check permissions
        if not await has_permission(current_admin.id, current_admin.role, "can_edit_student"):
            raise HTTPException(status_code=403, detail="Permission denied: cannot update student status")
        
        # Verify student exists
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check admin branch access
        if not await can_access_branch(current_admin.id, current_admin.role, student.get("branch")):
            raise HTTPException(status_code=403, detail="Access denied: cannot manage this student's branch")
        
        # Validate status transition
        valid_statuses = ["pending", "reserved_test", "admitted_pending", "enrolled", "leave", "withdrawn"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        current_status = student.get("status")
        
        # Validate specific transitions
        if status_update.status == "enrolled":
            # enrolled requires class assignment
            class_assignment = await db.class_assignments.find_one({
                "student_id": student_id,
                "status": "active"
            })
            if not class_assignment:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot set status to 'enrolled': student must have an active class assignment"
                )
        
        # Update student status
        await db.students.update_one(
            {"id": student_id},
            {
                "$set": {
                    "status": status_update.status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Log audit trail
        await log_audit(
            current_admin.id,
            "UPDATE_STATUS",
            "Student",
            student_id,
            {
                "prev_status": current_status,
                "new_status": status_update.status,
                "notes": status_update.notes
            }
        )
        
        # Send notification for certain status changes
        if status_update.status in ["leave", "withdrawn"]:
            await send_status_change_notification(student_id, f"status_{status_update.status}", {
                "notes": status_update.notes
            })
        
        return {
            "message": f"Student status updated to {status_update.status}",
            "student_id": student_id,
            "previous_status": current_status,
            "current_status": status_update.status
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error updating student status: {str(e)}")

@api_router.post("/admin/students/{student_id}/reserve-test")
async def reserve_student_test(
    student_id: str,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Admin endpoint to reserve test for student (pending -> reserved_test)"""
    try:
        # Check permissions
        if not await has_permission(current_admin.id, current_admin.role, "can_edit_student"):
            raise HTTPException(status_code=403, detail="Permission denied: cannot reserve tests")
        
        # Verify student exists and is in pending status
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        if student.get("status") != "pending":
            raise HTTPException(
                status_code=400, 
                detail=f"Student must be in 'pending' status to reserve test. Current status: {student.get('status')}"
            )
        
        # Update student status to reserved_test
        await db.students.update_one(
            {"id": student_id},
            {
                "$set": {
                    "status": "reserved_test",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Log audit trail
        await log_audit(
            current_admin.id,
            "RESERVE_TEST",
            "Student",
            student_id,
            {
                "prev_status": "pending",
                "new_status": "reserved_test"
            }
        )
        
        return {
            "message": "Test reserved successfully",
            "student_id": student_id,
            "previous_status": "pending",
            "current_status": "reserved_test"
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error reserving test: {str(e)}")

@api_router.get("/admin/students/{student_id}/dashboard-preview")
async def get_student_dashboard_preview(
    student_id: str,
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Admin endpoint to preview how student dashboard looks"""
    try:
        # Get student info
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get parent info
        parent = await db.parents.find_one({"id": student["parent_id"]})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")
        
        # Clean student data
        if '_id' in student:
            del student['_id']
        
        # Build student info
        program_display = await get_program_display_name(
            student.get("branch", ""), 
            student.get("program_subtype", "regular")
        )
        
        student_info = StudentInfo(
            id=student["id"],
            name=student["name"],
            grade=student.get("grade", ""),
            birthdate=student.get("birthdate"),
            branch=student.get("branch", ""),
            program_subtype=student.get("program_subtype", "regular"),
            requires_exam=student.get("requires_exam", True),
            program_display=program_display
        )
        
        # Build all dashboard cards (same as parent view)
        admission_progress = await build_admission_progress_card(student["id"])
        exam_card = await build_exam_card(student["id"], student)
        timetable_card = await build_timetable_card(student["id"])
        homework_card = await build_homework_card(student["id"])
        attendance_card = await build_attendance_card(student["id"]) 
        billing_card = await build_billing_card(student["id"], parent["household_token"])
        notices_card = await build_notices_card(student["id"], student)
        resources_card = await build_resources_card(student["id"], parent["household_token"], student)
        
        # Build dashboard preview
        dashboard_preview = DashboardCardsResponse(
            student_info=student_info,
            admission_progress=admission_progress,
            exam=exam_card,
            timetable=timetable_card,
            homework=homework_card,
            attendance=attendance_card,
            billing=billing_card,
            notices=notices_card,
            resources=resources_card
        )
        
        return {
            "student_info": student_info,
            "parent_info": {
                "name": parent.get("name", ""),
                "email": parent.get("email", ""),
                "phone": parent.get("phone", ""),
                "household_token": parent["household_token"]
            },
            "dashboard": dashboard_preview,
            "admin_actions": {
                "can_update_status": True,
                "can_assign_class": not timetable_card.is_enrolled,
                "can_add_homework": timetable_card.is_enrolled,
                "can_record_attendance": timetable_card.is_enrolled
            }
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard preview: {str(e)}")

@api_router.post("/find-username")
async def find_username(request: FindUsernameRequest):
    """Find username by parent name, student name and birthdate"""
    try:
        # Find student by name and birthdate
        student = await db.students.find_one({
            "name": request.student_name,
            "birthdate": request.student_birthdate
        })
        
        if not student:
            # Don't reveal if student exists or not for security
            return {"message": "입력하신 정보로 계정을 찾을 수 없습니다. 정보를 다시 확인해주세요."}
        
        # Find parent by student's parent_id and name
        parent = await db.parents.find_one({
            "id": student["parent_id"],
            "name": request.parent_name
        })
        
        if not parent:
            return {"message": "입력하신 정보로 계정을 찾을 수 없습니다. 정보를 다시 확인해주세요."}
        
        # Find user account
        user = await db.users.find_one({"id": parent["user_id"]})
        
        if not user:
            return {"message": "입력하신 정보로 계정을 찾을 수 없습니다. 정보를 다시 확인해주세요."}
        
        # Log the account recovery attempt
        recovery_log = {
            "type": "username_recovery",
            "parent_name": request.parent_name,
            "student_name": request.student_name,
            "student_birthdate": request.student_birthdate,
            "found_email": user.get("email", ""),
            "user_id": user.get("id"),
            "ip": "system",  # Should get real IP
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.account_recovery_logs.insert_one(recovery_log)
        
        # In production, send this via SMS or secure method
        # For demo, we'll return the masked email
        email = user.get("email", "")
        if email:
            # Mask email for security: test***@example.com
            email_parts = email.split("@")
            if len(email_parts) == 2:
                username = email_parts[0]
                domain = email_parts[1]
                if len(username) > 3:
                    masked_username = username[:2] + "*" * (len(username) - 2)
                else:
                    masked_username = username[0] + "*" * (len(username) - 1)
                masked_email = f"{masked_username}@{domain}"
            else:
                masked_email = email
        else:
            masked_email = "이메일 정보 없음"
        
        return {
            "message": "계정을 찾았습니다!",
            "found_account": {
                "parent_name": parent.get("name", ""),
                "email": masked_email,
                "student_name": student.get("name", ""),
                "created_date": user.get("created_at", "")[:10] if user.get("created_at") else ""
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="계정 찾기 처리 중 오류가 발생했습니다.")

@api_router.post("/reset-password")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset via email"""
    try:
        # Look for user by email
        user = await db.users.find_one({"email": request.email.lower()})
        
        if not user:
            # Don't reveal if email exists or not for security
            return {"message": "비밀번호 재설정 링크를 이메일로 전송했습니다."}
        
        # Generate reset token (6 digits for simplicity)
        reset_token = str(random.randint(100000, 999999))
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
        
        # Save reset token
        reset_record = PasswordResetToken(
            email=request.email.lower(),
            reset_token=reset_token,
            expires_at=expires_at
        )
        
        reset_dict = reset_record.dict()
        reset_dict['created_at'] = reset_dict['created_at'].isoformat()
        reset_dict['expires_at'] = reset_dict['expires_at'].isoformat()
        
        await db.password_reset_tokens.insert_one(reset_dict)
        
        # In a real system, send email with reset_token
        print(f"Password reset token for {request.email}: {reset_token}")
        print(f"Token expires at: {expires_at}")
        
        # For demo purposes, we can return the token (NEVER do this in production)
        return {
            "message": "비밀번호 재설정 인증번호를 이메일로 전송했습니다.",
            "demo_token": reset_token,  # Remove this in production
            "demo_note": "실제 서비스에서는 이메일로만 전송됩니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="비밀번호 재설정 요청 처리 중 오류가 발생했습니다.")

@api_router.post("/reset-password/confirm")
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset with token and set new password"""
    try:
        # Find valid reset token
        reset_record = await db.password_reset_tokens.find_one({
            "email": request.email.lower(),
            "reset_token": request.reset_token,
            "used": False
        })
        
        if not reset_record:
            raise HTTPException(status_code=400, detail="잘못된 인증번호입니다.")
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(reset_record["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="인증번호가 만료되었습니다. 다시 요청해주세요.")
        
        # Find user and update password
        user = await db.users.find_one({"email": request.email.lower()})
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # Update password
        new_password_hash = hash_password(request.new_password)
        await db.users.update_one(
            {"id": user["id"]},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Mark reset token as used
        await db.password_reset_tokens.update_one(
            {"id": reset_record["id"]},
            {"$set": {"used": True}}
        )
        
        # Log password reset
        reset_log = {
            "type": "password_reset",
            "email": request.email,
            "user_id": user["id"],
            "reset_token_id": reset_record["id"],
            "ip": "system",  # Should get real IP
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.account_recovery_logs.insert_one(reset_log)
        
        return {"message": "비밀번호가 성공적으로 변경되었습니다. 새 비밀번호로 로그인해주세요."}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="비밀번호 변경 처리 중 오류가 발생했습니다.")

# RBAC System Utility Functions
async def initialize_rbac_system():
    """Initialize Role-Based Access Control system with default permissions and roles"""
    
    # Default permissions
    default_permissions = [
        # Student Management
        {"code": "can_view_student", "description": "학생 정보 조회", "category": "student"},
        {"code": "can_edit_student", "description": "학생 정보 수정", "category": "student"},
        {"code": "can_delete_student", "description": "학생 삭제", "category": "student"},
        {"code": "can_create_student", "description": "학생 등록", "category": "student"},
        
        # Class Management
        {"code": "can_view_class", "description": "반 정보 조회", "category": "class"},
        {"code": "can_edit_class", "description": "반 배정/수정", "category": "class"},
        {"code": "can_manage_attendance", "description": "출결 관리", "category": "class"},
        
        # Notice & Communication
        {"code": "can_send_notice", "description": "공지사항 발송", "category": "notice"},
        {"code": "can_send_sms", "description": "SMS 발송", "category": "notice"},
        
        # Payment Management  
        {"code": "can_manage_payment", "description": "결제 관리", "category": "payment"},
        {"code": "can_view_payment", "description": "결제 조회", "category": "payment"},
        
        # Exam Management
        {"code": "can_view_exam", "description": "시험 조회", "category": "exam"},
        {"code": "can_manage_exam", "description": "시험 관리", "category": "exam"},
        
        # System Administration
        {"code": "can_manage_admins", "description": "관리자 계정 관리", "category": "system"},
        {"code": "can_manage_permissions", "description": "권한 관리", "category": "system"},
        {"code": "can_view_audit_log", "description": "감사 로그 조회", "category": "system"},
    ]
    
    # Insert permissions if not exists
    for perm in default_permissions:
        existing = await db.permissions.find_one({"code": perm["code"]})
        if not existing:
            permission = Permission(**perm)
            perm_dict = permission.dict()
            perm_dict['created_at'] = perm_dict['created_at'].isoformat()
            await db.permissions.insert_one(perm_dict)
    
    # Default role permissions
    role_permissions = {
        "super_admin": [
            "can_view_student", "can_edit_student", "can_delete_student", "can_create_student",
            "can_view_class", "can_edit_class", "can_manage_attendance",
            "can_send_notice", "can_send_sms",
            "can_manage_payment", "can_view_payment",
            "can_view_exam", "can_manage_exam",
            "can_manage_admins", "can_manage_permissions", "can_view_audit_log"
        ],
        "kinder_admin": ["can_view_student", "can_view_class", "can_view_payment"],
        "junior_admin": ["can_view_student", "can_view_class", "can_view_payment"],
        "middle_admin": ["can_view_student", "can_view_class", "can_view_payment"]
    }
    
    # Insert role permissions
    for role, perms in role_permissions.items():
        for perm_code in perms:
            existing = await db.role_permissions.find_one({"role": role, "permission_code": perm_code})
            if not existing:
                role_perm = RolePermission(
                    role=role,
                    permission_code=perm_code,
                    default_value=True
                )
                role_perm_dict = role_perm.dict()
                role_perm_dict['created_at'] = role_perm_dict['created_at'].isoformat()
                await db.role_permissions.insert_one(role_perm_dict)
    
    return "RBAC system initialized successfully"

async def get_allowed_branches(admin_user_id: str) -> List[str]:
    """Get branches that an admin user is allowed to access"""
    branches = await db.admin_user_allowed_branches.find({"admin_user_id": admin_user_id}).to_list(10)
    return [branch["branch"] for branch in branches]

async def has_permission(admin_user_id: str, admin_role: str, permission_code: str) -> bool:
    """Check if admin user has specific permission"""
    
    # Check user-specific permission override first
    user_override = await db.admin_user_permissions.find_one({
        "admin_user_id": admin_user_id,
        "permission_code": permission_code
    })
    
    if user_override:
        return user_override["value"]
    
    # Check role default permission
    role_permission = await db.role_permissions.find_one({
        "role": admin_role,
        "permission_code": permission_code
    })
    
    return role_permission["default_value"] if role_permission else False

async def get_user_permissions(admin_user_id: str, admin_role: str) -> List[PermissionResponse]:
    """Get all permissions for an admin user"""
    
    # Get all permissions
    all_permissions = await db.permissions.find({}).to_list(100)
    
    result = []
    for perm in all_permissions:
        has_perm = await has_permission(admin_user_id, admin_role, perm["code"])
        result.append(PermissionResponse(
            code=perm["code"],
            description=perm["description"],
            category=perm["category"],
            has_permission=has_perm
        ))
    
    return result

async def set_admin_branches(admin_user_id: str, branches: List[str], granted_by: str):
    """Set allowed branches for an admin user"""
    
    # Remove existing branches
    await db.admin_user_allowed_branches.delete_many({"admin_user_id": admin_user_id})
    
    # Add new branches
    for branch in branches:
        branch_record = AdminUserAllowedBranch(
            admin_user_id=admin_user_id,
            branch=branch
        )
        branch_dict = branch_record.dict()
        branch_dict['created_at'] = branch_dict['created_at'].isoformat()
        await db.admin_user_allowed_branches.insert_one(branch_dict)
    
    # Log the change
    await log_audit(
        granted_by,
        "SET_ADMIN_BRANCHES",
        "Admin",
        admin_user_id,
        {"branches": branches}
    )

async def set_admin_permission(admin_user_id: str, permission_code: str, value: bool, granted_by: str):
    """Set specific permission for an admin user"""
    
    # Remove existing permission override
    await db.admin_user_permissions.delete_many({
        "admin_user_id": admin_user_id,
        "permission_code": permission_code
    })
    
    # Add new permission override
    perm_record = AdminUserPermission(
        admin_user_id=admin_user_id,
        permission_code=permission_code,
        value=value,
        granted_by=granted_by
    )
    perm_dict = perm_record.dict()
    perm_dict['created_at'] = perm_dict['created_at'].isoformat()
    await db.admin_user_permissions.insert_one(perm_dict)
    
    # Log the change
    await log_audit(
        granted_by,
        f"SET_PERMISSION:{permission_code}",
        "Admin",
        admin_user_id,
        {"permission": permission_code, "value": value}
    )

async def filter_students_by_admin_access(admin_user_id: str, admin_role: str) -> Dict[str, Any]:
    """Get students filtered by admin's allowed branches"""
    
    # Super admin sees all
    if admin_role == "super_admin":
        allowed_branches = ["kinder", "junior", "middle", "kinder_single"]
    else:
        allowed_branches = await get_allowed_branches(admin_user_id)
        
        # If no branches set, use role defaults
        if not allowed_branches:
            if admin_role == "kinder_admin":
                allowed_branches = ["kinder"]
            elif admin_role == "junior_admin":
                allowed_branches = ["junior", "kinder_single", "middle"]  # As requested
            elif admin_role == "middle_admin":
                allowed_branches = ["middle"]
    
    return {
        "allowed_branches": allowed_branches,
        "branch_filter": {"$in": allowed_branches} if allowed_branches else {}
    }

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

async def can_access_branch(admin_user_id: str, admin_role: str, branch: str) -> bool:
    """Check if admin user can access specific branch"""
    if admin_role == "super_admin":
        return True
    
    # Check user's allowed branches
    allowed_branches = await get_allowed_branches(admin_user_id)
    return branch in allowed_branches

async def send_status_change_notification(student_id: str, notification_type: str, data: Dict = None):
    """Send notification when student status changes"""
    try:
        student = await db.students.find_one({"id": student_id})
        if not student:
            return
        
        parent = await db.parents.find_one({"id": student["parent_id"]})
        if not parent:
            return
        
        notification_templates = {
            "admission_approved": "입학 승인되었습니다. 반 배정 안내를 기다려 주세요.",
            "class_assigned": f"반 배정이 완료되었습니다. 담임교사: {data.get('teacher', 'N/A')}",
            "status_leave": "휴학 처리가 완료되었습니다.",
            "status_withdrawn": "퇴원 처리가 완료되었습니다."
        }
        
        message = notification_templates.get(notification_type, f"상태가 변경되었습니다.")
        
        # Log notification (actual AlimTalk integration would go here)
        notification_log = {
            "student_id": student_id,
            "parent_phone": parent.get("phone", ""),
            "notification_type": notification_type,
            "message": message,
            "data": data or {},
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.notification_logs.insert_one(notification_log)
        print(f"Status change notification queued: {notification_type} for student {student['name']}")
        
    except Exception as e:
        print(f"Error sending status change notification: {str(e)}")

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
    
    # Create student record with birthdate and branch
    student = Student(
        parent_id=parent.id,
        name=user_data.student_name,
        grade="1",  # Default grade, can be updated later
        birthdate=user_data.student_birthdate,  # Add birthdate
        branch=user_data.branch,  # Add branch
        program_subtype="regular" if user_data.branch == "kinder" else "regular",
        requires_exam=False if user_data.branch == "kinder" else True
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
@api_router.post("/admin/create-with-role")
async def create_admin_with_role(admin_data: AdminCreateWithRole, current_admin: AdminResponse = Depends(get_current_admin)):
    """Create admin account with specific role (super_admin only)"""
    try:
        # Only super_admin can create admins with specific roles
        if current_admin.role not in ["admin", "super_admin"]:  # Temporarily allow admin for setup
            raise HTTPException(status_code=403, detail="Only super admin can create admin accounts with roles")
        
        # Validate role
        valid_roles = ["admin", "super_admin", "kinder_admin", "junior_admin", "middle_admin"]
        if admin_data.role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
        
        # Check if admin already exists
        existing_admin = await db.admins.find_one({"$or": [{"username": admin_data.username}, {"email": admin_data.email}]})
        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin already exists")
        
        # Create admin with specified role
        admin = Admin(
            username=admin_data.username,
            email=admin_data.email,
            password_hash=hash_password(admin_data.password),
            role=admin_data.role
        )
        
        admin_dict = admin.dict()
        admin_dict['created_at'] = admin_dict['created_at'].isoformat()
        admin_dict['last_login'] = None
        
        # Insert admin
        await db.admins.insert_one(admin_dict)
        
        # Log the creation
        await log_audit(
            current_admin.id,
            "CREATE_ADMIN",
            "Admin",
            admin.id,
            {"role": admin_data.role, "username": admin_data.username}
        )
        
        return {
            "message": f"Admin '{admin_data.username}' created successfully with role '{admin_data.role}'",
            "admin": AdminResponse(**admin_dict)
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error creating admin: {str(e)}")

@api_router.post("/admin/setup-default-admins")
async def setup_default_admin_accounts(current_admin: AdminResponse = Depends(get_current_admin)):
    """Create default admin accounts for each role type (setup only)"""
    try:
        # Only allow admin or super_admin to run setup
        if current_admin.role not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Only admin can setup default accounts")
        
        default_admins = [
            {"username": "super_admin", "email": "super@frage.edu", "password": "Super123!", "role": "super_admin"},
            {"username": "kinder_admin", "email": "kinder@frage.edu", "password": "Kinder123!", "role": "kinder_admin"},
            {"username": "junior_admin", "email": "junior@frage.edu", "password": "Junior123!", "role": "junior_admin"},
            {"username": "middle_admin", "email": "middle@frage.edu", "password": "Middle123!", "role": "middle_admin"}
        ]
        
        created_admins = []
        skipped_admins = []
        
        for admin_data in default_admins:
            # Check if admin already exists
            existing = await db.admins.find_one({"username": admin_data["username"]})
            if existing:
                skipped_admins.append(admin_data["username"])
                continue
            
            # Create admin
            admin = Admin(
                username=admin_data["username"],
                email=admin_data["email"],
                password_hash=hash_password(admin_data["password"]),
                role=admin_data["role"]
            )
            
            admin_dict = admin.dict()
            admin_dict['created_at'] = admin_dict['created_at'].isoformat()
            admin_dict['last_login'] = None
            
            await db.admins.insert_one(admin_dict)
            created_admins.append({"username": admin_data["username"], "role": admin_data["role"]})
            
            # Log the creation
            await log_audit(
                current_admin.id,
                "SETUP_DEFAULT_ADMIN",
                "Admin",
                admin.id,
                {"role": admin_data["role"], "username": admin_data["username"]}
            )
        
        return {
            "message": f"Setup complete. Created {len(created_admins)} admin accounts.",
            "created_admins": created_admins,
            "skipped_admins": skipped_admins
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error setting up default admins: {str(e)}")

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