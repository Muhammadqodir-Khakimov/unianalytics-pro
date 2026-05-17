import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../../../theme/gradients.dart';

/// GPA dinamikasi — semestrlar bo'yicha line chart.
/// `trend` har bir element: `{academic_year, semester, gpa, ...}`.
class GpaTrendChart extends StatelessWidget {
  final List<Map<String, dynamic>> trend;

  const GpaTrendChart({super.key, required this.trend});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final points = <FlSpot>[];
    final labels = <String>[];

    for (var i = 0; i < trend.length; i++) {
      final gpa = (trend[i]['gpa'] as num?)?.toDouble();
      if (gpa == null) continue;
      points.add(FlSpot(i.toDouble(), gpa));
      final year = (trend[i]['academic_year'] ?? '').toString();
      final sem = (trend[i]['semester'] ?? '').toString();
      labels.add(_compactLabel(year, sem));
    }

    if (points.length < 2) {
      return _Empty(theme: theme, hint: 'GPA dinamikasi uchun yetarli '
          'ma‘lumot yo‘q (kamida 2 ta semestr kerak)');
    }

    final minY = (points.map((p) => p.y).reduce((a, b) => a < b ? a : b) - 0.2)
        .clamp(0.0, 4.0);
    final maxY = (points.map((p) => p.y).reduce((a, b) => a > b ? a : b) + 0.2)
        .clamp(0.0, 4.0);

    // Konstanta balandlik (220px) — keng ekranda cheksiz cho'zilmaslik
    // uchun. Avval AspectRatio 1.7 edi: tablet va landscape mobilda
    // chart balandligi 400px+ bo'lib ekranni ortiqcha egallardi.
    return SizedBox(
      height: 220,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(8, 16, 16, 8),
        child: LineChart(
          LineChartData(
            minY: minY,
            maxY: maxY,
            gridData: FlGridData(
              show: true,
              drawVerticalLine: false,
              getDrawingHorizontalLine: (_) => FlLine(
                color: theme.colorScheme.outlineVariant.withValues(alpha: 0.4),
                strokeWidth: 1,
              ),
            ),
            borderData: FlBorderData(show: false),
            titlesData: FlTitlesData(
              topTitles: const AxisTitles(
                sideTitles: SideTitles(showTitles: false),
              ),
              rightTitles: const AxisTitles(
                sideTitles: SideTitles(showTitles: false),
              ),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 32,
                  interval: 0.5,
                  getTitlesWidget: (v, _) => Text(
                    v.toStringAsFixed(1),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ),
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 28,
                  interval: 1,
                  getTitlesWidget: (v, _) {
                    final i = v.toInt();
                    if (i < 0 || i >= labels.length) {
                      return const SizedBox.shrink();
                    }
                    return Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        labels[i],
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
            lineBarsData: [
              LineChartBarData(
                spots: points,
                isCurved: true,
                curveSmoothness: 0.3,
                gradient: AppGradients.chartLine(theme.colorScheme),
                barWidth: 4,
                dotData: FlDotData(
                  show: true,
                  getDotPainter: (_, _, _, _) => FlDotCirclePainter(
                    radius: 5,
                    color: theme.colorScheme.primary,
                    strokeColor: theme.colorScheme.surface,
                    strokeWidth: 2.5,
                  ),
                ),
                belowBarData: BarAreaData(
                  show: true,
                  gradient: AppGradients.chartArea(theme.colorScheme),
                ),
              ),
            ],
            lineTouchData: LineTouchData(
              touchTooltipData: LineTouchTooltipData(
                getTooltipColor: (_) => theme.colorScheme.inverseSurface,
                getTooltipItems: (touched) => touched
                    .map((s) => LineTooltipItem(
                          'GPA ${s.y.toStringAsFixed(2)}',
                          TextStyle(
                            color: theme.colorScheme.onInverseSurface,
                            fontWeight: FontWeight.w600,
                          ),
                        ))
                    .toList(),
              ),
            ),
          ),
        ),
      ),
    );
  }

  static String _compactLabel(String year, String sem) {
    // "2024-2025" + "autumn" → "24K"
    final shortYear = year.length >= 7 ? year.substring(2, 4) : year;
    final letter = switch (sem.toLowerCase()) {
      'autumn' || 'kuzgi' || 'fall' => 'K',
      'spring' || 'bahorgi' => 'B',
      _ => sem.isNotEmpty ? sem.substring(0, 1).toUpperCase() : '',
    };
    return '$shortYear$letter';
  }
}

class _Empty extends StatelessWidget {
  final ThemeData theme;
  final String hint;
  const _Empty({required this.theme, required this.hint});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Icon(Icons.show_chart,
              size: 40, color: theme.colorScheme.outline),
          const SizedBox(height: 8),
          Text(
            hint,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
