// @ts-nocheck — needs `npm i d3 @types/d3`
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Series { name: string; values: number[]; color?: string; }
interface Props { axes: string[]; series: Series[]; size?: number; max?: number; }

/**
 * Multi-series radar (a.k.a. spider) chart for faculty comparison
 * across N criteria. Pure D3, no chart-lib needed.
 */
export default function RadarChartD3({ axes, series, size = 400, max = 5 }: Props) {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();
    const cx = size / 2;
    const cy = size / 2;
    const radius = Math.min(cx, cy) - 40;
    const angle = (i: number) => (Math.PI * 2 * i) / axes.length - Math.PI / 2;

    const g = svg.append('g').attr('transform', `translate(${cx},${cy})`);

    [0.25, 0.5, 0.75, 1].forEach((r) => {
      g.append('circle').attr('r', radius * r).attr('fill', 'none').attr('stroke', '#e5e7eb');
    });

    axes.forEach((label, i) => {
      const x = Math.cos(angle(i)) * radius;
      const y = Math.sin(angle(i)) * radius;
      g.append('line').attr('x1', 0).attr('y1', 0).attr('x2', x).attr('y2', y).attr('stroke', '#e5e7eb');
      g.append('text')
        .attr('x', x * 1.1)
        .attr('y', y * 1.1)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', 12)
        .text(label);
    });

    const palette = ['#1677ff', '#fa541c', '#52c41a', '#722ed1', '#fa8c16'];
    series.forEach((s, idx) => {
      const color = s.color || palette[idx % palette.length];
      const pts = s.values.map((v, i) => {
        const r = (v / max) * radius;
        return [Math.cos(angle(i)) * r, Math.sin(angle(i)) * r] as [number, number];
      });
      const path = d3.line()(pts.concat([pts[0]]));
      g.append('path').attr('d', path!).attr('fill', color + '33').attr('stroke', color).attr('stroke-width', 2);
      pts.forEach(([x, y]) => g.append('circle').attr('cx', x).attr('cy', y).attr('r', 3).attr('fill', color));
    });

    const legend = svg.append('g').attr('transform', `translate(10,${size - series.length * 18 - 8})`);
    series.forEach((s, i) => {
      const color = s.color || palette[i % palette.length];
      legend.append('rect').attr('x', 0).attr('y', i * 18).attr('width', 12).attr('height', 12).attr('fill', color);
      legend.append('text').attr('x', 18).attr('y', i * 18 + 10).attr('font-size', 12).text(s.name);
    });
  }, [axes, series, size, max]);

  return <svg ref={ref} width={size} height={size} />;
}
