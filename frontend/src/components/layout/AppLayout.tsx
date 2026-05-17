import { Layout, Menu, Avatar, Dropdown, Select, Button, theme, Tooltip } from 'antd';
import {
  DashboardOutlined,
  ApartmentOutlined,
  UserOutlined,
  BookOutlined,
  TeamOutlined,
  TableOutlined,
  FileTextOutlined,
  PieChartOutlined,
  LogoutOutlined,
  GlobalOutlined,
  SettingOutlined,
  ExperimentOutlined,
  EditOutlined,
  SunOutlined,
  MoonOutlined,
  CalendarOutlined,
  FileAddOutlined,
  DollarOutlined,
  AuditOutlined,
  NotificationOutlined,
  ReadOutlined,
  MailOutlined,
  FileProtectOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import { authService } from '@/services/authService';
import { GlobalSearch } from '@/components/common/GlobalSearch';
import { NotificationsBell } from '@/components/common/NotificationsBell';

const { Header, Sider, Content } = Layout;

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const logout = useAuthStore((s) => s.logout);
  const { isDark, toggle: toggleTheme, sidebarCollapsed, setSidebarCollapsed } = useThemeStore();
  const collapsed = sidebarCollapsed;
  const setCollapsed = setSidebarCollapsed;
  const { token } = theme.useToken();

  useEffect(() => {
    if (!user) {
      authService.me().then(setUser).catch(() => logout());
    }
  }, []);

  const menuItems: any[] = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: t('menu.dashboard') },
  ];

  if (user?.role !== 'student') {
    menuItems.push({
      key: 'olap',
      icon: <ApartmentOutlined />,
      label: t('menu.olap'),
      children: [
        { key: '/olap/cube', icon: <PieChartOutlined />, label: t('menu.cube') },
        { key: '/olap/pivot', icon: <TableOutlined />, label: t('menu.pivot') },
      ],
    });
    menuItems.push({
      key: 'ai',
      icon: <ExperimentOutlined />,
      label: 'AI / ML',
      children: [
        { key: '/analytics', icon: <ExperimentOutlined />, label: 'Tahlil' },
        { key: '/ml-insights', icon: <ExperimentOutlined />, label: 'ML Insights' },
        { key: '/ai-tutor', icon: <ExperimentOutlined />, label: 'AI Tutor' },
      ],
    });
  }

  // Akademik bo'lim — hammasi uchun
  const academic: any = {
    key: 'academic',
    icon: <CalendarOutlined />,
    label: 'Akademik',
    children: [
      { key: '/schedule', icon: <CalendarOutlined />, label: 'Jadval' },
      { key: '/applications', icon: <FileAddOutlined />, label: 'Arizalar' },
    ],
  };
  if (user?.role === 'dekan' || user?.role === 'admin') {
    academic.children.push({ key: '/scholarship', icon: <DollarOutlined />, label: 'Stipendiya' });
  }
  menuItems.push(academic);

  // HEMIS bo'limi (e'lonlar, kalendar, kitobxona, xabarlar, hujjatlar, to'lovlar, yotoqxona)
  menuItems.push({
    key: 'hemis',
    icon: <NotificationOutlined />,
    label: 'HEMIS',
    children: [
      { key: '/announcements', icon: <NotificationOutlined />, label: "E'lonlar" },
      { key: '/calendar', icon: <CalendarOutlined />, label: 'Kalendar' },
      { key: '/library', icon: <ReadOutlined />, label: 'Kutubxona' },
      { key: '/messages', icon: <MailOutlined />, label: 'Xabarlar' },
      { key: '/documents', icon: <FileProtectOutlined />, label: 'Hujjatlar' },
      { key: '/payments', icon: <DollarOutlined />, label: "To'lovlar" },
      { key: '/dormitory', icon: <HomeOutlined />, label: 'Yotoqxona' },
      ...(user?.role !== 'student'
        ? [{ key: '/thesis', icon: <ExperimentOutlined />, label: 'Bitiruv ishlari' }]
        : []),
    ],
  });

  if (user?.role === 'teacher' || user?.role === 'dekan' || user?.role === 'admin') {
    menuItems.push({ key: '/grade-entry', icon: <EditOutlined />, label: 'Baho kiritish' });
  }

  if (user?.role === 'admin' || user?.role === 'dekan') {
    menuItems.push(
      { key: '/students', icon: <UserOutlined />, label: t('menu.students') },
      { key: '/teachers', icon: <TeamOutlined />, label: t('menu.teachers') },
      { key: '/subjects', icon: <BookOutlined />, label: t('menu.subjects') },
      { key: '/grades', icon: <FileTextOutlined />, label: t('menu.grades') },
      { key: '/faculties', icon: <ApartmentOutlined />, label: t('menu.faculties') },
    );
  } else if (user?.role === 'teacher') {
    menuItems.push(
      { key: '/students', icon: <UserOutlined />, label: t('menu.students') },
      { key: '/subjects', icon: <BookOutlined />, label: t('menu.subjects') },
    );
  }

  menuItems.push({ key: '/reports', icon: <FileTextOutlined />, label: t('menu.reports') });

  if (user?.role === 'admin') {
    menuItems.push({
      key: 'admin',
      icon: <SettingOutlined />,
      label: 'Admin',
      children: [
        { key: '/admin/users', icon: <UserOutlined />, label: "Foydalanuvchilar" },
        { key: '/admin/audit', icon: <AuditOutlined />, label: 'Audit log' },
      ],
    });
  }

  menuItems.push({ key: '/settings', icon: <SettingOutlined />, label: t('menu.settings') });

  const userMenu = {
    items: [
      { key: 'settings', icon: <SettingOutlined />, label: t('menu.settings'), onClick: () => navigate('/settings') },
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: t('menu.logout'),
        onClick: () => { logout(); navigate('/login'); },
      },
    ],
  };

  const changeLang = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('lang', lng);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="dark" width={240}>
        <div
          style={{
            color: 'white',
            textAlign: 'center',
            padding: 16,
            fontWeight: 'bold',
            fontSize: collapsed ? 14 : 18,
            background: 'rgba(0,0,0,0.2)',
          }}
        >
          {collapsed ? 'SR' : '📊 Student OLAP'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['olap', 'academic']}
          items={menuItems}
          onClick={({ key }) => { if (key.startsWith('/')) navigate(key); }}
        />
      </Sider>

      <Layout>
        <Header
          style={{
            background: token.colorBgContainer,
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: `1px solid ${token.colorBorderSecondary}`,
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <h2 style={{ margin: 0, color: token.colorText }}>{t('app_name')}</h2>
            <GlobalSearch />
          </div>

          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <NotificationsBell />

            <Tooltip title={isDark ? "Yorug' rejim" : 'Tungi rejim'}>
              <Button shape="circle" icon={isDark ? <SunOutlined /> : <MoonOutlined />} onClick={toggleTheme} />
            </Tooltip>

            <Select
              value={i18n.language}
              onChange={changeLang}
              size="small"
              style={{ width: 90 }}
              suffixIcon={<GlobalOutlined />}
              options={[
                { value: 'uz', label: '🇺🇿 UZ' },
                { value: 'ru', label: '🇷🇺 RU' },
                { value: 'en', label: '🇬🇧 EN' },
              ]}
            />

            <Dropdown menu={userMenu} placement="bottomRight">
              <Button type="text" style={{ display: 'flex', alignItems: 'center', gap: 8, height: 40 }}>
                <Avatar icon={<UserOutlined />} style={{ background: '#1677ff' }} />
                <div style={{ textAlign: 'left', lineHeight: 1.2 }}>
                  <div>{user?.full_name || user?.username}</div>
                  <div style={{ color: token.colorTextSecondary, fontSize: 11 }}>{user?.role}</div>
                </div>
              </Button>
            </Dropdown>
          </div>
        </Header>

        <Content style={{ margin: 0, background: isDark ? '#141414' : '#f5f7fa', minHeight: 'calc(100vh - 64px)' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
