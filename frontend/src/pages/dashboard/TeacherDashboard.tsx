import { Row, Col, Card, Statistic, Table, Tag, Alert } from 'antd';
import {
  TeamOutlined,
  BookOutlined,
  FileTextOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { myService } from '@/services/myService';

export function TeacherDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['my', 'dashboard'],
    queryFn: myService.dashboard,
  });

  if (isLoading) return <Card loading style={{ margin: 24 }} />;
  if (!data || data.linked === false) {
    return (
      <div className="olap-page">
        <Alert type="warning" message="O'qituvchi hisobi bog'lanmagan" showIcon />
      </div>
    );
  }

  const { teacher, stats, by_subject, recent_grades } = data;

  const subjectOption = {
    title: { text: 'Fanlar bo\'yicha statistika', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { top: 30, data: ['Talabalar', 'O\'rtacha ball'] },
    xAxis: {
      type: 'category',
      data: by_subject.slice(0, 10).map((s: any) => s.subject_name),
      axisLabel: { rotate: 30, fontSize: 10 },
    },
    yAxis: [
      { type: 'value', name: 'Soni' },
      { type: 'value', name: 'Ball', max: 100 },
    ],
    series: [
      {
        name: 'Talabalar',
        type: 'bar',
        data: by_subject.slice(0, 10).map((s: any) => s.students_count),
        itemStyle: { color: '#1677ff' },
      },
      {
        name: "O'rtacha ball",
        type: 'line',
        yAxisIndex: 1,
        data: by_subject.slice(0, 10).map((s: any) => s.avg_grade),
        itemStyle: { color: '#fa8c16' },
      },
    ],
  };

  return (
    <div className="olap-page">
      <h1>O'qituvchi paneli — {teacher.full_name}</h1>
      <p style={{ color: '#888', marginBottom: 16 }}>
        {teacher.position} • {teacher.department}
      </p>

      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Baholar berildi" value={stats.grades_given || 0} prefix={<FileTextOutlined />} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Talabalar" value={stats.students_taught || 0} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Fanlar" value={stats.subjects_taught || 0} prefix={<BookOutlined />} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="O'rtacha berilgan ball"
              value={stats.avg_grade_given || 0}
              precision={1}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <ReactECharts option={subjectOption} style={{ height: 360 }} />
      </Card>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <Card title="Mening fanlarim">
            <Table
              size="small"
              dataSource={by_subject}
              rowKey="subject_name"
              pagination={{ pageSize: 10 }}
              columns={[
                { title: 'Fan', dataIndex: 'subject_name' },
                { title: 'Talabalar', dataIndex: 'students_count' },
                { title: 'Baholar', dataIndex: 'grades_count' },
                {
                  title: "O'rtacha",
                  dataIndex: 'avg_grade',
                  render: (v: number) => (
                    <Tag color={v >= 75 ? 'green' : v >= 60 ? 'blue' : 'red'}>{v}</Tag>
                  ),
                },
                { title: 'GPA', dataIndex: 'avg_gpa' },
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="So'nggi baholar">
            <Table
              size="small"
              dataSource={recent_grades}
              rowKey="id"
              pagination={false}
              columns={[
                { title: 'Student #', dataIndex: 'student_id', width: 90 },
                {
                  title: 'Ball',
                  dataIndex: 'grade_value',
                  render: (v: number) => (
                    <Tag color={v >= 75 ? 'green' : v >= 60 ? 'blue' : 'red'}>{v}</Tag>
                  ),
                },
                { title: 'Semester', dataIndex: 'semester' },
                { title: 'Sana', dataIndex: 'grade_date', width: 100 },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
