import 'package:flutter/material.dart';

/// Tema-aware gradientlar to'plami. Yorug' va qorong'i rejimda mos
/// rang berishi uchun [ColorScheme] orqali quriladi.
class AppGradients {
  AppGradients._();

  /// Login/Splash uchun yumshoq, brand rangli fon gradient.
  static LinearGradient brand(ColorScheme scheme) {
    final isDark = scheme.brightness == Brightness.dark;
    return LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: isDark
          ? [
              const Color(0xFF1A1B2E),
              const Color(0xFF2D1B4E),
              const Color(0xFF1F1147),
            ]
          : [
              const Color(0xFFEEF0FF),
              const Color(0xFFF5EAFE),
              const Color(0xFFFFF1F8),
            ],
    );
  }

  /// Hero header uchun ko'p qatlamli gradient (dashboard).
  static LinearGradient hero(ColorScheme scheme) {
    return LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        scheme.primary,
        Color.lerp(scheme.primary, scheme.tertiary, 0.6)!,
        scheme.tertiary,
      ],
    );
  }

  /// GPA chart uchun line + area fill gradient.
  static LinearGradient chartLine(ColorScheme scheme) {
    return LinearGradient(
      begin: Alignment.centerLeft,
      end: Alignment.centerRight,
      colors: [
        scheme.primary,
        scheme.tertiary,
      ],
    );
  }

  static LinearGradient chartArea(ColorScheme scheme) {
    return LinearGradient(
      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
      colors: [
        scheme.primary.withValues(alpha: 0.25),
        scheme.primary.withValues(alpha: 0.02),
      ],
    );
  }

  /// Stat kartalar uchun nozik fon gradient (rang asosida).
  static LinearGradient statTile(Color color) {
    return LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        color.withValues(alpha: 0.18),
        color.withValues(alpha: 0.05),
      ],
    );
  }
}
