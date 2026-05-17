# UniAnalytics PRO — Mobile (Flutter)

Talabalar reyting natijalarini tahlil qilish tizimining mobil mijozi.

## Texnologiyalar

- **Flutter** 3.38 / Dart 3.10
- **State:** flutter_riverpod 2.x
- **Routing:** go_router (auth + app-lock aware redirect, slide transitions)
- **Network:** Dio (+ pretty_dio_logger, JWT auth interceptor)
- **Storage:** flutter_secure_storage (tokens), Hive CE (offline cache), SharedPreferences (sozlamalar)
- **Theme:** Material 3 (light/dark/system), Google Fonts (Inter)
- **Charts:** fl_chart (GPA trend line, fanlar bar)
- **Skeletons:** shimmer (Dashboard, Grades)
- **i18n:** uz / ru / en
- **Biometric:** local_auth (Touch ID / Face ID / PIN fallback)
- **Push notifications:** stub (FCM keyingi versiyada)

## Arxitektura

Clean Architecture:

```
lib/
├── core/                # constants, errors, network (Dio + interceptors)
├── data/datasources/    # 6 ta remote datasource (auth, my, grades, subjects, schedule, notifications)
├── domain/entities/     # 7 ta entity (User, Grade, Subject, ScheduleItem, NotificationItem, MyDashboard, Paginated)
├── providers/           # auth, data, settings, app-lock (Riverpod)
├── routing/             # go_router (auth+lock redirect, page transitions)
├── services/            # SecureStorage, HiveCache, Biometric, PushNotifications
├── theme/               # Material 3 light/dark
├── presentation/
│   ├── auth/            # Splash, Login, Register, AppLock
│   ├── dashboard/       # Real /my/dashboard + GPA chart + Subjects chart
│   ├── grades/          # Filter + qidirish
│   ├── subjects/        # Fanlar
│   ├── schedule/        # Kunlar bo'yicha
│   ├── notifications/   # Read holatini boshqarish
│   ├── profile/         # Akkaunt + logout
│   ├── settings/        # Tema, til, biometric
│   ├── teacher/         # MySubjects, MyGroups, GradeEntry
│   └── widgets/         # AppShell (bottom nav), charts, skeletons, async views
└── main.dart            # ProviderScope + Hive init + MaterialApp.router
```

## Funksiyalar

### Talaba uchun
- ✅ Real-time dashboard: GPA, o'rt. ball, davomat, guruhda o'rin (rank card)
- ✅ GPA dinamikasi line chart (fl_chart)
- ✅ Fanlar bo'yicha o'rtacha bar chart (fl_chart, top-5)
- ✅ Baholar: qidiruv + filtre (Hammasi / O'tgan / O'tmagan)
- ✅ Dars jadvali kunlar bo'yicha
- ✅ Bildirishnomalar: tap'da read, hammasini read qilish
- ✅ Offline cache (Hive): tarmoq yo'q bo'lganda 3 kungacha eski ma'lumot

### O'qituvchi uchun
- ✅ Dashboard fanlar bo'yicha statistika
- ✅ Mening fanlarim (real `/my/dashboard`)
- ✅ Baho qo'yish MVP form (student_id, fan_id, JN/ON/YN/FINAL, ball)
- ⏳ MyGroups (backend `/teachers/me/groups` endpoint keyingi versiyada)

### Xavfsizlik va polish
- ✅ Biometrik qulflash (Touch ID / Face ID / PIN) — settings'dan yoqiladi
- ✅ App boshlanganda lock screen (biometric)
- ✅ Shimmer skeleton loaderlar
- ✅ Sliding page transitions
- ✅ Tema (Tizim / Yorug' / Qorong'i) + tilni almashtirish (uz/ru/en)
- ✅ Material 3 dizayn
- ⏳ FCM push (Firebase loyiha sozlanganda)

## Ishga tushirish

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

- **Android emulator:** host kompyuter `localhost` = `10.0.2.2`
- **iOS simulator:** `localhost` ishlaydi
- **Real qurilma:** kompyuter IP manzili (masalan, `http://192.168.1.10:8000/api/v1`)

## Test

```bash
flutter test         # widget testlar
flutter analyze      # static analysis
```

## Build

```bash
flutter build apk --release         # Android (D:\Program Files\Android — SDK yo'lida bo'sh joy bor, kerak bo'lsa ko'chiring)
flutter build appbundle --release   # Google Play
flutter build ipa --release         # iOS (macOS kerak)
```

## Native sozlamalar

### Android (`android/app/src/main/AndroidManifest.xml`)
- `USE_BIOMETRIC`, `USE_FINGERPRINT` — biometric auth
- `INTERNET` — Dio HTTP requestlari
- `MainActivity` → `FlutterFragmentActivity` (local_auth talabi)

### iOS (`ios/Runner/Info.plist`)
- `NSFaceIDUsageDescription` — Face ID prompt

## Bosqichlar

- [x] **Bosqich 12** — Skeleton, auth (login + me + logout), splash, dashboard placeholder
- [x] **Bosqich 13** — Talaba va o'qituvchi ekranlari, navigation shell, settings
- [x] **Bosqich 14** — fl_chart grafikalar, Hive offline cache, biometric auth, shimmer skeletonlar, page transitions
- [ ] **Bosqich 14b (kelajak)** — FCM push notifications (Firebase loyiha sozlash kerak)
- [ ] **E2E testlar** — flutter integration_test yoki Maestro
