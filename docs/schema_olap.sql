-- ============================================================
-- ReytingOLAP DWH — Star Schema (PostgreSQL 15+)
-- 1 fakt + 7 dimension. TZ 6.2 ga muvofiq.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS dwh;
SET search_path = dwh, public;

-- ---------- DIMENSION JADVALLAR ----------

CREATE TABLE dim_fakultet (
    fakultet_id    SERIAL PRIMARY KEY,
    fakultet_nomi  VARCHAR(200) NOT NULL,
    fakultet_kodi  VARCHAR(20)  UNIQUE NOT NULL,
    dekan_id       INT,
    faol           BOOLEAN DEFAULT TRUE,
    yaratilgan     TIMESTAMP DEFAULT now()
);

CREATE TABLE dim_kafedra (
    kafedra_id    SERIAL PRIMARY KEY,
    kafedra_nomi  VARCHAR(200) NOT NULL,
    kafedra_kodi  VARCHAR(20)  UNIQUE NOT NULL,
    fakultet_id   INT NOT NULL REFERENCES dim_fakultet(fakultet_id),
    mudir_id      INT,
    faol          BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_guruh (
    guruh_id        SERIAL PRIMARY KEY,
    guruh_nomi      VARCHAR(50) NOT NULL,
    guruh_kodi      VARCHAR(20) UNIQUE NOT NULL,
    kurs            INT CHECK (kurs BETWEEN 1 AND 6),
    kafedra_id      INT NOT NULL REFERENCES dim_kafedra(kafedra_id),
    talabalar_soni  INT DEFAULT 0,
    faol            BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_talaba (
    talaba_id     SERIAL PRIMARY KEY,
    hemis_id      VARCHAR(20) UNIQUE,
    passport      BYTEA,                       -- AES-256 shifrlangan
    ism           VARCHAR(50) NOT NULL,
    familiya      VARCHAR(50) NOT NULL,
    sharif        VARCHAR(50),
    jins          CHAR(1) CHECK (jins IN ('M','F')),
    tugilgan_sana DATE,
    telefon       BYTEA,                       -- shifrlangan
    email         BYTEA,                       -- shifrlangan
    telegram_id   BIGINT UNIQUE,
    kurs          INT,
    talim_shakli  VARCHAR(20),
    talim_turi    VARCHAR(20),
    status        VARCHAR(20) DEFAULT 'faol',
    kirgan_yil    INT
);

CREATE TABLE dim_fan (
    fan_id         SERIAL PRIMARY KEY,
    fan_nomi       VARCHAR(200) NOT NULL,
    fan_kodi       VARCHAR(20) UNIQUE NOT NULL,
    kredit         INT NOT NULL DEFAULT 3,
    soat_jami      INT,
    soat_maruza    INT,
    soat_amaliy    INT,
    soat_lab       INT,
    soat_mustaqil  INT,
    fan_turi       VARCHAR(50),    -- majburiy/tanlov/qo'shimcha
    fan_blok       VARCHAR(50)     -- gumanitar/asosiy/ixtisoslik
);

CREATE TABLE dim_oqituvchi (
    oqituvchi_id   SERIAL PRIMARY KEY,
    hemis_id       VARCHAR(20) UNIQUE,
    fish           VARCHAR(200) NOT NULL,
    lavozim        VARCHAR(100),
    ilmiy_daraja   VARCHAR(50),
    ilmiy_unvon    VARCHAR(50),
    staj           INT,
    kafedra_id     INT REFERENCES dim_kafedra(kafedra_id),
    telefon        BYTEA,
    email          BYTEA
);

CREATE TABLE dim_semestr (
    semestr_id       SERIAL PRIMARY KEY,
    oquv_yili        VARCHAR(10) NOT NULL,    -- '2025-2026'
    semestr_raqami   INT CHECK (semestr_raqami IN (1,2)),
    boshlanish_sana  DATE NOT NULL,
    tugash_sana      DATE NOT NULL,
    faol             BOOLEAN DEFAULT FALSE,
    UNIQUE (oquv_yili, semestr_raqami)
);

-- ---------- FAKT JADVAL (PARTITSIYALANGAN) ----------

CREATE TABLE fact_reyting (
    fact_id           BIGSERIAL,
    talaba_id         INT NOT NULL REFERENCES dim_talaba(talaba_id),
    fan_id            INT NOT NULL REFERENCES dim_fan(fan_id),
    oqituvchi_id      INT NOT NULL REFERENCES dim_oqituvchi(oqituvchi_id),
    semestr_id        INT NOT NULL REFERENCES dim_semestr(semestr_id),
    fakultet_id       INT NOT NULL REFERENCES dim_fakultet(fakultet_id),
    guruh_id          INT NOT NULL REFERENCES dim_guruh(guruh_id),
    kafedra_id        INT NOT NULL REFERENCES dim_kafedra(kafedra_id),
    jn_ball           DECIMAL(5,2) CHECK (jn_ball  BETWEEN 0 AND 30),
    on_ball           DECIMAL(5,2) CHECK (on_ball  BETWEEN 0 AND 30),
    yan_ball          DECIMAL(5,2) CHECK (yan_ball BETWEEN 0 AND 40),
    umumiy_ball       DECIMAL(5,2) GENERATED ALWAYS AS
                      (COALESCE(jn_ball,0)+COALESCE(on_ball,0)+COALESCE(yan_ball,0)) STORED,
    baho_harfi        VARCHAR(2),
    baho_5_lik        DECIMAL(3,2),
    kredit            INT NOT NULL,
    vaznlangan_ball   DECIMAL(8,4),
    davomat_foiz      DECIMAL(5,2),
    topshirilgan_sana DATE NOT NULL,
    yaratilgan_vaqt   TIMESTAMP DEFAULT now(),
    yangilangan_vaqt  TIMESTAMP DEFAULT now(),
    PRIMARY KEY (fact_id, topshirilgan_sana)
) PARTITION BY RANGE (topshirilgan_sana);

-- Partitsiyalar (har semestr uchun)
CREATE TABLE fact_reyting_2025_2026_kuz  PARTITION OF fact_reyting
    FOR VALUES FROM ('2025-09-01') TO ('2026-02-01');
CREATE TABLE fact_reyting_2025_2026_bahor PARTITION OF fact_reyting
    FOR VALUES FROM ('2026-02-01') TO ('2026-09-01');
CREATE TABLE fact_reyting_default PARTITION OF fact_reyting DEFAULT;

-- ---------- INDEKSLAR ----------
CREATE INDEX ix_fact_talaba    ON fact_reyting (talaba_id);
CREATE INDEX ix_fact_fan       ON fact_reyting (fan_id);
CREATE INDEX ix_fact_semestr   ON fact_reyting (semestr_id);
CREATE INDEX ix_fact_fakultet  ON fact_reyting (fakultet_id);
CREATE INDEX ix_fact_guruh     ON fact_reyting (guruh_id);
CREATE INDEX ix_fact_kafedra   ON fact_reyting (kafedra_id);
CREATE INDEX ix_fact_fak_sem   ON fact_reyting (fakultet_id, semestr_id);
CREATE INDEX ix_fact_tal_sem   ON fact_reyting (talaba_id, semestr_id);
CREATE INDEX ix_fact_oqit_sem  ON fact_reyting (oqituvchi_id, semestr_id);

-- ---------- MATERIALIZED VIEWS (eng ko'p so'raladigan agregatlar) ----------

CREATE MATERIALIZED VIEW mv_gpa_talaba_semestr AS
SELECT
    f.talaba_id,
    f.semestr_id,
    f.fakultet_id,
    f.guruh_id,
    SUM(f.vaznlangan_ball) / NULLIF(SUM(f.kredit),0)            AS gpa_100,
    (SUM(f.vaznlangan_ball) / NULLIF(SUM(f.kredit),0)) / 20.0   AS gpa_5,
    AVG(f.davomat_foiz)                                          AS avg_davomat,
    COUNT(*) FILTER (WHERE f.umumiy_ball < 60)                  AS qarzdor_fanlar,
    COUNT(*)                                                     AS jami_fanlar
FROM fact_reyting f
GROUP BY f.talaba_id, f.semestr_id, f.fakultet_id, f.guruh_id;

CREATE UNIQUE INDEX ux_mv_gpa_talaba_semestr
    ON mv_gpa_talaba_semestr (talaba_id, semestr_id);

CREATE MATERIALIZED VIEW mv_fakultet_reyting AS
SELECT
    f.fakultet_id,
    f.semestr_id,
    AVG(f.umumiy_ball)                  AS ortacha_ball,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.umumiy_ball) AS mediana,
    COUNT(DISTINCT f.talaba_id)         AS talabalar_soni,
    COUNT(DISTINCT f.oqituvchi_id)      AS oqituvchilar_soni
FROM fact_reyting f
GROUP BY f.fakultet_id, f.semestr_id;

CREATE UNIQUE INDEX ux_mv_fakultet_reyting
    ON mv_fakultet_reyting (fakultet_id, semestr_id);

-- Yangilash:  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gpa_talaba_semestr;

-- ---------- AUDIT (ETL ishi loglari) ----------
CREATE TABLE etl_audit (
    audit_id     BIGSERIAL PRIMARY KEY,
    ish_nomi     VARCHAR(100) NOT NULL,
    boshlangan   TIMESTAMP NOT NULL,
    tugagan      TIMESTAMP,
    status       VARCHAR(20),     -- success / failed / running
    qatorlar     INT,
    xatolar      INT,
    xato_matni   TEXT
);
