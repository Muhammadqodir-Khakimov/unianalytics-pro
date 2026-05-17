import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/entities/grade.dart';
import '../../providers/data_providers.dart';
import '../widgets/async_views.dart';
import '../widgets/skeletons.dart';

class GradesScreen extends ConsumerStatefulWidget {
  const GradesScreen({super.key});

  @override
  ConsumerState<GradesScreen> createState() => _GradesScreenState();
}

class _GradesScreenState extends ConsumerState<GradesScreen> {
  String _filter = 'all'; // all / passed / failed
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(myGradesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Baholar'),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Fan nomi bo‘yicha qidirish…',
                prefixIcon: Icon(Icons.search),
              ),
              onChanged: (v) => setState(() => _query = v.trim().toLowerCase()),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'all', label: Text('Hammasi')),
                ButtonSegment(value: 'passed', label: Text('O‘tgan')),
                ButtonSegment(value: 'failed', label: Text('O‘tmagan')),
              ],
              selected: {_filter},
              onSelectionChanged: (s) => setState(() => _filter = s.first),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () async => ref.refresh(myGradesProvider.future),
              child: async.when(
                loading: () => const ListSkeleton(),
                error: (e, _) => ErrorRetry(
                  message: '$e',
                  onRetry: () => ref.invalidate(myGradesProvider),
                ),
                data: (page) {
                  final items = _apply(page.items);
                  if (items.isEmpty) {
                    return const EmptyView(
                      icon: Icons.assessment_outlined,
                      message: 'Baholar topilmadi',
                    );
                  }
                  return ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
                    itemCount: items.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 8),
                    itemBuilder: (_, i) => _GradeTile(grade: items[i]),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  List<Grade> _apply(List<Grade> all) {
    return all.where((g) {
      if (_filter == 'passed' && !g.isPassed) return false;
      if (_filter == 'failed' && g.isPassed) return false;
      if (_query.isNotEmpty) {
        final name = (g.subjectName ?? '').toLowerCase();
        if (!name.contains(_query)) return false;
      }
      return true;
    }).toList(growable: false);
  }
}

class _GradeTile extends StatelessWidget {
  final Grade grade;
  const _GradeTile({required this.grade});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = grade.isPassed
        ? Colors.green.shade600
        : theme.colorScheme.error;
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withValues(alpha: 0.12),
          child: Text(
            grade.gradeValue.toStringAsFixed(0),
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
        ),
        title: Text(
          grade.subjectName ?? 'Fan #${grade.subjectId}',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text([
          if (grade.assessmentType != null) grade.assessmentType,
          if (grade.semester != null) grade.semester,
          if (grade.academicYear != null) grade.academicYear,
          if (grade.gradeDate != null)
            DateFormat('yyyy-MM-dd').format(grade.gradeDate!),
        ].whereType<String>().join(' • ')),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            grade.isPassed ? 'O‘TDI' : 'O‘TMADI',
            style: theme.textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }
}
