import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/schedule_item.dart';
import '../../providers/data_providers.dart';
import '../widgets/async_views.dart';

const _weekdays = [
  'Dushanba',
  'Seshanba',
  'Chorshanba',
  'Payshanba',
  'Juma',
  'Shanba',
  'Yakshanba',
];

class ScheduleScreen extends ConsumerWidget {
  const ScheduleScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(myScheduleProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Dars jadvali')),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(myScheduleProvider.future),
        child: async.when(
          loading: () => const LoadingCenter(),
          error: (e, _) => ErrorRetry(
            message: '$e',
            onRetry: () => ref.invalidate(myScheduleProvider),
          ),
          data: (items) {
            if (items.isEmpty) {
              return const EmptyView(
                icon: Icons.calendar_today_outlined,
                message: 'Jadval mavjud emas',
              );
            }
            final grouped = <int, List<ScheduleItem>>{};
            for (final it in items) {
              grouped.putIfAbsent(it.weekday, () => []).add(it);
            }
            for (final list in grouped.values) {
              list.sort((a, b) => a.startTime.compareTo(b.startTime));
            }
            final days = grouped.keys.toList()..sort();
            return ListView.builder(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              itemCount: days.length,
              itemBuilder: (_, i) {
                final day = days[i];
                final list = grouped[day]!;
                return _DaySection(day: day, lessons: list);
              },
            );
          },
        ),
      ),
    );
  }
}

class _DaySection extends StatelessWidget {
  final int day;
  final List<ScheduleItem> lessons;
  const _DaySection({required this.day, required this.lessons});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final name = day >= 1 && day <= 7 ? _weekdays[day - 1] : 'Kun $day';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(4, 16, 0, 8),
          child: Text(
            name,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        ...lessons.map((l) => Card(
              child: ListTile(
                leading: SizedBox(
                  width: 56,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        l.startTime,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Text(
                        l.endTime,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                title: Text(
                  l.subjectName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: Text([
                  if (l.teacherName != null) l.teacherName,
                  if (l.room != null) 'Xona ${l.room}',
                  if (l.lessonType != null) l.lessonType,
                ].whereType<String>().join(' • ')),
              ),
            )),
      ],
    );
  }
}
