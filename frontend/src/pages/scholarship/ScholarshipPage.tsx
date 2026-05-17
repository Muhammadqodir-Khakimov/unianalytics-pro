import { Card, Row, Col, Statistic, Table, Tag, Empty } from 'antd';
import { DollarOutlined, UserOutlined, TrophyOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { scholarshipService } from '@/services/notificationService';

export function ScholarshipPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['scholarship', 'summary'],
    queryFn: scholarshipService.summary,
  });

  if (isLoading) return <Card loading style={{ margin: 24 }} />;
  if (!data) return <Empty />;

  const tierColors: Record<string, string> = {
    excellent: 'gold',
    good: 'green',
    satisfactory: 'blue',
    insufficient: 'red',
    failed: 'volcano',
    no_data: 'default',
  };
  const tierLabels: Record<string, string> = {
    excellent: "A'lo (1.25x)",
    good: 'Yaxshi (1.0x)',
    satisfactory: 'Qoniqarli (0.7x)',
    insufficient: 'GPA past',
    failed: 'Qarz fanlari',
    no_data: 'Ma\'lumot yo\'q',
  };

  const tableData = Object.entries(data.by_tier).map(([tier, v]: any) => ({
    tier,
    count: v.count,
    amount: v.amount,
    avg_per_student: v.count > 0 ? Math.round(v.amount / v.count) : 0,
  }));

  return (
    <div className="olap-page">
      <h1>
        <DollarOutlined /> Stipendiya tizimi
      </h1>
      <p style={{ color: '#666' }}>
        GPA va qarz fanlar asosida avtomatik hisoblangan oylik stipendiya. Asosiy summa: {data.base_amount.toLocaleString()} so'm
      </p>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={6}>
          <Card>
            <Statistic title="Jami talabalar" value={data.total_students} prefix={<UserOutlined />} />
          </Card>
        </Col>
        <Col xs={24} md={6}>
          <Card>
            <Statistic
              title="Stipendiya oluvchilar"
              value={data.by_tier.excellent.count + data.by_tier.good.count + data.by_tier.satisfactory.count}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card>
            <Statistic
              title="Oylik umumiy fond"
              value={data.total_monthly_amount}
              suffix="so'm"
              valueStyle={{ color: '#1677ff' }}
              formatter={(v) => Number(v).toLocaleString()}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }} title="Daraja bo'yicha taqsimot">
        <Table
          dataSource={tableData}
          rowKey="tier"
          pagination={false}
          columns={[
            {
              title: 'Daraja',
              dataIndex: 'tier',
              render: (v: string) => <Tag color={tierColors[v]}>{tierLabels[v]}</Tag>,
            },
            { title: 'Talabalar soni', dataIndex: 'count' },
            {
              title: 'Oylik summa (so\'m)',
              dataIndex: 'amount',
              render: (v: number) => v.toLocaleString(),
            },
            {
              title: 'O\'rtacha bir kishiga',
              dataIndex: 'avg_per_student',
              render: (v: number) => v.toLocaleString(),
            },
          ]}
        />
      </Card>

      <Card style={{ marginTop: 16 }} title="Hisoblash qoidasi">
        <ul>
          <li>GPA ≥ 3.5 va qarzsiz: <strong>1.25x</strong> asosiy stipendiya — A'lo</li>
          <li>GPA ≥ 3.0 va qarzsiz: <strong>1.0x</strong> asosiy stipendiya — Yaxshi</li>
          <li>GPA ≥ 2.5 va qarzsiz: <strong>0.7x</strong> asosiy stipendiya — Qoniqarli</li>
          <li>GPA &lt; 2.5: stipendiya berilmaydi</li>
          <li>Qarz fanlar mavjud bo'lsa: stipendiya berilmaydi</li>
        </ul>
      </Card>
    </div>
  );
}
