import { Card, Row, Col, Tag, Progress, Empty, Statistic } from 'antd';
import { HomeOutlined, TeamOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { dormitoryService } from '@/services/hemisService';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';
import { useAuthStore } from '@/store/authStore';

export function DormitoryPage() {
  const user = useAuthStore((s) => s.user);
  const isStudent = user?.role === 'student';

  const roomsQ = useQuery({ queryKey: ['dormitory', 'rooms'], queryFn: dormitoryService.rooms });
  const myQ = useQuery({ queryKey: ['dormitory', 'my'], queryFn: dormitoryService.my, enabled: isStudent });

  if (isStudent) {
    return (
      <div className="olap-page">
        <PageHeader title="Mening yotoqxonam" icon={<HomeOutlined />} />
        {!myQ.data ? (
          <Card><EmptyState title="Yotoqxonaga biriktirilmagansiz" description="Dekanat orqali ariza yozing" /></Card>
        ) : (
          <Card>
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <Statistic title="Bino" value={myQ.data.building_name} />
              </Col>
              <Col span={8}>
                <Statistic title="Xona" value={myQ.data.room_number} />
              </Col>
              <Col span={8}>
                <Statistic title="Qavat" value={myQ.data.floor} />
              </Col>
              <Col span={12}>
                <Statistic title="Kirgan sana" value={myQ.data.check_in_date} />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Oylik to'lov"
                  value={myQ.data.monthly_fee}
                  suffix="so'm"
                  formatter={(v) => Number(v).toLocaleString()}
                />
              </Col>
            </Row>
          </Card>
        )}
      </div>
    );
  }

  const rooms = roomsQ.data || [];
  const totalCapacity = rooms.reduce((s: number, r: any) => s + r.capacity, 0);
  const totalOccupied = rooms.reduce((s: number, r: any) => s + r.occupied, 0);
  const occupancyRate = totalCapacity > 0 ? Math.round((totalOccupied * 100) / totalCapacity) : 0;

  return (
    <div className="olap-page">
      <PageHeader title="Yotoqxona boshqaruvi" subtitle="Xonalar, talaba taqsimoti" icon={<HomeOutlined />} />

      <Row gutter={[16, 16]}>
        <Col xs={12} md={8}>
          <Card>
            <Statistic title="Xonalar soni" value={rooms.length} prefix={<HomeOutlined />} />
          </Card>
        </Col>
        <Col xs={12} md={8}>
          <Card>
            <Statistic title="Joylar" value={totalCapacity} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="To'lganlik" value={`${occupancyRate}%`} />
            <Progress percent={occupancyRate} />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }} title="Xonalar">
        {rooms.length === 0 ? (
          <EmptyState title="Xonalar yo'q" description="Admin tomonidan xona qo'shilishi kerak" />
        ) : (
          <Row gutter={[16, 16]}>
            {rooms.map((r: any) => (
              <Col xs={12} sm={8} md={6} lg={4} key={r.id}>
                <Card
                  size="small"
                  style={{
                    textAlign: 'center',
                    borderTop: `4px solid ${r.available > 0 ? '#10b981' : '#ef4444'}`,
                  }}
                >
                  <div style={{ fontSize: 24, fontWeight: 700 }}>{r.room_number}</div>
                  <div style={{ color: '#666', fontSize: 12 }}>{r.building_name}</div>
                  <Tag color={r.available > 0 ? 'green' : 'red'} style={{ marginTop: 8 }}>
                    {r.occupied}/{r.capacity}
                  </Tag>
                  <div style={{ marginTop: 4, fontSize: 11, color: '#999' }}>{r.gender}</div>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Card>
    </div>
  );
}
