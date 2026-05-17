"""HEMIS-style endpointlar: e'lonlar, to'lov, imtihon, bitiruv, kutubxona, yotoqxona, hujjatlar, suhbat."""
from datetime import date as date_type, datetime, time as time_type, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin, require_any, require_dekan, require_teacher
from app.database import get_oltp_db
from app.models.oltp.hemis import (
    Announcement,
    AnnouncementAudience,
    AnnouncementPriority,
    Book,
    BookCategory,
    BookLoan,
    BookLoanStatus,
    CoursePrerequisite,
    DocumentType,
    DormitoryAssignment,
    DormitoryBuilding,
    DormitoryRoom,
    ExamSchedule,
    ExamType,
    Message,
    Payment,
    PaymentStatus,
    PaymentType,
    Thesis,
    ThesisStatus,
    UserDocument,
)
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject
from app.models.oltp.teacher import Teacher
from app.models.oltp.user import User
from app.services import notification_service

router = APIRouter(tags=["HEMIS"])


# ============================================================
# 1. E'LONLAR
# ============================================================


class AnnouncementCreate(BaseModel):
    title: str = Field(..., max_length=256)
    body: str
    audience: AnnouncementAudience = AnnouncementAudience.ALL
    target_id: int | None = None
    priority: AnnouncementPriority = AnnouncementPriority.NORMAL
    image_url: str | None = None
    is_pinned: bool = False
    expires_at: datetime | None = None


@router.get("/announcements", dependencies=[Depends(require_any)])
def list_announcements(
    audience: AnnouncementAudience | None = None,
    pinned_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_oltp_db),
):
    """E'lonlar ro'yxati (yangi tepada, pin qilinganlar birinchi)."""
    q = db.query(Announcement)
    if audience:
        q = q.filter(Announcement.audience == audience)
    if pinned_only:
        q = q.filter(Announcement.is_pinned == True)  # noqa: E712
    items = q.order_by(Announcement.is_pinned.desc(), Announcement.published_at.desc()).limit(limit).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "body": a.body,
            "audience": a.audience.value,
            "priority": a.priority.value,
            "image_url": a.image_url,
            "is_pinned": a.is_pinned,
            "published_at": a.published_at.isoformat(),
            "expires_at": a.expires_at.isoformat() if a.expires_at else None,
        }
        for a in items
    ]


@router.post("/announcements", dependencies=[Depends(require_dekan)])
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    ann = Announcement(**payload.model_dump(), author_id=user.id)
    db.add(ann)
    db.commit()
    db.refresh(ann)

    # URGENT bo'lsa hammaga notification
    if payload.priority == AnnouncementPriority.URGENT:
        users = db.query(User).all()
        for u in users[:200]:
            notification_service.create_notification(
                db,
                user_id=u.id,
                title=f"📢 {payload.title}",
                message=payload.body[:200],
                notification_type="warning",
                link="/announcements",
            )

    return {"id": ann.id, "success": True}


@router.delete("/announcements/{ann_id}", dependencies=[Depends(require_dekan)])
def delete_announcement(ann_id: int, db: Session = Depends(get_oltp_db)):
    ann = db.query(Announcement).filter(Announcement.id == ann_id).first()
    if not ann:
        raise HTTPException(404)
    db.delete(ann)
    db.commit()
    return {"success": True}


# ============================================================
# 2. TO'LOV TIZIMI
# ============================================================


class PaymentCreate(BaseModel):
    student_id: int
    payment_type: PaymentType
    amount: float
    description: str | None = None
    academic_year: str | None = None
    due_date: date_type


class PaymentPay(BaseModel):
    amount: float
    method: str = "click"
    reference: str | None = None


def _payment_to_dict(p: Payment, db: Session) -> dict:
    st = db.query(Student).filter(Student.id == p.student_id).first()
    return {
        "id": p.id,
        "student_id": p.student_id,
        "student_name": st.full_name if st else None,
        "payment_type": p.payment_type.value,
        "amount": float(p.amount),
        "paid_amount": float(p.paid_amount),
        "remaining": float(p.amount) - float(p.paid_amount),
        "currency": p.currency,
        "status": p.status.value,
        "description": p.description,
        "academic_year": p.academic_year,
        "due_date": p.due_date.isoformat(),
        "paid_date": p.paid_date.isoformat() if p.paid_date else None,
        "payment_method": p.payment_method,
        "created_at": p.created_at.isoformat(),
    }


@router.get("/payments/my", dependencies=[Depends(require_any)])
def my_payments(
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    """Talaba o'z to'lovlarini ko'radi."""
    student = (
        db.query(Student)
        .filter((Student.email == user.email) | (Student.user_id == user.id))
        .first()
    )
    if not student and user.username == "student":
        student = db.query(Student).first()
    if not student:
        return {"total_due": 0, "items": []}
    items = db.query(Payment).filter(Payment.student_id == student.id).order_by(Payment.due_date.desc()).all()
    total_due = sum(float(p.amount) - float(p.paid_amount) for p in items if p.status != PaymentStatus.PAID)
    total_paid = sum(float(p.paid_amount) for p in items)
    return {
        "total_due": total_due,
        "total_paid": total_paid,
        "items": [_payment_to_dict(p, db) for p in items],
    }


@router.get("/payments", dependencies=[Depends(require_dekan)])
def list_payments(
    status: PaymentStatus | None = None,
    student_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_oltp_db),
):
    q = db.query(Payment)
    if status:
        q = q.filter(Payment.status == status)
    if student_id:
        q = q.filter(Payment.student_id == student_id)
    total = q.count()
    items = q.order_by(Payment.due_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [_payment_to_dict(p, db) for p in items]}


@router.post("/payments", dependencies=[Depends(require_admin)])
def create_payment(payload: PaymentCreate, db: Session = Depends(get_oltp_db)):
    p = Payment(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _payment_to_dict(p, db)


@router.post("/payments/{payment_id}/pay", dependencies=[Depends(require_any)])
def pay_payment(payment_id: int, payload: PaymentPay, db: Session = Depends(get_oltp_db)):
    """To'lov amalga oshirish (demo)."""
    p = db.query(Payment).filter(Payment.id == payment_id).first()
    if not p:
        raise HTTPException(404)
    p.paid_amount = float(p.paid_amount) + payload.amount
    p.payment_method = payload.method
    p.reference = payload.reference
    p.paid_date = date_type.today()
    if float(p.paid_amount) >= float(p.amount):
        p.status = PaymentStatus.PAID
    db.commit()
    return _payment_to_dict(p, db)


@router.get("/payments/summary", dependencies=[Depends(require_dekan)])
def payment_summary(db: Session = Depends(get_oltp_db)):
    payments = db.query(Payment).all()
    total = sum(float(p.amount) for p in payments)
    paid = sum(float(p.paid_amount) for p in payments)
    overdue = sum(
        float(p.amount) - float(p.paid_amount)
        for p in payments
        if p.status != PaymentStatus.PAID and p.due_date < date_type.today()
    )
    return {
        "total_billed": total,
        "total_collected": paid,
        "total_pending": total - paid,
        "total_overdue": overdue,
        "collection_rate": round(paid * 100 / total, 2) if total > 0 else 0,
        "count_pending": sum(1 for p in payments if p.status == PaymentStatus.PENDING),
        "count_paid": sum(1 for p in payments if p.status == PaymentStatus.PAID),
    }


# ============================================================
# 3. IMTIHON JADVALI
# ============================================================


class ExamCreate(BaseModel):
    subject_id: int
    group_id: int
    teacher_id: int
    exam_type: ExamType
    exam_date: date_type
    start_time: time_type
    duration_minutes: int = 90
    room: str | None = None
    notes: str | None = None
    academic_year: str
    semester: str


def _exam_to_dict(e: ExamSchedule, db: Session) -> dict:
    subj = db.query(Subject).filter(Subject.id == e.subject_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == e.teacher_id).first()
    return {
        "id": e.id,
        "subject_id": e.subject_id,
        "subject_name": subj.name if subj else None,
        "subject_code": subj.code if subj else None,
        "teacher_id": e.teacher_id,
        "teacher_name": teacher.full_name if teacher else None,
        "group_id": e.group_id,
        "exam_type": e.exam_type.value,
        "exam_date": e.exam_date.isoformat(),
        "start_time": e.start_time.isoformat() if e.start_time else None,
        "duration_minutes": e.duration_minutes,
        "room": e.room,
        "notes": e.notes,
        "academic_year": e.academic_year,
        "semester": e.semester,
    }


@router.get("/exams", dependencies=[Depends(require_any)])
def list_exams(
    group_id: int | None = None,
    academic_year: str | None = None,
    semester: str | None = None,
    db: Session = Depends(get_oltp_db),
):
    q = db.query(ExamSchedule)
    if group_id:
        q = q.filter(ExamSchedule.group_id == group_id)
    if academic_year:
        q = q.filter(ExamSchedule.academic_year == academic_year)
    if semester:
        q = q.filter(ExamSchedule.semester == semester)
    items = q.order_by(ExamSchedule.exam_date, ExamSchedule.start_time).all()
    return [_exam_to_dict(e, db) for e in items]


@router.post("/exams", dependencies=[Depends(require_teacher)])
def create_exam(payload: ExamCreate, db: Session = Depends(get_oltp_db)):
    e = ExamSchedule(**payload.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return _exam_to_dict(e, db)


# ============================================================
# 4. BITIRUV ISHI (Thesis)
# ============================================================


class ThesisCreate(BaseModel):
    student_id: int
    supervisor_id: int
    title: str = Field(..., max_length=512)
    abstract: str | None = None
    keywords: str | None = None
    academic_year: str


class ThesisUpdate(BaseModel):
    title: str | None = None
    abstract: str | None = None
    keywords: str | None = None
    status: ThesisStatus | None = None
    file_url: str | None = None
    defense_date: date_type | None = None
    defense_grade: float | None = None


def _thesis_to_dict(t: Thesis, db: Session) -> dict:
    student = db.query(Student).filter(Student.id == t.student_id).first()
    supervisor = db.query(Teacher).filter(Teacher.id == t.supervisor_id).first()
    return {
        "id": t.id,
        "student_id": t.student_id,
        "student_name": student.full_name if student else None,
        "supervisor_id": t.supervisor_id,
        "supervisor_name": supervisor.full_name if supervisor else None,
        "title": t.title,
        "abstract": t.abstract,
        "keywords": t.keywords,
        "status": t.status.value,
        "file_url": t.file_url,
        "defense_date": t.defense_date.isoformat() if t.defense_date else None,
        "defense_grade": float(t.defense_grade) if t.defense_grade else None,
        "academic_year": t.academic_year,
    }


@router.get("/theses", dependencies=[Depends(require_any)])
def list_theses(
    status: ThesisStatus | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_oltp_db),
):
    q = db.query(Thesis)
    if status:
        q = q.filter(Thesis.status == status)
    if student_id:
        q = q.filter(Thesis.student_id == student_id)
    return [_thesis_to_dict(t, db) for t in q.all()]


@router.post("/theses", dependencies=[Depends(require_dekan)])
def create_thesis(payload: ThesisCreate, db: Session = Depends(get_oltp_db)):
    t = Thesis(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return _thesis_to_dict(t, db)


@router.put("/theses/{thesis_id}", dependencies=[Depends(require_teacher)])
def update_thesis(thesis_id: int, payload: ThesisUpdate, db: Session = Depends(get_oltp_db)):
    t = db.query(Thesis).filter(Thesis.id == thesis_id).first()
    if not t:
        raise HTTPException(404)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return _thesis_to_dict(t, db)


# ============================================================
# 5. KITOBXONA
# ============================================================


class BookCreate(BaseModel):
    isbn: str | None = None
    title: str
    author: str
    publisher: str | None = None
    year: int | None = None
    category: BookCategory = BookCategory.TEXTBOOK
    language: str = "uz"
    pages: int | None = None
    description: str | None = None
    cover_url: str | None = None
    total_copies: int = 1


class BookLoanCreate(BaseModel):
    book_id: int
    student_id: int
    days: int = 14


@router.get("/library/books", dependencies=[Depends(require_any)])
def list_books(
    category: BookCategory | None = None,
    search: str | None = None,
    available_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_oltp_db),
):
    q = db.query(Book)
    if category:
        q = q.filter(Book.category == category)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))
    if available_only:
        q = q.filter(Book.available_copies > 0)
    total = q.count()
    items = q.order_by(Book.title).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [
            {
                "id": b.id,
                "isbn": b.isbn,
                "title": b.title,
                "author": b.author,
                "publisher": b.publisher,
                "year": b.year,
                "category": b.category.value,
                "language": b.language,
                "pages": b.pages,
                "description": b.description,
                "cover_url": b.cover_url,
                "total_copies": b.total_copies,
                "available_copies": b.available_copies,
            }
            for b in items
        ],
    }


@router.post("/library/books", dependencies=[Depends(require_admin)])
def create_book(payload: BookCreate, db: Session = Depends(get_oltp_db)):
    b = Book(**payload.model_dump(), available_copies=payload.total_copies)
    db.add(b)
    db.commit()
    db.refresh(b)
    return {"id": b.id, "title": b.title}


@router.post("/library/loans", dependencies=[Depends(require_admin)])
def loan_book(payload: BookLoanCreate, db: Session = Depends(get_oltp_db)):
    book = db.query(Book).filter(Book.id == payload.book_id).first()
    if not book:
        raise HTTPException(404, "Kitob topilmadi")
    if book.available_copies < 1:
        raise HTTPException(400, "Kitob mavjud emas")
    book.available_copies -= 1
    loan = BookLoan(
        book_id=payload.book_id,
        student_id=payload.student_id,
        due_date=date_type.today() + timedelta(days=payload.days),
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return {"id": loan.id, "due_date": loan.due_date.isoformat()}


@router.post("/library/loans/{loan_id}/return", dependencies=[Depends(require_admin)])
def return_book(loan_id: int, db: Session = Depends(get_oltp_db)):
    loan = db.query(BookLoan).filter(BookLoan.id == loan_id).first()
    if not loan:
        raise HTTPException(404)
    loan.return_date = date_type.today()
    loan.status = BookLoanStatus.RETURNED
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if book:
        book.available_copies += 1
    db.commit()
    return {"success": True}


@router.get("/library/my-loans", dependencies=[Depends(require_any)])
def my_loans(
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    student = (
        db.query(Student)
        .filter((Student.email == user.email) | (Student.user_id == user.id))
        .first()
    )
    if not student and user.username == "student":
        student = db.query(Student).first()
    if not student:
        return []
    loans = (
        db.query(BookLoan).filter(BookLoan.student_id == student.id).order_by(BookLoan.loan_date.desc()).all()
    )
    return [
        {
            "id": l.id,
            "book_id": l.book_id,
            "book_title": (db.query(Book).filter(Book.id == l.book_id).first().title if l.book_id else None),
            "loan_date": l.loan_date.isoformat(),
            "due_date": l.due_date.isoformat(),
            "return_date": l.return_date.isoformat() if l.return_date else None,
            "status": l.status.value,
            "fine_amount": float(l.fine_amount),
        }
        for l in loans
    ]


# ============================================================
# 6. YOTOQXONA
# ============================================================


@router.get("/dormitory/rooms", dependencies=[Depends(require_any)])
def list_rooms(db: Session = Depends(get_oltp_db)):
    rooms = db.query(DormitoryRoom).all()
    items = []
    for r in rooms:
        occupied = (
            db.query(DormitoryAssignment)
            .filter(DormitoryAssignment.room_id == r.id, DormitoryAssignment.is_active == True)  # noqa: E712
            .count()
        )
        building = db.query(DormitoryBuilding).filter(DormitoryBuilding.id == r.building_id).first()
        items.append({
            "id": r.id,
            "building_id": r.building_id,
            "building_name": building.name if building else None,
            "room_number": r.room_number,
            "floor": r.floor,
            "capacity": r.capacity,
            "occupied": occupied,
            "available": r.capacity - occupied,
            "gender": r.gender,
            "monthly_fee": float(r.monthly_fee),
        })
    return items


class DormitoryAssign(BaseModel):
    room_id: int
    student_id: int


@router.post("/dormitory/assign", dependencies=[Depends(require_admin)])
def assign_to_room(payload: DormitoryAssign, db: Session = Depends(get_oltp_db)):
    existing = (
        db.query(DormitoryAssignment)
        .filter(DormitoryAssignment.student_id == payload.student_id, DormitoryAssignment.is_active == True)  # noqa: E712
        .first()
    )
    if existing:
        raise HTTPException(409, "Talaba allaqachon xonaga biriktirilgan")
    room = db.query(DormitoryRoom).filter(DormitoryRoom.id == payload.room_id).first()
    if not room:
        raise HTTPException(404)
    occupied = (
        db.query(DormitoryAssignment)
        .filter(DormitoryAssignment.room_id == payload.room_id, DormitoryAssignment.is_active == True)  # noqa: E712
        .count()
    )
    if occupied >= room.capacity:
        raise HTTPException(400, "Xona to'la")
    a = DormitoryAssignment(room_id=payload.room_id, student_id=payload.student_id)
    db.add(a)
    db.commit()
    return {"success": True}


@router.get("/dormitory/my", dependencies=[Depends(require_any)])
def my_dormitory(
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    student = (
        db.query(Student)
        .filter((Student.email == user.email) | (Student.user_id == user.id))
        .first()
    )
    if not student and user.username == "student":
        student = db.query(Student).first()
    if not student:
        return None
    a = (
        db.query(DormitoryAssignment)
        .filter(DormitoryAssignment.student_id == student.id, DormitoryAssignment.is_active == True)  # noqa: E712
        .first()
    )
    if not a:
        return None
    room = db.query(DormitoryRoom).filter(DormitoryRoom.id == a.room_id).first()
    building = db.query(DormitoryBuilding).filter(DormitoryBuilding.id == room.building_id).first() if room else None
    return {
        "building_name": building.name if building else None,
        "room_number": room.room_number if room else None,
        "floor": room.floor if room else None,
        "check_in_date": a.check_in_date.isoformat(),
        "monthly_fee": float(room.monthly_fee) if room else 0,
    }


# ============================================================
# 7. DOCUMENT STORAGE
# ============================================================


class DocumentRegister(BaseModel):
    document_type: DocumentType
    title: str
    file_url: str
    file_size: int | None = None
    mime_type: str | None = None


@router.get("/documents/my", dependencies=[Depends(require_any)])
def my_documents(
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    docs = db.query(UserDocument).filter(UserDocument.user_id == user.id).all()
    return [
        {
            "id": d.id,
            "document_type": d.document_type.value,
            "title": d.title,
            "file_url": d.file_url,
            "file_size": d.file_size,
            "is_verified": d.is_verified,
            "uploaded_at": d.uploaded_at.isoformat(),
        }
        for d in docs
    ]


@router.post("/documents", dependencies=[Depends(require_any)])
def register_document(
    payload: DocumentRegister,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    doc = UserDocument(user_id=user.id, **payload.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id}


@router.delete("/documents/{doc_id}", dependencies=[Depends(require_any)])
def delete_document(
    doc_id: int,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    doc = db.query(UserDocument).filter(UserDocument.id == doc_id, UserDocument.user_id == user.id).first()
    if not doc:
        raise HTTPException(404)
    db.delete(doc)
    db.commit()
    return {"success": True}


# ============================================================
# 8. MESSAGING
# ============================================================


class MessageCreate(BaseModel):
    recipient_id: int
    subject: str | None = None
    body: str
    parent_id: int | None = None


@router.get("/messages", dependencies=[Depends(require_any)])
def list_messages(
    folder: Literal["inbox", "sent"] = "inbox",
    unread_only: bool = False,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    if folder == "inbox":
        q = db.query(Message).filter(Message.recipient_id == user.id)
    else:
        q = db.query(Message).filter(Message.sender_id == user.id)
    if unread_only:
        q = q.filter(Message.is_read == False)  # noqa: E712
    msgs = q.order_by(Message.sent_at.desc()).limit(200).all()
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": (db.query(User).filter(User.id == m.sender_id).first().full_name if m.sender_id else None),
            "recipient_id": m.recipient_id,
            "recipient_name": (db.query(User).filter(User.id == m.recipient_id).first().full_name if m.recipient_id else None),
            "subject": m.subject,
            "body": m.body,
            "is_read": m.is_read,
            "sent_at": m.sent_at.isoformat(),
        }
        for m in msgs
    ]


@router.post("/messages", dependencies=[Depends(require_any)])
def send_message(
    payload: MessageCreate,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    m = Message(sender_id=user.id, **payload.model_dump())
    db.add(m)
    db.commit()
    # Notify recipient
    notification_service.create_notification(
        db,
        user_id=payload.recipient_id,
        title=f"Yangi xabar: {user.full_name}",
        message=payload.body[:100],
        notification_type="info",
        link="/messages",
    )
    return {"id": m.id}


@router.post("/messages/{msg_id}/read", dependencies=[Depends(require_any)])
def mark_message_read(
    msg_id: int,
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    m = db.query(Message).filter(Message.id == msg_id, Message.recipient_id == user.id).first()
    if not m:
        raise HTTPException(404)
    m.is_read = True
    m.read_at = datetime.utcnow()
    db.commit()
    return {"success": True}


# ============================================================
# 9. KALENDAR EVENTS (jamlash)
# ============================================================


@router.get("/calendar/events", dependencies=[Depends(require_any)])
def calendar_events(
    start: date_type,
    end: date_type,
    db: Session = Depends(get_oltp_db),
):
    """Berilgan oraliqdagi barcha tadbirlar: jadval, imtihon, e'lon."""
    from app.models.oltp.schedule import ScheduleEntry

    events = []

    # Imtihonlar
    exams = (
        db.query(ExamSchedule)
        .filter(and_(ExamSchedule.exam_date >= start, ExamSchedule.exam_date <= end))
        .all()
    )
    for e in exams:
        subj = db.query(Subject).filter(Subject.id == e.subject_id).first()
        events.append({
            "id": f"exam-{e.id}",
            "title": f"📝 {subj.name if subj else 'Imtihon'}",
            "date": e.exam_date.isoformat(),
            "type": "exam",
            "color": "#ef4444",
            "room": e.room,
        })

    # E'lonlar
    anns = (
        db.query(Announcement)
        .filter(Announcement.published_at >= datetime.combine(start, time_type.min))
        .filter(Announcement.published_at <= datetime.combine(end, time_type.max))
        .all()
    )
    for a in anns:
        events.append({
            "id": f"ann-{a.id}",
            "title": f"📢 {a.title}",
            "date": a.published_at.date().isoformat(),
            "type": "announcement",
            "color": "#f59e0b" if a.priority != AnnouncementPriority.NORMAL else "#3b82f6",
        })

    return events


# ============================================================
# 10. COURSE PREREQUISITES
# ============================================================


@router.get("/courses/prerequisites/{subject_id}", dependencies=[Depends(require_any)])
def get_prerequisites(subject_id: int, db: Session = Depends(get_oltp_db)):
    prereqs = db.query(CoursePrerequisite).filter(CoursePrerequisite.subject_id == subject_id).all()
    items = []
    for p in prereqs:
        prereq_subj = db.query(Subject).filter(Subject.id == p.prerequisite_id).first()
        items.append({
            "prerequisite_id": p.prerequisite_id,
            "prerequisite_name": prereq_subj.name if prereq_subj else None,
            "prerequisite_code": prereq_subj.code if prereq_subj else None,
            "min_grade": float(p.min_grade),
            "is_required": p.is_required,
        })
    return items


class PrerequisiteCreate(BaseModel):
    subject_id: int
    prerequisite_id: int
    min_grade: float = 55.0
    is_required: bool = True


@router.post("/courses/prerequisites", dependencies=[Depends(require_admin)])
def add_prerequisite(payload: PrerequisiteCreate, db: Session = Depends(get_oltp_db)):
    if payload.subject_id == payload.prerequisite_id:
        raise HTTPException(400, "Fan o'ziga prerequisite bo'la olmaydi")
    p = CoursePrerequisite(**payload.model_dump())
    db.add(p)
    db.commit()
    return {"id": p.id}
