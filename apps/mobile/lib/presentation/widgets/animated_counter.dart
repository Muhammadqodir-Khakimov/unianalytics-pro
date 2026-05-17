import 'package:flutter/material.dart';

/// 0 dan berilgan qiymatga ravon o'sib boruvchi raqamli hisoblagich.
/// Kelgan ma'lumotni "tirik" qilib ko'rsatish uchun.
class AnimatedCounter extends StatelessWidget {
  final double value;
  final int fractionDigits;
  final String suffix;
  final TextStyle? style;
  final Duration duration;

  const AnimatedCounter({
    super.key,
    required this.value,
    this.fractionDigits = 0,
    this.suffix = '',
    this.style,
    this.duration = const Duration(milliseconds: 900),
  });

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: value),
      duration: duration,
      curve: Curves.easeOutCubic,
      builder: (context, v, _) => Text(
        '${v.toStringAsFixed(fractionDigits)}$suffix',
        style: style,
      ),
    );
  }
}
