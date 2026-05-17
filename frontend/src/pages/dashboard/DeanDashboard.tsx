import { Row, Col, Card, Statistic, Table, Tag, Alert } from 'antd';
import {
  TeamOutlined,
  BookOutlined,
  ApartmentOutlined,
  TrophyOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { myService } from '@/services/myService';
import { analyticsService } from '@/services/analyticsService';

export function DeanDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['my', 'dashboard'],
    queryFn: myService.dashboard,
  });

  const facultyName = data?.faculty?.name;
  const insightsQ = useQuery({
    queryKey: ['analytics', 'insights', facultyName],
    queryFn: () => analyticsService.facultyInsights(facultyName!),
    enabled: !!facultyName,
  });

  if (isLoading) return <Card loading style={{ margin: 24 }} />;
  if (!data) return null;

  const num = (v: any): number => {
    if (v === null || v === undefined) return 0;
    if (typeof v === 'number') return v;
    const n = parseFloat(String(v));
    return Number.isFinite(n) ? n : 0;
  };
  const { faculty, stats: rawStats, by_specialty: rawSpec, by_course: rawCourse } = data;
  const stats = {
    ...rawStats,
    avg_grade: num(rawStats.avg_grade),
    avg_gpa: num(rawStats.avg_gpa),
    avg_attendance: num(rawStats.avg_attendance),
    passing_rate: num(rawStats.passing_rate),
    total_students: num(rawStats.total_students),
    total_teachers: num(rawStats.total_teachers),
    total_subjects: num(rawStats.total_subjects),
    total_grades: num(rawStats.total_grades),
  };
  const by_specialty = (rawSpec || []).map((s: any) => ({
    ...s, avg_grade: num(s.avg_grade), avg_gpa: num(s.avg_gpa), students: num(s.students),
  }));
  const by_course = (rawCourse || []).map((c: any) => ({
    ...c, avg_grade: num(c.avg_grade), avg_gpa: num(c.avg_gpa),
    students: num(c.students), course: num(c.course),
  }));

  const courseOption = {
    title: { text: 'Kurs bo\'yicha o\'zlashtirish', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: by_course.map((c: any) => `${c.course}-kurs`) },
    yAxis: [
      { type: 'value', name: 'GPA', max: 4 },
      { type: 'value', name: 'Talabalar' },
    ],
    legend: { top: 30 },
    series: [
      {
        name: 'GPA',
        type: 'bar',
        data: by_course.map((c: any) => c.avg_gpa),
        itemStyle: { color: '#1677ff' },
      },
      {
        name: 'Talabalar',
        type: 'line',
        yAxisIndex: 1,
        data: by_course.map((c: any) => c.students),
        itemStyle: { color: '#52c41a' },
      },
    ],
  };

  return (
    <div className="olap-page">
      <h1>Dekan paneli — {faculty.name}</h1>

      {insightsQ.data?.recommendations?.length > 0 && (
        <Alert
          type="info"
          message="AI tavsiyalari"
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {insightsQ.data.recommendations.map((r: string, i: number) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          }
          style={{ marginBottom: 16 }}
          showIcon
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Talabalar" value={stats.total_students || 0} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="O'qituvchilar"
              value={stats.total_teachers || 0}
              prefix={<ApartmentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Fanlar" value={stats.total_subjects || 0} prefix={<BookOutlined />} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="O'rtacha GPA"
              value={stats.avg_gpa || 0}
              precision={2}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: (stats.avg_gpa || 0) >= 3 ? '#3f8600' : '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="O'tish darajasi"
              value={stats.passing_rate || 0}
              suffix="%"
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="O'rtacha davomat"
              value={stats.avg_attendance || 0}
              suffix="%"
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Jami baholar" value={stats.total_grades || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="O'rtacha ball"
              value={stats.avg_grade || 0}
              precision={1}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <ReactECharts option={courseOption} style={{ height: 360 }} />
      </Card>

      <Card title="Yo'nalishlar kesimida" style={{ marginTop: 16 }}>
        <Table
          size="small"
          dataSource={by_specialty}
          rowKey="specialty"
          pagination={false}
          columns={[
            { title: 'Yo\'nalish', dataIndex: 'specialty' },
            { title: 'Talabalar', dataIndex: 'students' },
            {
              title: "O'rtacha ball",
              dataIndex: 'avg_grade',
              sorter: (a: any, b: any) => a.avg_grade - b.avg_grade,
            },
            {
              title: 'GPA',
              dataIndex: 'avg_gpa',
              sorter: (a: any, b: any) => a.avg_gpa - b.avg_gpa,
              render: (v: number) => (
                <Tag color={v >= 3 ? 'green' : v >= 2.5 ? 'blue' : 'red'}>{v}</Tag>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
