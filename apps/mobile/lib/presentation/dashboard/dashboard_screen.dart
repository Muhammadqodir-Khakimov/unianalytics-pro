import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/my_dashboard.dart';
import '../../domain/entities/user.dart';
import '../../providers/auth_provider.dart';
import '../../providers/data_providers.dart';
import '../../theme/gradients.dart';
import '../widgets/animated_counter.dart';
import '../widgets/charts/gpa_trend_chart.dart';
import '../widgets/charts/subjects_bar_chart.dart';
import '../widgets/skeletons.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);
    final user = auth is Authenticated ? auth.user : null;
    final dash = ref.watch(myDashboardProvider);

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(myDashboardProvider.future),
        child: dash.when(
          data: (data) => _DashboardContent(user: user, data: data),
          loading: () => const DashboardSkeleton(),
          error: (e, _) => _ErrorView(
            message: '$e',
            onRetry: () => ref.invalidate(myDashboardProvider),
          ),
        ),
      ),
    );
  }
}

class _DashboardContent extends StatelessWidget {
  final User? user;
  final MyDashboard data;
  const _DashboardContent({required this.user, required this.data});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: _HeroHeader(user: user, data: data, theme: theme),
        ),
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
          sliver: SliverList.list(
            children: _buildSections(data, scheme),
          ),
        ),
      ],
    );
  }

  List<Widget> _buildSections(MyDashboard data, ColorScheme scheme) {
    final sections = <Widget>[];

    if (!data.linked && data.message != null) {
      sections.add(_LinkedWarning(message: data.message!));
    }
    if (data.linked) {
      sections.add(_StatsGrid(data: data, scheme: scheme));
    }
    if (data.linked && data.role == 'student') {
      sections.add(const SizedBox(height: 14));
      sections.add(_AchievementsRow(data: data));
    }
    if (data.linked && data.rank != null) {
      sections.add(const SizedBox(height: 14));
      sections.add(_RankCard(rank: data.rank!, total: data.rankTotal));
    }
    if (data.gpaTrend.isNotEmpty) {
      sections.add(const SizedBox(height: 24));
      sections.add(_SectionHeader(
          title: 'GPA dinamikasi', icon: Icons.show_chart));
      sections.add(const SizedBox(height: 10));
      sections.add(Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: GpaTrendChart(trend: data.gpaTrend),
        ),
      ));
    }
    if (data.role == 'teacher') {
      sections.add(const SizedBox(height: 24));
      sections.add(_SectionHeader(
          title: 'O‘qituvchi bo‘limi', icon: Icons.school_outlined));
      sections.add(const SizedBox(height: 10));
      sections.add(_TeacherQuickLinks());
    }
    if (data.bySubject.isNotEmpty) {
      sections.add(const SizedBox(height: 24));
      sections.add(_SectionHeader(
        title: data.role == 'teacher'
            ? 'Mening fanlarim'
            : 'Fanlar bo‘yicha o‘rtacha',
        icon: Icons.bar_chart,
      ));
      sections.add(const SizedBox(height: 10));
      sections.add(Card(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
          child: SubjectsBarChart(bySubject: data.bySubject),
        ),
      ));
    }
    sections.add(const SizedBox(height: 16));

    // Staggered fade-in + slide-up entry animation
    return [
      for (int i = 0; i < sections.length; i++)
        sections[i]
            .animate(delay: (60 * i).ms)
            .fadeIn(duration: 400.ms)
            .slideY(begin: 0.06, curve: Curves.easeOutCubic),
    ];
  }
}

// ---------------------------------------------------------------------------
// Hero header (gradient)
// ---------------------------------------------------------------------------
class _HeroHeader extends StatelessWidget {
  final User? user;
  final MyDashboard data;
  final ThemeData theme;
  const _HeroHeader({
    required this.user,
    required this.data,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    final scheme = theme.colorScheme;
    final name = data.studentFullName ?? data.teacherFullName ?? user?.fullName ?? '—';
    final subtitle = _subtitle();
    final initials = _initials(name);

    return Container(
      decoration: BoxDecoration(
        gradient: AppGradients.hero(scheme),
        borderRadius: const BorderRadius.vertical(
          bottom: Radius.circular(28),
        ),
      ),
      padding: EdgeInsets.fromLTRB(
        20,
        MediaQuery.of(context).padding.top + 16,
        20,
        24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Salom 👋',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: Colors.white.withValues(alpha: 0.85),
                  fontWeight: FontWeight.w500,
                ),
              ),
              const Spacer(),
              _IconBtn(
                icon: Icons.notifications_none_outlined,
                onTap: () => GoRouter.of(context).go('/notifications'),
              ),
              const SizedBox(width: 8),
              _IconBtn(
                icon: Icons.person_outline,
                onTap: () => GoRouter.of(context).push('/profile'),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.22),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.3),
                    width: 1.5,
                  ),
                ),
                child: Center(
                  child: Text(
                    initials,
                    style: theme.textTheme.titleLarge?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: theme.textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        subtitle,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: Colors.white.withValues(alpha: 0.85),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String? _subtitle() {
    switch (data.role) {
      case 'student':
        final parts = <String>[
          if (data.course != null) '${data.course}-kurs',
          if (data.groupName != null) data.groupName!,
        ];
        return parts.isEmpty ? null : parts.join(' • ');
      case 'teacher':
        final parts = <String>[
          if (data.department != null) data.department!,
          if (data.position != null) data.position!,
        ];
        return parts.isEmpty ? null : parts.join(' • ');
      default:
        return data.role.toUpperCase();
    }
  }

  String _initials(String name) {
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.isEmpty) return '?';
    if (parts.length == 1) {
      return parts[0].isNotEmpty ? parts[0][0].toUpperCase() : '?';
    }
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
}

class _IconBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _IconBtn({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white.withValues(alpha: 0.18),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: SizedBox(
          width: 40,
          height: 40,
          child: Icon(icon, color: Colors.white, size: 22),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Section header
// ---------------------------------------------------------------------------
class _SectionHeader extends StatelessWidget {
  final String title;
  final IconData icon;
  const _SectionHeader({required this.title, required this.icon});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Icon(icon, size: 20, color: theme.colorScheme.primary),
        const SizedBox(width: 8),
        Text(
          title,
          style: theme.textTheme.titleMedium,
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Stats grid (4 ta karta)
// ---------------------------------------------------------------------------
class _StatsGrid extends StatelessWidget {
  final MyDashboard data;
  final ColorScheme scheme;
  const _StatsGrid({required this.data, required this.scheme});

  @override
  Widget build(BuildContext context) {
    final tiles = <_StatData>[
      _StatData(
        label: 'GPA',
        value: data.avgGpa?.toStringAsFixed(2) ?? '—',
        numericValue: data.avgGpa,
        fractionDigits: 2,
        icon: Icons.auto_graph,
        color: scheme.primary,
      ),
      _StatData(
        label: 'O‘rt. ball',
        value: data.avgGrade?.toStringAsFixed(1) ?? '—',
        numericValue: data.avgGrade,
        fractionDigits: 1,
        icon: Icons.percent,
        color: scheme.tertiary,
      ),
      _StatData(
        label: 'Baholar',
        value: data.gradesCount?.toString() ?? '0',
        numericValue: data.gradesCount?.toDouble(),
        icon: Icons.assessment_outlined,
        color: scheme.secondary,
      ),
      _StatData(
        label: 'Davomat',
        value: data.avgAttendance != null
            ? '${data.avgAttendance!.toStringAsFixed(0)}%'
            : '—',
        numericValue: data.avgAttendance,
        suffix: '%',
        icon: Icons.event_available_outlined,
        color: const Color(0xFF10B981),
      ),
    ];
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: tiles.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 1.35,
      ),
      itemBuilder: (_, i) => _StatCard(stat: tiles[i]),
    );
  }
}

class _StatData {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  /// Agar berilsa — animatsiyalangan hisoblagich ko'rsatiladi.
  final double? numericValue;
  final int fractionDigits;
  final String suffix;
  const _StatData({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
    this.numericValue,
    this.fractionDigits = 0,
    this.suffix = '',
  });
}

class _StatCard extends StatelessWidget {
  final _StatData stat;
  const _StatCard({required this.stat});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final numericValue = stat.numericValue;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: AppGradients.statTile(stat.color),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: stat.color.withValues(alpha: 0.18),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: stat.color.withValues(alpha: 0.18),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(stat.icon, color: stat.color, size: 20),
          ),
          const SizedBox(height: 6),
          if (numericValue != null)
            AnimatedCounter(
              value: numericValue,
              fractionDigits: stat.fractionDigits,
              suffix: stat.suffix,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
                color: stat.color,
                letterSpacing: -0.5,
              ),
            )
          else
            Text(
              stat.value,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
                color: stat.color,
                letterSpacing: -0.5,
              ),
            ),
          Text(
            stat.label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Achievements / progress chips
// ---------------------------------------------------------------------------
class _AchievementsRow extends StatelessWidget {
  final MyDashboard data;
  const _AchievementsRow({required this.data});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    final passed = data.passedCount ?? 0;
    final total = (data.gradesCount ?? 0).clamp(1, 1 << 30);
    final passRate = (passed / total * 100).clamp(0, 100).toDouble();
    final gpaPct = ((data.avgGpa ?? 0) / 4.0 * 100).clamp(0, 100).toDouble();
    final attendance = (data.avgAttendance ?? 0).clamp(0, 100).toDouble();

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
      decoration: BoxDecoration(
        color: scheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: scheme.outlineVariant.withValues(alpha: 0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Haftalik ko‘rsatkichlar',
            style: theme.textTheme.titleSmall,
          ),
          const SizedBox(height: 12),
          _ProgressRow(
            label: 'GPA / 4.0',
            valueLabel: (data.avgGpa ?? 0).toStringAsFixed(2),
            percent: gpaPct,
            color: scheme.primary,
            icon: Icons.auto_graph,
          ),
          const SizedBox(height: 10),
          _ProgressRow(
            label: 'O‘zlashtirish',
            valueLabel: '${passRate.toStringAsFixed(0)}%',
            percent: passRate,
            color: const Color(0xFF10B981),
            icon: Icons.check_circle_outline,
          ),
          const SizedBox(height: 10),
          _ProgressRow(
            label: 'Davomat',
            valueLabel: '${attendance.toStringAsFixed(0)}%',
            percent: attendance,
            color: scheme.tertiary,
            icon: Icons.event_available_outlined,
          ),
        ],
      ),
    );
  }
}

class _ProgressRow extends StatelessWidget {
  final String label;
  final String valueLabel;
  final double percent; // 0-100
  final Color color;
  final IconData icon;
  const _ProgressRow({
    required this.label,
    required this.valueLabel,
    required this.percent,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    return Row(
      children: [
        Container(
          width: 30,
          height: 30,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.16),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, size: 16, color: color),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      label,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: scheme.onSurfaceVariant,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  Text(
                    valueLabel,
                    style: theme.textTheme.labelMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: color,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              TweenAnimationBuilder<double>(
                tween: Tween<double>(begin: 0, end: percent / 100),
                duration: const Duration(milliseconds: 800),
                curve: Curves.easeOutCubic,
                builder: (context, v, _) => ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: v,
                    minHeight: 8,
                    backgroundColor: color.withValues(alpha: 0.12),
                    valueColor: AlwaysStoppedAnimation(color),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Rank card
// ---------------------------------------------------------------------------
class _RankCard extends StatelessWidget {
  final int rank;
  final int? total;
  const _RankCard({required this.rank, this.total});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            scheme.tertiaryContainer,
            scheme.primaryContainer,
          ],
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.85),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(
              Icons.emoji_events_rounded,
              size: 32,
              color: const Color(0xFFEAB308),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Guruh ichida o‘rin',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: scheme.onTertiaryContainer,
                  ),
                ),
                const SizedBox(height: 2),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.baseline,
                  textBaseline: TextBaseline.alphabetic,
                  children: [
                    Text(
                      '#$rank',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        color: scheme.onTertiaryContainer,
                      ),
                    ),
                    if (total != null) ...[
                      const SizedBox(width: 4),
                      Text(
                        '/ $total',
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: scheme.onTertiaryContainer
                              .withValues(alpha: 0.7),
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Teacher quick links
// ---------------------------------------------------------------------------
class _TeacherQuickLinks extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    final tiles = <(String, IconData, String)>[
      ('Mening fanlarim', Icons.menu_book_outlined, '/teacher/subjects'),
      ('Mening guruhlarim', Icons.groups_outlined, '/teacher/groups'),
      ('Baho qo‘yish', Icons.edit_note_outlined, '/teacher/grade-entry'),
    ];
    return Column(
      children: [
        for (final (label, icon, path) in tiles) ...[
          Card(
            child: ListTile(
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: scheme.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: scheme.onPrimaryContainer),
              ),
              title: Text(label,
                  style: theme.textTheme.titleSmall),
              trailing: Icon(
                Icons.chevron_right_rounded,
                color: scheme.onSurfaceVariant,
              ),
              onTap: () => GoRouter.of(context).push(path),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Warning + Error views
// ---------------------------------------------------------------------------
class _LinkedWarning extends StatelessWidget {
  final String message;
  const _LinkedWarning({required this.message});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: scheme.errorContainer,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: scheme.onErrorContainer),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: scheme.onErrorContainer,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        const SizedBox(height: 80),
        Icon(Icons.error_outline,
            size: 56, color: theme.colorScheme.error),
        const SizedBox(height: 16),
        Text(
          'Ma‘lumotni yuklab bo‘lmadi',
          style: theme.textTheme.titleMedium,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          message,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 16),
        Center(
          child: FilledButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh),
            label: const Text('Qayta urinish'),
          ),
        ),
      ],
    );
  }
}
