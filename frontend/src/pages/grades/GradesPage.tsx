import { Form, Input, InputNumber, DatePicker, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import dayjs from 'dayjs';
import { CrudTable } from '@/components/common/CrudTable';
import { gradeService } from '@/services/crudService';
import { Grade } from '@/types';

export function GradesPage() {
  const { t } = useTranslation();

  const columns = [
    { title: 'Student', dataIndex: 'student_id', width: 100 },
    { title: 'Subject', dataIndex: 'subject_id', width: 100 },
    { title: 'Teacher', dataIndex: 'teacher_id', width: 100 },
    {
      title: 'Ball',
      dataIndex: 'grade_value',
      width: 100,
      render: (v: number) => <strong style={{ color: v >= 60 ? '#52c41a' : '#ff4d4f' }}>{v}</strong>,
    },
    { title: 'Davomat', dataIndex: 'attendance_percentage', render: (v: number) => `${v}%` },
    {
      title: "O'tdi?",
      dataIndex: 'is_passed',
      render: (v: boolean) => (v ? '✅' : '❌'),
    },
    { title: 'Semester', dataIndex: 'semester' },
    { title: "O'quv yili", dataIndex: 'academic_year' },
    { title: 'Sana', dataIndex: 'grade_date' },
  ];

  return (
    <CrudTable<Grade>
      title={t('menu.grades')}
      resource="grades"
      service={gradeService}
      columns={columns}
      FormFields={
        <>
          <Form.Item label="Student ID" name="student_id" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Subject ID" name="subject_id" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Teacher ID" name="teacher_id" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Assessment Type ID" name="assessment_type_id" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Ball (0-100)" name="grade_value" rules={[{ required: true }]}>
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Davomat %" name="attendance_percentage" initialValue={100}>
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Semester" name="semester" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'kuzgi', label: 'Kuzgi' },
                { value: 'bahorgi', label: 'Bahorgi' },
              ]}
            />
          </Form.Item>
          <Form.Item label="O'quv yili" name="academic_year" rules={[{ required: true }]}>
            <Input placeholder="2024-2025" />
          </Form.Item>
          <Form.Item
            label="Sana"
            name="grade_date"
            rules={[{ required: true }]}
            getValueProps={(v) => ({ value: v ? dayjs(v) : null })}
            normalize={(v) => (v ? dayjs(v).format('YYYY-MM-DD') : v)}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </>
      }
    />
  );
}
