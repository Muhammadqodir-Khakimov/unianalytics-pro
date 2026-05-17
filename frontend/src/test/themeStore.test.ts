import { describe, it, expect, beforeEach } from 'vitest';
import { useThemeStore, THEME_COLORS } from '@/store/themeStore';

describe('themeStore', () => {
  beforeEach(() => {
    useThemeStore.setState({ isDark: false, color: 'blue' });
  });

  it('starts in light mode with blue', () => {
    const s = useThemeStore.getState();
    expect(s.isDark).toBe(false);
    expect(s.color).toBe('blue');
  });

  it('toggles to dark', () => {
    useThemeStore.getState().toggle();
    expect(useThemeStore.getState().isDark).toBe(true);
  });

  it('sets color', () => {
    useThemeStore.getState().setColor('purple');
    expect(useThemeStore.getState().color).toBe('purple');
  });

  it('THEME_COLORS includes blue and purple', () => {
    expect(THEME_COLORS).toHaveProperty('blue');
    expect(THEME_COLORS).toHaveProperty('purple');
    expect(THEME_COLORS.blue.primary).toMatch(/^#/);
  });
});
