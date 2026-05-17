import { AutoComplete, Input, Tag, Empty } from 'antd';
import { SearchOutlined, UserOutlined, TeamOutlined, BookOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchService } from '@/services/searchService';

export function GlobalSearch() {
  const [value, setValue] = useState('');
  const [options, setOptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (value.length < 2) {
      setOptions([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await searchService.global(value, 5);
        const items: any[] = [];

        if (data.students?.length) {
          items.push({
            label: <span style={{ color: '#1677ff', fontWeight: 600 }}>Talabalar</span>,
            options: data.students.map((s: any) => ({
              value: `student-${s.id}`,
              label: (
                <div onClick={() => { navigate(s.link); setValue(''); }}>
                  <UserOutlined /> <strong>{s.full_name}</strong>{' '}
                  <Tag>{s.student_id}</Tag>{' '}
                  <span style={{ color: '#999' }}>{s.group_name}</span>
                </div>
              ),
            })),
          });
        }
        if (data.teachers?.length) {
          items.push({
            label: <span style={{ color: '#722ed1', fontWeight: 600 }}>O'qituvchilar</span>,
            options: data.teachers.map((t: any) => ({
              value: `teacher-${t.id}`,
              label: (
                <div onClick={() => { navigate(t.link); setValue(''); }}>
                  <TeamOutlined /> <strong>{t.full_name}</strong>{' '}
                  <Tag>{t.teacher_id}</Tag>{' '}
                  <span style={{ color: '#999' }}>{t.department}</span>
                </div>
              ),
            })),
          });
        }
        if (data.subjects?.length) {
          items.push({
            label: <span style={{ color: '#fa8c16', fontWeight: 600 }}>Fanlar</span>,
            options: data.subjects.map((s: any) => ({
              value: `subject-${s.id}`,
              label: (
                <div onClick={() => { navigate(s.link); setValue(''); }}>
                  <BookOutlined /> <strong>{s.name}</strong>{' '}
                  <Tag>{s.code}</Tag>
                </div>
              ),
            })),
          });
        }
        setOptions(items);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [value, navigate]);

  return (
    <AutoComplete
      value={value}
      options={options}
      style={{ width: 360 }}
      onSearch={setValue}
      onChange={setValue}
      notFoundContent={value.length < 2 ? null : loading ? 'Qidirilmoqda...' : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Topilmadi" />}
      popupMatchSelectWidth={420}
    >
      <Input
        size="middle"
        prefix={<SearchOutlined />}
        placeholder="Talaba, o'qituvchi, fan qidirish..."
        allowClear
      />
    </AutoComplete>
  );
}
