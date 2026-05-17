# UniAnalytics Mobile (React Native + Expo)

## Ishga tushirish

```bash
cd apps/mobile
npm install
npx expo start
```

Brauzerda QR kodni Expo Go ilovasi orqali skanerlash, yoki:
- iOS simulator: `i` ni bosing
- Android emulator: `a` ni bosing
- Web: `w` ni bosing

## Features

- ✅ Login (parol + Face ID/Touch ID)
- ✅ Dashboard (GPA, davomat KPI)
- ✅ Baholar ro'yxati
- ✅ Jadval + QR scan (davomat uchun)
- ✅ Profil
- ✅ Push notifications (FCM)

## Build

iOS:
```bash
eas build --platform ios
```

Android:
```bash
eas build --platform android
```

App Store / Google Play ga submission uchun:
- Apple Developer: $99/yil
- Google Play: $25 bir martalik

## API endpoint

`apps/mobile/services/api.ts` da:
```typescript
const API_URL = 'https://backend-production-89be.up.railway.app/api/v1';
```
