"""HEMIS-style modellar: e'lonlar, to'lov, imtihon, bitiruv ishi, kutubxona, yotoqxona, hujjatlar, suhbat, prerequisites."""
from datetime import date, datetime, time
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import OLTPBase


# ============================================================
# 1. E'LONLAR (Announcements)
# ============================================================


class AnnouncementAudience(str, Enum):
    ALL = "all"
    STUDENTS = "students"
    TEACHERS = "teachers"
    FACULTY = "faculty"
    GROUP = "group"


class AnnouncementPriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Announcement(OLTPBase):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[AnnouncementAudience] = mapped_column(
        SAEnum(AnnouncementAudience, name="audience_type"),
        default=AnnouncementAudience.ALL,
        index=True,
    )
    target_id: Mapped[int | None] = mapped_column(Integer)  # faculty_id yoki group_id
    priority: Mapped[AnnouncementPriority] = mapped_column(
        SAEnum(AnnouncementPriority, name="ann_priority"),
        default=AnnouncementPriority.NORMAL,
    )
    image_url: Mapped[str | None] = mapped_column(String(512))
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)


# ============================================================
# 2. TO'LOV TIZIMI (Payments)
# ============================================================


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentType(str, Enum):
    CONTRACT = "contract"  # Asosiy kontrakt
    DORMITORY = "dormitory"  # Yotoqxona
    LIBRARY_FINE = "library_fine"  # Kitob jarima
    OTHER = "other"


class Payment(OLTPBase):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    payment_type: Mapped[PaymentType] = mapped_column(SAEnum(PaymentType, name="payment_type"))
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(8), default="UZS")
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, name="payment_status"), default=PaymentStatus.PENDING, index=True
    )
    description: Mapped[str | None] = mapped_column(String(512))
    academic_year: Mapped[str | None] = mapped_column(String(16), index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    paid_date: Mapped[date | None] = mapped_column(Date)
    payment_method: Mapped[str | None] = mapped_column(String(64))  # click/payme/bank/cash
    reference: Mapped[str | None] = mapped_column(String(128))  # transaction id
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============================================================
# 3. IMTIHON JADVALI (Exam Schedule)
# ============================================================


class ExamType(str, Enum):
    MIDTERM = "midterm"  # Oraliq
    FINAL = "final"  # Yakuniy
    RETAKE = "retake"  # Qayta topshirish
    STATE = "state"  # Davlat
    THESIS = "thesis"  # Bitiruv


class ExamSchedule(OLTPBase):
    __tablename__ = "exam_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    exam_type: Mapped[ExamType] = mapped_column(SAEnum(ExamType, name="exam_type"))
    exam_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=90)
    room: Mapped[str | None] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(String(512))
    academic_year: Mapped[str] = mapped_column(String(16), index=True)
    semester: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============================================================
# 4. BITIRUV ISHI (Thesis)
# ============================================================


class ThesisStatus(str, Enum):
    DRAFT = "draft"  # Ko'rib chiqilmoqda
    APPROVED = "approved"  # Mavzu tasdiqlandi
    IN_PROGRESS = "in_progress"  # Yozilmoqda
    SUBMITTED = "submitted"  # Topshirildi
    DEFENDED = "defended"  # Himoya qilindi
    REJECTED = "rejected"


class Thesis(OLTPBase):
    __tablename__ = "theses"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), unique=True, index=True)
    supervisor_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text)
    keywords: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[ThesisStatus] = mapped_column(
        SAEnum(ThesisStatus, name="thesis_status"), default=ThesisStatus.DRAFT, index=True
    )
    file_url: Mapped[str | None] = mapped_column(String(512))
    defense_date: Mapped[date | None] = mapped_column(Date)
    defense_grade: Mapped[float | None] = mapped_column(Numeric(5, 2))
    academic_year: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================
# 5. KITOBXONA (Library)
# ============================================================


class BookCategory(str, Enum):
    TEXTBOOK = "textbook"  # Darslik
    SCIENTIFIC = "scientific"  # Ilmiy
    FICTION = "fiction"  # Badiiy
    REFERENCE = "reference"  # Ma'lumotnoma
    JOURNAL = "journal"  # Jurnal


class Book(OLTPBase):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str | None] = mapped_column(String(32), unique=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(256))
    publisher: Mapped[str | None] = mapped_column(String(256))
    year: Mapped[int | None] = mapped_column(Integer)
    category: Mapped[BookCategory] = mapped_column(
        SAEnum(BookCategory, name="book_category"), default=BookCategory.TEXTBOOK, index=True
    )
    language: Mapped[str] = mapped_column(String(16), default="uz")
    pages: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(512))
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BookLoanStatus(str, Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"


class BookLoan(OLTPBase):
    __tablename__ = "book_loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    loan_date: Mapped[date] = mapped_column(Date, default=date.today)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    return_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[BookLoanStatus] = mapped_column(
        SAEnum(BookLoanStatus, name="book_loan_status"), default=BookLoanStatus.ACTIVE, index=True
    )
    fine_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    notes: Mapped[str | None] = mapped_column(String(256))


# ============================================================
# 6. YOTOQXONA (Dormitory)
# ============================================================


class DormitoryBuilding(OLTPBase):
    __tablename__ = "dormitory_buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    address: Mapped[str | None] = mapped_column(String(256))
    total_rooms: Mapped[int] = mapped_column(Integer, default=0)


class DormitoryRoom(OLTPBase):
    __tablename__ = "dormitory_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("dormitory_buildings.id"))
    room_number: Mapped[str] = mapped_column(String(16))
    floor: Mapped[int] = mapped_column(Integer)
    capacity: Mapped[int] = mapped_column(Integer, default=4)
    gender: Mapped[str] = mapped_column(String(1), default="M")  # M / F / X (aralash)
    monthly_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)


class DormitoryAssignment(OLTPBase):
    __tablename__ = "dormitory_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("dormitory_rooms.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), unique=True, index=True)
    check_in_date: Mapped[date] = mapped_column(Date, default=date.today)
    check_out_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(String(256))


# ============================================================
# 7. DOCUMENT STORAGE (Shaxsiy hujjatlar)
# ============================================================


class DocumentType(str, Enum):
    PASSPORT = "passport"
    ATTESTAT = "attestat"  # 11-sinf attestati
    DIPLOMA = "diploma"  # Oldingi diplom
    CERTIFICATE = "certificate"  # Sertifikat
    MEDICAL = "medical"  # Tibbiy ma'lumotnoma
    OTHER = "other"


class UserDocument(OLTPBase):
    __tablename__ = "user_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type"), index=True
    )
    title: Mapped[str] = mapped_column(String(256))
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer)  # bytes
    mime_type: Mapped[str | None] = mapped_column(String(64))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============================================================
# 8. STUDENT-TEACHER MESSAGING
# ============================================================


class Message(OLTPBase):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    subject: Mapped[str | None] = mapped_column(String(256))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("messages.id"))  # reply
    attachment_url: Mapped[str | None] = mapped_column(String(512))
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime)


# ============================================================
# 9. COURSE PREREQUISITES (oldingi fanlar)
# ============================================================


class CoursePrerequisite(OLTPBase):
    __tablename__ = "course_prerequisites"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    prerequisite_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    min_grade: Mapped[float] = mapped_column(Numeric(5, 2), default=55.0)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
