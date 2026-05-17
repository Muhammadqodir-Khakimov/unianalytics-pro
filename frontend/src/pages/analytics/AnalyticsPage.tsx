import { Card, Row, Col, Table, Tag, Statistic, Tabs, Empty, Alert, Button, Progress } from 'antd';
import {
  ExperimentOutlined,
  WarningOutlined,
  TrophyOutlined,
  AlertOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { analyticsService } from '@/services/analyticsService';

export function AnalyticsPage() {
  const atRiskQ = useQuery({ queryKey: ['analytics', 'at-risk'], queryFn: () => analyticsService.atRisk(2.5, 30) });
  const topQ = useQuery({ queryKey: ['analytics', 'top'], queryFn: () => analyticsService.topPerformers(20) });
  const anomQ = useQuery({ queryKey: ['analytics', 'anomalies'], queryFn: () => analyticsService.anomalies() });

  return (
    <div className="olap-page">
      <h1>
        <ExperimentOutlined /> AI Analitika va Tavsiyalar
      </h1>
      <p style={{ color: '#666', marginBottom: 16 }}>
        Sun'iy intellekt asosida talabalar muvaffaqiyatini prognoz qilish, xavf zonasini aniqlash va
        avtomatik tavsiyalar.
      </p>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic
              title="Xavf zonasidagi talabalar"
              value={atRiskQ.data?.count || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
            <p style={{ color: '#666', marginTop: 8 }}>GPA &lt; 2.5 yoki 3+ marta o'tmagan</p>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic
              title="Eng yaxshi talabalar"
              value={topQ.data?.count || 0}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
            <p style={{ color: '#666', marginTop: 8 }}>GPA ≥ 3.5</p>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic
              title="Anomaliyalar"
              value={anomQ.data?.count || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
            <p style={{ color: '#666', marginTop: 8 }}>O'rtachadan keskin ajraladigan</p>
          </Card>
        </Col>
      </Row>

      <Tabs
        defaultActiveKey="at-risk"
        style={{ marginTop: 16 }}
        items={[
          {
            key: 'at-risk',
            label: <><WarningOutlined /> Xavf zonasi</>,
            children: (
              <Card>
                <Alert
                  type="warning"
                  message="Bu talabalar bilan individual ishlash kerak"
                  description="Kechki konsultatsiyalar, mentor biriktirish, ota-onalar bilan suhbat tavsiya etiladi."
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Table
                  loading={atRiskQ.isLoading}
                  dataSource={atRiskQ.data?.items || []}
                  rowKey="student_id"
                  size="small"
                  pagination={{ pageSize: 15 }}
                  columns={[
                    { title: 'ID', dataIndex: 'student_id', width: 100 },
                    { title: 'F.I.Sh.', dataIndex: 'full_name' },
                    { title: 'Guruh', dataIndex: 'group_name' },
                    {
                      title: 'GPA',
                      dataIndex: 'avg_gpa',
                      render: (v: number) => <strong style={{ color: '#cf1322' }}>{v}</strong>,
                      sorter: (a: any, b: any) => a.avg_gpa - b.avg_gpa,
                    },
                    {
                      title: 'Davomat',
                      dataIndex: 'avg_attendance',
                      render: (v: number) => `${v}%`,
                    },
                    { title: "O'tmagan", dataIndex: 'failed_count' },
                    {
                      title: 'Xavf darajasi',
                      dataIndex: 'risk_level',
                      render: (level: string, row: any) => (
                        <div style={{ minWidth: 120 }}>
                          <Tag color={level === 'kritik' ? 'red' : level === 'yuqori' ? 'orange' : 'yellow'}>
                            {level}
                          </Tag>
                          <Progress
                            percent={row.risk_score}
                            size="small"
                            showInfo={false}
                            strokeColor={level === 'kritik' ? '#ff4d4f' : '#fa8c16'}
                          />
                        </div>
                      ),
                    },
                  ]}
                />
              </Card>
            ),
          },
          {
            key: 'top',
            label: <><TrophyOutlined /> Eng yaxshi natijalar</>,
            children: (
              <Card>
                <Alert
                  type="success"
                  message="Stipendiya va ilmiy ishga tavsiya"
                  description="Bu talabalar yuqori akademik natijalarni ko'rsatmoqda — stipendiya, granta tavsiya etiladi."
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Table
                  loading={topQ.isLoading}
                  dataSource={topQ.data?.items || []}
                  rowKey="student_id"
                  size="small"
                  pagination={{ pageSize: 15 }}
                  columns={[
                    { title: '#', render: (_, __, i) => i + 1, width: 50 },
                    { title: 'ID', dataIndex: 'student_id' },
                    { title: 'F.I.Sh.', dataIndex: 'full_name' },
                    { title: 'Guruh', dataIndex: 'group_name' },
                    {
                      title: 'GPA',
                      dataIndex: 'avg_gpa',
                      render: (v: number) => <strong style={{ color: '#3f8600' }}>{v}</strong>,
                      sorter: (a: any, b: any) => a.avg_gpa - b.avg_gpa,
                    },
                    {
                      title: 'Davomat',
                      dataIndex: 'avg_attendance',
                      render: (v: number) => `${v}%`,
                    },
                    { title: 'Baholar', dataIndex: 'grades_count' },
                  ]}
                />
              </Card>
            ),
          },
          {
            key: 'anomalies',
            label: <><AlertOutlined /> Anomaliyalar</>,
            children: (
              <Card>
                <Alert
                  type="info"
                  message="Statistik anomaliyalar"
                  description="Fakultet o'rtacha ko'rsatkichlaridan keskin ajraladigan talabalar. Sabablarini aniqlash uchun individual tahlil kerak."
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                {!anomQ.data?.items?.length ? (
                  <Empty description="Anomaliyalar topilmadi" />
                ) : (
                  <Table
                    loading={anomQ.isLoading}
                    dataSource={anomQ.data?.items}
                    rowKey={(r: any) => `${r.student_id}-${r.faculty}`}
                    size="small"
                    pagination={{ pageSize: 15 }}
                    columns={[
                      { title: 'Talaba', dataIndex: 'full_name' },
                      { title: 'Guruh', dataIndex: 'group_name' },
                      { title: 'Fakultet', dataIndex: 'faculty' },
                      { title: 'Ball', dataIndex: 'avg_grade' },
                      { title: 'Fak. o\'rtachasi', dataIndex: 'faculty_mean' },
                      {
                        title: 'Farq',
                        dataIndex: 'deviation',
                        render: (v: number) => (
                          <Tag color={v < 0 ? 'red' : 'green'}>
                            {v > 0 ? '+' : ''}{v}
                          </Tag>
                        ),
                      },
                      {
                        title: 'Turi',
                        dataIndex: 'type',
                        render: (v: string) => <Tag color={v.includes('past') ? 'red' : 'gold'}>{v}</Tag>,
                      },
                    ]}
                  />
                )}
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
}
