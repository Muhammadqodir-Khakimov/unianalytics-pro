class AppConstants {
  AppConstants._();

  static const String appName = 'UniAnalytics PRO';
  static const String appVersion = '1.0.0';

  // Backend base URL — Android emulator uchun 10.0.2.2, iOS simulator uchun localhost
  // Build vaqtida override: --dart-define=API_BASE_URL=https://api.example.com
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  // Tokenlar uchun secure storage kalitlari
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'current_user';

  // Til/tema kalitlari (SharedPreferences)
  static const String localeKey = 'app_locale';
  static const String themeModeKey = 'app_theme_mode';

  // Timeoutlar (millisekund)
  static const int connectTimeoutMs = 15000;
  static const int receiveTimeoutMs = 20000;
}
