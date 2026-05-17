"""Test ma'lumotlarini OLTP databazaga yuklash.

Ishga tushirish:
    docker-compose exec backend python scripts/seed_data.py

Hajm (default):
    - 5 fakultet, 15 yo'nalish, 60 guruh
    - 5000 talaba, 200 o'qituvchi, 80 fan
    - 50,000+ baho (3 yillik tarix)
"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from faker import Faker
from loguru import logger
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database import OLTPBase, oltp_engine, oltp_session
from app.models.oltp.faculty import Faculty, Group, Specialty
from app.models.oltp.grade import AssessmentType, Grade
from app.models.oltp.student import EducationForm, Gender, Student, StudentStatus
from app.models.oltp.subject import Subject, SubjectType
from app.models.oltp.teacher import Teacher
from app.models.oltp.user import User, UserRole

# uz_UZ locale faker da bo'lmasligi mumkin — ru_RU ishlatamiz
try:
    fake = Faker("uz_UZ")
except (AttributeError, KeyError):
    fake = Faker("ru_RU")
random.seed(42)
Faker.seed(42)

FACULTIES = [
    {"name": "Fizika-Matematika", "code": "FM", "specs": ["Amaliy matematika", "Fizika", "Matematika"]},
    {"name": "Informatika", "code": "INF", "specs": ["Dasturiy injiniring", "Axborot xavfsizligi", "Sun'iy intellekt"]},
    {"name": "Iqtisodiyot", "code": "ECO", "specs": ["Biznes boshqaruv", "Buxgalteriya", "Moliya"]},
    {"name": "Filologiya", "code": "PHI", "specs": ["O'zbek tili", "Ingliz tili", "Rus tili"]},
    {"name": "Tarix", "code": "HIS", "specs": ["Umumiy tarix", "O'zbekiston tarixi", "Arxeologiya"]},
]

SUBJECTS_BY_DEPT = {
    "FM": ["Matematik analiz", "Algebra", "Geometriya", "Fizika", "Diskret matematika", "Differensial tenglamalar"],
    "INF": ["Dasturlash asoslari", "Algoritmlar", "Ma'lumotlar bazasi", "Tarmoq texnologiyalari",
            "Veb-dasturlash", "Sun'iy intellekt", "Mashinaviy o'rganish", "Operatsion tizimlar"],
    "ECO": ["Mikroiqtisodiyot", "Makroiqtisodiyot", "Buxgalteriya hisobi", "Marketing", "Menejment"],
    "PHI": ["O'zbek tili", "Ingliz tili", "Rus tili", "Adabiyot tarixi", "Tilshunoslik"],
    "HIS": ["Jahon tarixi", "O'zbekiston tarixi", "Arxeologiya", "Etnografiya"],
}

ASSESSMENT_TYPES = [
    ("JN", "Joriy nazorat", 30.0),
    ("ON", "Oraliq nazorat", 30.0),
    ("YN", "Yakuniy nazorat", 30.0),
    ("Mustaqil ish", "Mustaqil ish bahosi", 10.0),
]

CURRENT_YEAR = 2025


def reset_database():
    """Barcha jadvallarni qayta yaratish."""
    logger.warning("OLTP databazadagi barcha jadvallar o'chirilib qayta yaratiladi...")
    OLTPBase.metadata.drop_all(bind=oltp_engine)
    OLTPBase.metadata.create_all(bind=oltp_engine)
    logger.info("Jadvallar tayyor.")


def create_users(db: Session):
    """4 ta rol uchun test userlar."""
    users = [
        ("admin", "admin@university.uz", "Admin User", "admin123", UserRole.ADMIN),
        ("dekan", "dekan@university.uz", "Dekan Dekanov", "dekan123", UserRole.DEKAN),
        ("teacher", "teacher@university.uz", "O'qituvchi Test", "teacher123", UserRole.TEACHER),
        ("student", "student@university.uz", "Talaba Test", "student123", UserRole.STUDENT),
    ]
    for username, email, full_name, password, role in users:
        u = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            is_active=True,
            is_verified=True,
        )
        db.add(u)
    db.commit()
    logger.info("4 ta test foydalanuvchi yaratildi.")


def create_faculties(db: Session) -> list[Faculty]:
    objs = []
    for f in FACULTIES:
        fac = Faculty(name=f["name"], code=f["code"], description=f"{f['name']} fakulteti")
        db.add(fac)
        objs.append(fac)
    db.commit()
    for fac in objs:
        db.refresh(fac)
    logger.info("{} ta fakultet yaratildi.", len(objs))
    return objs


def create_specialties(db: Session, faculties: list[Faculty]) -> list[Specialty]:
    specs = []
    for fac, fac_data in zip(faculties, FACULTIES):
        for spec_name in fac_data["specs"]:
            sp = Specialty(
                name=spec_name,
                code=f"{fac.code}-{spec_name[:3].upper()}",
                faculty_id=fac.id,
            )
            db.add(sp)
            specs.append(sp)
    db.commit()
    for s in specs:
        db.refresh(s)
    logger.info("{} ta yo'nalish yaratildi.", len(specs))
    return specs


def create_groups(db: Session, specialties: list[Specialty]) -> list[Group]:
    groups = []
    for sp in specialties:
        # Har bir yo'nalish uchun 4 kurs * 1 guruh = 4 guruh (jami 60 ga yaqin)
        for course in range(1, 5):
            enrollment_year = CURRENT_YEAR - course + 1
            g = Group(
                name=f"{sp.code}-{course}{random.randint(1, 9)}{enrollment_year % 100:02d}",
                course=course,
                specialty_id=sp.id,
                enrollment_year=enrollment_year,
            )
            db.add(g)
            groups.append(g)
    db.commit()
    for g in groups:
        db.refresh(g)
    logger.info("{} ta guruh yaratildi.", len(groups))
    return groups


def create_students(db: Session, groups: list[Group], count: int = 5000) -> list[Student]:
    students = []
    batch = []
    for i in range(count):
        gender = random.choice([Gender.MALE, Gender.FEMALE])
        full_name = fake.name_male() if gender == Gender.MALE else fake.name_female()
        group = random.choice(groups)
        birth_year = group.enrollment_year - random.randint(17, 22)
        student = Student(
            student_id=f"ST{CURRENT_YEAR}{i + 1:05d}",
            full_name=full_name,
            gender=gender,
            birth_date=fake.date_between_dates(
                date_start=date(birth_year, 1, 1),
                date_end=date(birth_year, 12, 31),
            ),
            phone=f"+99890{random.randint(1000000, 9999999)}",
            email=f"student{i + 1}@university.uz",
            group_id=group.id,
            education_form=random.choices(
                [EducationForm.KUNDUZGI, EducationForm.SIRTQI, EducationForm.KECHKI],
                weights=[0.7, 0.2, 0.1],
            )[0],
            status=random.choices(
                [StudentStatus.FAOL, StudentStatus.AKADEMIK_TATIL, StudentStatus.BITIRGAN],
                weights=[0.92, 0.05, 0.03],
            )[0],
            enrollment_year=group.enrollment_year,
        )
        batch.append(student)
        if len(batch) >= 500:
            db.bulk_save_objects(batch)
            db.commit()
            students.extend(batch)
            batch = []
            logger.info("Talaba yuklandi: {}", len(students))
    if batch:
        db.bulk_save_objects(batch)
        db.commit()
        students.extend(batch)
    logger.info("Jami {} ta talaba yaratildi.", len(students))
    return db.query(Student).all()


def create_teachers(db: Session, count: int = 200) -> list[Teacher]:
    degrees = ["PhD", "DSc", "Katta o'qituvchi", "Assistent", "Dotsent", "Professor"]
    positions = ["O'qituvchi", "Katta o'qituvchi", "Dotsent", "Professor", "Kafedra mudiri"]
    departments = [f["name"] for f in FACULTIES]

    teachers = []
    for i in range(count):
        gender = random.choice([Gender.MALE, Gender.FEMALE])
        full_name = fake.name_male() if gender == Gender.MALE else fake.name_female()
        t = Teacher(
            teacher_id=f"T{CURRENT_YEAR}{i + 1:04d}",
            full_name=full_name,
            academic_degree=random.choice(degrees),
            position=random.choice(positions),
            department=random.choice(departments),
            phone=f"+99890{random.randint(1000000, 9999999)}",
            email=f"teacher{i + 1}@university.uz",
        )
        db.add(t)
        teachers.append(t)
    db.commit()
    for t in teachers:
        db.refresh(t)
    logger.info("{} ta o'qituvchi yaratildi.", count)
    return teachers


def create_subjects(db: Session, faculties: list[Faculty]) -> list[Subject]:
    subjects = []
    counter = 1
    for fac, fac_data in zip(faculties, FACULTIES):
        subject_names = SUBJECTS_BY_DEPT.get(fac.code, [])
        # Har bir fakultet uchun 15-20 ta fan
        all_subjects = subject_names * 3  # takrorlanish va variantlar
        for name in all_subjects[:18]:
            sub = Subject(
                code=f"{fac.code}{counter:03d}",
                name=name,
                department=fac.name,
                credit_hours=random.choice([2, 3, 4, 5, 6]),
                subject_type=random.choice([SubjectType.MAJBURIY, SubjectType.TANLOV]),
                semester=random.randint(1, 8),
                description=f"{name} fani — {fac.name}",
            )
            db.add(sub)
            subjects.append(sub)
            counter += 1
    db.commit()
    for s in subjects:
        db.refresh(s)
    logger.info("{} ta fan yaratildi.", len(subjects))
    return subjects


def create_assessment_types(db: Session) -> list[AssessmentType]:
    types = []
    for name, desc, weight in ASSESSMENT_TYPES:
        at = AssessmentType(name=name, description=desc, weight_percentage=weight)
        db.add(at)
        types.append(at)
    db.commit()
    for at in types:
        db.refresh(at)
    logger.info("{} ta baholash turi yaratildi.", len(types))
    return types


def _gen_grade_value(student_skill: float) -> float:
    """Talabaning ko'nikma darajasidan kelib chiqib ball generatsiya qilish."""
    base = student_skill * 100
    noise = random.gauss(0, 8)
    val = max(0, min(100, base + noise))
    return round(val, 2)


def create_grades(
    db: Session,
    students: list[Student],
    subjects: list[Subject],
    teachers: list[Teacher],
    assessment_types: list[AssessmentType],
    target_count: int = 50000,
):
    """3 yillik baho tarixi (2022-2025)."""
    logger.info("Baholar generatsiyasi boshlandi. Target: {}", target_count)
    semesters = [
        ("2022-2023", "kuzgi", date(2022, 11, 15)),
        ("2022-2023", "bahorgi", date(2023, 5, 15)),
        ("2023-2024", "kuzgi", date(2023, 11, 15)),
        ("2023-2024", "bahorgi", date(2024, 5, 15)),
        ("2024-2025", "kuzgi", date(2024, 11, 15)),
        ("2024-2025", "bahorgi", date(2025, 5, 15)),
    ]

    # Har bir talabaga ko'nikma "darajasi" beriladi (0.4-0.95)
    # Skill semestrlar bo'yicha biroz o'zgaradi (o'sish/pasayish trendi)
    student_skills = {s.id: random.uniform(0.4, 0.95) for s in students}
    student_trends = {s.id: random.uniform(-0.02, 0.03) for s in students}  # semesterga skill o'zgarishi

    # Baholarni semesterlar bo'yicha TENG taqsimlash
    target_per_semester = target_count // len(semesters)

    batch: list[Grade] = []
    grade_count = 0

    for sem_idx, (academic_year, semester, base_date) in enumerate(semesters):
        semester_count = 0
        # Talabalarni shuffle qilamiz — har semesterda boshqa tartibda
        shuffled_students = list(students)
        random.shuffle(shuffled_students)

        for student in shuffled_students:
            if semester_count >= target_per_semester:
                break
            # Skill bu semester uchun
            skill = max(0.2, min(0.99, student_skills[student.id] + student_trends[student.id] * sem_idx))

            # Har semester uchun 6-10 ta fan
            student_subjects = random.sample(subjects, min(random.randint(6, 10), len(subjects)))
            for subj in student_subjects:
                if semester_count >= target_per_semester:
                    break
                teacher = random.choice(teachers)
                for at in assessment_types:
                    val = _gen_grade_value(skill)
                    grade = Grade(
                        student_id=student.id,
                        subject_id=subj.id,
                        teacher_id=teacher.id,
                        assessment_type_id=at.id,
                        grade_value=val,
                        attendance_percentage=round(random.uniform(70, 100), 2),
                        is_passed=val >= 55,
                        semester=semester,
                        academic_year=academic_year,
                        grade_date=base_date + timedelta(days=random.randint(-30, 30)),
                    )
                    batch.append(grade)
                    grade_count += 1
                    semester_count += 1

                    if len(batch) >= 2000:
                        db.bulk_save_objects(batch)
                        db.commit()
                        logger.info("Yuklangan baholar: {} ({}/{})", grade_count, sem_idx + 1, len(semesters))
                        batch = []

                    if semester_count >= target_per_semester:
                        break

    if batch:
        db.bulk_save_objects(batch)
        db.commit()
    logger.info("Jami {} ta baho yaratildi ({} semesterga teng taqsimlangan).", grade_count, len(semesters))
    return grade_count


def main(reset: bool = True, students: int = 5000, teachers: int = 200, grades: int = 50000):
    if reset:
        reset_database()

    with oltp_session() as db:
        create_users(db)
        faculties = create_faculties(db)
        specialties = create_specialties(db, faculties)
        groups = create_groups(db, specialties)
        students_list = create_students(db, groups, count=students)
        teachers_list = create_teachers(db, count=teachers)
        subjects_list = create_subjects(db, faculties)
        assessment_types = create_assessment_types(db)
        create_grades(db, students_list, subjects_list, teachers_list, assessment_types, target_count=grades)

    logger.success("Seed data muvaffaqiyatli yuklandi!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-reset", action="store_true", help="Database ni reset qilmaslik")
    parser.add_argument("--students", type=int, default=5000)
    parser.add_argument("--teachers", type=int, default=200)
    parser.add_argument("--grades", type=int, default=50000)
    args = parser.parse_args()

    main(
        reset=not args.no_reset,
        students=args.students,
        teachers=args.teachers,
        grades=args.grades,
    )
