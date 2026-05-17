import type { Meta, StoryObj } from '@storybook/react';
import RadarChartD3 from './RadarChartD3';

const meta: Meta<typeof RadarChartD3> = {
  title: 'Widgets/RadarChartD3',
  component: RadarChartD3,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<typeof RadarChartD3>;

export const ThreeFaculties: Story = {
  args: {
    axes: ['GPA', 'Davomat', 'Faollik', 'Innovatsiya', 'Halqaro'],
    series: [
      { name: 'Iqtisodiyot', values: [4.2, 4.5, 3.8, 3.2, 2.9] },
      { name: 'Pedagogika', values: [4.0, 4.7, 4.1, 3.5, 2.5] },
      { name: 'IT', values: [4.6, 4.0, 4.4, 4.8, 3.7] },
    ],
    max: 5,
  },
};

export const SingleSeries: Story = {
  args: {
    axes: ['Bilim', 'Tushuntirish', 'Hurmat', 'Vaqtlilik', 'Foydalilik'],
    series: [{ name: 'O\'qituvchi A', values: [4.5, 4.2, 4.8, 4.1, 4.6] }],
    max: 5,
  },
};
