import { Form, Input, Button } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { CrudTable } from '@/components/common/CrudTable';
import { facultyService } from '@/services/crudService';
import { Faculty } from '@/types';

export function FacultiesPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: 'Kod', dataIndex: 'code', width: 100 },
    {
      title: 'Nomi',
      dataIndex: 'name',
      render: (v: string, r: Faculty) => (
        <a onClick={() => navigate(`/faculties/${r.id}`)}>
          <strong>{v}</strong>
        </a>
      ),
    },
    { title: 'Tavsif', dataIndex: 'description' },
    {
      title: 'Detail',
      key: 'view',
      width: 80,
      render: (_: any, r: Faculty) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/faculties/${r.id}`)} />
      ),
    },
  ];

  return (
    <CrudTable<Faculty>
      title={t('menu.faculties')}
      resource="faculties"
      service={facultyService}
      columns={columns}
      FormFields={
        <>
          <Form.Item label="Nomi" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Kod" name="code" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Tavsif" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
        </>
      }
    />
  );
}
