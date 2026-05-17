import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import BellCurveD3 from '@/components/widgets/BellCurveD3';
import RadarChartD3 from '@/components/widgets/RadarChartD3';
import HeatmapD3 from '@/components/widgets/HeatmapD3';

describe('BellCurveD3', () => {
  it('renders without crashing for empty data', () => {
    const { container } = render(<BellCurveD3 data={[]} />);
    expect(container.querySelector('svg')).toBeTruthy();
  });

  it('renders with data', () => {
    const data = Array.from({ length: 100 }, () => Math.random() * 100);
    const { container } = render(<BellCurveD3 data={data} highlightValue={50} />);
    expect(container.querySelector('svg')).toBeTruthy();
  });
});

describe('RadarChartD3', () => {
  it('renders with axes and series', () => {
    const { container } = render(
      <RadarChartD3
        axes={['A', 'B', 'C']}
        series={[{ name: 'Test', values: [4, 3, 5] }]}
      />,
    );
    expect(container.querySelector('svg')).toBeTruthy();
  });
});

describe('HeatmapD3', () => {
  it('renders heatmap cells', () => {
    const data = [
      { row: 'Mon', col: '9:00', value: 50 },
      { row: 'Tue', col: '9:00', value: 80 },
    ];
    const { container } = render(<HeatmapD3 data={data} />);
    expect(container.querySelector('svg')).toBeTruthy();
  });

  it('handles empty data', () => {
    const { container } = render(<HeatmapD3 data={[]} />);
    expect(container.querySelector('svg')).toBeTruthy();
  });
});
