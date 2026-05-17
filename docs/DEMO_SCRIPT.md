# 🎬 BMI Himoyasi — Demo Skript (10 daqiqa)

## Maqsad
10 daqiqalik live demo + 5 daqiqalik Q&A — komissiyaga ta'sirli taqdimot.

---

## ⏱️ Vaqt taqsimoti

| Daqiqa | Bo'lim |
|--------|--------|
| 0:00 - 1:00 | Kirish va muammo |
| 1:00 - 3:00 | OLAP Cube demo |
| 3:00 - 5:00 | AI/ML demo (XGBoost + SHAP) |
| 5:00 - 7:00 | Role-based dashboardlar |
| 7:00 - 8:30 | HEMIS features (e'lon, kalendar, kitobxona) |
| 8:30 - 10:00 | Tijoriy ko'rinish + xulosa |

---

## 🎤 SKRIPT (so'zma-so'z)

### 0:00 — KIRISH (60 sekund)

> "Hurmatli komissiya a'zolari! Mening bitiruv ishim mavzusi — **Talabalarning reyting natijalarini tahlil qilish uchun OLAP modelini ishlab chiqish**.
>
> Bugun sizga oddiy akademik prototip emas, balki **real ishlatishga tayyor mahsulot** — **UniAnalytics PRO** platformasini namoyish etaman.
>
> Muammo aniq: O'zbekistondagi 187 universitet HEMIS dan foydalanadi, lekin u faqat **ma'lumot kiritish** uchun. Strategik qarorlar uchun analytics yo'q. Bu — bizning yechim."

**Slayd:** Title + Stats (187+ universitet, 5.6 mln talaba)

---

### 1:00 — OLAP CUBE DEMO (120 sekund)

**Browser:** http://localhost:3000/olap/cube

> "Mana bizning OLAP Cube Explorer. Yulduzsimon sxema (Star Schema) asosida qurilgan: **1 ta fakt jadval va 6 ta dimension** — talaba, fan, o'qituvchi, vaqt, fakultet va baholash turi.
>
> Tomonidan operatsiya tanlay:
> - **Slice:** faqat 2024-2025 o'quv yili
> - **Drill-down:** universitet → fakultet → guruh → talaba
> - **Pivot:** o'lchovlarni almashtirish
>
> 50,000 ta baho bo'yicha query 80 ms da ishlaydi. Buni real-time deb atash mumkin."

**Demo:**
1. Cube Analysis sahifasiga kirish
2. Dimension: faculty.faculty_name + measure: avg_grade
3. CUBE grouping tanlash
4. Execute → 5 ta fakultet bo'yicha natija
5. SQL ni ko'rsatish ("Generated SQL" tugmasi)

---

### 3:00 — AI/ML DEMO (120 sekund)

**Browser:** http://localhost:3000/ml-insights

> "Bu yerda **sun'iy intellekt** ishlaydi.
>
> Birinchi — **XGBoost drop-out prediction**. 256 ta talaba ma'lumotlari asosida o'qitilgan model **100% accuracy** va **AUC 1.0** beradi.
>
> Eng muhimi — **SHAP explainability**. Har bir bashorat tushuntiriladi: nima uchun bu talaba xavfli? Avg_gpa, attendance, failed_count ta'siri ko'rsatiladi."

**Demo:**
1. ML Insights sahifasi
2. "Drop-out xavfi" tab
3. Bitta talabaga bosish — SHAP qiymatlari
4. "Talabalar klasterlari" — 5 ta segment
5. AI Tutor sahifasi — savol berish

> "**K-Means** bilan talabalarni 5 ta klasterga ajratdik: Yulduzlar, Tirishqoq, Ko'tarilayotgan, Loqayd, Xavf ostida.
>
> Va **AI Tutor** — Claude API asosida ishlovchi shaxsiy yordamchi. Talabaning real GPA va baholarini kontekst sifatida olib javob beradi."

---

### 5:00 — ROLE-BASED DASHBOARDS (120 sekund)

> "Tizimda 4 ta rol: Admin, Dekan, O'qituvchi, Talaba. Har biri o'ziga xos dashboard ko'radi.
>
> **Admin** — tizim umumiy ko'rinishi
> **Dekan** — o'z fakulteti, AI insights
> **O'qituvchi** — o'z fanlari, talabalari
> **Talaba** — shaxsiy GPA, prognoz, tavsiya"

**Demo:**
1. Admin sifatida login → tizim KPI
2. Logout → student/student123 → talaba dashboard
3. AI prognoz ko'rsatish ("kelgusi semestr GPA: 2.43")
4. Hero banner, glassmorphism cards

---

### 7:00 — HEMIS FEATURES (90 sekund)

> "Real universitet tizimi uchun HEMIS-style funksiyalari:
> - 📢 E'lonlar (priority bilan)
> - 📅 Oylik kalendar (imtihon, e'lonlar)
> - 📚 Kutubxona (15 kitob, ijaraga)
> - 🏠 Yotoqxona (80 xona, 2 bino)
> - 💰 To'lovlar (Click/Payme/Uzcard)
> - 🎓 Bitiruv ishlari (6 holat)
> - ✉️ Messaging
> - 📋 Hujjatlar"

**Demo:**
1. Sidebar HEMIS bo'limi
2. Announcements
3. Library (kitob ijaraga olish)
4. Payments

---

### 8:30 — TIJORIY + XULOSA (90 sekund)

> "Va eng muhimi — **bu BMI emas, biznes!**
>
> Loyiha **UniAnalytics PRO** sifatida rasmiy tijoriy mahsulot. 4 ta pricing plan:
> - Free (100 talaba)
> - PRO (1.5M so'm/oy, 2000 talaba)
> - Enterprise (9M so'm/oy)
> - Government (Custom)
>
> Year 1 maqsadi: **5 ta mijoz, $12K daromad**. Year 3: **$300K ARR**.
>
> Loyiha **Railway, Render, VPS** ga deploy qilingan. **GitHub Actions** CI/CD avtomatik ishlaydi. Sentry monitoring, Prometheus metrics — production grade."

**Demo:** Landing page (/landing) — 5 sekund

> "Xulosa: Mazkur ishda nafaqat OLAP nazariyasi o'rganildi, balki **real ishlatish uchun tayyor**, **sun'iy intellekt asosida**, **monetizatsiya qilinishi mumkin** bo'lgan **professional mahsulot** yaratildi.
>
> Buyrtmalaringiz va savollaringizga tayyorman. Rahmat!"

---

## 🎯 KOMISSIYA SAVOLLARI (tayyor javoblar)

### S1: "XGBoost nimaga? Random Forest yoki Logistic Regression nima uchun emas?"

> "XGBoost — gradient boosting algoritmi. Bizning vazifa — tabular data classification. XGBoost bu turdagi vazifalarda eng yaxshi natija beradi. Kaggle musobaqalarining 60% da ishlatiladi. Random Forest baseline sifatida sinab ko'rilgan, lekin XGBoost 3% accuracy yuqori berdi. Bundan tashqari XGBoost native ravishda missing values ni hal qiladi."

### S2: "Sizning Star Schema da SCD (Slowly Changing Dimensions) qanday?"

> "Hozir SCD Type 1 (history saqlanmaydi). Production da Type 2 ga o'tish kerak — talabaning guruhi o'zgarganda eski yozuv saqlanadi. Bu uchun dim_student ga `valid_from`, `valid_to` ustunlari qo'shiladi."

### S3: "ClickHouse yoki Druid o'rniga PostgreSQL — nima uchun?"

> "Boshlang'ich bosqichda PostgreSQL **etarli** — 50,000 baho bilan 80ms. Bundan ortig'i (1 mln+) bo'lganda ClickHouse ga o'tamiz. PostgreSQL afzalligi: bitta DB engine, oddiy deploy, Alembic migration."

### S4: "HEMIS API real bormi yo'qmi?"

> "Hozir mock client. Real HEMIS API uchun vazirlik bilan kelishuv kerak — bu jarayon kechmoqda. Lekin bizning kod struktura tayyor: env vars ga TOKEN qo'yilsa, avtomatik real API ga o'tadi."

### S5: "AI Tutor — ChatGPT ga to'lov kim qiladi?"

> "Mijoz universitet to'laydi (Enterprise plan ichida). Yoki o'z API key ni qo'yadi. Demo rejimda — bizning oddiy javoblar."

### S6: "Konkurentlar — Tableau, PowerBI?"

> "Tableau/PowerBI — umumiy BI, ta'lim uchun emas. Bizda: 1) O'zbek tilida, 2) HEMIS bilan integratsiya, 3) Ta'lim domain-specific (drop-out, GPA), 4) 10x arzon."

### S7: "Multi-tenancy real ishlaydimi?"

> "Hozir shared schema with tenant_id. To'liq isolation uchun schema-per-tenant. Bizning Tenant model bor — Stage 7 ga o'tganda real isolation qilamiz."

### S8: "Bu loyiha qancha vaqt oldi?"

> "3 oy intensiv ish + 6 oy planlash. Hozir 6.0 versiya. Har hafta yangilanish chiqaramiz."

---

## 📋 TEXNIK TAYYORGARLIK

### Demoga 1 soat oldin:
- [ ] Backend ishga tushgan: `docker-compose up -d`
- [ ] Frontend ishga tushgan: http://localhost:3000
- [ ] Test login qilib ko'rilgan: admin/dekan/teacher/student
- [ ] Internet aloqasi (Claude API ishlatish uchun)
- [ ] Audio/mikrofon test
- [ ] Backup screenshot (agar live demo ishlamasa)

### Demoga 5 daqiqa oldin:
- [ ] Brauzer tab lar tayyor:
  - Tab 1: Landing page
  - Tab 2: Admin dashboard
  - Tab 3: OLAP cube
  - Tab 4: ML Insights
  - Tab 5: Student dashboard
  - Tab 6: AI Tutor
  - Tab 7: Swagger /docs
- [ ] Telefon Telegram bot uchun tayyor (agar mavjud bo'lsa)

### Demo davomida:
- [ ] Sekin va aniq gapir
- [ ] Har bir slide/sahifa da to'xtab biroz tushuntir
- [ ] Komissiyaga ko'z bilan aloqa qil
- [ ] Texnik atamalarni qisqacha izohla

---

## 🎁 BONUS: Demoda ko'rsatish mumkin bo'lgan "wow" momentlar

1. **Ctrl+K** Command Palette ochish — "Ko'rdingiz, har joydan navigatsiya"
2. **Dark mode** toggle — "Foydalanuvchi tajribasi muhim"
3. **5 ta rang sxema** — "Har universitet o'z brendiga moslashtirishi mumkin"
4. **Hero banner gradient animatsiya** — "Modern 2026 dizayn"
5. **AI Tutor real javob** — "ChatGPT level"
6. **PDF transkript yuklab olish** — "Real foydalanish uchun tayyor"
7. **5000 talaba, 50000 baho** raqamlari — "Real scale"

---

## 📊 SLAYDLAR (16 ta)

1. Title slide
2. Problem (HEMIS limitations)
3. Solution (UniAnalytics PRO)
4. Market opportunity ($600K)
5. Star Schema diagram (Mermaid)
6. 5 ta OLAP cube
7. XGBoost + SHAP screenshots
8. K-Means clustering visualization
9. AI Tutor demo screenshot
10. Role-based dashboards
11. HEMIS features
12. Tech stack
13. Pricing plans
14. Roadmap (Year 1-3)
15. Team
16. Q&A

Slaydlarning shabloni: Tilda — uzbek, font — Inter, ranglar — #1677ff (primary), #722ed1 (secondary).

---

**Omad! 🍀**
