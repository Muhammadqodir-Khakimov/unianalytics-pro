import { Card, Form, Input, Button, message, Switch, Select, Tabs, Avatar, Space, Tag } from 'antd';
import {
  UserOutlined,
  LockOutlined,
  BgColorsOutlined,
  GlobalOutlined,
  SaveOutlined,
  CheckCircleFilled,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore, THEME_COLORS, ColorTheme } from '@/store/themeStore';
import { userService } from '@/services/userService';
import { PageHeader } from '@/components/common/PageHeader';

export function SettingsPage() {
  const { t, i18n } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const { isDark, toggle, color, setColor } = useThemeStore();
  const qc = useQueryClient();

  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const updateProfileM = useMutation({
    mutationFn: userService.updateProfile,
    onSuccess: (data) => {
      setUser(data);
      message.success('Profil yangilandi');
      qc.invalidateQueries({ queryKey: ['auth'] });
    },
  });

  const changePasswordM = useMutation({
    mutationFn: ({ old_password, new_password }: any) =>
      userService.changePassword(old_password, new_password),
    onSuccess: () => {
      message.success("Parol o'zgartirildi");
      passwordForm.resetFields();
    },
  });

  if (!user) return null;

  return (
    <div className="olap-page">
      <PageHeader
        title="Sozlamalar"
        subtitle="Profil, parol, ko'rinish va til sozlamalari"
        icon={<BgColorsOutlined />}
      />

      <Card style={{ marginBottom: 16 }}>
        <Space size={16} align="center">
          <Avatar size={64} icon={<UserOutlined />} style={{ background: THEME_COLORS[color].gradient }} />
          <div>
            <h2 style={{ margin: 0 }}>{user.full_name}</h2>
            <p style={{ color: '#666', margin: 0 }}>{user.email}</p>
            <Tag color="blue">{user.role}</Tag>
          </div>
        </Space>
      </Card>

      <Tabs
        defaultActiveKey="theme"
        items={[
          {
            key: 'theme',
            label: <><BgColorsOutlined /> Ko'rinish</>,
            children: (
              <Card>
                <Form layout="vertical" style={{ maxWidth: 700 }}>
                  <Form.Item label={<strong>Tungi rejim (dark mode)</strong>}>
                    <Switch
                      checked={isDark}
                      onChange={toggle}
                      checkedChildren="Yoqilgan"
                      unCheckedChildren="O'chirilgan"
                    />
                    <p style={{ color: '#666', marginTop: 8, fontSize: 13 }}>
                      Tungi rejim ko'zga yumshoq, kechqurun foydalanish uchun qulay.
                    </p>
                  </Form.Item>

                  <Form.Item label={<strong>Asosiy rang sxemasi</strong>}>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                      {Object.entries(THEME_COLORS).map(([key, t]) => (
                        <div
                          key={key}
                          onClick={() => { setColor(key as ColorTheme); message.success(`Tema: ${t.label}`); }}
                          style={{
                            cursor: 'pointer',
                            width: 100,
                            height: 90,
                            borderRadius: 12,
                            background: t.gradient,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: 600,
                            fontSize: 12,
                            boxShadow: color === key ? `0 0 0 3px ${t.primary}` : 'none',
                            transition: 'all 0.2s',
                            position: 'relative',
                          }}
                        >
                          <div style={{ fontSize: 32 }}>{t.emoji}</div>
                          <div>{t.label}</div>
                          {color === key && (
                            <CheckCircleFilled style={{ position: 'absolute', top: 8, right: 8, fontSize: 18 }} />
                          )}
                        </div>
                      ))}
                    </div>
                  </Form.Item>

                  <Form.Item label={<><GlobalOutlined /> <strong>Til</strong></>}>
                    <Select
                      value={i18n.language}
                      onChange={(lng) => {
                        i18n.changeLanguage(lng);
                        localStorage.setItem('lang', lng);
                        message.success("Til o'zgartirildi");
                      }}
                      style={{ width: 200 }}
                      options={[
                        { value: 'uz', label: "🇺🇿 O'zbek" },
                        { value: 'ru', label: '🇷🇺 Русский' },
                        { value: 'en', label: '🇬🇧 English' },
                      ]}
                    />
                  </Form.Item>

                  <Form.Item label={<strong>Onboarding tur</strong>}>
                    <Button onClick={() => { localStorage.removeItem('onboarding-completed'); window.location.reload(); }}>
                      Birinchi sayohatni qayta ko'rsatish
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            ),
          },
          {
            key: 'profile',
            label: <><UserOutlined /> Profil</>,
            children: (
              <Card>
                <Form
                  form={profileForm}
                  layout="vertical"
                  initialValues={{ full_name: user.full_name, email: user.email }}
                  onFinish={(values) => updateProfileM.mutate(values)}
                  style={{ maxWidth: 500 }}
                >
                  <Form.Item label="Username (o'zgartirib bo'lmaydi)">
                    <Input value={user.username} disabled />
                  </Form.Item>
                  <Form.Item label="F.I.Sh." name="full_name" rules={[{ required: true, min: 2 }]}>
                    <Input />
                  </Form.Item>
                  <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
                    <Input />
                  </Form.Item>
                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<SaveOutlined />}
                      loading={updateProfileM.isPending}
                    >
                      Saqlash
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            ),
          },
          {
            key: 'password',
            label: <><LockOutlined /> Parol</>,
            children: (
              <Card>
                <Form
                  form={passwordForm}
                  layout="vertical"
                  onFinish={(values) => changePasswordM.mutate(values)}
                  style={{ maxWidth: 500 }}
                >
                  <Form.Item label="Eski parol" name="old_password" rules={[{ required: true }]}>
                    <Input.Password />
                  </Form.Item>
                  <Form.Item
                    label="Yangi parol"
                    name="new_password"
                    rules={[{ required: true, min: 6, message: 'Kamida 6 belgi' }]}
                  >
                    <Input.Password />
                  </Form.Item>
                  <Form.Item
                    label="Yangi parolni takrorlang"
                    name="confirm_password"
                    dependencies={['new_password']}
                    rules={[
                      { required: true },
                      ({ getFieldValue }) => ({
                        validator(_, value) {
                          if (!value || getFieldValue('new_password') === value) {
                            return Promise.resolve();
                          }
                          return Promise.reject(new Error('Parollar mos kelmadi'));
                        },
                      }),
                    ]}
                  >
                    <Input.Password />
                  </Form.Item>
                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<LockOutlined />}
                      loading={changePasswordM.isPending}
                    >
                      Parolni o'zgartirish
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
}
