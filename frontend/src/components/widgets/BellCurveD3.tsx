// @ts-nocheck — d3 v7 has strict typings that need `npm i d3 @types/d3` first
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Props {
  data: number[];
  width?: number;
  height?: number;
  title?: string;
  highlightValue?: number;
}

/**
 * D3 powered Bell Curve (normal distribution) of GPA / grades.
 * Useful for showing where a student falls relative to peers.
 */
export default function BellCurveD3({ data, width = 600, height = 320, title, highlightValue }: Props) {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current || data.length === 0) return;
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();

    const margin = { top: 30, right: 30, bottom: 40, left: 40 };
    const w = width - margin.left - margin.right;
    const h = height - margin.top - margin.bottom;

    const mean = d3.mean(data) ?? 0;
    const std = d3.deviation(data) ?? 1;
    const xMin = d3.min(data) ?? 0;
    const xMax = d3.max(data) ?? 100;

    const x = d3.scaleLinear().domain([xMin, xMax]).range([0, w]);
    const pdf = (v: number) =>
      (1 / (std * Math.sqrt(2 * Math.PI))) * Math.exp(-((v - mean) ** 2) / (2 * std * std));
    const points = d3.range(xMin, xMax, (xMax - xMin) / 100).map((v) => ({ x: v, y: pdf(v) }));
    const yMax = d3.max(points, (d) => d.y) ?? 1;
    const y = d3.scaleLinear().domain([0, yMax]).range([h, 0]);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const area = d3
      .area<{ x: number; y: number }>()
      .x((d) => x(d.x))
      .y0(h)
      .y1((d) => y(d.y))
      .curve(d3.curveBasis);

    g.append('path').datum(points).attr('fill', '#1677ff33').attr('d', area);
    g.append('path')
      .datum(points)
      .attr('fill', 'none')
      .attr('stroke', '#1677ff')
      .attr('stroke-width', 2)
      .attr(
        'd',
        d3
          .line<{ x: number; y: number }>()
          .x((d) => x(d.x))
          .y((d) => y(d.y))
          .curve(d3.curveBasis) as any,
      );

    g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x));
    g.append('g').call(d3.axisLeft(y).ticks(5));

    g.append('line')
      .attr('x1', x(mean))
      .attr('x2', x(mean))
      .attr('y1', 0)
      .attr('y2', h)
      .attr('stroke', '#52c41a')
      .attr('stroke-dasharray', '4 4');
    g.append('text').attr('x', x(mean) + 4).attr('y', 12).attr('fill', '#52c41a').text(`μ=${mean.toFixed(2)}`);

    if (highlightValue !== undefined) {
      g.append('line')
        .attr('x1', x(highlightValue))
        .attr('x2', x(highlightValue))
        .attr('y1', 0)
        .attr('y2', h)
        .attr('stroke', '#fa541c')
        .attr('stroke-width', 2);
      g.append('text')
        .attr('x', x(highlightValue) + 4)
        .attr('y', 24)
        .attr('fill', '#fa541c')
        .text(`Siz: ${highlightValue.toFixed(2)}`);
    }

    if (title) {
      svg.append('text').attr('x', width / 2).attr('y', 18).attr('text-anchor', 'middle').attr('font-weight', 600).text(title);
    }
  }, [data, width, height, title, highlightValue]);

  return <svg ref={ref} width={width} height={height} />;
}
