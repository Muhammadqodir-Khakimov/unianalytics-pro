import 'dart:ui';

import 'package:flutter/material.dart';

/// Haqiqiy "frosted glass" kartochka — BackdropFilter orqali ortidagi
/// pikselslarni xiralashtirib, yarim shaffof qatlam bilan qoplaydi.
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final double radius;
  final double blur;

  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.fromLTRB(22, 24, 22, 22),
    this.radius = 24,
    this.blur = 22,
  });

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final isDark = scheme.brightness == Brightness.dark;

    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: isDark
                ? Colors.white.withValues(alpha: 0.06)
                : Colors.white.withValues(alpha: 0.55),
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(
              color: isDark
                  ? Colors.white.withValues(alpha: 0.10)
                  : Colors.white.withValues(alpha: 0.6),
              width: 1.2,
            ),
            boxShadow: [
              BoxShadow(
                color: scheme.shadow.withValues(alpha: isDark ? 0.4 : 0.08),
                blurRadius: 32,
                offset: const Offset(0, 12),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
