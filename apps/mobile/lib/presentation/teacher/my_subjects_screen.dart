import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/data_providers.dart';
import '../widgets/async_views.dart';

/// O'qituvchining o'z fanlari — `/my/dashboard.by_subject` dan oladi.
/// Aniqroq endpoint kerak bo'lsa keyingi iteratsiyada `/teachers/me/subjects`
/// qo'shamiz.
class MySubjectsScreen extends ConsumerWidget {
  const MySubjectsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(myDashboardProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Mening fanlarim')),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(myDashboardProvider.future),
        child: async.when(
          loading: () => const LoadingCenter(),
          error: (e, _) => ErrorRetry(
            message: '$e',
            onRetry: () => ref.invalidate(myDashboardProvider),
          ),
          data: (data) {
            final items = data.bySubject;
            if (items.isEmpty) {
              return const EmptyView(
                icon: Icons.menu_book_outlined,
                message: 'Fanlar topilmadi',
              );
            }
            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 8),
              itemBuilder: (_, i) {
                final m = items[i];
                final name = (m['subject_name'] ?? '—').toString();
                final avg = (m['avg_grade'] as num?)?.toDouble();
                final count = (m['grades_count'] as num?)?.toInt();
                final students = (m['students_count'] as num?)?.toInt();
                return Card(
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor:
                          theme.colorScheme.primaryContainer,
                      child: Icon(
                        Icons.menu_book_outlined,
                        color: theme.colorScheme.onPrimaryContainer,
                      ),
                    ),
                    title: Text(
                      name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    subtitle: Text([
                      if (count != null) '$count baho',
                      if (students != null) '$students talaba',
                    ].whereType<String>().join(' • ')),
                    trailing: avg != null
                        ? Text(
                            avg.toStringAsFixed(1),
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: theme.colorScheme.primary,
                            ),
                          )
                        : null,
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
