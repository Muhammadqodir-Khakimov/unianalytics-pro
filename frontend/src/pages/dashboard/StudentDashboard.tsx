import { Row, Col, Card, Table, Tag, Alert, Progress, Button } from 'antd';
import {
  TrophyOutlined,
  BookOutlined,
  RiseOutlined,
  CalendarOutlined,
  StarOutlined,
  WarningOutlined,
  DownloadOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { myService } from '@/services/myService';
import { HeroBanner } from '@/components/common/HeroBanner';
import { KpiCard } from '@/components/common/KpiCard';
import { SkeletonKpi } from '@/components/common/SkeletonCard';
import { EmptyState } from '@/components/common/EmptyState';
import { transcriptService } from '@/services/userService';
import { smoothChart, modernLineSeries, CHART_COLORS } from '@/utils/chartHelpers';

export function StudentDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['my', 'dashboard'],
    queryFn: myService.dashboard,
  });

  if (!data || data.linked === false) {
    return (
      <div className="olap-page">
        {isLoading ? <SkeletonKpi /> : (
          <Alert
            type="warning"
            message="Hisob bog'lanmagan"
            description={data?.message || "Talaba hisobingiz tizimdagi talaba bilan bog'lanmagan"}
            showIcon
          />
        )}
      </div>
    );
  }

  // Backend Decimal'larni JSON string ('3.800') qaytaradi — number'ga cast qilish shart.
  const num = (v: any): number => {
    if (v === null || v === undefined) return 0;
    if (typeof v === 'number') return v;
    const n = parseFloat(String(v));
    return Number.isFinite(n) ? n : 0;
  };
  const { student, stats: rawStats, rank, gpa_trend, by_subject } = data;
  const stats = {
    ...rawStats,
    avg_gpa: num(rawStats.avg_gpa),
    avg_grade: num(rawStats.avg_grade),
    avg_attendance: num(rawStats.avg_attendance),
    grades_count: num(rawStats.grades_count),
    subjects_count: num(rawStats.subjects_count),
    passed_count: num(rawStats.passed_count),
    failed_count: num(rawStats.failed_count),
  };
  const isLowGPA = stats.avg_gpa < 2.5;
  const isExcellent = stats.avg_gpa >= 3.5;

  const trendOption = smoothChart({
    title: { text: 'GPA dinamikasi', left: 'center', textStyle: { fontWeight: 600, fontSize: 16 } },
    xAxis: {
      type: 'category',
      data: gpa_trend.map((t: any) => `${t.academic_year} ${t.semester}`),
    },
    yAxis: { type: 'value', min: 0, max: 4, name: 'GPA' },
    series: [
      {
        ...modernLineSeries(gpa_trend.map((t: any) => t.gpa), 'GPA', CHART_COLORS.purple),
        markLine: {
          symbol: 'none',
          data: [
            { yAxis: 2.5, lineStyle: { color: '#f59e0b' }, label: { formatter: 'Minimal 2.5' } },
            { yAxis: 3.5, lineStyle: { color: '#10b981' }, label: { formatter: "A'lo 3.5" } },
          ],
        },
      },
    ],
  });

  return (
    <div className="olap-page">
      <HeroBanner
        title={`Salom, ${student.full_name}! 👋`}
        subtitle={`${student.group_name} • ${student.course}-kurs • ${student.enrollment_year}-yil kirgan`}
        gradient={isExcellent ? 'success' : isLowGPA ? 'warning' : 'primary'}
        actions={
          <Button
            ghost
            icon={<DownloadOutlined />}
            onClick={() => transcriptService.download(1, student.full_name)}
          >
            Transkript yuklash
          </Button>
        }
      />

      {isLowGPA && (
        <Alert
          type="warning"
          icon={<WarningOutlined />}
          message="Diqqat: GPA past"
          description="GPA 2.5 dan past. O'qituvchilar bilan maslahatlashing va qo'shimcha mashg'ulotlarga qatnashing."
          style={{ marginBottom: 16, borderRadius: 12 }}
          showIcon
        />
      )}
      {isExcellent && (
        <Alert
          type="success"
          icon={<StarOutlined />}
          message="A'lo natija!"
          description="Stipendiyaga tavsiya qilinasiz. Ilmiy ish bilan shug'ullanish imkoniyatlari mavjud."
          style={{ marginBottom: 16, borderRadius: 12 }}
          showIcon
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          {isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="O'rtacha GPA"
              value={(stats.avg_gpa || 0).toFixed(2)}
              icon={<TrophyOutlined />}
              variant={isExcellent ? 'success' : isLowGPA ? 'danger' : 'primary'}
            />
          )}
        </Col>
        <Col xs={12} md={6}>
          {isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="O'rtacha ball"
              value={(stats.avg_grade || 0).toFixed(1)}
              icon={<RiseOutlined />}
              variant="info"
            />
          )}
        </Col>
        <Col xs={12} md={6}>
          {isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="Fanlar"
              value={stats.subjects_count || 0}
              icon={<BookOutlined />}
              variant="purple"
            />
          )}
        </Col>
        <Col xs={12} md={6}>
          {isLoading ? <SkeletonKpi /> : (
            <KpiCard
              label="Guruh ichida"
              value={rank.rnk ? `${rank.rnk}/${rank.total}` : '-'}
              icon={<StarOutlined />}
              variant="pink"
            />
          )}
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title={<><CalendarOutlined /> Davomat</>}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 48, fontWeight: 700, color: (stats.avg_attendance || 0) >= 80 ? '#10b981' : '#f59e0b' }}>
                {stats.avg_attendance || 0}%
              </div>
              <Progress
                percent={stats.avg_attendance || 0}
                status={(stats.avg_attendance || 0) >= 80 ? 'success' : 'exception'}
                showInfo={false}
                strokeWidth={10}
              />
              <p style={{ color: '#666', marginTop: 8 }}>
                {stats.passed_count || 0} ta o'tgan, {stats.failed_count || 0} ta o'tmagan baho
              </p>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            {gpa_trend.length > 0 ? (
              <ReactECharts option={trendOption} style={{ height: 280 }} />
            ) : (
              <EmptyState title="GPA dinamikasi yo'q" description="Baholar yuklangach paydo bo'ladi" />
            )}
          </Card>
        </Col>
      </Row>

      <Card title={<><FileTextOutlined /> Fanlar bo'yicha natijalar</>} style={{ marginTop: 16 }}>
        {by_subject?.length > 0 ? (
          <Table
            size="small"
            dataSource={by_subject}
            rowKey="subject_name"
            pagination={{ pageSize: 10 }}
            columns={[
              { title: 'Fan', dataIndex: 'subject_name' },
              { title: 'Kafedra', dataIndex: 'department' },
              {
                title: "O'rtacha ball",
                dataIndex: 'avg_grade',
                sorter: (a: any, b: any) => a.avg_grade - b.avg_grade,
                render: (v: number) => (
                  <Tag color={v >= 85 ? 'green' : v >= 70 ? 'blue' : v >= 55 ? 'orange' : 'red'}>{v}</Tag>
                ),
              },
              { title: 'Baholar', dataIndex: 'grades_count', width: 80 },
            ]}
          />
        ) : (
          <EmptyState description="Hozircha baholar yo'q" />
        )}
      </Card>
    </div>
  );
}
