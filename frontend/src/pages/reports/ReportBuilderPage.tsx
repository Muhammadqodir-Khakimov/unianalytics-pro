import { Card, Row, Col, Select, Button, Table, Tag, Space, message, Divider, Input } from 'antd';
import { DragOutlined, PlayCircleOutlined, SaveOutlined, DeleteOutlined, FilePdfOutlined, FileExcelOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { olapService, DimensionSelect } from '@/services/olapService';
import { reportService } from '@/services/reportService';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';

/**
 * DRAG-DROP REPORT BUILDER (Sprint 4.2)
 *
 * Foydalanuvchi o'zining maxsus hisobotlarini quradi:
 * - O'lchovlar (dimensions) tanlash
 * - O'lchamlar (measures) tanlash
 * - Vizualizatsiya turi (table/bar/line/pie)
 * - Filterlar
 * - Saqlash + email orqali yuborish
 */
export function ReportBuilderPage() {
  const [selectedDims, setSelectedDims] = useState<DimensionSelect[]>([
    { dimension: 'faculty', attribute: 'faculty_name' },
  ]);
  const [selectedMeasures, setSelectedMeasures] = useState<string[]>(['avg_grade', 'total_grades']);
  const [chartType, setChartType] = useState<'table' | 'bar' | 'line' | 'pie'>('bar');
  const [reportTitle, setReportTitle] = useState('Maxsus hisobot');
  const [result, setResult] = useState<any>(null);

  const dimsQ = useQuery({ queryKey: ['olap', 'dims'], queryFn: olapService.getDimensions });
  const measuresQ = useQuery({ queryKey: ['olap', 'measures'], queryFn: olapService.getMeasures });

  const runM = useMutation({
    mutationFn: olapService.query,
    onSuccess: (data) => {
      setResult(data);
      message.success(`${data.row_count} qator`);
    },
  });

  const exportM = useMutation({
    mutationFn: (format: 'pdf' | 'excel') =>
      reportService.generate({
        title: reportTitle,
        format,
        query: {
          dimensions: selectedDims,
          measures: selectedMeasures,
        },
      }),
    onSuccess: (_, format) => message.success(`${format.toUpperCase()} yuklandi`),
  });

  const addDim = () => {
    if (!dimsQ.data?.length) return;
    setSelectedDims([...selectedDims, { dimension: dimsQ.data[0].name, attribute: dimsQ.data[0].attributes[0] }]);
  };

  const removeDim = (idx: number) => setSelectedDims(selectedDims.filter((_, i) => i !== idx));

  const handleRun = () => {
    runM.mutate({
      dimensions: selectedDims,
      measures: selectedMeasures,
      limit: 1000,
    });
  };

  // Chart option
  const chartOption = result?.rows?.length && chartType !== 'table' ? (() => {
    const labels = result.rows.map((r: any) => r[`${selectedDims[0].dimension}_${selectedDims[0].attribute}`]);
    const baseOption: any = {
      title: { text: reportTitle, left: 'center' },
      tooltip: { trigger: chartType === 'pie' ? 'item' : 'axis' },
      legend: { top: 30 },
    };
    if (chartType === 'pie') {
      return {
        ...baseOption,
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: labels.map((l: string, i: number) => ({ name: l, value: result.rows[i][selectedMeasures[0]] })),
        }],
      };
    }
    return {
      ...baseOption,
      xAxis: { type: 'category', data: labels, axisLabel: { rotate: 30 } },
      yAxis: { type: 'value' },
      series: selectedMeasures.map(m => ({
        name: m,
        type: chartType,
        data: result.rows.map((r: any) => r[m]),
        smooth: chartType === 'line',
        itemStyle: { borderRadius: chartType === 'bar' ? [8, 8, 0, 0] : 0 },
      })),
    };
  })() : null;

  return (
    <div className="olap-page">
      <PageHeader
        title="Hisobot quruvchi"
        subtitle="Maxsus hisobotni o'zingiz qurganchi (drag-drop)"
        icon={<DragOutlined />}
        actions={
          <Space>
            <Button icon={<FilePdfOutlined />} onClick={() => exportM.mutate('pdf')}>
              PDF
            </Button>
            <Button icon={<FileExcelOutlined />} onClick={() => exportM.mutate('excel')}>
              Excel
            </Button>
          </Space>
        }
      />

      <Card>
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Input
              placeholder="Hisobot nomi"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              size="large"
            />
          </Col>
          <Col xs={24} md={12}>
            <h4>📊 O'lchovlar (DIMENSIONS)</h4>
            <Space direction="vertical" style={{ width: '100%' }}>
              {selectedDims.map((d, idx) => (
                <Space key={idx} style={{ width: '100%' }}>
                  <Select
                    value={d.dimension}
                    onChange={(v) => {
                      const dim = dimsQ.data?.find((x: any) => x.name === v);
                      const newDims = [...selectedDims];
                      newDims[idx] = { dimension: v, attribute: dim?.attributes[0] || '' };
                      setSelectedDims(newDims);
                    }}
                    style={{ width: 160 }}
                    options={(dimsQ.data || []).map((x: any) => ({ value: x.name, label: x.label }))}
                  />
                  <Select
                    value={d.attribute}
                    onChange={(v) => {
                      const newDims = [...selectedDims];
                      newDims[idx] = { ...newDims[idx], attribute: v };
                      setSelectedDims(newDims);
                    }}
                    style={{ width: 200 }}
                    options={(dimsQ.data?.find((x: any) => x.name === d.dimension)?.attributes || []).map((a: string) => ({ value: a, label: a }))}
                  />
                  <Button danger icon={<DeleteOutlined />} onClick={() => removeDim(idx)} />
                </Space>
              ))}
              <Button onClick={addDim} type="dashed" block>+ O'lchov</Button>
            </Space>
          </Col>
          <Col xs={24} md={12}>
            <h4>📈 O'lchamlar (MEASURES)</h4>
            <Select
              mode="multiple"
              value={selectedMeasures}
              onChange={setSelectedMeasures}
              style={{ width: '100%' }}
              options={(measuresQ.data || []).map((m: any) => ({ value: m.name, label: `${m.label} (${m.aggregation})` }))}
            />

            <Divider />
            <h4>📋 Vizualizatsiya turi</h4>
            <Select
              value={chartType}
              onChange={setChartType}
              style={{ width: '100%' }}
              options={[
                { value: 'table', label: '📋 Jadval' },
                { value: 'bar', label: '📊 Bar chart' },
                { value: 'line', label: '📈 Line chart' },
                { value: 'pie', label: '🥧 Pie chart' },
              ]}
            />
          </Col>
        </Row>

        <Divider />
        <Button type="primary" icon={<PlayCircleOutlined />} size="large" onClick={handleRun} loading={runM.isPending}>
          Bajarish
        </Button>
      </Card>

      {result && (
        <Card style={{ marginTop: 16 }} title={`${result.row_count} qator natija`}>
          {chartType === 'table' || !chartOption ? (
            <Table
              size="small"
              dataSource={result.rows.map((r: any, i: number) => ({ ...r, _key: i }))}
              rowKey="_key"
              pagination={{ pageSize: 30 }}
              scroll={{ x: 'max-content' }}
              columns={Object.keys(result.rows[0] || {}).map(k => ({
                title: k,
                dataIndex: k,
                render: (v: any) => typeof v === 'number' ? Math.round(v * 100) / 100 : v,
              }))}
            />
          ) : (
            <ReactECharts option={chartOption} style={{ height: 480 }} />
          )}
        </Card>
      )}

      {!result && (
        <Card style={{ marginTop: 16 }}>
          <EmptyState title="Hisobot tayyor emas" description="O'lchov va o'lchamlarni tanlab, Bajarish tugmasini bosing" />
        </Card>
      )}
    </div>
  );
}
