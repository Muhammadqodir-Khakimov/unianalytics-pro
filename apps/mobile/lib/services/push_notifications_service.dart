import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Push notifications stub.
///
/// Production'da Firebase Cloud Messaging (FCM) ulanadi:
///   1. `firebase_messaging` paketini `pubspec.yaml` ga qo'shing
///   2. Android: `android/app/google-services.json` qo'shing va Gradle plugin
///      sozlamalarini yangilang
///   3. iOS: APNs sertifikatlari + `GoogleService-Info.plist`
///   4. Bu yerdagi `register()` metodi token oladi va backendga yuboradi
///      (`POST /users/me/push-token`)
class PushNotificationsService {
  /// Tokenni olish va serverga yuborish — stub.
  Future<String?> register() async {
    if (kDebugMode) {
      debugPrint('PushNotificationsService: FCM hali ulanmagan (stub).');
    }
    return null;
  }

  Future<void> unregister() async {
    // FCM token o'chirish va serverga xabar berish.
  }
}

final pushServiceProvider =
    Provider<PushNotificationsService>((ref) => PushNotificationsService());
