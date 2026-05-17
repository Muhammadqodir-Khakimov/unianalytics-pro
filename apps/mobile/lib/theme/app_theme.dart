import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  AppTheme._();

  // Texnik Topshiriqdagi (TZ §4.4) brend rang-gammasi:
  //   Primary  — ko'k     #1E3A8A
  //   Accent   — zarg'aldoq #F59E0B
  //   Secondary— kulrang  #6B7280
  //   Success  — yashil   #10B981
  //   Error    — qizil    #EF4444
  static const Color brandBlue = Color(0xFF1E3A8A);
  static const Color brandAmber = Color(0xFFF59E0B);
  static const Color brandGreen = Color(0xFF10B981);
  static const Color brandRed = Color(0xFFEF4444);

  static ThemeData light() {
    final base = ColorScheme.fromSeed(
      seedColor: brandBlue,
      brightness: Brightness.light,
    );
    // Tertiary'ni TZ zarg'aldoqiga aniq moslab qo'yamiz —
    // gradient va aksent elementlar shu rangda chiqadi.
    final scheme = base.copyWith(
      tertiary: brandAmber,
      tertiaryContainer: brandAmber.withValues(alpha: 0.18),
      onTertiary: Colors.white,
      error: brandRed,
    );
    return _base(scheme);
  }

  static ThemeData dark() {
    final base = ColorScheme.fromSeed(
      seedColor: brandBlue,
      brightness: Brightness.dark,
    );
    final scheme = base.copyWith(
      tertiary: brandAmber,
      tertiaryContainer: const Color(0xFF5B3A00),
      onTertiary: Colors.black,
      error: brandRed,
    );
    return _base(scheme);
  }

  static ThemeData _base(ColorScheme scheme) {
    final isDark = scheme.brightness == Brightness.dark;
    final textTheme = GoogleFonts.interTextTheme(
      ThemeData(brightness: scheme.brightness).textTheme,
    ).copyWith(
      displayLarge: GoogleFonts.inter(
        fontWeight: FontWeight.w800,
        letterSpacing: -1.5,
      ),
      headlineMedium: GoogleFonts.inter(
        fontWeight: FontWeight.w800,
        letterSpacing: -0.5,
      ),
      headlineSmall: GoogleFonts.inter(fontWeight: FontWeight.w700),
      titleLarge: GoogleFonts.inter(fontWeight: FontWeight.w700),
      titleMedium: GoogleFonts.inter(fontWeight: FontWeight.w600),
      titleSmall: GoogleFonts.inter(fontWeight: FontWeight.w600),
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      textTheme: textTheme,
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        foregroundColor: scheme.onSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: scheme.onSurface,
          letterSpacing: -0.3,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(56),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.1,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size.fromHeight(56),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          textStyle: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: isDark
            ? scheme.surfaceContainerHigh.withValues(alpha: 0.6)
            : Colors.white.withValues(alpha: 0.85),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: scheme.outlineVariant.withValues(alpha: 0.4),
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(
            color: scheme.outlineVariant.withValues(alpha: 0.4),
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: scheme.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: scheme.error, width: 1.5),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 18,
        ),
        labelStyle: TextStyle(
          color: scheme.onSurfaceVariant,
          fontWeight: FontWeight.w500,
        ),
      ),
      cardTheme: CardThemeData(
        color: scheme.surfaceContainerLow,
        elevation: 0,
        shadowColor: scheme.shadow.withValues(alpha: 0.04),
        surfaceTintColor: Colors.transparent,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: scheme.outlineVariant.withValues(alpha: 0.3),
            width: 1,
          ),
        ),
      ),
      dividerTheme: DividerThemeData(
        color: scheme.outlineVariant.withValues(alpha: 0.4),
        thickness: 1,
        space: 1,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: scheme.surface,
        indicatorColor: scheme.primaryContainer,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => GoogleFonts.inter(
            fontSize: 12,
            fontWeight: states.contains(WidgetState.selected)
                ? FontWeight.w700
                : FontWeight.w500,
            color: states.contains(WidgetState.selected)
                ? scheme.onSurface
                : scheme.onSurfaceVariant,
          ),
        ),
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            color: states.contains(WidgetState.selected)
                ? scheme.onPrimaryContainer
                : scheme.onSurfaceVariant,
            size: 26,
          ),
        ),
        height: 72,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: scheme.inverseSurface,
        contentTextStyle: GoogleFonts.inter(
          color: scheme.onInverseSurface,
          fontWeight: FontWeight.w500,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
      ),
      listTileTheme: const ListTileThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
        ),
      ),
    );
  }
}
