import 'dart:math' as math;
import 'dart:ui';

import 'package:flutter/material.dart';

/// Ekran ortida sekin suzayotgan rangli "blob"lar — premium auth ekranlari
/// uchun zamonaviy fon effekti. BackdropFilter bilan kombinatsiyada
/// glassmorphism kartochkalari uchun mukammal asos beradi.
class AnimatedBlobsBackground extends StatefulWidget {
  final Widget child;
  const AnimatedBlobsBackground({super.key, required this.child});

  @override
  State<AnimatedBlobsBackground> createState() =>
      _AnimatedBlobsBackgroundState();
}

class _AnimatedBlobsBackgroundState extends State<AnimatedBlobsBackground>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 18),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final isDark = scheme.brightness == Brightness.dark;
    final baseColor = isDark
        ? const Color(0xFF0F1029)
        : const Color(0xFFF7F8FF);

    return Stack(
      fit: StackFit.expand,
      children: [
        ColoredBox(color: baseColor),
        AnimatedBuilder(
          animation: _ctrl,
          builder: (context, _) {
            return CustomPaint(
              painter: _BlobsPainter(
                progress: _ctrl.value,
                primary: scheme.primary,
                tertiary: scheme.tertiary,
                isDark: isDark,
              ),
              size: Size.infinite,
            );
          },
        ),
        // Yengil shisha qatlam — blur ortidagi blob'lar yumshoq bo'lib ko'rinadi.
        BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
          child: const ColoredBox(color: Colors.transparent),
        ),
        widget.child,
      ],
    );
  }
}

class _BlobsPainter extends CustomPainter {
  final double progress; // 0..1
  final Color primary;
  final Color tertiary;
  final bool isDark;

  _BlobsPainter({
    required this.progress,
    required this.primary,
    required this.tertiary,
    required this.isDark,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final t = progress * 2 * math.pi;
    final alpha = isDark ? 0.55 : 0.45;

    _paintBlob(
      canvas,
      size,
      Offset(
        size.width * (0.25 + 0.08 * math.cos(t)),
        size.height * (0.22 + 0.05 * math.sin(t)),
      ),
      size.width * 0.55,
      primary.withValues(alpha: alpha),
    );
    _paintBlob(
      canvas,
      size,
      Offset(
        size.width * (0.75 + 0.06 * math.cos(t + math.pi / 2)),
        size.height * (0.35 + 0.06 * math.sin(t + math.pi / 2)),
      ),
      size.width * 0.5,
      tertiary.withValues(alpha: alpha * 0.9),
    );
    _paintBlob(
      canvas,
      size,
      Offset(
        size.width * (0.4 + 0.07 * math.cos(t + math.pi)),
        size.height * (0.82 + 0.05 * math.sin(t + math.pi)),
      ),
      size.width * 0.6,
      Color.lerp(primary, tertiary, 0.5)!.withValues(alpha: alpha * 0.8),
    );
  }

  void _paintBlob(
      Canvas canvas, Size size, Offset center, double radius, Color color) {
    final paint = Paint()
      ..shader = RadialGradient(
        colors: [color, color.withValues(alpha: 0)],
      ).createShader(Rect.fromCircle(center: center, radius: radius));
    canvas.drawCircle(center, radius, paint);
  }

  @override
  bool shouldRepaint(covariant _BlobsPainter old) =>
      old.progress != progress ||
      old.primary != primary ||
      old.tertiary != tertiary;
}
