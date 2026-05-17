import { Card, Row, Col, Button, Tag, Tabs, Table, message, Empty, Statistic, Progress } from 'antd';
import {
  ExperimentOutlined,
  WarningOutlined,
  TrophyOutlined,
  RobotOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mlService } from '@/services/mlService';
import { PageHeader } from '@/components/common/PageHeader';
import { KpiCard } from '@/components/common/KpiCard';

const CLUSTER_COLORS: Record<string, string> = {
  stars: 'gold',
  diligent: 'blue',
  rising: 'green',
  lazy: 'orange',
  at_risk: 'red',
};

export function MLInsightsPage() {
  const qc = useQueryClient();

  const dropoutStatusQ = useQuery({ queryKey: ['ml', 'dropout-status'], queryFn: mlService.dropoutStatus });
  const atRiskQ = useQuery({ queryKey: ['ml', 'at-risk'], queryFn: () => mlService.dropoutAtRisk(30) });
  const clustersQ = useQuery({ queryKey: ['ml', 'clusters'], queryFn: mlService.allClusters });
  const anomalyStudentsQ = useQuery({ queryKey: ['ml', 'anom-s'], queryFn: mlService.anomaliesStudents });
  const anomalyTeachersQ = useQuery({ queryKey: ['ml', 'anom-t'], queryFn: mlService.anomaliesTeachers });
  const subjectDiffQ = useQuery({ queryKey: ['ml', 'subj-diff'], queryFn: mlService.subjectsDifficulty });
  const enrollmentQ = useQuery({ queryKey: ['ml', 'enroll'], queryFn: mlService.forecastEnrollment });

  const trainDropoutM = useMutation({
    mutationFn: mlService.trainDropout,
    onSuccess: () => {
      message.success("Drop-out modeli o'qitildi");
      qc.invalidateQueries({ queryKey: ['ml'] });
    },
  });

  const trainClustersM = useMutation({
    mutationFn: () => mlService.trainClusters(5),
    onSuccess: () => {
      message.success("Clustering modeli o'qitildi");
      qc.invalidateQueries({ queryKey: ['ml'] });
    },
  });

  const ds = dropoutStatusQ.data?.metrics;

  return (
    <div className="olap-page">
      <PageHeader
        title="ML Insights"
        subtitle="XGBoost, K-Means, Isolation Forest asosida tahlil"
        icon={<ExperimentOutlined />}
        actions={
          <>
            <Button icon={<ThunderboltOutlined />} onClick={() => trainDropoutM.mutate()} loading={trainDropoutM.isPending}>
              XGBoost qayta o'qitish
            </Button>
            <Button icon={<ThunderboltOutlined />} onClick={() => trainClustersM.mutate()} loading={trainClustersM.isPending} style={{ marginLeft: 8 }}>
              K-Means qayta o'qitish
            </Button>
          </>
        }
      />

      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          <KpiCard
            label="Model accuracy"
            value={ds ? `${(ds.accuracy * 100).toFixed(1)}%` : '-'}
            icon={<RobotOutlined />}
            variant="primary"
          />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard
            label="ROC AUC"
            value={ds?.roc_auc ? ds.roc_auc.toFixed(3) : '-'}
            icon={<ExperimentOutlined />}
            variant="info"
          />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard
            label="Xavf zonasida"
            value={atRiskQ.data?.items?.filter((s: any) => s.risk_code === 'critical' || s.risk_code === 'risk').length || 0}
            icon={<WarningOutlined />}
            variant="danger"
          />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard
            label="O'qitildi"
            value={ds?.n_samples || 0}
            icon={<TrophyOutlined />}
            variant="success"
          />
        </Col>
      </Row>

      <Tabs
        defaultActiveKey="risk"
        style={{ marginTop: 16 }}
        items={[
          {
            key: 'risk',
            label: 'Drop-out xavfi (XGBoost)',
            children: (
              <Card>
                {!atRiskQ.data?.items?.length ? (
                  <Empty description="Model o'qitilmagan yoki ma'lumot yo'q. Yuqori o'ng tugmadan model o'qiting." />
                ) : (
                  <Table
                    dataSource={atRiskQ.data.items}
                    rowKey="student_id"
                    pagination={{ pageSize: 15 }}
                    columns={[
                      { title: 'Talaba ID', dataIndex: 'student_id', width: 110 },
                      {
                        title: 'Drop-out ehtimoli',
                        dataIndex: 'dropout_probability',
                        sorter: (a: any, b: any) => a.dropout_probability - b.dropout_probability,
                        render: (v: number) => (
                          <div style={{ minWidth: 150 }}>
                            <Progress
                              percent={Math.round(v * 100)}
                              size="small"
                              strokeColor={v >= 0.75 ? '#ff4d4f' : v >= 0.5 ? '#fa8c16' : v >= 0.2 ? '#fadb14' : '#52c41a'}
                            />
                          </div>
                        ),
                      },
                      {
                        title: 'Risk',
                        dataIndex: 'risk_code',
                        render: (v: string) => {
                          const colors: Record<string, string> = { critical: 'red', risk: 'orange', watch: 'gold', safe: 'green' };
                          return <Tag color={colors[v] || 'default'}>{v}</Tag>;
                        },
                      },
                      { title: 'GPA', dataIndex: 'avg_gpa' },
                      { title: 'Davomat', dataIndex: 'avg_attendance', render: (v: number) => `${v}%` },
                      { title: "O'tmagan", dataIndex: 'failed_count' },
                    ]}
                  />
                )}
              </Card>
            ),
          },
          {
            key: 'clusters',
            label: 'Talabalar klasterlari (K-Means)',
            children: (
              <Card>
                {!clustersQ.data?.clusters ? (
                  <Empty description="K-Means modeli o'qitilmagan" />
                ) : (
                  <Row gutter={[16, 16]}>
                    {clustersQ.data.clusters.map((c: any) => (
                      <Col xs={24} sm={12} md={8} key={c.cluster_id}>
                        <Card
                          style={{
                            borderTop: `4px solid ${c.color}`,
                            textAlign: 'center',
                          }}
                        >
                          <div style={{ fontSize: 48 }}>{c.emoji}</div>
                          <h2 style={{ margin: 8 }}>{c.name}</h2>
                          <Statistic value={c.count} suffix="talaba" />
                          <p style={{ color: '#666', marginTop: 8 }}>
                            GPA: <strong>{c.avg_gpa}</strong> · Davomat: <strong>{c.avg_attendance}%</strong>
                          </p>
                          <Tag color={CLUSTER_COLORS[c.code]}>{c.code}</Tag>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}
              </Card>
            ),
          },
          {
            key: 'enroll',
            label: 'Enrollment forecast',
            children: (
              <Card title="Yangi talabalar qabuli prognozi">
                {!enrollmentQ.data?.predictions ? <Empty /> : (
                  <>
                    <Table
                      dataSource={[...(enrollmentQ.data.history || []).map((r: any) => ({ ...r, type: 'real' })),
                                   ...(enrollmentQ.data.predictions || []).map((r: any) => ({ ...r, type: 'prognoz' }))]}
                      rowKey="year"
                      pagination={false}
                      columns={[
                        { title: 'Yil', dataIndex: 'year' },
                        {
                          title: 'Talabalar soni',
                          dataIndex: 'count',
                          render: (v: number, r: any) => (
                            <strong style={{ color: r.type === 'prognoz' ? '#fa8c16' : '#1677ff' }}>
                              {v} {r.type === 'prognoz' && '🔮'}
                            </strong>
                          ),
                        },
                        { title: 'Turi', dataIndex: 'type', render: (v: string) => <Tag color={v === 'prognoz' ? 'orange' : 'blue'}>{v}</Tag> },
                      ]}
                    />
                    <p style={{ marginTop: 12 }}>
                      <strong>Trend yiliga:</strong> {enrollmentQ.data.trend_per_year > 0 ? '+' : ''}{enrollmentQ.data.trend_per_year} ta talaba
                    </p>
                  </>
                )}
              </Card>
            ),
          },
          {
            key: 'anomalies',
            label: 'Anomaliyalar (Isolation Forest)',
            children: (
              <>
                <Card title="🚨 Talabalar anomaliyalari" style={{ marginBottom: 16 }}>
                  <Table
                    size="small"
                    dataSource={anomalyStudentsQ.data?.items || []}
                    rowKey="student_id"
                    pagination={{ pageSize: 10 }}
                    columns={[
                      { title: 'Talaba', dataIndex: 'full_name' },
                      { title: 'Guruh', dataIndex: 'group_name' },
                      { title: 'O\'rtacha ball', dataIndex: 'avg_grade' },
                      { title: 'Davomat', dataIndex: 'avg_attendance', render: (v: number) => `${v}%` },
                      { title: 'Tur', dataIndex: 'type', render: (v: string) => <Tag color="red">{v}</Tag> },
                      { title: 'Score', dataIndex: 'anomaly_score' },
                    ]}
                  />
                </Card>

                <Card title="👨‍🏫 O'qituvchi anomaliyalari (grade inflation)" style={{ marginBottom: 16 }}>
                  <Table
                    size="small"
                    dataSource={anomalyTeachersQ.data?.items || []}
                    rowKey="teacher_id"
                    pagination={false}
                    columns={[
                      { title: 'O\'qituvchi', dataIndex: 'full_name' },
                      { title: 'O\'rtacha berilgan ball', dataIndex: 'avg_grade' },
                      { title: 'Talabalar', dataIndex: 'students_count' },
                      { title: 'Tur', dataIndex: 'type', render: (v: string) => <Tag color="orange">{v}</Tag> },
                    ]}
                  />
                </Card>

                <Card title="📚 Fanlar qiyinligi tahlili">
                  <Table
                    size="small"
                    dataSource={subjectDiffQ.data?.items || []}
                    rowKey="subject_name"
                    pagination={{ pageSize: 10 }}
                    columns={[
                      { title: 'Fan', dataIndex: 'subject_name' },
                      { title: 'O\'rtacha ball', dataIndex: 'avg_grade' },
                      { title: 'O\'tmaganlar %', dataIndex: 'fail_rate', render: (v: number) => `${v}%` },
                      { title: 'Qiyinlik', dataIndex: 'difficulty' },
                    ]}
                  />
                </Card>
              </>
            ),
          },
        ]}
      />
    </div>
  );
}
