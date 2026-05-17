import { Card, Select, Table, Tag, Empty, Spin, Space } from 'antd';
import { CalendarOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { scheduleService } from '@/services/notificationService';
import { api } from '@/services/api';

const WEEKDAYS = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba'];

export function SchedulePage() {
  const [groupId, setGroupId] = useState<number | undefined>(undefined);

  const groupsQ = useQuery({
    queryKey: ['groups'],
    queryFn: () => api.get('/faculties/groups/all').then((r) => r.data),
  });

  const scheduleQ = useQuery({
    queryKey: ['schedule', groupId],
    queryFn: () => scheduleService.list({ group_id: groupId }),
  });

  // Haftaning kunlari bo'yicha guruhlash
  const byDay: Record<number, any[]> = {};
  for (const e of scheduleQ.data || []) {
    if (!byDay[e.weekday]) byDay[e.weekday] = [];
    byDay[e.weekday].push(e);
  }

  return (
    <div className="olap-page">
      <h1>
        <CalendarOutlined /> Haftalik jadval
      </h1>

      <Card>
        <Space>
          <span>Guruh:</span>
          <Select
            allowClear
            placeholder="Barchasi"
            value={groupId}
            onChange={setGroupId}
            showSearch
            optionFilterProp="label"
            style={{ width: 280 }}
            options={(groupsQ.data || []).map((g: any) => ({
              value: g.id,
              label: `${g.name} (${g.course}-kurs)`,
            }))}
          />
        </Space>
      </Card>

      {scheduleQ.isLoading ? (
        <Card style={{ marginTop: 16, textAlign: 'center' }}>
          <Spin />
        </Card>
      ) : !scheduleQ.data?.length ? (
        <Card style={{ marginTop: 16 }}>
          <Empty description="Jadval yo'q. Yangi yozuv qo'shish uchun admin/dekan panelidan foydalaning." />
        </Card>
      ) : (
        WEEKDAYS.map((day, idx) => {
          const lessons = byDay[idx + 1] || [];
          if (lessons.length === 0) return null;
          return (
            <Card key={idx} title={day} style={{ marginTop: 16 }}>
              <Table
                size="small"
                dataSource={lessons}
                rowKey="id"
                pagination={false}
                columns={[
                  {
                    title: 'Vaqt',
                    render: (_, r: any) => (
                      <Tag color="blue">
                        {r.start_time?.slice(0, 5)} - {r.end_time?.slice(0, 5)}
                      </Tag>
                    ),
                    width: 130,
                  },
                  { title: 'Fan', dataIndex: 'subject_name', render: (v: string, r: any) => <><strong>{v}</strong> <Tag>{r.subject_code}</Tag></> },
                  {
                    title: "Turi",
                    dataIndex: 'lesson_type',
                    render: (v: string) => <Tag color={v === 'lecture' ? 'purple' : v === 'lab' ? 'green' : 'cyan'}>{v}</Tag>,
                  },
                  { title: "O'qituvchi", dataIndex: 'teacher_name' },
                  { title: 'Guruh', dataIndex: 'group_name' },
                  { title: 'Xona', dataIndex: 'room', render: (v: string) => v && <Tag>{v}</Tag> },
                ]}
              />
            </Card>
          );
        })
      )}
    </div>
  );
}
