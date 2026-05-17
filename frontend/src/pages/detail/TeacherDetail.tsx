import { useParams, useNavigate } from 'react-router-dom';
import {
  Row,
  Col,
  Card,
  Descriptions,
  Statistic,
  Table,
  Tag,
  Button,
  Avatar,
  Spin,
  Empty,
  Space,
} from 'antd';
import { TeamOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { detailService } from '@/services/detailService';

export function TeacherDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const teacherId = Number(id);

  const { data, isLoading } = useQuery({
    queryKey: ['detail', 'teacher', teacherId],
    queryFn: () => detailService.teacher(teacherId),
  });

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: 100 }} />;
  if (!data) return <Empty />;

  const { teacher, stats, subjects, trend } = data;

  const trendOption = {
    title: { text: 'Berilgan baholar dinamikasi', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trend.map((t: any) => `${t.academic_year} ${t.semester}`) },
    yAxis: [
      { type: 'value', name: "O'rtacha ball", max: 100 },
      { type: 'value', name: 'Baholar soni' },
    ],
    legend: { top: 30 },
    series: [
      {
        name: "O'rtacha ball",
        type: 'line',
        smooth: true,
        data: trend.map((t: any) => t.avg_grade),
        itemStyle: { color: '#1677ff' },
      },
      {
        name: 'Baholar',
        type: 'bar',
        yAxisIndex: 1,
        data: trend.map((t: any) => t.grades),
        itemStyle: { color: '#52c41a' },
      },
    ],
  };

  return (
    <div className="olap-page">
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/teachers')} style={{ marginBottom: 16 }}>
        Orqaga
      </Button>

      <Card>
        <Row gutter={24} align="middle">
          <Col>
            <Avatar size={96} icon={<TeamOutlined />} style={{ background: '#722ed1' }} />
          </Col>
          <Col flex="auto">
            <h1 style={{ margin: 0 }}>{teacher.full_name}</h1>
            <p style={{ color: '#666', fontSize: 16 }}>
              {teacher.teacher_id} • {teacher.position} • {teacher.department}
            </p>
            <Space>
              <Tag color="purple">{teacher.academic_degree}</Tag>
              <Tag>{teacher.department}</Tag>
            </Space>
          </Col>
        </Row>
      </Card>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Baholar bergan" value={stats.grades_given || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Talabalar soni" value={stats.students_taught || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Fanlar soni" value={stats.subjects_taught || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="O'rtacha ball" value={stats.avg_grade_given || 0} precision={1} />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <ReactECharts option={trendOption} style={{ height: 360 }} />
      </Card>

      <Card title="O'qiyotgan fanlari" style={{ marginTop: 16 }}>
        <Table
          dataSource={subjects}
          rowKey="subject_name"
          size="small"
          pagination={false}
          columns={[
            { title: 'Fan', dataIndex: 'subject_name' },
            { title: 'Kafedra', dataIndex: 'department' },
            { title: 'Talabalar', dataIndex: 'students' },
            { title: 'Baholar', dataIndex: 'grades_count' },
            {
              title: "O'rtacha",
              dataIndex: 'avg_grade',
              render: (v: number) => <Tag color={v >= 75 ? 'green' : 'blue'}>{v}</Tag>,
            },
          ]}
        />
      </Card>

      <Card title="Kontakt ma'lumotlari" style={{ marginTop: 16 }}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="Teacher ID">{teacher.teacher_id}</Descriptions.Item>
          <Descriptions.Item label="F.I.Sh.">{teacher.full_name}</Descriptions.Item>
          <Descriptions.Item label="Akademik daraja">{teacher.academic_degree}</Descriptions.Item>
          <Descriptions.Item label="Lavozim">{teacher.position}</Descriptions.Item>
          <Descriptions.Item label="Kafedra">{teacher.department}</Descriptions.Item>
          <Descriptions.Item label="Telefon">{teacher.phone}</Descriptions.Item>
          <Descriptions.Item label="Email">{teacher.email}</Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
}
