import { useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Space, Popconfirm, message, Tag, Progress, Statistic, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CrownOutlined } from '@ant-design/icons';

interface Tenant {
  id: number;
  name: string;
  subdomain: string;
  plan: 'trial' | 'free' | 'pro' | 'enterprise';
  status: 'active' | 'suspended' | 'expired';
  students_used: number;
  students_limit: number;
  trial_ends?: string;
  mrr: number; // monthly recurring revenue, UZS
}

const MOCK: Tenant[] = [
  { id: 1, name: 'TDTU', subdomain: 'tdtu', plan: 'enterprise', status: 'active', students_used: 25000, students_limit: 50000, mrr: 9000000 },
  { id: 2, name: 'BuxDU', subdomain: 'buxdu', plan: 'pro', status: 'active', students_used: 1800, students_limit: 2000, mrr: 1500000 },
  { id: 3, name: 'Inha University', subdomain: 'iut', plan: 'pro', status: 'active', students_used: 2800, students_limit: 2000, mrr: 1500000 },
  { id: 4, name: 'Test University', subdomain: 'test', plan: 'trial', status: 'active', students_used: 45, students_limit: 100, trial_ends: '2026-05-30', mrr: 0 },
];

export default function TenantsAdmin() {
  const [list, setList] = useState<Tenant[]>(MOCK);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Tenant | null>(null);
  const [form] = Form.useForm();

  const totalMrr = list.reduce((s, t) => s + t.mrr, 0);
  const totalStudents = list.reduce((s, t) => s + t.students_used, 0);
  const activeCount = list.filter((t) => t.status === 'active').length;

  const openCreate = () => { setEditing(null); form.resetFields(); setOpen(true); };
  const openEdit = (t: Tenant) => { setEditing(t); form.setFieldsValue(t); setOpen(true); };

  const onSubmit = async () => {
    try {
      const v = await form.validateFields();
      if (editing) {
        setList((p) => p.map((t) => (t.id === editing.id ? { ...t, ...v } : t)));
        message.success('Tenant yangilandi');
      } else {
        setList((p) => [{ id: Math.max(...p.map((x) => x.id), 0) + 1, ...v, students_used: 0, students_limit: 100, status: 'active', mrr: 0 }, ...p]);
        message.success("Tenant qo'shildi");
      }
      setOpen(false);
    } catch {}
  };

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}><Card><Statistic title="Jami tenants" value={list.length} /></Card></Col>
        <Col span={6}><Card><Statistic title="Faol" value={activeCount} /></Card></Col>
        <Col span={6}><Card><Statistic title="Jami talabalar" value={totalStudents.toLocaleString()} /></Card></Col>
        <Col span={6}><Card><Statistic title="MRR (UZS)" value={totalMrr.toLocaleString()} prefix={<CrownOutlined />} /></Card></Col>
      </Row>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Multi-tenant boshqaruv</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Yangi tenant</Button>
      </div>

      <Table
        rowKey="id"
        dataSource={list}
        columns={[
          { title: 'Nom', dataIndex: 'name', render: (v, r) => (<><b>{v}</b><div style={{ fontSize: 12, color: '#888' }}>{r.subdomain}.unianalytics.uz</div></>) },
          { title: 'Plan', dataIndex: 'plan', width: 110, render: (p) => {
            const colors: any = { enterprise: 'gold', pro: 'blue', free: 'default', trial: 'orange' };
            return <Tag color={colors[p]}>{p.toUpperCase()}</Tag>;
          }},
          { title: 'Talabalar', width: 200, render: (_, r) => (
            <div>
              <span>{r.students_used.toLocaleString()} / {r.students_limit.toLocaleString()}</span>
              <Progress percent={Math.min(100, (r.students_used / r.students_limit) * 100)} size="small"
                status={r.students_used > r.students_limit ? 'exception' : 'normal'} />
            </div>
          )},
          { title: 'MRR (UZS)', dataIndex: 'mrr', width: 130, render: (v) => v.toLocaleString() },
          { title: 'Status', dataIndex: 'status', width: 110, render: (s) => {
            const c = s === 'active' ? 'green' : s === 'suspended' ? 'orange' : 'red';
            return <Tag color={c}>{s}</Tag>;
          }},
          { title: 'Trial', dataIndex: 'trial_ends', width: 110, render: (v) => v || '-' },
          { title: 'Amallar', width: 110, render: (_, r) => (
            <Space>
              <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
              <Popconfirm title="Suspend qilinsinmi?" onConfirm={() => message.warning('Suspended')}>
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </Space>
          )},
        ]}
      />

      <Modal title={editing ? 'Tenant tahrir' : 'Yangi tenant'} open={open} onCancel={() => setOpen(false)} onOk={onSubmit}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Universitet nomi" rules={[{ required: true }]}>
            <Input placeholder="Toshkent davlat universiteti" />
          </Form.Item>
          <Form.Item name="subdomain" label="Subdomain" rules={[{ required: true, pattern: /^[a-z][a-z0-9-]{2,30}$/, message: 'Faqat kichik harf, raqam, tire (3-30)' }]}>
            <Input addonAfter=".unianalytics.uz" placeholder="tdtu" />
          </Form.Item>
          <Form.Item name="plan" label="Plan" rules={[{ required: true }]}>
            <Select options={[
              { value: 'trial', label: 'Trial (14 kun bepul)' },
              { value: 'free', label: 'Free (100 talaba)' },
              { value: 'pro', label: 'PRO (1.5M UZS/oy, 2000 talaba)' },
              { value: 'enterprise', label: 'Enterprise (9M UZS/oy, cheksiz)' },
            ]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
