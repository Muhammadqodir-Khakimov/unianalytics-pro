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
  Tabs,
} from 'antd';
import {
  UserOutlined,
  ArrowLeftOutlined,
  DownloadOutlined,
  ExperimentOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { detailService } from '@/services/detailService';
import { analyticsService } from '@/services/analyticsService';
import { transcriptService } from '@/services/userService';

export function StudentDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const studentId = Number(id);

  const detailQ = useQuery({
    queryKey: ['detail', 'student', studentId],
    queryFn: () => detailService.student(studentId),
  });

  const predictionQ = useQuery({
    queryKey: ['analytics', 'prediction', studentId],
    queryFn: () => analyticsService.studentPrediction(studentId),
  });

  if (detailQ.isLoading) return <Spin size="large" style={{ display: 'block', margin: 100 }} />;
  if (!detailQ.data) return <Empty description="Ma'lumot topilmadi" />;

  const { student, stats, rank, gpa_trend, by_subject } = detailQ.data;
  const pred = predictionQ.data;

  // GPA trend + prediction chart
  const trendData = (gpa_trend || []).map((t: any) => ({
    name: `${t.academic_year} ${t.semester}`,
    value: t.gpa,
    type: 'actual',
  }));
  const predData = (pred?.predictions || []).map((p: any) => ({
    name: p.period,
    value: p.gpa,
    type: 'prediction',
  }));
  const allLabels = [...trendData.map((d: any) => d.name), ...predData.map((d: any) => d.name)];

  const trendOption = {
    title: { text: 'GPA dinamikasi + AI prognoz', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { top: 30, data: ['Real', 'AI prognoz'] },
    xAxis: { type: 'category', data: allLabels },
    yAxis: { type: 'value', min: 0, max: 4 },
    series: [
      {
        name: 'Real',
        type: 'line',
        smooth: true,
        data: [...trendData.map((d: any) => d.value), ...predData.map(() => null)],
        itemStyle: { color: '#1677ff' },
      },
      {
        name: 'AI prognoz',
        type: 'line',
        smooth: true,
        data: [
          ...trendData.map(() => null),
          ...predData.map((d: any) => d.value),
        ],
        itemStyle: { color: '#fa8c16' },
        lineStyle: { type: 'dashed' },
      },
    ],
  };

  return (
    <div className="olap-page">
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/students')}>
          Orqaga
        </Button>
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={() => transcriptService.download(studentId, student.full_name)}
        >
          Transkript yuklash (PDF)
        </Button>
      </Space>

      <Card>
        <Row gutter={24} align="middle">
          <Col>
            <Avatar size={96} icon={<UserOutlined />} style={{ background: '#1677ff' }} />
          </Col>
          <Col flex="auto">
            <h1 style={{ margin: 0 }}>{student.full_name}</h1>
            <p style={{ color: '#666', fontSize: 16 }}>
              {student.student_id} • {student.group_name} • {student.course}-kurs
            </p>
            <Space>
              <Tag color="blue">{student.specialty}</Tag>
              <Tag color="purple">{student.faculty}</Tag>
              <Tag color="green">{student.status}</Tag>
              <Tag>{student.education_form}</Tag>
            </Space>
          </Col>
          <Col>
            {pred?.risk_level === 'yuqori' && <Tag color="red" style={{ fontSize: 14 }}>Xavf zonasi</Tag>}
            {pred?.risk_level === 'past' && stats.avg_gpa >= 3.5 && (
              <Tag color="gold" icon={<TrophyOutlined />} style={{ fontSize: 14 }}>
                Eng yaxshilar
              </Tag>
            )}
          </Col>
        </Row>
      </Card>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="GPA" value={stats.avg_gpa || 0} precision={2} valueStyle={{ color: '#1677ff' }} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="O'rtacha ball" value={stats.avg_grade || 0} precision={1} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Davomat" value={stats.avg_attendance || 0} suffix="%" />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Guruh ichida o'rin"
              value={rank.rnk || '-'}
              suffix={rank.total ? `/ ${rank.total}` : ''}
            />
          </Card>
        </Col>
      </Row>

      {pred && pred.predictions?.length > 0 && (
        <Card style={{ marginTop: 16 }} title={<><ExperimentOutlined /> AI prognoz</>}>
          <Row gutter={16}>
            <Col span={16}>
              <p>
                <strong>Trend:</strong>{' '}
                <Tag color={pred.trend === 'o\'sayotgan' ? 'green' : pred.trend === 'pasayayotgan' ? 'red' : 'blue'}>
                  {pred.trend}
                </Tag>
                <strong style={{ marginLeft: 16 }}>Xavf darajasi:</strong>{' '}
                <Tag color={pred.risk_level === 'yuqori' ? 'red' : pred.risk_level === 'o\'rta' ? 'orange' : 'green'}>
                  {pred.risk_level}
                </Tag>
              </p>
              <p>
                <strong>Tavsiya:</strong> {pred.recommendation}
              </p>
            </Col>
            <Col span={8}>
              {pred.predictions.map((p: any, i: number) => (
                <div key={i} style={{ marginBottom: 8 }}>
                  <strong>{p.period}:</strong> GPA = {p.gpa}{' '}
                  <Tag color="orange">{p.confidence} ishonch</Tag>
                </div>
              ))}
            </Col>
          </Row>
        </Card>
      )}

      <Tabs
        defaultActiveKey="trend"
        style={{ marginTop: 16 }}
        items={[
          {
            key: 'trend',
            label: 'GPA dinamikasi',
            children: (
              <Card>
                <ReactECharts option={trendOption} style={{ height: 400 }} />
              </Card>
            ),
          },
          {
            key: 'subjects',
            label: 'Fanlar bo\'yicha',
            children: (
              <Card>
                <Table
                  size="small"
                  dataSource={by_subject}
                  rowKey="subject_name"
                  pagination={{ pageSize: 15 }}
                  columns={[
                    { title: 'Fan', dataIndex: 'subject_name' },
                    { title: 'Kafedra', dataIndex: 'department' },
                    { title: 'Kredit', dataIndex: 'credit_hours', width: 80 },
                    {
                      title: "O'rtacha ball",
                      dataIndex: 'avg_grade',
                      sorter: (a: any, b: any) => a.avg_grade - b.avg_grade,
                      render: (v: number) => (
                        <Tag color={v >= 85 ? 'green' : v >= 70 ? 'blue' : v >= 55 ? 'orange' : 'red'}>{v}</Tag>
                      ),
                    },
                    { title: 'GPA', dataIndex: 'avg_gpa' },
                    { title: 'Baholar soni', dataIndex: 'grades_count' },
                  ]}
                />
              </Card>
            ),
          },
          {
            key: 'info',
            label: "Shaxsiy ma'lumot",
            children: (
              <Card>
                <Descriptions column={2} bordered>
                  <Descriptions.Item label="Student ID">{student.student_id}</Descriptions.Item>
                  <Descriptions.Item label="F.I.Sh.">{student.full_name}</Descriptions.Item>
                  <Descriptions.Item label="Jinsi">{student.gender}</Descriptions.Item>
                  <Descriptions.Item label="Tug'ilgan sana">{student.birth_date}</Descriptions.Item>
                  <Descriptions.Item label="Telefon">{student.phone}</Descriptions.Item>
                  <Descriptions.Item label="Email">{student.email}</Descriptions.Item>
                  <Descriptions.Item label="Guruh">{student.group_name}</Descriptions.Item>
                  <Descriptions.Item label="Kurs">{student.course}</Descriptions.Item>
                  <Descriptions.Item label="Yo'nalish">{student.specialty}</Descriptions.Item>
                  <Descriptions.Item label="Fakultet">{student.faculty}</Descriptions.Item>
                  <Descriptions.Item label="Ta'lim shakli">{student.education_form}</Descriptions.Item>
                  <Descriptions.Item label="Status">{student.status}</Descriptions.Item>
                  <Descriptions.Item label="Kirgan yili">{student.enrollment_year}</Descriptions.Item>
                </Descriptions>
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
}
