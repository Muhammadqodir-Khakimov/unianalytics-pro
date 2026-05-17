"""SQLAlchemy modellari — OLTP va OLAP."""
from app.models.oltp.user import User, UserRole
from app.models.oltp.faculty import Faculty, Specialty, Group
from app.models.oltp.student import Student
from app.models.oltp.teacher import Teacher
from app.models.oltp.subject import Subject
from app.models.oltp.grade import Grade, AssessmentType
from app.models.oltp.audit import AuditLog
from app.models.oltp.notification import Notification
from app.models.oltp.schedule import ScheduleEntry, AttendanceRecord
from app.models.oltp.application import Application
from app.models.oltp.hemis import (
    Announcement,
    Book,
    BookLoan,
    CoursePrerequisite,
    DormitoryAssignment,
    DormitoryBuilding,
    DormitoryRoom,
    ExamSchedule,
    Message,
    Payment,
    Thesis,
    UserDocument,
)
from app.models.oltp.tenant import Permission, RolePermission, Tenant, Webhook
from app.models.oltp.billing import Invoice, Subscription

from app.models.olap.dim_student import DimStudent
from app.models.olap.dim_subject import DimSubject
from app.models.olap.dim_teacher import DimTeacher
from app.models.olap.dim_time import DimTime
from app.models.olap.dim_faculty import DimFaculty
from app.models.olap.dim_assessment import DimAssessmentType
from app.models.olap.fact_grades import FactStudentGrade

__all__ = [
    # OLTP
    "User",
    "UserRole",
    "Faculty",
    "Specialty",
    "Group",
    "Student",
    "Teacher",
    "Subject",
    "Grade",
    "AssessmentType",
    # OLAP
    "DimStudent",
    "DimSubject",
    "DimTeacher",
    "DimTime",
    "DimFaculty",
    "DimAssessmentType",
    "FactStudentGrade",
]
