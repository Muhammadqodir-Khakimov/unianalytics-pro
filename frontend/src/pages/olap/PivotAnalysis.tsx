import { useState } from 'react';
import { Card, Row, Col, Select, Button, Table, Empty, Spin, message } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import ReactECharts from 'echarts-for-react';
import { olapService, DimensionSelect } from '@/services/olapService';

export function PivotAnalysis() {
  const { t } = useTranslation();
  const [rowDim, setRowDim] = useState<DimensionSelect>({ dimension: 'faculty', attribute: 'faculty_name' });
  const [colDim, setColDim] = useState<DimensionSelect>({ dimension: 'time', attribute: 'semester' });
  const [measure, setMeasure] = useState<string>('avg_grade');
  const [result, setResult] = useState<any>(null);

  const dimsQ = useQuery({ queryKey: ['olap', 'dims'], queryFn: olapService.getDimensions });
  const measuresQ = useQuery({ queryKey: ['olap', 'measures'], queryFn: olapService.getMeasures });

  const pivotMutation = useMutation({
    mutationFn: olapService.pivot,
    onSuccess: (data) => {
      setResult(data);
      message.success(`Pivot tayyor: ${data.rows.length}×${data.columns.length}`);
    },
  });

  const dimensions = dimsQ.data || [];
  const measures = measuresQ.data || [];

  const handleRun = () => {
    pivotMutation.mutate({
      row_dimension: rowDim,
      column_dimension: colDim,
      measure,
      filters: [],
    });
  };

  // Pivot jadval columnlari
  const pivotColumns = result
    ? [
        {
          title: `${rowDim.dimension} / ${colDim.dimension}`,
          dataIndex: 'rowValue',
          fixed: 'left' as const,
          width: 200,
          render: (v: any) => <strong>{v ?? '(jami)'}</strong>,
        },
        ...result.columns.map((c: any) => ({
          title: c ?? '(jami)',
          dataIndex: String(c),
          render: (v: any) =>
            typeof v === 'number' ? (
              <span style={{ color: v > 75 ? '#52c41a' : v > 60 ? '#fa8c16' : '#ff4d4f' }}>
                {Math.round(v * 100) / 100}
              </span>
            ) : (
              v ?? '-'
            ),
          align: 'right' as const,
        })),
      ]
    : [];

  const pivotData = result
    ? result.rows.map((r: any, idx: number) => {
        const row: any = { rowValue: r, key: idx };
        result.columns.forEach((c: any) => {
          row[String(c)] = result.matrix[r]?.[c] ?? null;
        });
        return row;
      })
    : [];

  // Heatmap chart
  const heatmapOption = result
    ? {
        title: { text: `${measure} (Pivot)`, left: 'center' },
        tooltip: { position: 'top' },
        grid: { left: 150, bottom: 80 },
        xAxis: { type: 'category', data: result.columns.map(String), axisLabel: { rotate: 30 } },
        yAxis: { type: 'category', data: result.rows.map(String) },
        visualMap: {
          min: 0,
          max: 100,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: 0,
        },
        series: [
          {
            name: measure,
            type: 'heatmap',
            data: result.rows.flatMap((r: any, ri: number) =>
              result.columns.map((c: any, ci: number) => [ci, ri, result.matrix[r]?.[c] ?? null])
            ),
            label: { show: true, fontSize: 10 },
          },
        ],
      }
    : null;

  return (
    <div className="olap-page">
      <h1>{t('olap.pivot')} — Pivot Table tahlili</h1>

      <Card>
        <Row gutter={[16, 16]} align="bottom">
          <Col xs={24} md={8}>
            <h4>Qator o'lchovi</h4>
            <Select
              value={rowDim.dimension}
              style={{ width: '100%' }}
              onChange={(v) => {
                const dim = dimensions.find((d) => d.name === v);
                setRowDim({ dimension: v, attribute: dim?.attributes[0] || '' });
              }}
              options={dimensions.map((d) => ({ value: d.name, label: d.label }))}
            />
            <Select
              value={rowDim.attribute}
              style={{ width: '100%', marginTop: 8 }}
              onChange={(v) => setRowDim({ ...rowDim, attribute: v })}
              options={(dimensions.find((d) => d.name === rowDim.dimension)?.attributes || []).map(
                (a) => ({ value: a, label: a })
              )}
            />
          </Col>

          <Col xs={24} md={8}>
            <h4>Ustun o'lchovi</h4>
            <Select
              value={colDim.dimension}
              style={{ width: '100%' }}
              onChange={(v) => {
                const dim = dimensions.find((d) => d.name === v);
                setColDim({ dimension: v, attribute: dim?.attributes[0] || '' });
              }}
              options={dimensions.map((d) => ({ value: d.name, label: d.label }))}
            />
            <Select
              value={colDim.attribute}
              style={{ width: '100%', marginTop: 8 }}
              onChange={(v) => setColDim({ ...colDim, attribute: v })}
              options={(dimensions.find((d) => d.name === colDim.dimension)?.attributes || []).map(
                (a) => ({ value: a, label: a })
              )}
            />
          </Col>

          <Col xs={24} md={8}>
            <h4>O'lcham</h4>
            <Select
              value={measure}
              style={{ width: '100%' }}
              onChange={setMeasure}
              options={measures.map((m) => ({ value: m.name, label: m.label }))}
            />
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleRun}
              loading={pivotMutation.isPending}
              style={{ marginTop: 16, width: '100%' }}
              size="large"
            >
              Pivot bajarish
            </Button>
          </Col>
        </Row>
      </Card>

      {pivotMutation.isPending && (
        <Card style={{ marginTop: 16, textAlign: 'center' }}>
          <Spin size="large" />
        </Card>
      )}

      {result && (
        <>
          <Card style={{ marginTop: 16 }}>
            <ReactECharts option={heatmapOption!} style={{ height: 480 }} />
          </Card>

          <Card style={{ marginTop: 16 }} title="Pivot jadval">
            <Table
              size="small"
              dataSource={pivotData}
              columns={pivotColumns}
              scroll={{ x: 'max-content' }}
              pagination={{ pageSize: 30 }}
              bordered
            />
          </Card>
        </>
      )}

      {!result && !pivotMutation.isPending && (
        <Card style={{ marginTop: 16 }}>
          <Empty description="Qator, ustun va o'lchamni tanlang" />
        </Card>
      )}
    </div>
  );
}
