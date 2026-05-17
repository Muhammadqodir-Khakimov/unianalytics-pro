import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants/app_constants.dart';

class AppSettings {
  final ThemeMode themeMode;
  final Locale locale;
  final bool biometricEnabled;

  const AppSettings({
    this.themeMode = ThemeMode.system,
    this.locale = const Locale('uz'),
    this.biometricEnabled = false,
  });

  AppSettings copyWith({
    ThemeMode? themeMode,
    Locale? locale,
    bool? biometricEnabled,
  }) =>
      AppSettings(
        themeMode: themeMode ?? this.themeMode,
        locale: locale ?? this.locale,
        biometricEnabled: biometricEnabled ?? this.biometricEnabled,
      );
}

final settingsControllerProvider =
    StateNotifierProvider<SettingsController, AppSettings>((ref) {
  return SettingsController()..load();
});

class SettingsController extends StateNotifier<AppSettings> {
  static const _biometricKey = 'biometric_enabled';

  SettingsController() : super(const AppSettings());

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    state = AppSettings(
      themeMode: _themeFromString(prefs.getString(AppConstants.themeModeKey)),
      locale: Locale(prefs.getString(AppConstants.localeKey) ?? 'uz'),
      biometricEnabled: prefs.getBool(_biometricKey) ?? false,
    );
  }

  Future<void> setTheme(ThemeMode mode) async {
    state = state.copyWith(themeMode: mode);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.themeModeKey, mode.name);
  }

  Future<void> setLocale(Locale locale) async {
    state = state.copyWith(locale: locale);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.localeKey, locale.languageCode);
  }

  Future<void> setBiometric(bool enabled) async {
    state = state.copyWith(biometricEnabled: enabled);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_biometricKey, enabled);
  }

  static ThemeMode _themeFromString(String? s) {
    switch (s) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      default:
        return ThemeMode.system;
    }
  }
}

/// App lock — biometric yoqilgan bo'lsa, app boshlanganda lock screen ko'rinadi.
/// Auth ready + biometric on bo'lsa => `true`. User pass qilsa => `false`.
final appLockProvider = StateProvider<bool>((ref) {
  final settings = ref.watch(settingsControllerProvider);
  return settings.biometricEnabled;
});
