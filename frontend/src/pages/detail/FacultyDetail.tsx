import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Card, Statistic, Table, Tag, Button, Spin, Empty, Alert } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { detailService } from '@/services/detailService';
import { analyticsService } from '@/services/analyticsService';

export function FacultyDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const facultyId = Number(id);

  const { data, isLoading } = useQuery({
    queryKey: ['detail', 'faculty', facultyId],
    queryFn: () => detailService.faculty(facultyId),
  });

  const insightsQ = useQuery({
    queryKey: ['analytics', 'insights', data?.faculty?.name],
    queryFn: () => analyticsService.facultyInsights(data!.faculty.name),
    enabled: !!data?.faculty?.name,
  });

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: 100 }} />;
  if (!data) return <Empty />;

  const { faculty, stats, by_specialty, by_course, trend } = data;

  const trendOption = {
    title: { text: 'GPA dinamikasi', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trend.map((t: any) => `${t.academic_year} ${t.semester}`) },
    yAxis: { type: 'value', max: 4, name: 'GPA' },
    series: [
      {
        type: 'line',
        smooth: true,
        data: trend.map((t: any) => t.avg_gpa),
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#1677ff' },
      },
    ],
  };

  const specialtyOption = {
    title: { text: "Yo'nalishlar bo'yicha", left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: by_specialty.map((s: any) => s.specialty),
      axisLabel: { rotate: 30 },
    },
    yAxis: [
      { type: 'value', name: 'GPA', max: 4 },
      { type: 'value', name: 'Talabalar' },
    ],
    legend: { top: 30 },
    series: [
      {
        name: 'GPA',
        type: 'bar',
        data: by_specialty.map((s: any) => s.avg_gpa),
        itemStyle: { color: '#722ed1' },
      },
      {
        name: 'Talabalar',
        type: 'line',
        yAxisIndex: 1,
        data: by_specialty.map((s: any) => s.students),
        itemStyle: { color: '#fa8c16' },
      },
    ],
  };

  return (
    <div className="olap-page">
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/faculties')} style={{ marginBottom: 16 }}>
        Orqaga
      </Button>

      <Card>
        <h1 style={{ margin: 0 }}>{faculty.name}</h1>
        <p style={{ color: '#666' }}>Kod: {faculty.code}</p>
        {faculty.description && <p>{faculty.description}</p>}
      </Card>

      {insightsQ.data?.insights && (
        <Alert
          type={insightsQ.data.recommendations?.length > 0 ? 'warning' : 'success'}
          message="AI tahlili"
          description={
            <div>
              <strong>Kuzatishlar:</strong>
              <ul>
                {insightsQ.data.insights.map((i: string, idx: number) => (
                  <li key={idx}>{i}</li>
                ))}
              </ul>
              {insightsQ.data.recommendations?.length > 0 && (
                <>
                  <strong>Tavsiyalar:</strong>
                  <ul>
                    {insightsQ.data.recommendations.map((r: string, idx: number) => (
                      <li key={idx}>{r}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          }
          style={{ marginTop: 16 }}
          showIcon
        />
      )}

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Talabalar" value={stats.students_count || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="O'qituvchilar" value={stats.teachers_count || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Fanlar" value={stats.subjects_count || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="GPA" value={stats.avg_gpa || 0} precision={2} valueStyle={{ color: '#1677ff' }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts option={trendOption} style={{ height: 360 }} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts option={specialtyOption} style={{ height: 360 }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Yo'nalishlar">
            <Table
              size="small"
              dataSource={by_specialty}
              rowKey="specialty"
              pagination={false}
              columns={[
                { title: "Yo'nalish", dataIndex: 'specialty' },
                { title: 'Talabalar', dataIndex: 'students' },
                {
                  title: 'GPA',
                  dataIndex: 'avg_gpa',
                  render: (v: number) => <Tag color={v >= 3 ? 'green' : 'orange'}>{v}</Tag>,
                },
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Kurslar">
            <Table
              size="small"
              dataSource={by_course}
              rowKey="course"
              pagination={false}
              columns={[
                { title: 'Kurs', dataIndex: 'course', render: (v: number) => `${v}-kurs` },
                { title: 'Talabalar', dataIndex: 'students' },
                {
                  title: 'GPA',
                  dataIndex: 'avg_gpa',
                  render: (v: number) => <Tag color={v >= 3 ? 'green' : 'orange'}>{v}</Tag>,
                },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
