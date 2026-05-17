import { Row, Col, Card, Table, Tag, Statistic, Alert, Button } from 'antd';
import {
  BankOutlined,
  GlobalOutlined,
  EnvironmentOutlined,
  BarChartOutlined,
  TrophyOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { HeroBanner } from '@/components/common/HeroBanner';
import { KpiCard } from '@/components/common/KpiCard';
import { SkeletonKpi, SkeletonChart } from '@/components/common/SkeletonCard';
import { dashboardService } from '@/services/dashboardService';
import { smoothChart, modernBarSeries, modernPie, CHART_COLORS } from '@/utils/chartHelpers';

/**
 * VAZIRLIK (Ministry) Dashboard
 *
 * O'zbekiston Oliy Ta'lim Vazirligi uchun 187+ universitet bo'yicha
 * markazlashgan tahlil.
 *
 * Widget lar:
 * - Milliy KPI
 * - Hududiy taqsimot
 * - Top universitetlar reytingi
 * - Yillik o'sish
 */
export function MinistryDashboard() {
  const summaryQ = useQuery({ queryKey: ['ministry', 'summary'], queryFn: dashboardService.summary });
  const facultyQ = useQuery({ queryKey: ['ministry', 'faculty'], queryFn: dashboardService.facultyComparison });

  // Mock: real prod da 187 universitet ma'lumoti bo'lardi
  const regions = [
    { region: 'Toshkent shahar', universities: 24, students: 145_000 },
    { region: 'Toshkent viloyati', universities: 12, students: 45_000 },
    { region: 'Samarqand', universities: 11, students: 56_000 },
    { region: 'Buxoro', universities: 8, students: 32_000 },
    { region: 'Andijon', universities: 10, students: 41_000 },
    { region: 'Farg\'ona', universities: 14, students: 52_000 },
    { region: 'Namangan', universities: 9, students: 38_000 },
    { region: 'Qashqadaryo', universities: 7, students: 28_000 },
    { region: 'Surxondaryo', universities: 6, students: 22_000 },
    { region: 'Xorazm', universities: 7, students: 25_000 },
    { region: 'Navoiy', universities: 5, students: 18_000 },
    { region: 'Jizzax', universities: 5, students: 17_000 },
    { region: 'Sirdaryo', universities: 4, students: 13_000 },
    { region: 'Qoraqalpog\'iston', universities: 9, students: 35_000 },
  ];
  const totalUni = regions.reduce((s, r) => s + r.universities, 0);
  const totalStudents = regions.reduce((s, r) => s + r.students, 0);

  const topUniversities = [
    { rank: 1, name: 'O\'zMU', score: 92.5, students: 32_000 },
    { rank: 2, name: 'TATU', score: 91.8, students: 25_000 },
    { rank: 3, name: 'TDIU', score: 90.3, students: 28_000 },
    { rank: 4, name: 'SamDU', score: 89.7, students: 30_000 },
    { rank: 5, name: 'BuxDU', score: 88.2, students: 18_000 },
    { rank: 6, name: 'NamDU', score: 87.5, students: 22_000 },
    { rank: 7, name: 'AndDU', score: 86.9, students: 20_000 },
    { rank: 8, name: 'QarDU', score: 85.4, students: 16_000 },
    { rank: 9, name: 'XorDU', score: 84.8, students: 14_000 },
    { rank: 10, name: 'JIZPI', score: 83.2, students: 12_000 },
  ];

  const regionOption = smoothChart({
    title: { text: 'Hududlar bo\'yicha talabalar taqsimoti', left: 'center', textStyle: { fontWeight: 600 } },
    xAxis: { type: 'category', data: regions.map(r => r.region), axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: [{ type: 'value', name: 'Talabalar' }, { type: 'value', name: 'OTM' }],
    legend: { top: 30 },
    series: [
      modernBarSeries(regions.map(r => r.students), 'Talabalar', CHART_COLORS.primary),
      { ...modernBarSeries(regions.map(r => r.universities), 'OTM', CHART_COLORS.success), yAxisIndex: 1 },
    ],
  });

  const universityScatter = smoothChart({
    title: { text: 'Universitetlar reytingi va o\'lcham', left: 'center', textStyle: { fontWeight: 600 } },
    tooltip: { trigger: 'item' },
    xAxis: { type: 'value', name: 'Talabalar soni' },
    yAxis: { type: 'value', name: 'Reyting balli', min: 70, max: 100 },
    series: [{
      type: 'scatter',
      symbolSize: (d: number[]) => Math.sqrt(d[0]) / 10,
      data: topUniversities.map(u => [u.students, u.score, u.name]),
      label: { show: true, formatter: (p: any) => p.data[2], position: 'top', fontSize: 10 },
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 1,
          colorStops: [{ offset: 0, color: '#667eea' }, { offset: 1, color: '#764ba2' }],
        },
      },
    }],
  });

  return (
    <div className="olap-page">
      <HeroBanner
        title="🏛️ O'zbekiston Oliy Ta'lim Vazirligi"
        subtitle="187+ universitet bo'yicha markazlashgan tahlil"
        gradient="ocean"
        actions={
          <Button ghost icon={<DownloadOutlined />}>
            Milliy hisobot
          </Button>
        }
      />

      <Alert
        type="info"
        message="Demo ma'lumotlar"
        description="Hozir mock ma'lumotlar ko'rsatilmoqda. Real HEMIS API integratsiyasidan keyin 187 universitet jonli ma'lumotlari ko'rsatiladi."
        showIcon
        style={{ marginBottom: 16, borderRadius: 12 }}
      />

      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          <KpiCard label="OTM (Universitet)" value={totalUni.toString()} icon={<BankOutlined />} variant="primary" />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard label="Talabalar" value={totalStudents.toLocaleString()} icon={<GlobalOutlined />} variant="info" />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard label="Hududlar" value={regions.length.toString()} icon={<EnvironmentOutlined />} variant="purple" />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard label="O'rtacha GPA" value="3.12" icon={<TrophyOutlined />} variant="success" />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card>
            <ReactECharts option={regionOption} style={{ height: 400 }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts option={universityScatter} style={{ height: 400 }} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title={<><TrophyOutlined /> Milliy reyting (TOP-10)</>}>
            <Table
              dataSource={topUniversities}
              size="small"
              rowKey="rank"
              pagination={false}
              columns={[
                { title: '#', dataIndex: 'rank', render: (v: number) => v <= 3 ? ['🥇', '🥈', '🥉'][v-1] : v, width: 50 },
                { title: 'Universitet', dataIndex: 'name', render: (v: string) => <strong>{v}</strong> },
                { title: 'Talabalar', dataIndex: 'students', render: (v: number) => v.toLocaleString() },
                { title: 'Reyting', dataIndex: 'score', render: (v: number) => <Tag color="blue">{v}</Tag> },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
