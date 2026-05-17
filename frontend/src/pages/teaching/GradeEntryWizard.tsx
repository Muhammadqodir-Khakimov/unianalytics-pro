import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import {
  Card,
  Steps,
  Select,
  Button,
  Table,
  InputNumber,
  message,
  Space,
  Tag,
  Alert,
  DatePicker,
  Upload,
} from 'antd';
import {
  RightOutlined,
  LeftOutlined,
  SaveOutlined,
  UploadOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { api } from '@/services/api';
import { facultyService, studentService, subjectService, gradeService } from '@/services/crudService';

interface GradeRow {
  student_id: number;
  student_name: string;
  grade_value: number | null;
  attendance: number;
}

export function GradeEntryWizard() {
  const currentTeacherId = useAuthStore((s) => s.user?.id ?? 1);
  const [step, setStep] = useState(0);
  const [groupId, setGroupId] = useState<number | null>(null);
  const [subjectId, setSubjectId] = useState<number | null>(null);
  const [assessmentId, setAssessmentId] = useState<number | null>(null);
  const [academicYear, setAcademicYear] = useState('2024-2025');
  const [semester, setSemester] = useState('kuzgi');
  const [gradeDate, setGradeDate] = useState(dayjs());
  const [gradeRows, setGradeRows] = useState<GradeRow[]>([]);
  const qc = useQueryClient();

  const groupsQ = useQuery({ queryKey: ['groups'], queryFn: () => api.get('/faculties/groups/all').then(r => r.data) });
  const subjectsQ = useQuery({ queryKey: ['subjects', 'all'], queryFn: () => subjectService.list({ page_size: 200 }) });
  const assessmentQ = useQuery({
    queryKey: ['assessment-types'],
    queryFn: () => api.get('/grades/assessment-types/all').then(r => r.data),
  });
  const studentsQ = useQuery({
    queryKey: ['students', 'by-group', groupId],
    queryFn: () => studentService.list({ page_size: 200, group_id: groupId }),
    enabled: !!groupId,
  });

  const submitM = useMutation({
    mutationFn: async () => {
      // Bulk insert
      const valid = gradeRows.filter((r) => r.grade_value !== null && r.grade_value !== undefined);
      const results = await Promise.allSettled(
        valid.map((r) =>
          gradeService.create({
            student_id: r.student_id,
            subject_id: subjectId,
            teacher_id: currentTeacherId,
            assessment_type_id: assessmentId,
            grade_value: r.grade_value,
            attendance_percentage: r.attendance,
            is_passed: (r.grade_value || 0) >= 55,
            semester,
            academic_year: academicYear,
            grade_date: gradeDate.format('YYYY-MM-DD'),
          })
        )
      );
      const success = results.filter((r) => r.status === 'fulfilled').length;
      const failed = results.filter((r) => r.status === 'rejected').length;
      return { success, failed, total: valid.length };
    },
    onSuccess: (data) => {
      message.success(`${data.success} ta baho saqlandi (xatolar: ${data.failed})`);
      qc.invalidateQueries({ queryKey: ['grades'] });
      setStep(3);
    },
  });

  const next = () => {
    if (step === 0 && !groupId) return message.warning('Guruh tanlang');
    if (step === 1 && (!subjectId || !assessmentId)) return message.warning('Fan va baholash turini tanlang');
    if (step === 1 && studentsQ.data?.items) {
      // Talabalar ro'yxati tayyorlanyapti
      setGradeRows(
        studentsQ.data.items.map((s: any) => ({
          student_id: s.id,
          student_name: s.full_name,
          grade_value: null,
          attendance: 100,
        }))
      );
    }
    setStep(step + 1);
  };

  const updateGrade = (idx: number, field: 'grade_value' | 'attendance', val: number | null) => {
    const rows = [...gradeRows];
    (rows[idx] as any)[field] = val;
    setGradeRows(rows);
  };

  return (
    <div className="olap-page">
      <h1>Baho kiritish</h1>
      <p style={{ color: '#666' }}>Bosqichma-bosqich talabalar guruhiga baholar kiritish</p>

      <Card>
        <Steps
          current={step}
          items={[
            { title: 'Guruh tanlash' },
            { title: 'Fan va baholash turi' },
            { title: 'Baholar kiritish' },
            { title: 'Yakunlandi' },
          ]}
        />

        <div style={{ marginTop: 32 }}>
          {step === 0 && (
            <div style={{ maxWidth: 500 }}>
              <h3>Guruhni tanlang</h3>
              <Select
                value={groupId}
                onChange={setGroupId}
                placeholder="Guruh"
                style={{ width: '100%' }}
                showSearch
                optionFilterProp="label"
                options={(groupsQ.data || []).map((g: any) => ({
                  value: g.id,
                  label: `${g.name} (${g.course}-kurs)`,
                }))}
              />
            </div>
          )}

          {step === 1 && (
            <Space direction="vertical" style={{ width: 500 }}>
              <div>
                <label>Fan</label>
                <Select
                  value={subjectId}
                  onChange={setSubjectId}
                  placeholder="Fan tanlang"
                  style={{ width: '100%' }}
                  showSearch
                  optionFilterProp="label"
                  options={(subjectsQ.data?.items || []).map((s: any) => ({
                    value: s.id,
                    label: `${s.name} (${s.code})`,
                  }))}
                />
              </div>
              <div>
                <label>Baholash turi</label>
                <Select
                  value={assessmentId}
                  onChange={setAssessmentId}
                  placeholder="Baholash turi"
                  style={{ width: '100%' }}
                  options={(assessmentQ.data || []).map((a: any) => ({
                    value: a.id,
                    label: `${a.name} (${a.weight_percentage}%)`,
                  }))}
                />
              </div>
              <Space>
                <div>
                  <label>O'quv yili</label>
                  <Select
                    value={academicYear}
                    onChange={setAcademicYear}
                    style={{ width: 150 }}
                    options={[
                      { value: '2023-2024', label: '2023-2024' },
                      { value: '2024-2025', label: '2024-2025' },
                      { value: '2025-2026', label: '2025-2026' },
                    ]}
                  />
                </div>
                <div>
                  <label>Semester</label>
                  <Select
                    value={semester}
                    onChange={setSemester}
                    style={{ width: 120 }}
                    options={[
                      { value: 'kuzgi', label: 'Kuzgi' },
                      { value: 'bahorgi', label: 'Bahorgi' },
                    ]}
                  />
                </div>
                <div>
                  <label>Sana</label>
                  <DatePicker
                    value={gradeDate}
                    onChange={(d) => d && setGradeDate(d)}
                    style={{ width: 140 }}
                  />
                </div>
              </Space>
            </Space>
          )}

          {step === 2 && (
            <div>
              <Alert
                message="Har bir talaba uchun ball kiriting (0-100)"
                description="Ball kiritilmaganlari saqlanmaydi. Avtomatik o'tdi/o'tmadi 55 ball asosida belgilanadi."
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              <Table
                size="small"
                dataSource={gradeRows}
                rowKey="student_id"
                pagination={false}
                columns={[
                  { title: '#', render: (_, __, i) => i + 1, width: 50 },
                  { title: 'Talaba', dataIndex: 'student_name' },
                  {
                    title: 'Ball (0-100)',
                    render: (_, _row, i) => (
                      <InputNumber
                        min={0}
                        max={100}
                        value={gradeRows[i].grade_value}
                        onChange={(v) => updateGrade(i, 'grade_value', v as number)}
                        placeholder="Ball"
                        style={{ width: 100 }}
                      />
                    ),
                  },
                  {
                    title: 'Davomat %',
                    render: (_, _row, i) => (
                      <InputNumber
                        min={0}
                        max={100}
                        value={gradeRows[i].attendance}
                        onChange={(v) => updateGrade(i, 'attendance', v as number)}
                        style={{ width: 80 }}
                      />
                    ),
                  },
                  {
                    title: 'Holat',
                    render: (_, _row, i) => {
                      const v = gradeRows[i].grade_value;
                      if (v === null || v === undefined) return <Tag>Bo'sh</Tag>;
                      return v >= 55 ? <Tag color="green">O'tdi</Tag> : <Tag color="red">O'tmadi</Tag>;
                    },
                  },
                ]}
              />
            </div>
          )}

          {step === 3 && (
            <div style={{ textAlign: 'center', padding: 48 }}>
              <CheckCircleOutlined style={{ fontSize: 64, color: '#52c41a' }} />
              <h2>Baholar muvaffaqiyatli saqlandi!</h2>
              <Button type="primary" onClick={() => { setStep(0); setGroupId(null); setSubjectId(null); setAssessmentId(null); setGradeRows([]); }}>
                Yangi kiritish
              </Button>
            </div>
          )}
        </div>

        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
          {step > 0 && step < 3 && (
            <Button icon={<LeftOutlined />} onClick={() => setStep(step - 1)}>
              Orqaga
            </Button>
          )}
          <div style={{ marginLeft: 'auto' }}>
            {step < 2 && (
              <Button type="primary" onClick={next} icon={<RightOutlined />} iconPosition="end">
                Keyingi
              </Button>
            )}
            {step === 2 && (
              <Button
                type="primary"
                size="large"
                icon={<SaveOutlined />}
                loading={submitM.isPending}
                onClick={() => submitM.mutate()}
              >
                Saqlash ({gradeRows.filter(r => r.grade_value !== null).length} ta baho)
              </Button>
            )}
          </div>
        </div>
      </Card>

      <Card title="Yoki CSV fayldan import" style={{ marginTop: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <p>CSV format: <code>student_id,subject_code,assessment_type,grade_value,attendance,semester,academic_year,grade_date</code></p>
          <Space>
            <Button onClick={() => window.open('/api/v1/imports/grades/csv/template', '_blank')}>
              Namuna shablon yuklash
            </Button>
            <Upload
              name="file"
              accept=".csv"
              action="/api/v1/imports/grades/csv?teacher_id=1"
              headers={{
                Authorization: `Bearer ${localStorage.getItem('auth-storage') ? JSON.parse(localStorage.getItem('auth-storage')!).state.accessToken : ''}`,
              }}
              onChange={(info) => {
                if (info.file.status === 'done') {
                  message.success(`${info.file.response?.inserted || 0} ta baho yuklandi`);
                } else if (info.file.status === 'error') {
                  message.error('Yuklashda xato');
                }
              }}
            >
              <Button icon={<UploadOutlined />}>CSV fayl tanlash</Button>
            </Upload>
          </Space>
        </Space>
      </Card>
    </div>
  );
}
