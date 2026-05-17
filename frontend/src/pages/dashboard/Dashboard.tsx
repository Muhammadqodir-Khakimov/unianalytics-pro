import { Row, Col, Card, Table } from 'antd';
import {
  UserOutlined,
  BookOutlined,
  TrophyOutlined,
  RiseOutlined,
  ApartmentOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { dashboardService } from '@/services/dashboardService';
import { useAuthStore } from '@/store/authStore';
import { StudentDashboard } from './StudentDashboard';
import { TeacherDashboard } from './TeacherDashboard';
import { DeanDashboard } from './DeanDashboard';
import { HeroBanner } from '@/components/common/HeroBanner';
import { KpiCard } from '@/components/common/KpiCard';
import { SkeletonKpi, SkeletonChart } from '@/components/common/SkeletonCard';
import {
  smoothChart,
  modernLineSeries,
  modernBarSeries,
  modernPie,
  CHART_COLORS,
  CHART_PALETTE,
  linearGradient,
} from '@/utils/chartHelpers';

export function Dashboard() {
  const user = useAuthStore((s) => s.user);

  if (user?.role === 'student') return <StudentDashboard />;
  if (user?.role === 'teacher') return <TeacherDashboard />;
  if (user?.role === 'dekan') return <DeanDashboard />;

  return <AdminDashboard />;
}

function AdminDashboard() {
  const summaryQ = useQuery({ queryKey: ['dashboard', 'summary'], queryFn: dashboardService.summary });
  const trendQ = useQuery({ queryKey: ['dashboard', 'trend'], queryFn: dashboardService.gpaTrend });
  const facultyQ = useQuery({
    queryKey: ['dashboard', 'faculty'],
    queryFn: dashboardService.facultyComparison,
  });
  const topQ = useQuery({ queryKey: ['dashboard', 'top'], queryFn: () => dashboardService.topStudents(10) });
  const subjectQ = useQuery({
    queryKey: ['dashboard', 'subjects'],
    queryFn: dashboardService.subjectPerformance,
  });
  const genderQ = useQuery({
    queryKey: ['dashboard', 'gender'],
    queryFn: dashboardService.genderDistribution,
  });
  const heatmapQ = useQuery({
    queryKey: ['dashboard', 'heatmap'],
    queryFn: dashboardService.heatmapFacultySemester,
  });

  const summary = summaryQ.data || {};

  const trendOption = smoothChart({
    title: { text: "GPA dinamikasi", left: 'center', textStyle: { fontWeight: 600, fontSize: 16 } },
    xAxis: { type: 'category', data: (trendQ.data || []).map((r: any) => `${r.academic_year} ${r.semester}`) },
    yAxis: { type: 'value', name: 'GPA', min: 0, max: 4 },
    series: [modernLineSeries((trendQ.data || []).map((r: any) => r.avg_gpa), 'GPA', CHART_COLORS.purple)],
  });

  const facultyOption = smoothChart({
    title: { text: 'Fakultetlar solishtirma', left: 'center', textStyle: { fontWeight: 600, fontSize: 16 } },
    legend: { data: ["O'rtacha ball", 'GPA'], top: 30 },
    xAxis: {
      type: 'category',
      data: (facultyQ.data || []).map((r: any) => r.faculty_name),
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: [
      { type: 'value', name: 'Ball' },
      { type: 'value', name: 'GPA', max: 4 },
    ],
    series: [
      modernBarSeries((facultyQ.data || []).map((r: any) => r.avg_grade), "O'rtacha ball", CHART_COLORS.success),
      { ...modernLineSeries((facultyQ.data || []).map((r: any) => r.avg_gpa), 'GPA', CHART_COLORS.warning), yAxisIndex: 1 },
    ],
  });

  const subjectOption = smoothChart({
    title: { text: "Eng yaxshi 15 ta fan", left: 'center', textStyle: { fontWeight: 600, fontSize: 16 } },
    xAxis: {
      type: 'category',
      data: (subjectQ.data || []).slice(0, 15).map((r: any) => r.subject_name),
      axisLabel: { rotate: 45, fontSize: 10 },
    },
    yAxis: { type: 'value' },
    series: [modernBarSeries((subjectQ.data || []).slice(0, 15).map((r: any) => r.avg_grade), 'Ball', CHART_COLORS.purple)],
  });

  const genderOption = smoothChart({
    title: { text: 'Gender taqsimoti', left: 'center', textStyle: { fontWeight: 600, fontSize: 16 } },
    tooltip: { trigger: 'item' },
    series: [
      modernPie(
        (genderQ.data || []).map((r: any) => ({
          name: r.gender === 'M' ? 'Erkak' : 'Ayol',
          value: r.students_count,
        })),
        'Gender',
      ),
    ],
  });

  const heatmapData = heatmapQ.data || [];
  const heatmapFaculties = [...new Set(heatmapData.map((r: any) => r.faculty_name))];
  const heatmapPeriods = [...new Set(heatmapData.map((r: any) => r.period))];
  const heatmapValues = heatmapData.map((r: any) => [
    heatmapPeriods.indexOf(r.period),
    heatmapFaculties.indexOf(r.faculty_name),
    r.avg_grade,
  ]);

  const heatmapOption = smoothChart({
    title: { text: 'Fakultet × Semester Heatmap', left: 'center', textStyle: { fontWeight: 600, fontSize: 16 } },
    tooltip: { position: 'top' },
    grid: { left: 140, bottom: 80 },
    xAxis: { type: 'category', data: heatmapPeriods, axisLabel: { rotate: 30 } },
    yAxis: { type: 'category', data: heatmapFaculties },
    visualMap: {
      min: 50,
      max: 90,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: { color: ['#fef3c7', '#fde047', '#84cc16', '#10b981'] },
    },
    series: [
      {
        name: "O'rtacha ball",
        type: 'heatmap',
        data: heatmapValues,
        label: { show: true, fontSize: 10 },
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      },
    ],
  });

  return (
    <div className="olap-page">
      <HeroBanner
        title="Tizim Boshqaruv Paneli"
        subtitle="Universitet bo'yicha umumiy ko'rsatkichlar va OLAP tahlil"
        gradient="ocean"
      />

      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          {summaryQ.isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="Talabalar"
              value={(summary.total_students || 0).toLocaleString()}
              icon={<UserOutlined />}
              variant="primary"
            />
          )}
        </Col>
        <Col xs={12} md={6}>
          {summaryQ.isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="Jami baholar"
              value={(summary.total_grades || 0).toLocaleString()}
              icon={<BookOutlined />}
              variant="info"
            />
          )}
        </Col>
        <Col xs={12} md={6}>
          {summaryQ.isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="O'rtacha GPA"
              value={(summary.avg_gpa || 0).toFixed(2)}
              icon={<TrophyOutlined />}
              variant="success"
            />
          )}
        </Col>
        <Col xs={12} md={6}>
          {summaryQ.isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="O'tish darajasi"
              value={`${summary.passing_rate || 0}%`}
              icon={<RiseOutlined />}
              variant={(summary.passing_rate || 0) > 80 ? 'success' : 'warning'}
            />
          )}
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card styles={{ body: { padding: 8 } }}>
            {trendQ.isLoading ? <SkeletonChart /> : <ReactECharts option={trendOption} style={{ height: 360 }} />}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card styles={{ body: { padding: 8 } }}>
            {genderQ.isLoading ? <SkeletonChart /> : <ReactECharts option={genderOption} style={{ height: 360 }} />}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card styles={{ body: { padding: 8 } }}>
            {facultyQ.isLoading ? <SkeletonChart /> : <ReactECharts option={facultyOption} style={{ height: 400 }} />}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card styles={{ body: { padding: 8 } }}>
            {subjectQ.isLoading ? <SkeletonChart /> : <ReactECharts option={subjectOption} style={{ height: 400 }} />}
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }} styles={{ body: { padding: 8 } }}>
        {heatmapQ.isLoading ? <SkeletonChart /> : <ReactECharts option={heatmapOption} style={{ height: 440 }} />}
      </Card>

      <Card title={<><StarOutlined /> TOP-10 talaba</>} style={{ marginTop: 16 }}>
        <Table
          size="small"
          loading={topQ.isLoading}
          dataSource={topQ.data || []}
          rowKey="student_id"
          pagination={false}
          columns={[
            {
              title: '#',
              render: (_, __, i) => {
                const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}`;
                return <span style={{ fontSize: i < 3 ? 22 : 14, fontWeight: 600 }}>{medal}</span>;
              },
              width: 60,
            },
            { title: 'ID', dataIndex: 'student_id' },
            { title: 'F.I.Sh.', dataIndex: 'full_name', render: (v: string) => <strong>{v}</strong> },
            { title: 'Guruh', dataIndex: 'group_name' },
            {
              title: 'GPA',
              dataIndex: 'avg_gpa',
              render: (v: number) => (
                <div style={{
                  display: 'inline-block',
                  background: linearGradient('#667eea', '#764ba2') as any,
                  color: 'white',
                  padding: '2px 10px',
                  borderRadius: 6,
                  fontWeight: 600,
                }}>
                  {v}
                </div>
              ),
            },
            { title: "O'rtacha ball", dataIndex: 'avg_grade' },
            { title: 'Baholar', dataIndex: 'grades_count' },
          ]}
        />
      </Card>
    </div>
  );
}
