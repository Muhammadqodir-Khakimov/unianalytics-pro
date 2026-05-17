import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ColorTheme = 'blue' | 'purple' | 'green' | 'orange' | 'pink';

interface ThemeState {
  isDark: boolean;
  color: ColorTheme;
  sidebarCollapsed: boolean;
  toggle: () => void;
  setDark: (v: boolean) => void;
  setColor: (c: ColorTheme) => void;
  setSidebarCollapsed: (v: boolean) => void;
}

export const THEME_COLORS: Record<ColorTheme, { primary: string; gradient: string; label: string; emoji: string }> = {
  blue: { primary: '#1677ff', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', label: 'Klassik ko\'k', emoji: '💙' },
  purple: { primary: '#722ed1', gradient: 'linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)', label: 'Mukammal binafsha', emoji: '💜' },
  green: { primary: '#10b981', gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', label: 'Tabiiy yashil', emoji: '💚' },
  orange: { primary: '#f97316', gradient: 'linear-gradient(135deg, #f97316 0%, #ec4899 100%)', label: "Quyosh nuri", emoji: '🧡' },
  pink: { primary: '#ec4899', gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)', label: 'Yumshoq pushti', emoji: '💗' },
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: false,
      color: 'blue',
      sidebarCollapsed: false,
      toggle: () => set((s) => ({ isDark: !s.isDark })),
      setDark: (v) => set({ isDark: v }),
      setColor: (c) => set({ color: c }),
      setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
    }),
    { name: 'theme-storage' }
  )
);
