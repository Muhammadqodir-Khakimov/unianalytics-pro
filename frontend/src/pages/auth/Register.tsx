import { Form, Input, Button, Card, Select, message, Typography } from 'antd';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { authService } from '@/services/authService';

export function Register() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await authService.register(values);
      message.success(t('auth.register_success'));
      navigate('/login');
    } catch {
      // interceptor
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <Card className="w-full max-w-md">
        <Typography.Title level={3} style={{ textAlign: 'center' }}>
          {t('auth.register_title')}
        </Typography.Title>

        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label={t('auth.username')} name="username" rules={[{ required: true, min: 3 }]}>
            <Input />
          </Form.Item>
          <Form.Item label={t('auth.email')} name="email" rules={[{ required: true, type: 'email' }]}>
            <Input />
          </Form.Item>
          <Form.Item label={t('auth.full_name')} name="full_name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label={t('auth.password')} name="password" rules={[{ required: true, min: 6 }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item label={t('auth.role')} name="role" initialValue="student">
            <Select
              options={[
                { value: 'student', label: t('roles.student') },
                { value: 'teacher', label: t('roles.teacher') },
              ]}
            />
          </Form.Item>

          <Button type="primary" htmlType="submit" loading={loading} block size="large">
            {t('auth.register')}
          </Button>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Link to="/login">{t('auth.login_link')}</Link>
        </div>
      </Card>
    </div>
  );
}
