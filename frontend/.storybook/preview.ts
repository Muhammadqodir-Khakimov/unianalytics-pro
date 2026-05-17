import type { Preview } from '@storybook/react';
import 'antd/dist/reset.css';
import '../src/index.css';

const preview: Preview = {
  parameters: {
    controls: { matchers: { color: /(background|color)$/i, date: /Date$/i } },
    layout: 'centered',
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#141414' },
      ],
    },
  },
};
export default preview;
