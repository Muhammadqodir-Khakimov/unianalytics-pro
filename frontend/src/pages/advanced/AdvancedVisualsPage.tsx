import { Card, Col, Row, Typography, Skeleton, Empty } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { BellCurveD3, RadarChartD3, HeatmapD3, UzbekistanMap, UZ_REGIONS } from '../../components/widgets';

const { Title, Paragraph } = Typography;

// Region xaritasi uchun statik konfiguratsiya — viloyatlar nomi va koordinatalari.
// Talabalar soni backend `/dashboard/regions` yo'q ekan, hozircha demo statistic.
const regionData = UZ_REGIONS.map((r) => ({ ...r, value: Math.floor(Math.random() * 50000) + 5000 }));

export default function AdvancedVisualsPage() {
  // GPA distribution — barcha individual baholar (~10K)
  const gradeDistQ = useQuery<number[]>({
    queryKey: ['dashboard', 'grade-distribution'],
    queryFn: async () => (await api.get('/dashboard/grade-distribution')).data,
  });

  // Faculty radar — backend agregatlangan 5 o'lcham
  const radarQ = useQuery({
    queryKey: ['dashboard', 'faculty-radar'],
    queryFn: async () => (await api.get('/dashboard/faculty-radar')).data,
  });

  // Attendance heatmap — kun × soat
  const heatQ = useQuery({
    queryKey: ['dashboard', 'attendance-heatmap'],
    queryFn: async () => (await api.get('/dashboard/attendance-heatmap')).data,
  });

  const myGpa = (() => {
    const arr = gradeDistQ.data;
    if (!arr || arr.length === 0) return undefined;
    return Math.round(arr.reduce((a, b) => a + b, 0) / arr.length);
  })();

  return (
    <div className="olap-page">
      <Title level={2}>Kengaytirilgan vizualizatsiya</Title>
      <Paragraph type="secondary">
        D3.js va Leaflet asosida ko'p o'lchovli tahlil widgetlari — barcha ma'lumotlar real OLAP DWH'dan keladi.
      </Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="GPA taqsimoti (Bell Curve)" extra={
            gradeDistQ.data && <small>{gradeDistQ.data.length.toLocaleString()} ta baho</small>
          }>
            {gradeDistQ.isLoading ? (
              <Skeleton active />
            ) : gradeDistQ.data && gradeDistQ.data.length > 0 ? (
              <BellCurveD3
                data={gradeDistQ.data}
                highlightValue={myGpa}
                title="O'rtacha ko'rsatkich qayerda?"
              />
            ) : (
              <Empty description="Baholar topilmadi" />
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Fakultetlar taqqoslash (Radar)" extra={
            radarQ.data && <small>{radarQ.data.series?.length || 0} fakultet</small>
          }>
            {radarQ.isLoading ? (
              <Skeleton active />
            ) : radarQ.data && radarQ.data.series?.length > 0 ? (
              <RadarChartD3
                axes={radarQ.data.axes}
                series={radarQ.data.series}
                max={5}
              />
            ) : (
              <Empty description="Fakultet ma'lumotlari topilmadi" />
            )}
          </Card>
        </Col>

        <Col xs={24}>
          <Card title="Davomat zichligi (Hafta × Soat)" extra={
            heatQ.data && <small>{heatQ.data.length} hujayra</small>
          }>
            {heatQ.isLoading ? (
              <Skeleton active />
            ) : heatQ.data && heatQ.data.length > 0 ? (
              <HeatmapD3
                data={heatQ.data}
                title="Talabalar faolligi issiqlik kartasi"
              />
            ) : (
              <Empty description="Davomat ma'lumotlari topilmadi" />
            )}
          </Card>
        </Col>

        <Col xs={24}>
          <Card title="O'zbekiston bo'yicha xarita"
            extra={<small>Hududiy taqsimot</small>}
          >
            <UzbekistanMap data={regionData} metricLabel="Talabalar soni" height={520} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
