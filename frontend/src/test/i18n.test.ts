import { describe, it, expect } from 'vitest';
import uz from '@/locales/uz.json';
import ru from '@/locales/ru.json';
import en from '@/locales/en.json';
import qq from '@/locales/qq.json';

const langs = { uz, ru, en, qq };

describe('i18n locale files', () => {
  it('all locales have the same top-level keys', () => {
    const uzKeys = Object.keys(uz).sort();
    for (const [name, dict] of Object.entries(langs)) {
      expect(Object.keys(dict).sort(), `${name} mismatch`).toEqual(uzKeys);
    }
  });

  it('menu section has all required entries', () => {
    const required = ['dashboard', 'students', 'teachers', 'subjects', 'grades', 'logout'];
    for (const [name, dict] of Object.entries(langs)) {
      const menu = (dict as any).menu;
      for (const k of required) {
        expect(menu[k], `${name}.menu.${k} missing`).toBeTruthy();
      }
    }
  });

  it('auth keys present in all', () => {
    for (const [name, dict] of Object.entries(langs)) {
      expect((dict as any).auth.login, `${name}.auth.login missing`).toBeTruthy();
      expect((dict as any).auth.password, `${name}.auth.password missing`).toBeTruthy();
    }
  });

  it('qq is not just a copy of uz', () => {
    expect(qq.menu.dashboard).not.toBe(uz.menu.dashboard);
  });
});
