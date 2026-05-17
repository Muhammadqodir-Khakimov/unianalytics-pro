import { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Select,
  Button,
  Table,
  Space,
  Tag,
  Empty,
  Spin,
  message,
  Divider,
  Input,
} from 'antd';
import { PlayCircleOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import ReactECharts from 'echarts-for-react';
import { olapService, DimensionSelect, FilterClause } from '@/services/olapService';

export function CubeAnalysis() {
  const { t } = useTranslation();
  const [selectedDims, setSelectedDims] = useState<DimensionSelect[]>([
    { dimension: 'faculty', attribute: 'faculty_name' },
  ]);
  const [selectedMeasures, setSelectedMeasures] = useState<string[]>(['avg_grade', 'total_grades']);
  const [filters, setFilters] = useState<FilterClause[]>([]);
  const [groupingMode, setGroupingMode] = useState('GROUP BY');
  const [result, setResult] = useState<any>(null);
  const [sqlText, setSqlText] = useState<string>('');

  const dimsQ = useQuery({ queryKey: ['olap', 'dims'], queryFn: olapService.getDimensions });
  const measuresQ = useQuery({ queryKey: ['olap', 'measures'], queryFn: olapService.getMeasures });

  const runMutation = useMutation({
    mutationFn: olapService.query,
    onSuccess: (data) => {
      setResult(data);
      setSqlText(data.sql || '');
      message.success(`${data.row_count} ta qator topildi`);
    },
  });

  const dimensions = dimsQ.data || [];
  const measures = measuresQ.data || [];

  const addDimension = () => {
    if (dimensions.length === 0) return;
    setSelectedDims([
      ...selectedDims,
      { dimension: dimensions[0].name, attribute: dimensions[0].attributes[0] },
    ]);
  };

  const removeDimension = (idx: number) => {
    setSelectedDims(selectedDims.filter((_, i) => i !== idx));
  };

  const updateDimension = (idx: number, field: 'dimension' | 'attribute', value: string) => {
    const newDims = [...selectedDims];
    newDims[idx] = { ...newDims[idx], [field]: value };
    if (field === 'dimension') {
      const dim = dimensions.find((d) => d.name === value);
      newDims[idx].attribute = dim?.attributes[0] || '';
    }
    setSelectedDims(newDims);
  };

  const addFilter = () => {
    if (dimensions.length === 0) return;
    setFilters([
      ...filters,
      {
        dimension: dimensions[0].name,
        attribute: dimensions[0].attributes[0],
        operator: '=',
        value: '',
      },
    ]);
  };

  const removeFilter = (idx: number) => setFilters(filters.filter((_, i) => i !== idx));

  const updateFilter = (idx: number, field: string, value: any) => {
    const newFilters = [...filters];
    (newFilters[idx] as any)[field] = value;
    setFilters(newFilters);
  };

  const handleRun = () => {
    if (selectedDims.length === 0) {
      message.warning("Kamida bitta o'lchov tanlang");
      return;
    }
    if (selectedMeasures.length === 0) {
      message.warning("Kamida bitta o'lcham tanlang");
      return;
    }
    runMutation.mutate({
      dimensions: selectedDims,
      measures: selectedMeasures,
      filters: filters.filter((f) => f.value !== '' || f.values),
      grouping_mode: groupingMode,
      limit: 1000,
    });
  };

  // Result table columns
  const columns = result?.rows?.length
    ? Object.keys(result.rows[0]).map((key) => ({
        title: key,
        dataIndex: key,
        key,
        sorter: (a: any, b: any) => {
          if (typeof a[key] === 'number') return a[key] - b[key];
          return String(a[key] || '').localeCompare(String(b[key] || ''));
        },
        render: (v: any) => (typeof v === 'number' ? Math.round(v * 100) / 100 : v),
      }))
    : [];

  // Chart (agar 1 dim + 1 measure bo'lsa)
  const showChart = selectedDims.length === 1 && selectedMeasures.length >= 1 && result?.rows?.length;
  const chartOption = showChart
    ? {
        title: { text: `${selectedDims[0].attribute} bo'yicha`, left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { top: 30, data: selectedMeasures },
        xAxis: {
          type: 'category',
          data: result.rows.map((r: any) => r[`${selectedDims[0].dimension}_${selectedDims[0].attribute}`]),
          axisLabel: { rotate: 30 },
        },
        yAxis: { type: 'value' },
        series: selectedMeasures.map((m) => ({
          name: m,
          type: 'bar',
          data: result.rows.map((r: any) => r[m]),
        })),
      }
    : null;

  return (
    <div className="olap-page">
      <h1>{t('olap.title')} — OLAP Cube Explorer</h1>

      <Card title="Konfiguratsiya">
        <Row gutter={[16, 16]}>
          {/* Dimensions */}
          <Col xs={24} lg={12}>
            <h3>{t('olap.select_dimensions')}</h3>
            <Space direction="vertical" style={{ width: '100%' }}>
              {selectedDims.map((d, idx) => (
                <Space key={idx} style={{ width: '100%' }}>
                  <Select
                    value={d.dimension}
                    style={{ width: 160 }}
                    onChange={(v) => updateDimension(idx, 'dimension', v)}
                    options={dimensions.map((dim) => ({ value: dim.name, label: dim.label }))}
                  />
                  <Select
                    value={d.attribute}
                    style={{ width: 200 }}
                    onChange={(v) => updateDimension(idx, 'attribute', v)}
                    options={(dimensions.find((dim) => dim.name === d.dimension)?.attributes || []).map(
                      (a) => ({ value: a, label: a })
                    )}
                  />
                  <Button danger icon={<DeleteOutlined />} onClick={() => removeDimension(idx)} />
                </Space>
              ))}
              <Button type="dashed" icon={<PlusOutlined />} onClick={addDimension} block>
                O'lchov qo'shish
              </Button>
            </Space>
          </Col>

          {/* Measures */}
          <Col xs={24} lg={12}>
            <h3>{t('olap.select_measures')}</h3>
            <Select
              mode="multiple"
              style={{ width: '100%' }}
              value={selectedMeasures}
              onChange={setSelectedMeasures}
              options={measures.map((m) => ({ value: m.name, label: `${m.label} (${m.aggregation})` }))}
            />
            <h4 style={{ marginTop: 16 }}>Grouping mode</h4>
            <Select
              value={groupingMode}
              onChange={setGroupingMode}
              style={{ width: '100%' }}
              options={[
                { value: 'GROUP BY', label: 'GROUP BY (oddiy)' },
                { value: 'CUBE', label: 'CUBE (barcha kombinatsiyalar)' },
                { value: 'ROLLUP', label: 'ROLLUP (ierarxik)' },
                { value: 'GROUPING SETS', label: 'GROUPING SETS' },
              ]}
            />
          </Col>
        </Row>

        <Divider />

        {/* Filters */}
        <h3>{t('olap.filters')}</h3>
        <Space direction="vertical" style={{ width: '100%' }}>
          {filters.map((f, idx) => (
            <Space key={idx} style={{ width: '100%' }}>
              <Select
                value={f.dimension}
                style={{ width: 140 }}
                onChange={(v) => updateFilter(idx, 'dimension', v)}
                options={dimensions.map((dim) => ({ value: dim.name, label: dim.label }))}
              />
              <Select
                value={f.attribute}
                style={{ width: 180 }}
                onChange={(v) => updateFilter(idx, 'attribute', v)}
                options={(dimensions.find((dim) => dim.name === f.dimension)?.attributes || []).map(
                  (a) => ({ value: a, label: a })
                )}
              />
              <Select
                value={f.operator}
                style={{ width: 100 }}
                onChange={(v) => updateFilter(idx, 'operator', v)}
                options={['=', '!=', '>', '<', '>=', '<=', 'LIKE'].map((o) => ({ value: o, label: o }))}
              />
              <Input
                value={f.value}
                onChange={(e) => updateFilter(idx, 'value', e.target.value)}
                placeholder="Qiymat"
                style={{ width: 200 }}
              />
              <Button danger icon={<DeleteOutlined />} onClick={() => removeFilter(idx)} />
            </Space>
          ))}
          <Button type="dashed" icon={<PlusOutlined />} onClick={addFilter}>
            Filter qo'shish
          </Button>
        </Space>

        <Divider />

        <Button
          type="primary"
          size="large"
          icon={<PlayCircleOutlined />}
          onClick={handleRun}
          loading={runMutation.isPending}
        >
          {t('olap.execute')}
        </Button>
      </Card>

      {/* Natija */}
      {runMutation.isPending && (
        <Card style={{ marginTop: 16, textAlign: 'center' }}>
          <Spin tip="OLAP query bajarilmoqda..." size="large">
            <div style={{ minHeight: 100 }} />
          </Spin>
        </Card>
      )}

      {result && (
        <>
          {showChart && (
            <Card style={{ marginTop: 16 }}>
              <ReactECharts option={chartOption!} style={{ height: 400 }} />
            </Card>
          )}

          <Card
            style={{ marginTop: 16 }}
            title={
              <Space>
                Natija
                <Tag color="blue">{result.row_count} qator</Tag>
              </Space>
            }
            extra={
              <Button
                size="small"
                onClick={() => {
                  navigator.clipboard.writeText(sqlText);
                  message.success('SQL nusxalandi');
                }}
              >
                SQL nusxalash
              </Button>
            }
          >
            <Table
              size="small"
              dataSource={result.rows.map((r: any, i: number) => ({ ...r, _key: i }))}
              rowKey="_key"
              columns={columns}
              scroll={{ x: 'max-content' }}
              pagination={{ pageSize: 50, showSizeChanger: true }}
            />
            {sqlText && (
              <details style={{ marginTop: 16 }}>
                <summary>Generated SQL</summary>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, overflow: 'auto' }}>
                  {sqlText}
                </pre>
              </details>
            )}
          </Card>
        </>
      )}

      {!result && !runMutation.isPending && (
        <Card style={{ marginTop: 16 }}>
          <Empty description="Konfiguratsiya tanlang va Bajarish tugmasini bosing" />
        </Card>
      )}
    </div>
  );
}
