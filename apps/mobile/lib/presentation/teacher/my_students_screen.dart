import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/data_providers.dart';

/// O'qituvchi/dekan/admin uchun: talabalar ro'yxati GPA/davomat/baholar
/// soni bilan, sortlash va risk talabalarni belgilash.
class MyStudentsScreen extends ConsumerStatefulWidget {
  const MyStudentsScreen({super.key});

  @override
  ConsumerState<MyStudentsScreen> createState() => _MyStudentsScreenState();
}

class _MyStudentsScreenState extends ConsumerState<MyStudentsScreen> {
  String _sortBy = 'gpa'; // gpa | name | attendance
  bool _onlyRisk = false;
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(myStudentsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mening talabalarim'),
        actions: [
          IconButton(
            icon: Icon(_onlyRisk ? Icons.warning : Icons.warning_amber_outlined),
            tooltip: _onlyRisk ? 'Barchasini ko‘rsatish' : 'Faqat risk',
            onPressed: () => setState(() => _onlyRisk = !_onlyRisk),
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            tooltip: 'Saralash',
            onSelected: (v) => setState(() => _sortBy = v),
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'gpa', child: Text('GPA bo‘yicha')),
              PopupMenuItem(value: 'name', child: Text('Ism bo‘yicha')),
              PopupMenuItem(value: 'attendance', child: Text('Davomat bo‘yicha')),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
            child: TextField(
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.search),
                hintText: 'Ism yoki guruh bo‘yicha izlash',
                isDense: true,
                border: OutlineInputBorder(),
              ),
              onChanged: (v) => setState(() => _query = v.toLowerCase()),
            ),
          ),
          Expanded(
            child: async.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    const Icon(Icons.error_outline, size: 48),
                    const SizedBox(height: 12),
                    Text('$e', textAlign: TextAlign.center),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      onPressed: () => ref.invalidate(myStudentsProvider),
                      icon: const Icon(Icons.refresh),
                      label: const Text('Qayta urinish'),
                    ),
                  ]),
                ),
              ),
              data: (all) {
                var items = List<Map<String, dynamic>>.from(all);
                if (_onlyRisk) {
                  items = items.where((s) => s['is_risk'] == true).toList();
                }
                if (_query.isNotEmpty) {
                  items = items.where((s) =>
                    (s['full_name'] ?? '').toString().toLowerCase().contains(_query) ||
                    (s['group_name'] ?? '').toString().toLowerCase().contains(_query)
                  ).toList();
                }
                if (_sortBy == 'name') {
                  items.sort((a, b) => (a['full_name'] ?? '').toString().compareTo((b['full_name'] ?? '').toString()));
                } else if (_sortBy == 'attendance') {
                  items.sort((a, b) => ((b['attendance'] ?? 0) as num).compareTo((a['attendance'] ?? 0) as num));
                } else {
                  items.sort((a, b) => ((b['avg_gpa'] ?? 0) as num).compareTo((a['avg_gpa'] ?? 0) as num));
                }

                if (items.isEmpty) {
                  return Center(
                    child: Column(mainAxisSize: MainAxisSize.min, children: [
                      Icon(Icons.people_outline, size: 64, color: theme.colorScheme.outline),
                      const SizedBox(height: 12),
                      const Text('Talabalar topilmadi'),
                    ]),
                  );
                }

                return RefreshIndicator(
                  onRefresh: () async => ref.refresh(myStudentsProvider.future),
                  child: ListView.separated(
                    itemCount: items.length,
                    padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
                    separatorBuilder: (_, _) => const Divider(height: 1),
                    itemBuilder: (_, i) {
                      final s = items[i];
                      final gpa = (s['avg_gpa'] as num?)?.toDouble();
                      final att = (s['attendance'] as num?)?.toDouble();
                      final isRisk = s['is_risk'] == true;
                      return ListTile(
                        contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                        leading: CircleAvatar(
                          backgroundColor: isRisk
                              ? theme.colorScheme.errorContainer
                              : theme.colorScheme.primaryContainer,
                          child: Text(
                            (s['full_name'] ?? '?').toString().substring(0, 1).toUpperCase(),
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: isRisk
                                  ? theme.colorScheme.onErrorContainer
                                  : theme.colorScheme.onPrimaryContainer,
                            ),
                          ),
                        ),
                        title: Row(
                          children: [
                            Expanded(child: Text(s['full_name'] ?? '—',
                              maxLines: 1, overflow: TextOverflow.ellipsis)),
                            if (isRisk) ...[
                              const SizedBox(width: 4),
                              const Text('⚠️', style: TextStyle(fontSize: 14)),
                            ],
                          ],
                        ),
                        subtitle: Text(
                          '${s['group_name'] ?? ''}  •  ${s['grades_count']} baho'
                          '${att != null ? '  •  ${att.toStringAsFixed(0)}% davomat' : ''}',
                          style: theme.textTheme.bodySmall,
                        ),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              gpa != null ? gpa.toStringAsFixed(2) : '—',
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: isRisk
                                    ? theme.colorScheme.error
                                    : theme.colorScheme.primary,
                              ),
                            ),
                            Text('GPA', style: theme.textTheme.labelSmall),
                          ],
                        ),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
