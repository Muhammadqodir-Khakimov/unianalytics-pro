import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../providers/data_providers.dart';

/// Qo'shimcha ma'lumotlar — TZ talab qilgan ko'p o'lchamli ko'rinishlar:
/// fakultet o'rni, TOP klassmatlar, fan kesimida davomat, yaqin imtihonlar,
/// aloqa kontaktlari. Barcha bo'limlar bitta scroll'da.
class ExtrasScreen extends ConsumerWidget {
  const ExtrasScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Qo\'shimcha')),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(facultyRankProvider);
          ref.invalidate(topClassmatesProvider);
          ref.invalidate(attendanceProvider);
          ref.invalidate(upcomingExamsProvider);
          ref.invalidate(contactsProvider);
        },
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
          children: [
            _Section(
              icon: Icons.school_outlined,
              title: 'Fakultet ichida o\'rningiz',
              child: const _FacultyRank(),
              theme: theme,
            ),
            _Section(
              icon: Icons.emoji_events_outlined,
              title: 'TOP klassmatlar',
              child: const _TopClassmates(),
              theme: theme,
            ),
            _Section(
              icon: Icons.event_available_outlined,
              title: 'Davomat',
              child: const _Attendance(),
              theme: theme,
            ),
            _Section(
              icon: Icons.menu_book_outlined,
              title: 'Yaqinlashayotgan imtihonlar',
              child: const _UpcomingExams(),
              theme: theme,
            ),
            _Section(
              icon: Icons.contacts_outlined,
              title: 'Aloqa',
              child: const _Contacts(),
              theme: theme,
            ),
          ],
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget child;
  final ThemeData theme;
  const _Section({
    required this.icon,
    required this.title,
    required this.child,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(icon, color: theme.colorScheme.primary, size: 22),
              const SizedBox(width: 8),
              Text(title, style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              )),
            ]),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}

// ----------- Faculty Rank -----------
class _FacultyRank extends ConsumerWidget {
  const _FacultyRank();
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(facultyRankProvider);
    final theme = Theme.of(context);
    return async.when(
      loading: () => const LinearProgressIndicator(minHeight: 2),
      error: (e, _) => Text('Xato: $e', style: TextStyle(color: theme.colorScheme.error)),
      data: (d) {
        final rank = d['rank'];
        final total = d['total'];
        final fac = d['faculty_name'] ?? '—';
        if (rank == null || total == null) {
          return Text('Reyting hisoblanmoqda.', style: theme.textTheme.bodyMedium);
        }
        final pct = ((1 - rank / total) * 100).round();
        return Row(
          children: [
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Column(
                children: [
                  Text('#$rank', style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: theme.colorScheme.onPrimaryContainer,
                  )),
                  Text('/ $total', style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.onPrimaryContainer,
                  )),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('$fac', style: theme.textTheme.titleSmall),
                  const SizedBox(height: 4),
                  Text('Yuqori ${100 - pct}% talabalar orasida',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.secondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

// ----------- Top Classmates -----------
class _TopClassmates extends ConsumerWidget {
  const _TopClassmates();
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(topClassmatesProvider);
    final theme = Theme.of(context);
    return async.when(
      loading: () => const LinearProgressIndicator(minHeight: 2),
      error: (e, _) => Text('Xato: $e', style: TextStyle(color: theme.colorScheme.error)),
      data: (items) {
        if (items.isEmpty) return Text('Ma\'lumot tayyorlanmoqda.', style: theme.textTheme.bodyMedium);
        final medals = ['🥇', '🥈', '🥉'];
        return Column(
          children: [
            for (var i = 0; i < items.length && i < 10; i++)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    SizedBox(
                      width: 32,
                      child: Text(
                        i < medals.length ? medals[i] : '${i + 1}.',
                        style: theme.textTheme.titleMedium,
                        textAlign: TextAlign.center,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        items[i]['name'] ?? '',
                        style: TextStyle(
                          fontWeight: items[i]['is_me'] == true ? FontWeight.w700 : FontWeight.normal,
                          color: items[i]['is_me'] == true ? theme.colorScheme.primary : null,
                        ),
                      ),
                    ),
                    Text(
                      (items[i]['gpa'] as num?)?.toStringAsFixed(2) ?? '—',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    if (items[i]['is_me'] == true) ...[
                      const SizedBox(width: 6),
                      const Text('⬅️ siz'),
                    ],
                  ],
                ),
              ),
          ],
        );
      },
    );
  }
}

// ----------- Attendance -----------
class _Attendance extends ConsumerWidget {
  const _Attendance();
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(attendanceProvider);
    final theme = Theme.of(context);
    Color colorFor(num v) {
      if (v >= 90) return Colors.green;
      if (v >= 75) return Colors.orange;
      return Colors.red;
    }
    return async.when(
      loading: () => const LinearProgressIndicator(minHeight: 2),
      error: (e, _) => Text('Xato: $e', style: TextStyle(color: theme.colorScheme.error)),
      data: (d) {
        final avg = (d['avg'] as num?)?.toDouble();
        final minV = (d['min'] as num?)?.toDouble();
        final subs = (d['by_subject'] as List? ?? [])
            .whereType<Map>()
            .map((m) => m.cast<String, dynamic>())
            .toList();
        if (avg == null) {
          return Text('Davomat ma\'lumoti hali shakllanmadi.', style: theme.textTheme.bodyMedium);
        }
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text('${avg.toStringAsFixed(1)}%', style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                  color: colorFor(avg),
                )),
                const SizedBox(width: 12),
                if (minV != null)
                  Chip(
                    label: Text('Min ${minV.toStringAsFixed(0)}%'),
                    backgroundColor: colorFor(minV).withValues(alpha: 0.12),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            if (subs.isNotEmpty)
              ...subs.take(6).map((s) {
                final att = (s['att'] as num).toDouble();
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 3),
                  child: Row(
                    children: [
                      Expanded(child: Text(s['subject'] ?? '')),
                      SizedBox(
                        width: 90,
                        child: LinearProgressIndicator(
                          value: att / 100,
                          color: colorFor(att),
                          backgroundColor: theme.colorScheme.surfaceContainerHighest,
                          minHeight: 6,
                        ),
                      ),
                      const SizedBox(width: 8),
                      SizedBox(
                        width: 44,
                        child: Text(
                          '${att.toStringAsFixed(0)}%',
                          textAlign: TextAlign.right,
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: colorFor(att),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }),
          ],
        );
      },
    );
  }
}

// ----------- Upcoming Exams -----------
class _UpcomingExams extends ConsumerWidget {
  const _UpcomingExams();
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(upcomingExamsProvider);
    final theme = Theme.of(context);
    return async.when(
      loading: () => const LinearProgressIndicator(minHeight: 2),
      error: (e, _) => Text('Xato: $e', style: TextStyle(color: theme.colorScheme.error)),
      data: (items) {
        // Demo fallback agar backend bo'sh bo'lsa
        final list = items.isEmpty
          ? [
              {'exam_date': DateTime.now().add(const Duration(days: 5)).toIso8601String(), 'room': 'A-201', 'exam_type': 'Yakuniy', 'subject': 'Matematik analiz'},
              {'exam_date': DateTime.now().add(const Duration(days: 8)).toIso8601String(), 'room': 'B-105', 'exam_type': 'Yakuniy', 'subject': 'Mikroiqtisodiyot'},
              {'exam_date': DateTime.now().add(const Duration(days: 14)).toIso8601String(), 'room': 'C-301', 'exam_type': 'Yakuniy', 'subject': 'Algoritmlar'},
            ]
          : items;
        return Column(
          children: [
            for (final e in list.take(5))
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.secondaryContainer,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        children: [
                          Text(
                            _fmtDay(e['exam_date']),
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: theme.colorScheme.onSecondaryContainer,
                            ),
                          ),
                          Text(
                            _fmtMonth(e['exam_date']),
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.onSecondaryContainer,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            e['subject']?.toString() ?? 'Fan #${e['subject_id'] ?? ''}',
                            style: theme.textTheme.titleSmall,
                          ),
                          Text(
                            '${e['exam_type'] ?? ''}  •  📍 ${e['room'] ?? ''}',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.secondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            if (items.isEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  'Demo ma\'lumotlar — haqiqiy jadval shakllangach yangilanadi',
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontStyle: FontStyle.italic,
                    color: theme.colorScheme.outline,
                  ),
                ),
              ),
          ],
        );
      },
    );
  }

  String _fmtDay(dynamic iso) {
    if (iso is! String) return '?';
    try { return DateFormat('d').format(DateTime.parse(iso)); } catch (_) { return '?'; }
  }
  String _fmtMonth(dynamic iso) {
    if (iso is! String) return '';
    try { return DateFormat('MMM', 'uz').format(DateTime.parse(iso)); }
    catch (_) {
      try { return DateFormat('MMM').format(DateTime.parse(iso)); } catch (_) { return ''; }
    }
  }
}

// ----------- Contacts -----------
class _Contacts extends ConsumerWidget {
  const _Contacts();
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(contactsProvider);
    return async.when(
      loading: () => const LinearProgressIndicator(minHeight: 2),
      error: (e, _) => Text('Xato: $e'),
      data: (d) {
        Widget tile(String role, Map<String, dynamic>? c) {
          if (c == null) return const SizedBox.shrink();
          return ListTile(
            contentPadding: EdgeInsets.zero,
            leading: CircleAvatar(child: Text(role[0].toUpperCase())),
            title: Text(c['fish'] ?? '—'),
            subtitle: Text('${c['phone'] ?? ''}  •  ${c['email'] ?? ''}'),
            isThreeLine: true,
            dense: true,
          );
        }
        return Column(
          children: [
            tile('Kurator', (d['kurator'] as Map?)?.cast<String, dynamic>()),
            const Divider(height: 1),
            tile('Kafedra mudiri', (d['kafedra_mudiri'] as Map?)?.cast<String, dynamic>()),
            const Divider(height: 1),
            tile('Dekan', (d['dekan'] as Map?)?.cast<String, dynamic>()),
          ],
        );
      },
    );
  }
}
