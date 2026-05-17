-- OLAP performance uchun materialized views
-- Ishga tushirish: psql -U olap_user -d student_olap -f create_materialized_views.sql

-- 1. Fakultet x Semestr o'rtacha baholar
DROP MATERIALIZED VIEW IF EXISTS mv_faculty_semester_avg CASCADE;
CREATE MATERIALIZED VIEW mv_faculty_semester_avg AS
SELECT
    f.faculty_name,
    t.academic_year,
    t.semester,
    COUNT(*) AS grades_count,
    ROUND(AVG(g.grade_value)::numeric, 2) AS avg_grade,
    ROUND(AVG(g.gpa_points)::numeric, 3) AS avg_gpa,
    ROUND(AVG(g.attendance_percentage)::numeric, 2) AS avg_attendance,
    SUM(CASE WHEN g.is_passed THEN 1 ELSE 0 END) AS passed_count
FROM fact_student_grades g
JOIN dim_faculty f ON g.faculty_key = f.faculty_key
JOIN dim_time t ON g.time_key = t.time_key
GROUP BY f.faculty_name, t.academic_year, t.semester
WITH DATA;

CREATE UNIQUE INDEX idx_mv_faculty_semester
    ON mv_faculty_semester_avg(faculty_name, academic_year, semester);

-- 2. Talaba GPA agregatsiyasi
DROP MATERIALIZED VIEW IF EXISTS mv_student_gpa_yearly CASCADE;
CREATE MATERIALIZED VIEW mv_student_gpa_yearly AS
SELECT
    s.student_key,
    s.student_id,
    s.full_name,
    s.group_name,
    t.academic_year,
    ROUND(AVG(g.gpa_points)::numeric, 3) AS avg_gpa,
    ROUND(AVG(g.grade_value)::numeric, 2) AS avg_grade,
    COUNT(*) AS grades_count
FROM fact_student_grades g
JOIN dim_student s ON g.student_key = s.student_key
JOIN dim_time t ON g.time_key = t.time_key
GROUP BY s.student_key, s.student_id, s.full_name, s.group_name, t.academic_year
WITH DATA;

CREATE UNIQUE INDEX idx_mv_student_gpa
    ON mv_student_gpa_yearly(student_key, academic_year);

-- 3. Fan bo'yicha o'zlashtirish
DROP MATERIALIZED VIEW IF EXISTS mv_subject_performance CASCADE;
CREATE MATERIALIZED VIEW mv_subject_performance AS
SELECT
    sub.subject_key,
    sub.subject_name,
    sub.department,
    COUNT(*) AS grades_count,
    ROUND(AVG(g.grade_value)::numeric, 2) AS avg_grade,
    ROUND(AVG(g.gpa_points)::numeric, 3) AS avg_gpa,
    ROUND((SUM(CASE WHEN g.is_passed THEN 1 ELSE 0 END)::numeric * 100.0 / NULLIF(COUNT(*), 0)), 2) AS passing_rate
FROM fact_student_grades g
JOIN dim_subject sub ON g.subject_key = sub.subject_key
GROUP BY sub.subject_key, sub.subject_name, sub.department
WITH DATA;

CREATE UNIQUE INDEX idx_mv_subject_performance ON mv_subject_performance(subject_key);

-- Refresh buyrug'i (Celery beat orqali har tunda ishga tushadi):
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_faculty_semester_avg;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_student_gpa_yearly;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_subject_performance;
