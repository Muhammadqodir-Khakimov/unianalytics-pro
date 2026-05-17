import { useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, InputNumber, Space, Popconfirm, message, Tag, Tooltip } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';

interface University {
  id: number;
  name: string;
  short_name?: string;
  hemis_id?: string;
  city: string;
  founded_year?: number;
  student_count?: number;
  type?: 'state' | 'private' | 'international';
  status: 'active' | 'suspended' | 'archived';
}

const MOCK: University[] = [
  { id: 1, name: 'Toshkent davlat texnika universiteti', short_name: 'TDTU', city: 'Toshkent', type: 'state', founded_year: 1918, student_count: 25000, status: 'active', hemis_id: 'HM-TDTU' },
  { id: 2, name: 'Buxoro davlat universiteti', short_name: 'BuxDU', city: 'Buxoro', type: 'state', founded_year: 1992, student_count: 12000, status: 'active' },
  { id: 3, name: 'Inha University in Tashkent', short_name: 'IUT', city: 'Toshkent', type: 'international', founded_year: 2014, student_count: 3000, status: 'active' },
];

export default function UniversitiesAdmin() {
  const [list, setList] = useState<University[]>(MOCK);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<University | null>(null);
  const [form] = Form.useForm();

  const openCreate = () => { setEditing(null); form.resetFields(); setOpen(true); };
  const openEdit = (u: University) => { setEditing(u); form.setFieldsValue(u); setOpen(true); };

  const onSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editing) {
        setList((prev) => prev.map((u) => (u.id === editing.id ? { ...u, ...values } : u)));
        message.success("Universitet yangilandi");
      } else {
        const newU = { id: Math.max(...list.map((u) => u.id), 0) + 1, ...values, status: 'active' };
        setList((prev) => [newU, ...prev]);
        message.success("Universitet qo'shildi");
      }
      setOpen(false);
    } catch {}
  };

  const onDelete = (id: number) => {
    setList((prev) => prev.filter((u) => u.id !== id));
    message.success("O'chirildi");
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Universitetlar</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Yangi universitet</Button>
      </div>

      <Table
        rowKey="id"
        dataSource={list}
        columns={[
          { title: 'Nomi', dataIndex: 'name', render: (v, r) => (<><b>{v}</b>{r.short_name && <Tag style={{ marginLeft: 8 }}>{r.short_name}</Tag>}</>) },
          { title: 'Shahar', dataIndex: 'city', width: 120 },
          { title: 'Turi', dataIndex: 'type', width: 110, render: (t) => {
            const c = t === 'state' ? 'blue' : t === 'private' ? 'orange' : 'purple';
            return <Tag color={c}>{t === 'state' ? 'Davlat' : t === 'private' ? "Xususiy" : 'Xalqaro'}</Tag>;
          }},
          { title: "Tashkil et.", dataIndex: 'founded_year', width: 100 },
          { title: 'Talabalar', dataIndex: 'student_count', width: 100, render: (v) => v?.toLocaleString() ?? '-' },
          { title: 'HEMIS', dataIndex: 'hemis_id', width: 110, render: (v) => v ? <Tag color="green">{v}</Tag> : <Tag>Sync yo'q</Tag> },
          { title: 'Status', dataIndex: 'status', width: 100, render: (s) => {
            const c = s === 'active' ? 'green' : s === 'suspended' ? 'orange' : 'default';
            return <Tag color={c}>{s}</Tag>;
          }},
          {
            title: 'Amallar', width: 140, render: (_, r) => (
              <Space>
                <Tooltip title="Ko'rish"><Button size="small" icon={<EyeOutlined />} /></Tooltip>
                <Tooltip title="Tahrirlash"><Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} /></Tooltip>
                <Popconfirm title="O'chirilsinmi?" onConfirm={() => onDelete(r.id)}>
                  <Button size="small" danger icon={<DeleteOutlined />} />
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />

      <Modal
        title={editing ? 'Universitetni tahrirlash' : 'Yangi universitet'}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={onSubmit}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="To'liq nom" rules={[{ required: true, min: 3 }]}>
            <Input placeholder="Masalan: Toshkent davlat texnika universiteti" />
          </Form.Item>
          <Form.Item name="short_name" label="Qisqartma">
            <Input placeholder="TDTU" maxLength={20} />
          </Form.Item>
          <Form.Item name="city" label="Shahar" rules={[{ required: true }]}>
            <Input placeholder="Toshkent" />
          </Form.Item>
          <Space style={{ display: 'flex', width: '100%' }} size="middle">
            <Form.Item name="type" label="Turi" rules={[{ required: true }]} style={{ flex: 1 }}>
              <Select options={[
                { value: 'state', label: 'Davlat' },
                { value: 'private', label: 'Xususiy' },
                { value: 'international', label: 'Xalqaro' },
              ]} />
            </Form.Item>
            <Form.Item name="founded_year" label="Tashkil etilgan yil" style={{ flex: 1 }}>
              <InputNumber min={1800} max={new Date().getFullYear()} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="student_count" label="Talabalar soni" style={{ flex: 1 }}>
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Space>
          <Form.Item name="hemis_id" label="HEMIS ID" tooltip="HEMIS bilan sinxronizatsiya uchun">
            <Input placeholder="HM-XYZ123" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
