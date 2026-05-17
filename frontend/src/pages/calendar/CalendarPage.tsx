import { Calendar, Card, Badge, Tag } from 'antd';
import { CalendarOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import { calendarService } from '@/services/hemisService';
import { PageHeader } from '@/components/common/PageHeader';

export function CalendarPage() {
  const [month, setMonth] = useState(dayjs());
  const start = month.startOf('month').format('YYYY-MM-DD');
  const end = month.endOf('month').format('YYYY-MM-DD');

  const { data, isLoading } = useQuery({
    queryKey: ['calendar', start, end],
    queryFn: () => calendarService.events(start, end),
  });

  const eventsByDate: Record<string, any[]> = {};
  for (const e of data || []) {
    if (!eventsByDate[e.date]) eventsByDate[e.date] = [];
    eventsByDate[e.date].push(e);
  }

  const dateCellRender = (value: Dayjs) => {
    const ds = value.format('YYYY-MM-DD');
    const items = eventsByDate[ds] || [];
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {items.slice(0, 3).map((it, i) => (
          <div
            key={i}
            style={{
              fontSize: 11,
              padding: '2px 6px',
              borderRadius: 4,
              background: it.color + '20',
              color: it.color,
              fontWeight: 500,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
            title={it.title}
          >
            {it.title}
          </div>
        ))}
        {items.length > 3 && (
          <div style={{ fontSize: 10, color: '#999' }}>+{items.length - 3}</div>
        )}
      </div>
    );
  };

  return (
    <div className="olap-page">
      <PageHeader
        title="Kalendar"
        subtitle="Imtihonlar, e'lonlar va boshqa tadbirlar"
        icon={<CalendarOutlined />}
      />

      <Card loading={isLoading}>
        <Calendar
          cellRender={dateCellRender}
          onPanelChange={(date) => setMonth(date)}
        />
      </Card>

      <Card title="Tadbir turlari" style={{ marginTop: 16 }}>
        <Tag color="red">📝 Imtihon</Tag>
        <Tag color="orange">📢 E'lon (muhim)</Tag>
        <Tag color="blue">📢 E'lon (oddiy)</Tag>
      </Card>
    </div>
  );
}
