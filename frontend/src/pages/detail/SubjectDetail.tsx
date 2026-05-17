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
import { BookOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { detailService } from '@/services/detailService';

export function SubjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const subjectId = Number(id);

  const { data, isLoading } = useQuery({
    queryKey: ['detail', 'subject', subjectId],
    queryFn: () => detailService.subject(subjectId),
  });

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: 100 }} />;
  if (!data) return <Empty />;

  const { subject, stats, top_students, distribution } = data;

  const distOption = {
    title: { text: 'Ball taqsimoti', left: 'center' },
    tooltip: { trigger: 'item' },
    xAxis: {
      type: 'category',
      data: ['< 55 (FAIL)', '55-70 (D)', '70-85 (C)', '85-90 (B)', '90+ (A)'],
    },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data: [
          { value: distribution.bucket_fail || 0, itemStyle: { color: '#ff4d4f' } },
          { value: distribution.bucket_d || 0, itemStyle: { color: '#fa8c16' } },
          { value: distribution.bucket_c || 0, itemStyle: { color: '#fadb14' } },
          { value: distribution.bucket_b || 0, itemStyle: { color: '#52c41a' } },
          { value: distribution.bucket_a || 0, itemStyle: { color: '#1677ff' } },
        ],
        label: { show: true, position: 'top' },
      },
    ],
  };

  return (
    <div className="olap-page">
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/subjects')} style={{ marginBottom: 16 }}>
        Orqaga
      </Button>

      <Card>
        <Row gutter={24} align="middle">
          <Col>
            <Avatar size={96} icon={<BookOutlined />} style={{ background: '#fa8c16' }} />
          </Col>
          <Col flex="auto">
            <h1 style={{ margin: 0 }}>{subject.name}</h1>
            <p style={{ color: '#666', fontSize: 16 }}>
              {subject.code} • {subject.department}
            </p>
            <Space>
              <Tag color="blue">{subject.subject_type}</Tag>
              <Tag color="purple">{subject.credit_hours} kredit</Tag>
              <Tag>{subject.semester}-semester</Tag>
            </Space>
          </Col>
        </Row>
        {subject.description && <p style={{ marginTop: 16 }}>{subject.description}</p>}
      </Card>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="O'rtacha ball" value={stats.avg_grade || 0} precision={1} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Talabalar" value={stats.students_count || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Baholar" value={stats.grades_count || 0} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="O'tish darajasi"
              value={stats.passing_rate || 0}
              suffix="%"
              valueStyle={{ color: (stats.passing_rate || 0) > 75 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <Card>
            <ReactECharts option={distOption} style={{ height: 360 }} />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="Eng yuqori natija ko'rsatgan 10 ta talaba">
            <Table
              size="small"
              dataSource={top_students}
              rowKey="student_id"
              pagination={false}
              columns={[
                { title: '#', render: (_, __, i) => i + 1, width: 40 },
                { title: 'F.I.Sh.', dataIndex: 'full_name' },
                { title: 'Guruh', dataIndex: 'group_name' },
                {
                  title: 'Ball',
                  dataIndex: 'avg_grade',
                  render: (v: number) => <strong style={{ color: '#1677ff' }}>{v}</strong>,
                },
              ]}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Fan ma'lumotlari" style={{ marginTop: 16 }}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="Kod">{subject.code}</Descriptions.Item>
          <Descriptions.Item label="Nomi">{subject.name}</Descriptions.Item>
          <Descriptions.Item label="Kafedra">{subject.department}</Descriptions.Item>
          <Descriptions.Item label="Kredit soatlar">{subject.credit_hours}</Descriptions.Item>
          <Descriptions.Item label="Turi">{subject.subject_type}</Descriptions.Item>
          <Descriptions.Item label="Semester">{subject.semester}</Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
}
