/**
 * ECharts uchun zamonaviy konfiguratsiyalar:
 * - Gradient series
 * - Smooth animations
 * - Modern color palette
 * - Nice tooltips
 */

export const CHART_COLORS = {
  primary: ['#667eea', '#764ba2'],
  success: ['#10b981', '#059669'],
  warning: ['#f59e0b', '#d97706'],
  danger: ['#ef4444', '#dc2626'],
  info: ['#3b82f6', '#2563eb'],
  purple: ['#a855f7', '#7c3aed'],
  pink: ['#ec4899', '#db2777'],
  ocean: ['#06b6d4', '#3b82f6'],
};

export const CHART_PALETTE = [
  '#667eea',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#a855f7',
  '#06b6d4',
  '#ec4899',
  '#84cc16',
  '#f97316',
];

export function linearGradient(from: string, to: string) {
  return {
    type: 'linear',
    x: 0,
    y: 0,
    x2: 0,
    y2: 1,
    colorStops: [
      { offset: 0, color: from },
      { offset: 1, color: to },
    ],
  };
}

export function baseTooltip() {
  return {
    backgroundColor: 'rgba(31, 31, 37, 0.95)',
    borderColor: 'rgba(255,255,255,0.1)',
    textStyle: { color: '#fff', fontSize: 12 },
    extraCssText: 'border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); padding: 12px;',
  };
}

export function baseAxis() {
  return {
    axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)', type: 'dashed' } },
    axisLabel: { color: 'rgba(0,0,0,0.6)', fontSize: 11, fontFamily: 'Inter' },
  };
}

export function modernLineSeries(data: any[], name: string, color = CHART_COLORS.primary) {
  return {
    name,
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 8,
    lineStyle: { width: 3, color: color[0] },
    itemStyle: { color: color[0], borderColor: '#fff', borderWidth: 2 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: color[0] + '50' },
          { offset: 1, color: color[0] + '00' },
        ],
      },
    },
    data,
    animationDuration: 1500,
    animationEasing: 'cubicOut',
  };
}

export function modernBarSeries(data: any[], name: string, color = CHART_COLORS.primary) {
  return {
    name,
    type: 'bar',
    barMaxWidth: 40,
    itemStyle: {
      color: linearGradient(color[0], color[1]),
      borderRadius: [8, 8, 0, 0],
    },
    data,
    animationDuration: 1200,
    animationDelay: (idx: number) => idx * 60,
    emphasis: {
      itemStyle: { color: linearGradient(color[1], color[0]) },
    },
  };
}

export function modernPie(data: any[], name = '') {
  return {
    name,
    type: 'pie',
    radius: ['45%', '75%'],
    avoidLabelOverlap: false,
    itemStyle: {
      borderRadius: 8,
      borderColor: '#fff',
      borderWidth: 2,
    },
    label: {
      formatter: '{b}\n{d}%',
      fontSize: 11,
      fontFamily: 'Inter',
    },
    data,
    animationType: 'scale',
    animationEasing: 'elasticOut',
    color: CHART_PALETTE,
  };
}

export function smoothChart(option: any) {
  return {
    grid: { left: 50, right: 20, top: 60, bottom: 50, containLabel: true },
    tooltip: { ...baseTooltip(), trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#667eea' } } },
    textStyle: { fontFamily: 'Inter, sans-serif' },
    color: CHART_PALETTE,
    animation: true,
    animationDuration: 1200,
    ...option,
  };
}
