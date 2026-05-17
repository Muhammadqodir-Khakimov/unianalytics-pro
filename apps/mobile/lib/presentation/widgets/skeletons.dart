import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

class _ShimmerBox extends StatelessWidget {
  final double height;
  final BorderRadius? radius;
  const _ShimmerBox({required this.height, this.radius});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      height: height,
      width: double.infinity,
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: radius ?? BorderRadius.circular(8),
      ),
    );
  }
}

class _ShimmerWrap extends StatelessWidget {
  final Widget child;
  const _ShimmerWrap({required this.child});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final base = theme.colorScheme.surfaceContainerHighest;
    final highlight = theme.colorScheme.surfaceContainerLow;
    return Shimmer.fromColors(
      baseColor: base,
      highlightColor: highlight,
      period: const Duration(milliseconds: 1200),
      child: child,
    );
  }
}

/// Dashboard uchun skeleton (header + 2x2 stats grid).
class DashboardSkeleton extends StatelessWidget {
  const DashboardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return _ShimmerWrap(
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        children: [
          const _ShimmerBox(height: 84, radius: null),
          const SizedBox(height: 16),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.5,
            children: const [
              _ShimmerBox(height: 0),
              _ShimmerBox(height: 0),
              _ShimmerBox(height: 0),
              _ShimmerBox(height: 0),
            ],
          ),
          const SizedBox(height: 16),
          const _ShimmerBox(height: 80, radius: null),
          const SizedBox(height: 24),
          for (var i = 0; i < 3; i++) ...[
            const _ShimmerBox(height: 60, radius: null),
            const SizedBox(height: 8),
          ],
        ],
      ),
    );
  }
}

/// Ro'yxat (Grades, Subjects) uchun skeleton.
class ListSkeleton extends StatelessWidget {
  final int count;
  const ListSkeleton({super.key, this.count = 8});

  @override
  Widget build(BuildContext context) {
    return _ShimmerWrap(
      child: ListView.separated(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        itemCount: count,
        separatorBuilder: (_, _) => const SizedBox(height: 8),
        itemBuilder: (_, _) => const _ShimmerBox(height: 64, radius: null),
      ),
    );
  }
}
