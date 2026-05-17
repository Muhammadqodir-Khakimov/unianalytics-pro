# OLAP Modeli — Star Schema

Tizim **Star Schema** (yulduzsimon sxema) asosida qurilgan. Markazda bitta fact jadval (`fact_student_grades`), uning atrofida 6 ta dimension jadval joylashgan.

## Diagramma

```
                  ┌──────────────┐
                  │  dim_student │
                  └──────┬───────┘
                         │
   ┌──────────────┐      │      ┌──────────────┐
   │ dim_subject  │──────┼──────│  dim_teacher │
   └──────────────┘      │      └──────────────┘
                         ▼
                  ┌──────────────────────┐
                  │ fact_student_grades  │
                  │  (markaziy FAKT)     │
                  └──────────────────────┘
                         ▲
   ┌──────────────┐      │      ┌──────────────────────┐
   │   dim_time   │──────┼──────│  dim_faculty         │
   └──────────────┘      │      └──────────────────────┘
                         │
                  ┌──────────────────────┐
                  │ dim_assessment_type  │
                  └──────────────────────┘
```

## FACT TABLE: `fact_student_grades`

| Maydon | Tip | Tavsif |
|--------|-----|--------|
| grade_id | BIGSERIAL PK | Birlamchi kalit |
| student_key | INT FK | dim_student ga |
| subject_key | INT FK | dim_subject ga |
| teacher_key | INT FK | dim_teacher ga |
| time_key | INT FK | dim_time ga |
| faculty_key | INT FK | dim_faculty ga |
| assessment_type_key | INT FK | dim_assessment_type ga |
| grade_value | NUMERIC(5,2) | 0-100 ball |
| credit_hours | INT | Kredit soat |
| attendance_percentage | NUMERIC(5,2) | Davomat foizi |
| gpa_points | NUMERIC(3,2) | 4.0 shkalada |
| is_passed | BOOLEAN | O'zlashtirgan/o'zlashtirmagan |

## DIMENSION TABLE: `dim_student`

Talabalar haqida ma'lumot. Slowly Changing Dimension (SCD Type 1).

| Maydon | Tip |
|--------|-----|
| student_key | SERIAL PK |
| student_id | VARCHAR (real ID) |
| full_name | VARCHAR |
| gender | CHAR(1) (M/F) |
| birth_date | DATE |
| enrollment_year | INT |
| group_name | VARCHAR |
| education_form | VARCHAR (kunduzgi/sirtqi) |
| status | VARCHAR (faol/akademik_tatil/chetlatilgan) |

## DIMENSION TABLE: `dim_subject`

| Maydon | Tip |
|--------|-----|
| subject_key | SERIAL PK |
| subject_code | VARCHAR |
| subject_name | VARCHAR |
| department | VARCHAR |
| credit_hours | INT |
| subject_type | VARCHAR (majburiy/tanlov) |
| semester | INT |

## DIMENSION TABLE: `dim_teacher`

| Maydon | Tip |
|--------|-----|
| teacher_key | SERIAL PK |
| teacher_id | VARCHAR |
| full_name | VARCHAR |
| academic_degree | VARCHAR |
| position | VARCHAR |
| department | VARCHAR |

## DIMENSION TABLE: `dim_time` (IERARXIYA)

Vaqt o'lchovi ierarxik tuzilishga ega: `year → academic_year → semester → quarter → month → week → day`.

| Maydon | Tip |
|--------|-----|
| time_key | SERIAL PK |
| full_date | DATE |
| day | INT |
| week | INT |
| month | INT |
| quarter | INT |
| semester | VARCHAR (kuzgi/bahorgi) |
| academic_year | VARCHAR (masalan, 2024-2025) |
| year | INT |

## DIMENSION TABLE: `dim_faculty` (IERARXIYA)

Tashkiliy ierarxiya: `university → faculty → department → specialty → course → group`.

| Maydon | Tip |
|--------|-----|
| faculty_key | SERIAL PK |
| faculty_name | VARCHAR |
| department | VARCHAR |
| specialty | VARCHAR |
| course | INT (1-4) |
| group_name | VARCHAR |

## DIMENSION TABLE: `dim_assessment_type`

| Maydon | Tip |
|--------|-----|
| assessment_type_key | SERIAL PK |
| type_name | VARCHAR (JN/ON/YN/Yakuniy) |
| weight_percentage | NUMERIC(5,2) |

## OLAP Operatsiyalari

### Drill-down
Yuqori darajadan past darajaga tushish:
```
Universitet → Fakultet → Yo'nalish → Kurs → Guruh → Talaba
```

### Roll-up
Past darajadan yuqori darajaga ko'tarilish (drill-down ning teskarisi):
```
Talaba → Guruh → Kurs → Fakultet → Universitet
```

### Slice
Bir o'lchov bo'yicha bitta qiymatga filtrlash:
```sql
WHERE dim_time.academic_year = '2024-2025'
```

### Dice
Bir nechta o'lchov bo'yicha filtrlash:
```sql
WHERE dim_time.semester = 'kuzgi'
  AND dim_faculty.faculty_name = 'Informatika'
  AND dim_assessment_type.type_name = 'Yakuniy'
```

### Pivot
O'lchovlarni almashtirish (qator ↔ ustun):
- Qator: fakultet, Ustun: semestr → o'rinlarini almashtirish

### CUBE / ROLLUP / GROUPING SETS

```sql
-- CUBE: barcha mumkin bo'lgan kombinatsiyalar
SELECT f.faculty_name, t.semester, AVG(g.gpa_points)
FROM fact_student_grades g
JOIN dim_faculty f ON g.faculty_key = f.faculty_key
JOIN dim_time t ON g.time_key = t.time_key
GROUP BY CUBE(f.faculty_name, t.semester);

-- ROLLUP: ierarxik agregatsiya
GROUP BY ROLLUP(f.faculty_name, f.specialty, f.course, f.group_name);
```

## Indekslash va optimizatsiya

- Har bir FK ustida B-tree index
- `fact_student_grades` da composite index: (faculty_key, time_key)
- Materialized views eng tez-tez ishlatiladigan agregatsiyalar uchun:
  - `mv_faculty_semester_avg`
  - `mv_student_gpa_yearly`
- Partitsiyalash `time_key` bo'yicha (yiliga bitta partition)

## ETL Jarayoni

`OLTP → OLAP` ko'chirish:

1. **Extract** — OLTP db dan yangi yozuvlar (incremental)
2. **Transform** — denormalizatsiya, dimension keylarini topish/yaratish
3. **Load** — OLAP db ga yozish, materialized views ni `REFRESH`

Celery beat orqali har 1 soatda avtomatik ishlaydi.
