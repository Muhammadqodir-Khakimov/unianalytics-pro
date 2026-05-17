-- PostgreSQL initialization script for OLTP database
-- Avtomatik PostgreSQL container start qilganda ishga tushadi

-- Performance optimization extensions
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Trigram search uchun
CREATE EXTENSION IF NOT EXISTS unaccent;

-- O'zbek tilida full-text search uchun
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'uz_search') THEN
        CREATE TEXT SEARCH CONFIGURATION uz_search (COPY = simple);
    END IF;
END
$$;

-- Default timezone Tashkent
SET TIME ZONE 'Asia/Tashkent';
