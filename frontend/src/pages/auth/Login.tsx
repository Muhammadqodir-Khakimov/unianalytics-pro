import { Form, Input, Button, Card, message, Typography, Divider } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/store/authStore';

export function Login() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

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

        <Form layout="vertical" onFinish={onFinish}>
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

        <Divider />
        <Typography.Paragraph style={{ textAlign: 'center', marginBottom: 0 }}>
          <Typography.Text type="secondary">Test foydalanuvchilar:</Typography.Text>
          <br />
          <Typography.Text code>admin / admin123</Typography.Text> ·{' '}
          <Typography.Text code>dekan / dekan123</Typography.Text>
          <br />
          <Typography.Text code>teacher / teacher123</Typography.Text> ·{' '}
          <Typography.Text code>student / student123</Typography.Text>
        </Typography.Paragraph>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Link to="/register">{t('auth.register_link')}</Link>
        </div>
      </Card>
    </div>
  );
}
