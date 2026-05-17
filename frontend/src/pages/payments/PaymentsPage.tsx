import { Card, Table, Tag, Button, Modal, message, Row, Col, Progress } from 'antd';
import { DollarOutlined, CreditCardOutlined, CheckCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { paymentService } from '@/services/hemisService';
import { useAuthStore } from '@/store/authStore';
import { PageHeader } from '@/components/common/PageHeader';
import { KpiCard } from '@/components/common/KpiCard';
import { EmptyState } from '@/components/common/EmptyState';
import { HeroBanner } from '@/components/common/HeroBanner';

export function PaymentsPage() {
  const user = useAuthStore((s) => s.user);
  const isStudent = user?.role === 'student';
  const qc = useQueryClient();
  const [payOpen, setPayOpen] = useState<any>(null);

  const myQ = useQuery({ queryKey: ['payments', 'my'], queryFn: paymentService.my, enabled: isStudent });
  const summaryQ = useQuery({
    queryKey: ['payments', 'summary'],
    queryFn: paymentService.summary,
    enabled: !isStudent,
  });
  const listQ = useQuery({
    queryKey: ['payments', 'list'],
    queryFn: () => paymentService.list({}),
    enabled: !isStudent,
  });

  const payM = useMutation({
    mutationFn: ({ id, payload }: any) => paymentService.pay(id, payload),
    onSuccess: () => {
      message.success("To'lov amalga oshirildi");
      setPayOpen(null);
      qc.invalidateQueries({ queryKey: ['payments'] });
    },
  });

  const statusTag = (s: string) =>
    s === 'paid' ? <Tag color="green" icon={<CheckCircleOutlined />}>To'langan</Tag>
    : s === 'overdue' ? <Tag color="red" icon={<WarningOutlined />}>Muddati o'tgan</Tag>
    : <Tag color="orange">Kutilmoqda</Tag>;

  const fmt = (v: number) => v.toLocaleString() + " so'm";

  // STUDENT VIEW
  if (isStudent) {
    const my = myQ.data || { total_due: 0, total_paid: 0, items: [] };
    return (
      <div className="olap-page">
        <HeroBanner
          title="Mening to'lovlarim"
          subtitle={`Jami qarz: ${fmt(my.total_due)} • To'langan: ${fmt(my.total_paid)}`}
          gradient={my.total_due > 0 ? 'warning' : 'success'}
        />

        {my.items.length === 0 ? (
          <Card><EmptyState title="To'lovlar yo'q" /></Card>
        ) : (
          <Card>
            <Table
              dataSource={my.items}
              rowKey="id"
              loading={myQ.isLoading}
              columns={[
                { title: 'Turi', dataIndex: 'payment_type', render: (v: string) => <Tag>{v}</Tag> },
                { title: 'Tavsif', dataIndex: 'description' },
                { title: "O'quv yili", dataIndex: 'academic_year' },
                { title: 'Summa', dataIndex: 'amount', render: fmt },
                { title: "To'langan", dataIndex: 'paid_amount', render: fmt },
                { title: 'Qoldiq', dataIndex: 'remaining', render: (v: number) => <strong style={{ color: v > 0 ? '#ef4444' : '#10b981' }}>{fmt(v)}</strong> },
                { title: 'Muddat', dataIndex: 'due_date' },
                { title: 'Holat', dataIndex: 'status', render: statusTag },
                {
                  title: 'Amal',
                  render: (_: any, r: any) =>
                    r.status !== 'paid' && (
                      <Button type="primary" icon={<CreditCardOutlined />} onClick={() => setPayOpen(r)}>
                        To'lash
                      </Button>
                    ),
                },
              ]}
            />
          </Card>
        )}

        <Modal
          open={!!payOpen}
          onCancel={() => setPayOpen(null)}
          title="To'lov amalga oshirish"
          footer={null}
        >
          {payOpen && (
            <div>
              <p>To'lov turi: <strong>{payOpen.payment_type}</strong></p>
              <p>Qoldiq: <strong style={{ color: '#1677ff' }}>{fmt(payOpen.remaining)}</strong></p>
              <Row gutter={8} style={{ marginTop: 16 }}>
                <Col span={8}>
                  <Button block size="large" onClick={() => payM.mutate({ id: payOpen.id, payload: { amount: payOpen.remaining, method: 'click' } })}>
                    💳 Click
                  </Button>
                </Col>
                <Col span={8}>
                  <Button block size="large" onClick={() => payM.mutate({ id: payOpen.id, payload: { amount: payOpen.remaining, method: 'payme' } })}>
                    💰 Payme
                  </Button>
                </Col>
                <Col span={8}>
                  <Button block size="large" onClick={() => payM.mutate({ id: payOpen.id, payload: { amount: payOpen.remaining, method: 'uzcard' } })}>
                    🏦 Uzcard
                  </Button>
                </Col>
              </Row>
            </div>
          )}
        </Modal>
      </div>
    );
  }

  // DEAN/ADMIN VIEW
  const summary = summaryQ.data || {};
  return (
    <div className="olap-page">
      <PageHeader title="To'lovlar boshqaruvi" subtitle="Universitet to'lov tizimi" icon={<DollarOutlined />} />

      <Row gutter={[16, 16]}>
        <Col xs={12} md={6}>
          <KpiCard label="Jami hisoblangan" value={fmt(summary.total_billed || 0)} icon={<DollarOutlined />} variant="primary" />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard label="Yig'ilgan" value={fmt(summary.total_collected || 0)} icon={<CheckCircleOutlined />} variant="success" />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard label="Qarzdorlik" value={fmt(summary.total_pending || 0)} icon={<WarningOutlined />} variant="warning" />
        </Col>
        <Col xs={12} md={6}>
          <KpiCard label="Yig'ish darajasi" value={`${summary.collection_rate || 0}%`} icon={<Progress percent={summary.collection_rate || 0} type="circle" size={32} showInfo={false} />} variant="info" />
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <Table
          dataSource={listQ.data?.items}
          rowKey="id"
          loading={listQ.isLoading}
          columns={[
            { title: 'Talaba', dataIndex: 'student_name' },
            { title: 'Turi', dataIndex: 'payment_type' },
            { title: 'Summa', dataIndex: 'amount', render: fmt },
            { title: "To'langan", dataIndex: 'paid_amount', render: fmt },
            { title: 'Qoldiq', dataIndex: 'remaining', render: fmt },
            { title: 'Holat', dataIndex: 'status', render: statusTag },
            { title: 'Muddat', dataIndex: 'due_date' },
          ]}
        />
      </Card>
    </div>
  );
}
