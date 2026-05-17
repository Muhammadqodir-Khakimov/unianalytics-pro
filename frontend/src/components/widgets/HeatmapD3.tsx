// @ts-nocheck — needs `npm i d3 @types/d3`
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Cell { row: string; col: string; value: number; }
interface Props { data: Cell[]; width?: number; height?: number; title?: string; }

/**
 * D3 heatmap — e.g. week × hour attendance density,
 * or subject × faculty GPA matrix.
 */
export default function HeatmapD3({ data, width = 720, height = 360, title }: Props) {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current || data.length === 0) return;
    const svg = d3.select(ref.current);
    svg.selectAll('*').remove();
    const margin = { top: 40, right: 40, bottom: 60, left: 80 };
    const w = width - margin.left - margin.right;
    const h = height - margin.top - margin.bottom;

    const rows = Array.from(new Set(data.map((d) => d.row)));
    const cols = Array.from(new Set(data.map((d) => d.col)));

    const x = d3.scaleBand().domain(cols).range([0, w]).padding(0.05);
    const y = d3.scaleBand().domain(rows).range([0, h]).padding(0.05);
    const color = d3
      .scaleSequential()
      .interpolator(d3.interpolateRdYlGn)
      .domain([d3.min(data, (d) => d.value) ?? 0, d3.max(data, (d) => d.value) ?? 100]);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x)).selectAll('text').style('text-anchor', 'end').attr('transform', 'rotate(-30)');
    g.append('g').call(d3.axisLeft(y));

    g.selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', (d) => x(d.col)!)
      .attr('y', (d) => y(d.row)!)
      .attr('width', x.bandwidth())
      .attr('height', y.bandwidth())
      .attr('fill', (d) => color(d.value) as string)
      .append('title')
      .text((d) => `${d.row} × ${d.col}: ${d.value}`);

    g.selectAll('text.cell')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'cell')
      .attr('x', (d) => x(d.col)! + x.bandwidth() / 2)
      .attr('y', (d) => y(d.row)! + y.bandwidth() / 2 + 4)
      .attr('text-anchor', 'middle')
      .attr('font-size', 10)
      .attr('fill', '#000')
      .text((d) => d.value.toFixed(0));

    if (title) {
      svg.append('text').attr('x', width / 2).attr('y', 20).attr('text-anchor', 'middle').attr('font-weight', 600).text(title);
    }
  }, [data, width, height, title]);

  return <svg ref={ref} width={width} height={height} />;
}
