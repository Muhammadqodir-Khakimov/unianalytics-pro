import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

/// Fanlar bo'yicha o'rtacha ball — gorizontal-shimoliy bar chart (top-N).
class SubjectsBarChart extends StatelessWidget {
  final List<Map<String, dynamic>> bySubject;
  final int topN;

  const SubjectsBarChart({super.key, required this.bySubject, this.topN = 5});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    final items = bySubject
        .map((m) => (
              name: (m['subject_name'] ?? '—').toString(),
              avg: (m['avg_grade'] as num?)?.toDouble() ?? 0.0,
            ))
        .where((it) => it.avg > 0)
        .toList()
      ..sort((a, b) => b.avg.compareTo(a.avg));
    final top = items.take(topN).toList();

    if (top.isEmpty) {
      return const SizedBox.shrink();
    }

    final maxValue = top.first.avg.clamp(60.0, 100.0);

    return Padding(
      padding: const EdgeInsets.fromLTRB(0, 12, 0, 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final it in top)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Row(
                children: [
                  SizedBox(
                    width: 110,
                    child: Text(
                      it.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: AspectRatio(
                      aspectRatio: 24,
                      child: BarChart(BarChartData(
                        alignment: BarChartAlignment.spaceBetween,
                        maxY: maxValue,
                        minY: 0,
                        gridData: const FlGridData(show: false),
                        titlesData: const FlTitlesData(show: false),
                        borderData: FlBorderData(show: false),
                        barGroups: [
                          BarChartGroupData(x: 0, barRods: [
                            BarChartRodData(
                              toY: it.avg,
                              width: 14,
                              color: theme.colorScheme.primary,
                              borderRadius:
                                  BorderRadius.circular(6),
                              backDrawRodData: BackgroundBarChartRodData(
                                show: true,
                                toY: maxValue,
                                color: theme.colorScheme
                                    .surfaceContainerHighest,
                              ),
                            ),
                          ]),
                        ],
                      )),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 36,
                    child: Text(
                      it.avg.toStringAsFixed(1),
                      textAlign: TextAlign.right,
                      style: theme.textTheme.labelMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
