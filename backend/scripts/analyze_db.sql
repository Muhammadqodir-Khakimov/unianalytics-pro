-- EXPLAIN ANALYZE queries for tuning OLAP performance
-- Run after seeding ~100k rows to fact_grades

-- ============================================
-- 1. Faculty trend (most common dashboard query)
-- ============================================
EXPLAIN (ANALYZE, BUFFERS)
SELECT t.year, t.month, AVG(fg.grade_value)
FROM fact_grades fg
JOIN dim_time t ON fg.time_key = t.time_key
WHERE fg.faculty_key = 1
GROUP BY t.year, t.month
ORDER BY t.year, t.month;

-- ============================================
-- 2. Student detail with subject breakdown
-- ============================================
EXPLAIN (ANALYZE, BUFFERS)
SELECT s.name AS subject, AVG(fg.grade_value)
FROM fact_grades fg
JOIN dim_subject s ON fg.subject_key = s.subject_key
WHERE fg.student_key = 42
GROUP BY s.name;

-- ============================================
-- 3. Cross-filter: faculty + semester + grade range
-- ============================================
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM fact_grades fg
JOIN dim_time t ON fg.time_key = t.time_key
WHERE fg.faculty_key = 1
  AND t.year = 2025 AND t.semester = 1
  AND fg.grade_value < 60;

-- ============================================
-- 4. Materialized view hit
-- ============================================
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mv_faculty_gpa_monthly WHERE faculty_id = 1 ORDER BY year, month;

-- ============================================
-- 5. Stats
-- ============================================
SELECT schemaname, relname, n_live_tup AS rows, pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;
