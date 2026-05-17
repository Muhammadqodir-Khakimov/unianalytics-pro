# Mobile Build (Expo EAS)

## 1. Setup

```bash
npm i -g eas-cli
cd apps/mobile
npm install
eas login                         # Expo akkauntga kirish
eas init                          # project ID berish (expo.io'da yaratiladi)
```

## 2. Development APK

```bash
eas build --profile development --platform android
# QR code beradi → Expo Go bilan yoki devloper client bilan ochasiz
```

## 3. Preview APK (testerlar uchun)

```bash
eas build --profile preview --platform android
# .apk fayl yuklab beradi — Telegram'da yuborish mumkin
```

## 4. Production AAB (Google Play uchun)

```bash
eas build --profile production --platform android
# .aab fayl yaratadi
```

## 5. Google Play'ga yuborish

### Avval:
1. Google Play Console hisob ochish ($25 bir martalik)
2. App'ni qo'lda yaratish → Production track
3. Service Account JSON yuklab olish → `apps/mobile/google-service-account.json`

### Keyin:
```bash
eas submit --profile production --platform android
```

## 6. iOS (App Store)

```bash
eas build --profile production --platform ios
eas submit --profile production --platform ios
```

Talab: Apple Developer akkaunt ($99/yil)

## 7. Updates (OTA bez rebuild)

JS/asset o'zgarishlari APK'ni qayta yig'masdan push qilinishi mumkin:
```bash
eas update --branch production --message "Bug fix: login screen"
```

## Tavsiya yo'l xaritasi

1. `eas build --profile preview --platform android` (5-10 daqiqa)
2. APK'ni 5-10 ta talabaga yubor (alpha test)
3. Feedback yig' → tuzat → yangi preview APK
4. Tayyor bo'lganda → `production` build → Google Play
