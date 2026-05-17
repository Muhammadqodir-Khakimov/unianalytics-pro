import type { Meta, StoryObj } from '@storybook/react';
import BellCurveD3 from './BellCurveD3';

const meta: Meta<typeof BellCurveD3> = {
  title: 'Widgets/BellCurveD3',
  component: BellCurveD3,
  tags: ['autodocs'],
};
export default meta;
type Story = StoryObj<typeof BellCurveD3>;

const normalSample = Array.from({ length: 500 }, () =>
  Math.max(0, Math.min(100, 70 + Math.random() * 30 - Math.random() * 25)),
);

export const Default: Story = {
  args: { data: normalSample, title: 'GPA distribution' },
};

export const WithHighlight: Story = {
  args: { data: normalSample, title: 'Your position', highlightValue: 82 },
};

export const Wide: Story = {
  args: { data: normalSample, width: 900, height: 400 },
};
