import { Form, Input, Button, Card, message, Typography, Divider, Space, Tag } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/authStore';

// Demo akkauntlar — backend seed_data bilan mos
const DEMO_ACCOUNTS = [
  { role: 'admin',   user: 'admin',   pass: 'admin123',   color: 'magenta', label: 'Admin'    },
  { role: 'dean',    user: 'dekan',   pass: 'dekan123',   color: 'purple',  label: 'Dekan'    },
  { role: 'teacher', user: 'teacher', pass: 'teacher123', color: 'geekblue', label: 'O\'qituvchi' },
  { role: 'student', user: 'student', pass: 'student123', color: 'green',   label: 'Talaba'   },
];

export function Login() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm<{ username: string; password: string }>();
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  const fillDemo = (user: string, pass: string) => {
    form.setFieldsValue({ username: user, password: pass });
  };

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const tokens = await authService.login(values.username, values.password);
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await authService.me();
      setUser(user);
      message.success(t('auth.login_success'));
      navigate('/dashboard');
    } catch {
      // interceptor xabarini ko'rsatadi
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <Card className="w-full max-w-md" style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Typography.Title level={3} style={{ margin: 0 }}>
            {t('auth.login_title')}
          </Typography.Title>
          <Typography.Text type="secondary">Student Rating OLAP</Typography.Text>
        </div>

        <Form layout="vertical" onFinish={onFinish} form={form}>
          <Form.Item
            label={t('auth.username')}
            name="username"
            rules={[{ required: true, message: t('auth.username_required') }]}
          >
            <Input prefix={<UserOutlined />} placeholder="admin" size="large" />
          </Form.Item>

          <Form.Item
            label={t('auth.password')}
            name="password"
            rules={[{ required: true, message: t('auth.password_required') }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="••••••" size="large" />
          </Form.Item>

          <Button type="primary" htmlType="submit" loading={loading} block size="large">
            {t('auth.login')}
          </Button>
        </Form>

        <Divider>Demo akkauntlar</Divider>
        <div style={{ textAlign: 'center' }}>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            Bosing — avtomatik to'ldiradi
          </Typography.Text>
          <Space wrap style={{ marginTop: 8, justifyContent: 'center', width: '100%' }}>
            {DEMO_ACCOUNTS.map((a) => (
              <Tag
                key={a.user}
                color={a.color}
                style={{ cursor: 'pointer', padding: '4px 10px', fontSize: 12 }}
                onClick={() => fillDemo(a.user, a.pass)}
              >
                {a.label}
              </Tag>
            ))}
          </Space>
        </div>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Link to="/register">{t('auth.register_link')}</Link>
        </div>
      </Card>
    </div>
  );
}
