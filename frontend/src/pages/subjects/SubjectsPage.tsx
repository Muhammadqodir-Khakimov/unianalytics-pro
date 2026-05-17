import { Form, Input, Select, InputNumber, Button } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { CrudTable } from '@/components/common/CrudTable';
import { subjectService } from '@/services/crudService';
import { Subject } from '@/types';

export function SubjectsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const columns = [
    { title: 'Kod', dataIndex: 'code', width: 100 },
    {
      title: 'Nomi',
      dataIndex: 'name',
      render: (v: string, r: Subject) => (
        <a onClick={() => navigate(`/subjects/${r.id}`)}>
          <strong>{v}</strong>
        </a>
      ),
    },
    { title: 'Kafedra', dataIndex: 'department' },
    { title: 'Kredit', dataIndex: 'credit_hours', width: 80 },
    { title: 'Turi', dataIndex: 'subject_type', width: 100 },
    { title: 'Semester', dataIndex: 'semester', width: 80 },
    {
      title: 'Detail',
      key: 'view',
      width: 80,
      render: (_: any, r: Subject) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/subjects/${r.id}`)} />
      ),
    },
  ];

  return (
    <CrudTable<Subject>
      title={t('menu.subjects')}
      resource="subjects"
      service={subjectService}
      columns={columns}
      FormFields={
        <>
          <Form.Item label="Kod" name="code" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Nomi" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Kafedra" name="department">
            <Input />
          </Form.Item>
          <Form.Item label="Kredit soatlar" name="credit_hours" initialValue={3}>
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Turi" name="subject_type" initialValue="majburiy">
            <Select
              options={[
                { value: 'majburiy', label: 'Majburiy' },
                { value: 'tanlov', label: 'Tanlov' },
              ]}
            />
          </Form.Item>
          <Form.Item label="Semester" name="semester" initialValue={1}>
            <InputNumber min={1} max={8} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Tavsif" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
        </>
      }
    />
  );
}
