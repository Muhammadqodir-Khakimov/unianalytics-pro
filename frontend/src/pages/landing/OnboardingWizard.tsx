import { Card, Steps, Form, Input, Button, Select, Space, message, Result, Tag, ColorPicker } from 'antd';
import { CheckCircleFilled, ArrowRightOutlined, RocketOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function OnboardingWizard() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [tenantId, setTenantId] = useState<number | null>(null);
  const [form1] = Form.useForm();
  const [form2] = Form.useForm();
  const [form3] = Form.useForm();

  const plansQ = useQuery({ queryKey: ['plans'], queryFn: () => api.get('/billing/plans').then((r) => r.data) });

  const step1M = useMutation({
    mutationFn: (data: any) => api.post('/onboarding/start', data).then((r) => r.data),
    onSuccess: (data) => {
      setTenantId(data.tenant_id);
      message.success(data.message);
      setStep(1);
    },
  });

  const step2M = useMutation({
    mutationFn: (data: any) => api.post('/onboarding/branding', data).then((r) => r.data),
    onSuccess: () => setStep(2),
  });

  const step3M = useMutation({
    mutationFn: (data: any) => api.post('/onboarding/choose-plan', data).then((r) => r.data),
    onSuccess: () => setStep(3),
  });

  return (
    <div style={{ background: '#f5f7fa', minHeight: '100vh', padding: '40px 16px' }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h1 style={{ fontSize: 32, fontWeight: 700 }}>Universitetingizni qo'shing 🎓</h1>
          <p style={{ color: '#666' }}>4 ta oddiy qadamda boshlang</p>
        </div>

        <Card>
          <Steps current={step} items={[
            { title: 'Asosiy ma\'lumot' },
            { title: 'Brand' },
            { title: 'Plan' },
            { title: 'Tugadi' },
          ]} style={{ marginBottom: 32 }} />

          {step === 0 && (
            <Form
              form={form1}
              layout="vertical"
              onFinish={(v) => step1M.mutate(v)}
            >
              <Form.Item label="Universitet nomi" name="university_name" rules={[{ required: true }]}>
                <Input placeholder="Toshkent Davlat Universiteti" />
              </Form.Item>
              <Form.Item label="Qisqartma kod" name="university_code" rules={[{ required: true }]} extra="Subdomen: tdu.unianalytics.uz">
                <Input placeholder="tdu" />
              </Form.Item>
              <Form.Item label="Qisqa nom" name="short_name" rules={[{ required: true }]}>
                <Input placeholder="TDU" />
              </Form.Item>
              <Form.Item label="Admin F.I.Sh." name="admin_name" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item label="Admin email" name="admin_email" rules={[{ required: true, type: 'email' }]}>
                <Input type="email" />
              </Form.Item>
              <Form.Item label="Admin parol" name="admin_password" rules={[{ required: true, min: 6 }]}>
                <Input.Password />
              </Form.Item>
              <Form.Item label="Talabalar soni (taxminiy)" name="estimated_students" initialValue={1000}>
                <Input type="number" />
              </Form.Item>
              <Form.Item label="Telefon" name="phone">
                <Input />
              </Form.Item>
              <Form.Item label="Manzil" name="address">
                <Input />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={step1M.isPending} size="large" block icon={<ArrowRightOutlined />}>
                Keyingi
              </Button>
            </Form>
          )}

          {step === 1 && tenantId && (
            <Form
              form={form2}
              layout="vertical"
              initialValues={{ primary_color: '#1677ff', secondary_color: '#722ed1' }}
              onFinish={(v) => step2M.mutate({ ...v, tenant_id: tenantId, primary_color: typeof v.primary_color === 'string' ? v.primary_color : v.primary_color?.toHexString() })}
            >
              <Form.Item label="Asosiy rang" name="primary_color">
                <ColorPicker showText format="hex" />
              </Form.Item>
              <Form.Item label="Logo URL (ixtiyoriy)" name="logo_url">
                <Input placeholder="https://your-site.uz/logo.png" />
              </Form.Item>
              <Space>
                <Button onClick={() => setStep(0)}>Orqaga</Button>
                <Button type="primary" htmlType="submit" loading={step2M.isPending}>
                  Keyingi
                </Button>
              </Space>
            </Form>
          )}

          {step === 2 && tenantId && (
            <Form
              form={form3}
              layout="vertical"
              initialValues={{ plan: 'free' }}
              onFinish={(v) => step3M.mutate({ ...v, tenant_id: tenantId })}
            >
              <Form.Item label="Plan tanlang" name="plan">
                <Select size="large" options={(plansQ.data || []).map((p: any) => ({
                  value: p.code,
                  label: `${p.name} — ${p.price === 0 ? 'Bepul' : p.price ? `${(p.price / 1000000).toFixed(1)}M so'm/oy` : 'Custom'}`,
                }))} />
              </Form.Item>
              <p style={{ color: '#666' }}>
                ℹ️ Barcha rejalar 30 kun bepul sinov bilan boshlanadi
              </p>
              <Space>
                <Button onClick={() => setStep(1)}>Orqaga</Button>
                <Button type="primary" htmlType="submit" loading={step3M.isPending}>
                  Boshlash
                </Button>
              </Space>
            </Form>
          )}

          {step === 3 && (
            <Result
              status="success"
              icon={<CheckCircleFilled style={{ color: '#10b981' }} />}
              title="Tabriklaymiz! 🎉"
              subTitle="Universitetingiz muvaffaqiyatli qo'shildi va 30 kunlik bepul sinov boshlandi."
              extra={[
                <Button type="primary" key="login" onClick={() => navigate('/login')} icon={<RocketOutlined />}>
                  Tizimga kirish
                </Button>,
                <Button key="home" onClick={() => navigate('/landing')}>
                  Bosh sahifa
                </Button>,
              ]}
            />
          )}
        </Card>
      </div>
    </div>
  );
}
