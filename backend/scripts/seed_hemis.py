"""HEMIS namuna ma'lumotlarini yuklash: e'lonlar, to'lov, kitoblar, yotoqxona, imtihonlar."""
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import random

from loguru import logger

from app.database import oltp_session
from app.models.oltp.faculty import Group
from app.models.oltp.hemis import (
    Announcement,
    AnnouncementAudience,
    AnnouncementPriority,
    Book,
    BookCategory,
    DormitoryAssignment,
    DormitoryBuilding,
    DormitoryRoom,
    ExamSchedule,
    ExamType,
    Payment,
    PaymentStatus,
    PaymentType,
    Thesis,
    ThesisStatus,
)
from app.models.oltp.student import Student
from app.models.oltp.subject import Subject
from app.models.oltp.teacher import Teacher
from app.models.oltp.user import User, UserRole

random.seed(42)


def seed_announcements(db):
    items = [
        ("📢 2024-2025 o'quv yili boshlandi", "Talabalarni yangi o'quv yili bilan tabriklaymiz!", "normal"),
        ("⚠️ Imtihon sessiyasi yaqinlashmoqda", "Yakuniy imtihonlar 15-dekabrdan boshlanadi.", "high"),
        ("🚨 Karantin choralari", "Niqobsiz universitetga kirish taqiqlanadi!", "urgent"),
        ("🎓 Bitiruvchilar uchun", "Diplom ishi himoyasi 1-iyundan boshlanadi.", "normal"),
        ("💰 Stipendiya to'landi", "Yanvar oyi stipendiyasi kartalarga o'tkazildi.", "normal"),
    ]
    admin = db.query(User).filter(User.username == "admin").first()
    for title, body, prio in items:
        ann = Announcement(
            title=title,
            body=body,
            audience=AnnouncementAudience.ALL,
            priority=AnnouncementPriority(prio),
            author_id=admin.id if admin else 1,
            is_pinned=prio == "urgent",
        )
        db.add(ann)
    db.commit()
    logger.info("{} ta e'lon yaratildi", len(items))


def seed_payments(db):
    students = db.query(Student).limit(100).all()
    for st in students:
        for academic_year in ["2023-2024", "2024-2025"]:
            amount = random.choice([7_000_000, 9_000_000, 12_000_000])
            paid = random.choice([0, amount // 2, amount])
            p = Payment(
                student_id=st.id,
                payment_type=PaymentType.CONTRACT,
                amount=amount,
                paid_amount=paid,
                academic_year=academic_year,
                description=f"Kontrakt to'lovi {academic_year}",
                due_date=date(2024 if academic_year == "2023-2024" else 2025, 9, 1),
                status=PaymentStatus.PAID if paid >= amount else PaymentStatus.PENDING,
                paid_date=date.today() if paid > 0 else None,
            )
            db.add(p)
    db.commit()
    logger.info("To'lovlar yuklandi")


def seed_books(db):
    books_data = [
        ("Matematik analiz", "I.M.Sobolev", "Universitet nashriyoti", 2020, BookCategory.TEXTBOOK),
        ("Algoritmlar va ma'lumot tuzilmalari", "T.Cormen", "MIT Press", 2022, BookCategory.TEXTBOOK),
        ("O'zbekiston tarixi", "Sh.Mirziyoyev", "Sharq", 2019, BookCategory.TEXTBOOK),
        ("Sun'iy intellekt", "S.Russell", "Pearson", 2021, BookCategory.SCIENTIFIC),
        ("Iqtisodiyot nazariyasi", "P.Samuelson", "McGraw-Hill", 2020, BookCategory.TEXTBOOK),
        ("O'tgan kunlar", "A.Qodiriy", "Sharq", 2018, BookCategory.FICTION),
        ("Mehrobdan chayon", "A.Qodiriy", "Sharq", 2018, BookCategory.FICTION),
        ("Ma'lumotlar bazalari", "C.Date", "Pearson", 2023, BookCategory.TEXTBOOK),
        ("Veb-dasturlash JavaScript", "D.Crockford", "O'Reilly", 2022, BookCategory.TEXTBOOK),
        ("Operatsion tizimlar", "A.Tanenbaum", "Pearson", 2021, BookCategory.TEXTBOOK),
        ("Fizika asoslari", "R.Feynman", "Addison-Wesley", 2019, BookCategory.SCIENTIFIC),
        ("Diskret matematika", "K.Rosen", "McGraw-Hill", 2022, BookCategory.TEXTBOOK),
        ("Statistika va ehtimollar", "J.Devore", "Cengage", 2020, BookCategory.TEXTBOOK),
        ("Marketing asoslari", "P.Kotler", "Pearson", 2021, BookCategory.TEXTBOOK),
        ("Boshqaruv hisobi", "C.Horngren", "Pearson", 2020, BookCategory.TEXTBOOK),
    ]
    for title, author, pub, year, cat in books_data:
        total = random.randint(3, 10)
        b = Book(
            title=title,
            author=author,
            publisher=pub,
            year=year,
            category=cat,
            language="uz",
            pages=random.randint(200, 800),
            total_copies=total,
            available_copies=random.randint(0, total),
        )
        db.add(b)
    db.commit()
    logger.info("{} ta kitob yuklandi", len(books_data))


def seed_dormitory(db):
    buildings = [
        DormitoryBuilding(name="A-bino", address="Toshkent shahar, Universitet 1", total_rooms=30),
        DormitoryBuilding(name="B-bino", address="Toshkent shahar, Universitet 2", total_rooms=30),
    ]
    for b in buildings:
        db.add(b)
    db.commit()

    for b in db.query(DormitoryBuilding).all():
        for floor in range(1, 5):
            for room_num in range(1, 11):
                room = DormitoryRoom(
                    building_id=b.id,
                    room_number=f"{floor}{room_num:02d}",
                    floor=floor,
                    capacity=random.choice([3, 4]),
                    gender=random.choice(["M", "F"]),
                    monthly_fee=random.choice([300_000, 400_000, 500_000]),
                )
                db.add(room)
    db.commit()

    # Bir nechta talabani biriktirish
    rooms = db.query(DormitoryRoom).all()[:50]
    students = db.query(Student).limit(150).all()
    student_idx = 0
    for r in rooms:
        for _ in range(random.randint(1, r.capacity)):
            if student_idx >= len(students):
                break
            db.add(DormitoryAssignment(room_id=r.id, student_id=students[student_idx].id))
            student_idx += 1
    db.commit()
    logger.info("{} ta yotoqxona xonasi yaratildi", db.query(DormitoryRoom).count())


def seed_exams(db):
    groups = db.query(Group).all()[:10]
    subjects = db.query(Subject).all()[:20]
    teachers = db.query(Teacher).all()
    base_date = date(2024, 12, 15)

    count = 0
    for grp in groups:
        for i, subj in enumerate(random.sample(subjects, min(5, len(subjects)))):
            exam_date = base_date + timedelta(days=count // 5)
            e = ExamSchedule(
                subject_id=subj.id,
                group_id=grp.id,
                teacher_id=random.choice(teachers).id,
                exam_type=ExamType.FINAL,
                exam_date=exam_date,
                start_time=time(9 + (count % 4) * 2, 0),
                duration_minutes=90,
                room=f"A-{random.randint(101, 305)}",
                academic_year="2024-2025",
                semester="kuzgi",
            )
            db.add(e)
            count += 1
    db.commit()
    logger.info("{} ta imtihon jadvali yaratildi", count)


def seed_theses(db):
    students = db.query(Student).filter(Student.enrollment_year == 2022).limit(15).all()
    teachers = db.query(Teacher).all()
    topics = [
        "Talaba reyting tizimini OLAP modeli orqali tahlil qilish",
        "Sun'iy intellekt asosida talaba muvaffaqiyatini prognoz qilish",
        "Blockchain texnologiyasini ta'limda qo'llash",
        "Universitet boshqaruv tizimini avtomatlashtirish",
        "Mashinaviy o'rganish algoritmlari yordamida tahlil",
        "Microservice arxitekturasi va uning afzalliklari",
        "Cloud computing imkoniyatlari va xavfsizligi",
        "Big Data tahlil usullarini o'rganish",
        "IoT qurilmalari va aqlli universitet kontseptsiyasi",
        "DevOps amaliyotlari va CI/CD pipeline",
    ]
    for i, st in enumerate(students):
        topic = topics[i % len(topics)] + f" ({st.full_name})"
        t = Thesis(
            student_id=st.id,
            supervisor_id=random.choice(teachers).id,
            title=topic,
            abstract=f"Ushbu bitiruv ishida {topic.lower()} masalasi tadqiq qilinadi.",
            keywords="OLAP, tahlil, ML, prognoz",
            status=random.choice([ThesisStatus.DRAFT, ThesisStatus.APPROVED, ThesisStatus.IN_PROGRESS, ThesisStatus.SUBMITTED]),
            academic_year="2024-2025",
        )
        db.add(t)
    db.commit()
    logger.info("{} ta bitiruv ishi yaratildi", len(students))


def main():
    with oltp_session() as db:
        # Avval mavjudligini tekshirish
        if db.query(Announcement).first():
            logger.warning("HEMIS data allaqachon yuklangan — qayta tushirilmayapti")
            return

        logger.info("HEMIS ma'lumotlarini yuklash...")
        seed_announcements(db)
        seed_payments(db)
        seed_books(db)
        seed_dormitory(db)
        seed_exams(db)
        seed_theses(db)
        logger.success("HEMIS seed tugadi!")


if __name__ == "__main__":
    main()
