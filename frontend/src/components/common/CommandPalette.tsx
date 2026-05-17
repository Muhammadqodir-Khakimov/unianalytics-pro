import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  DashboardOutlined,
  UserOutlined,
  TeamOutlined,
  BookOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  PieChartOutlined,
  TableOutlined,
  CalendarOutlined,
  FileAddOutlined,
  DollarOutlined,
  SettingOutlined,
  AuditOutlined,
  EditOutlined,
  SearchOutlined,
  ApartmentOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';

interface Cmd {
  id: string;
  title: string;
  description?: string;
  icon: any;
  action: () => void;
  keywords?: string[];
  group: string;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(0);
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const { toggle: toggleTheme } = useThemeStore();

  // Cmd+K / Ctrl+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((o) => !o);
        setQuery('');
        setActive(0);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const allCommands: Cmd[] = useMemo(() => {
    const cmds: Cmd[] = [
      // Navigation
      { id: 'nav-dashboard', title: 'Dashboard', icon: DashboardOutlined, group: 'Navigatsiya', action: () => navigate('/dashboard') },
      { id: 'nav-cube', title: 'OLAP Cube Explorer', icon: PieChartOutlined, group: 'Navigatsiya', action: () => navigate('/olap/cube') },
      { id: 'nav-pivot', title: 'Pivot Table', icon: TableOutlined, group: 'Navigatsiya', action: () => navigate('/olap/pivot') },
      { id: 'nav-analytics', title: 'AI Analitika', icon: ExperimentOutlined, group: 'Navigatsiya', action: () => navigate('/analytics') },
      { id: 'nav-schedule', title: 'Jadval', icon: CalendarOutlined, group: 'Navigatsiya', action: () => navigate('/schedule') },
      { id: 'nav-applications', title: 'Arizalar', icon: FileAddOutlined, group: 'Navigatsiya', action: () => navigate('/applications') },
      { id: 'nav-students', title: 'Talabalar', icon: UserOutlined, group: 'Navigatsiya', action: () => navigate('/students') },
      { id: 'nav-teachers', title: "O'qituvchilar", icon: TeamOutlined, group: 'Navigatsiya', action: () => navigate('/teachers') },
      { id: 'nav-subjects', title: 'Fanlar', icon: BookOutlined, group: 'Navigatsiya', action: () => navigate('/subjects') },
      { id: 'nav-grades', title: 'Baholar', icon: FileTextOutlined, group: 'Navigatsiya', action: () => navigate('/grades') },
      { id: 'nav-faculties', title: 'Fakultetlar', icon: ApartmentOutlined, group: 'Navigatsiya', action: () => navigate('/faculties') },
      { id: 'nav-reports', title: 'Hisobotlar', icon: FileTextOutlined, group: 'Navigatsiya', action: () => navigate('/reports') },
      { id: 'nav-settings', title: 'Sozlamalar', icon: SettingOutlined, group: 'Navigatsiya', action: () => navigate('/settings') },

      // Amallar
      { id: 'act-theme', title: "Tema o'zgartirish (yorug'/tungi)", icon: SettingOutlined, group: 'Amallar', action: () => toggleTheme() },
      { id: 'act-grade-entry', title: 'Baho kiritish', icon: EditOutlined, group: 'Amallar', action: () => navigate('/grade-entry') },
      { id: 'act-logout', title: 'Chiqish', icon: SettingOutlined, group: 'Amallar', action: () => { logout(); navigate('/login'); } },

      // Tillar
      { id: 'lang-uz', title: "🇺🇿 O'zbek tili", icon: SettingOutlined, group: 'Til', action: () => { i18n.changeLanguage('uz'); localStorage.setItem('lang', 'uz'); } },
      { id: 'lang-ru', title: '🇷🇺 Русский', icon: SettingOutlined, group: 'Til', action: () => { i18n.changeLanguage('ru'); localStorage.setItem('lang', 'ru'); } },
      { id: 'lang-en', title: '🇬🇧 English', icon: SettingOutlined, group: 'Til', action: () => { i18n.changeLanguage('en'); localStorage.setItem('lang', 'en'); } },
    ];

    if (user?.role === 'admin') {
      cmds.push(
        { id: 'admin-users', title: 'Admin: Foydalanuvchilar', icon: UserOutlined, group: 'Admin', action: () => navigate('/admin/users') },
        { id: 'admin-audit', title: 'Admin: Audit log', icon: AuditOutlined, group: 'Admin', action: () => navigate('/admin/audit') },
      );
    }
    if (user?.role === 'dekan' || user?.role === 'admin') {
      cmds.push({ id: 'nav-scholarship', title: 'Stipendiya', icon: DollarOutlined, group: 'Navigatsiya', action: () => navigate('/scholarship') });
    }

    return cmds;
  }, [user, navigate, i18n, toggleTheme, logout]);

  const filtered = useMemo(() => {
    if (!query) return allCommands;
    const q = query.toLowerCase();
    return allCommands.filter(
      (c) => c.title.toLowerCase().includes(q) || c.group.toLowerCase().includes(q)
    );
  }, [query, allCommands]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((a) => Math.min(a + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((a) => Math.max(a - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const cmd = filtered[active];
      if (cmd) {
        cmd.action();
        setOpen(false);
      }
    }
  };

  if (!open) return null;

  // Group commands
  const groups: Record<string, Cmd[]> = {};
  filtered.forEach((c) => {
    if (!groups[c.group]) groups[c.group] = [];
    groups[c.group].push(c);
  });

  let globalIdx = 0;

  return (
    <div className="cmd-palette-overlay" onClick={() => setOpen(false)}>
      <div className="cmd-palette" onClick={(e) => e.stopPropagation()}>
        <div style={{ position: 'relative' }}>
          <SearchOutlined style={{ position: 'absolute', left: 20, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
          <input
            className="cmd-input"
            autoFocus
            placeholder="Buyruq, sahifa yoki amal qidiring..."
            value={query}
            onChange={(e) => { setQuery(e.target.value); setActive(0); }}
            onKeyDown={onKeyDown}
            style={{ paddingLeft: 48 }}
          />
        </div>
        <div className="cmd-list">
          {filtered.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>
              Natija topilmadi
            </div>
          ) : (
            Object.entries(groups).map(([group, cmds]) => (
              <div key={group}>
                <div style={{ padding: '8px 20px 4px', fontSize: 11, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {group}
                </div>
                {cmds.map((c) => {
                  const myIdx = globalIdx++;
                  const Icon = c.icon;
                  return (
                    <div
                      key={c.id}
                      className={`cmd-item ${myIdx === active ? 'active' : ''}`}
                      onClick={() => { c.action(); setOpen(false); }}
                      onMouseEnter={() => setActive(myIdx)}
                    >
                      <Icon style={{ color: '#667eea' }} />
                      <span className="cmd-item-title">{c.title}</span>
                      <span className="cmd-item-desc">{c.description || ''}</span>
                    </div>
                  );
                })}
              </div>
            ))
          )}
        </div>
        <div style={{ padding: '8px 20px', borderTop: '1px solid rgba(0,0,0,0.08)', fontSize: 11, color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
          <span>↑↓ tanlash · ↵ ochish · Esc yopish</span>
          <span>⌘K / Ctrl+K</span>
        </div>
      </div>
    </div>
  );
}
