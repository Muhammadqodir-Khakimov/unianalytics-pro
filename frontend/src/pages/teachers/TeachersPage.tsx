import { Form, Input, Button } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { CrudTable } from '@/components/common/CrudTable';
import { teacherService } from '@/services/crudService';
import { Teacher } from '@/types';

export function TeachersPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const columns = [
    { title: 'ID', dataIndex: 'teacher_id', width: 120 },
    {
      title: 'F.I.Sh.',
      dataIndex: 'full_name',
      render: (v: string, r: Teacher) => (
        <a onClick={() => navigate(`/teachers/${r.id}`)}>
          <strong>{v}</strong>
        </a>
      ),
    },
    { title: 'Daraja', dataIndex: 'academic_degree' },
    { title: 'Lavozim', dataIndex: 'position' },
    { title: 'Kafedra', dataIndex: 'department' },
    { title: 'Email', dataIndex: 'email' },
    { title: 'Telefon', dataIndex: 'phone' },
    {
      title: 'Profil',
      key: 'view',
      width: 80,
      render: (_: any, r: Teacher) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/teachers/${r.id}`)} />
      ),
    },
  ];

  return (
    <CrudTable<Teacher>
      title={t('menu.teachers')}
      resource="teachers"
      service={teacherService}
      columns={columns}
      FormFields={
        <>
          <Form.Item label="Teacher ID" name="teacher_id" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="F.I.Sh." name="full_name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Akademik daraja" name="academic_degree">
            <Input />
          </Form.Item>
          <Form.Item label="Lavozim" name="position">
            <Input />
          </Form.Item>
          <Form.Item label="Kafedra" name="department">
            <Input />
          </Form.Item>
          <Form.Item label="Email" name="email">
            <Input type="email" />
          </Form.Item>
          <Form.Item label="Telefon" name="phone">
            <Input />
          </Form.Item>
        </>
      }
    />
  );
}
