import { Form, Input, Select, DatePicker, InputNumber, Button } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { CrudTable } from '@/components/common/CrudTable';
import { studentService } from '@/services/crudService';
import { Student } from '@/types';

export function StudentsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const columns = [
    { title: 'ID', dataIndex: 'student_id', width: 120 },
    {
      title: 'F.I.Sh.',
      dataIndex: 'full_name',
      render: (v: string, r: Student) => (
        <a onClick={() => navigate(`/students/${r.id}`)}>
          <strong>{v}</strong>
        </a>
      ),
    },
    { title: 'Gender', dataIndex: 'gender', width: 80 },
    {
      title: 'Tug\'ilgan',
      dataIndex: 'birth_date',
      render: (v: string) => v && dayjs(v).format('YYYY-MM-DD'),
    },
    { title: 'Email', dataIndex: 'email' },
    { title: 'Telefon', dataIndex: 'phone' },
    { title: 'Guruh', dataIndex: 'group_id', width: 100 },
    { title: 'Forma', dataIndex: 'education_form', width: 100 },
    { title: 'Status', dataIndex: 'status', width: 100 },
    { title: 'Kirgan', dataIndex: 'enrollment_year', width: 80 },
    {
      title: 'Profil',
      key: 'view',
      width: 80,
      render: (_: any, r: Student) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => navigate(`/students/${r.id}`)} />
      ),
    },
  ];

  return (
    <CrudTable<Student>
      title={t('menu.students')}
      resource="students"
      service={studentService}
      columns={columns}
      FormFields={
        <>
          <Form.Item label="Student ID" name="student_id" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="F.I.Sh." name="full_name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Gender" name="gender" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'M', label: 'Erkak' },
                { value: 'F', label: 'Ayol' },
              ]}
            />
          </Form.Item>
          <Form.Item
            label="Tug'ilgan sana"
            name="birth_date"
            rules={[{ required: true }]}
            getValueProps={(v) => ({ value: v ? dayjs(v) : null })}
            normalize={(v) => (v ? dayjs(v).format('YYYY-MM-DD') : v)}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Email" name="email">
            <Input type="email" />
          </Form.Item>
          <Form.Item label="Telefon" name="phone">
            <Input />
          </Form.Item>
          <Form.Item label="Group ID" name="group_id" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={1} />
          </Form.Item>
          <Form.Item label="Ta'lim shakli" name="education_form" initialValue="kunduzgi">
            <Select
              options={[
                { value: 'kunduzgi', label: 'Kunduzgi' },
                { value: 'sirtqi', label: 'Sirtqi' },
                { value: 'kechki', label: 'Kechki' },
              ]}
            />
          </Form.Item>
          <Form.Item label="Status" name="status" initialValue="faol">
            <Select
              options={[
                { value: 'faol', label: 'Faol' },
                { value: 'akademik_tatil', label: "Akademik ta'til" },
                { value: 'bitirgan', label: 'Bitirgan' },
                { value: 'chetlatilgan', label: 'Chetlatilgan' },
              ]}
            />
          </Form.Item>
          <Form.Item label="Kirgan yili" name="enrollment_year" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={2000} max={2030} />
          </Form.Item>
        </>
      }
    />
  );
}
