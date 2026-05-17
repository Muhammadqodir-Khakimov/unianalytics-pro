import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/data_providers.dart';
import '../widgets/async_views.dart';

class SubjectsScreen extends ConsumerWidget {
  const SubjectsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(subjectsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Fanlar')),
      body: RefreshIndicator(
        onRefresh: () async => ref.refresh(subjectsProvider.future),
        child: async.when(
          loading: () => const LoadingCenter(),
          error: (e, _) => ErrorRetry(
            message: '$e',
            onRetry: () => ref.invalidate(subjectsProvider),
          ),
          data: (page) {
            if (page.items.isEmpty) {
              return const EmptyView(
                icon: Icons.menu_book_outlined,
                message: 'Fanlar topilmadi',
              );
            }
            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              itemCount: page.items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 8),
              itemBuilder: (_, i) {
                final s = page.items[i];
                final theme = Theme.of(context);
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
                      s.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    subtitle: Text([
                      if (s.code.isNotEmpty) s.code,
                      if (s.creditHours != null) '${s.creditHours} kredit',
                      if (s.semesterNum != null)
                        '${s.semesterNum}-semestr',
                      if (s.subjectType != null) s.subjectType,
                    ].whereType<String>().join(' • ')),
                    trailing: s.creditHours != null
                        ? Text(
                            '${s.creditHours}',
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
