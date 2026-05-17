import { Card, Col, Row, Typography } from 'antd';
import { BellCurveD3, RadarChartD3, HeatmapD3, UzbekistanMap, UZ_REGIONS } from '../../components/widgets';

const { Title, Paragraph } = Typography;

// Demo data — production da API dan keladi.
const gpaSample = Array.from({ length: 500 }, () => Math.max(0, Math.min(100, 70 + Math.random() * 30 - Math.random() * 25)));

const facultyAxes = ['GPA', 'Davomat', 'Faollik', 'Innovatsiya', 'Halqaro'];
const facultySeries = [
  { name: 'Iqtisodiyot', values: [4.2, 4.5, 3.8, 3.2, 2.9] },
  { name: 'Pedagogika', values: [4.0, 4.7, 4.1, 3.5, 2.5] },
  { name: 'IT', values: [4.6, 4.0, 4.4, 4.8, 3.7] },
];

const heatmapData = Array.from({ length: 7 }, (_, day) =>
  Array.from({ length: 8 }, (__, hour) => ({
    row: ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'][day],
    col: `${8 + hour}:00`,
    value: Math.floor(Math.random() * 100),
  })),
).flat();

const regionData = UZ_REGIONS.map((r) => ({ ...r, value: Math.floor(Math.random() * 50000) + 5000 }));

export default function AdvancedVisualsPage() {
  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Kengaytirilgan vizualizatsiya</Title>
      <Paragraph type="secondary">D3.js va Leaflet asosida maxsus tahlil widgetlari.</Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="GPA taqsimoti (Bell Curve)">
            <BellCurveD3 data={gpaSample} highlightValue={82} title="Sizning ko'rsatkichingiz qayerda?" />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Fakultetlar taqqoslash (Radar)">
            <RadarChartD3 axes={facultyAxes} series={facultySeries} max={5} />
          </Card>
        </Col>
        <Col xs={24}>
          <Card title="Davomat zichligi (Hafta × Soat)">
            <HeatmapD3 data={heatmapData} title="Talabalar davomati issiqlik kartasi" />
          </Card>
        </Col>
        <Col xs={24}>
          <Card title="O'zbekiston bo'yicha xarita">
            <UzbekistanMap data={regionData} metricLabel="Talabalar soni" height={520} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
