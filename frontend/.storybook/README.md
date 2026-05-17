# Storybook

Komponent kutubxonasi va dizayn tizimi (design system).

## Install (bir martalik)

```bash
npm i -D @storybook/react-vite @storybook/addon-essentials @storybook/addon-interactions @storybook/addon-a11y storybook
```

## Ishga tushirish

```bash
npm run storybook       # http://localhost:6006
npm run build-storybook # static build → storybook-static/
```

## Mavjud stories

- `Widgets/BellCurveD3` — 3 variant (default, highlight, wide)
- `Widgets/RadarChartD3` — multi-series, single-series

## Yangi story qo'shish

`src/components/SomeComponent.stories.tsx`:

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { SomeComponent } from './SomeComponent';

const meta: Meta<typeof SomeComponent> = { title: 'UI/SomeComponent', component: SomeComponent };
export default meta;
export const Default: StoryObj<typeof SomeComponent> = { args: { /* ... */ } };
```

## Deploy

GitHub Pages:
```bash
npm run build-storybook
npx gh-pages -d storybook-static
```
