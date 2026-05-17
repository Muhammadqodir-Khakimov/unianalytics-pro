import {
  Card,
  Button,
  Table,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Space,
  Tabs,
  Empty,
} from 'antd';
import { PlusOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { applicationService } from '@/services/notificationService';
import { useAuthStore } from '@/store/authStore';

export function ApplicationsPage() {
  const user = useAuthStore((s) => s.user);
  const isStudent = user?.role === 'student';
  const isDean = user?.role === 'dekan' || user?.role === 'admin';
  const qc = useQueryClient();

  const [createOpen, setCreateOpen] = useState(false);
  const [reviewOpen, setReviewOpen] = useState<any>(null);
  const [createForm] = Form.useForm();
  const [reviewForm] = Form.useForm();

  const typesQ = useQuery({ queryKey: ['app-types'], queryFn: applicationService.types });

  const myQ = useQuery({
    queryKey: ['apps', 'my'],
    queryFn: applicationService.my,
    enabled: isStudent,
  });

  const allQ = useQuery({
    queryKey: ['apps', 'all'],
    queryFn: () => applicationService.list(),
    enabled: isDean,
  });

  const submitM = useMutation({
    mutationFn: applicationService.submit,
    onSuccess: () => {
      message.success('Ariza yuborildi');
      setCreateOpen(false);
      createForm.resetFields();
      qc.invalidateQueries({ queryKey: ['apps'] });
    },
  });

  const reviewM = useMutation({
    mutationFn: ({ id, payload }: any) => applicationService.review(id, payload),
    onSuccess: () => {
      message.success('Ariza ko\'rib chiqildi');
      setReviewOpen(null);
      reviewForm.resetFields();
      qc.invalidateQueries({ queryKey: ['apps'] });
    },
  });

  const statusColor = (s: string) =>
    s === 'approved' ? 'green' : s === 'rejected' ? 'red' : s === 'cancelled' ? 'default' : 'orange';

  const labelType = (v: string) => typesQ.data?.find((t: any) => t.value === v)?.label || v;

  const studentColumns = [
    { title: 'Sana', dataIndex: 'created_at', render: (v: string) => dayjs(v).format('YYYY-MM-DD'), width: 100 },
    { title: 'Turi', dataIndex: 'application_type', render: labelType },
    { title: 'Sarlavha', dataIndex: 'subject' },
    {
      title: 'Holat',
      dataIndex: 'status',
      render: (v: string) => <Tag color={statusColor(v)}>{v}</Tag>,
      width: 120,
    },
    { title: 'Javob', dataIndex: 'response' },
  ];

  const deanColumns = [
    { title: 'Sana', dataIndex: 'created_at', render: (v: string) => dayjs(v).format('YYYY-MM-DD'), width: 100 },
    { title: 'Talaba', dataIndex: 'student_name' },
    { title: 'Turi', dataIndex: 'application_type', render: labelType },
    { title: 'Sarlavha', dataIndex: 'subject' },
    {
      title: 'Holat',
      dataIndex: 'status',
      render: (v: string) => <Tag color={statusColor(v)}>{v}</Tag>,
      width: 120,
    },
    {
      title: 'Amal',
      render: (_: any, r: any) =>
        r.status === 'pending' ? (
          <Button size="small" type="primary" onClick={() => setReviewOpen(r)}>
            Ko'rib chiqish
          </Button>
        ) : null,
    },
  ];

  return (
    <div className="olap-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>Arizalar</h1>
        {isStudent && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
            Yangi ariza
          </Button>
        )}
      </div>

      {isStudent && (
        <Card title="Mening arizalarim">
          <Table
            dataSource={myQ.data}
            rowKey="id"
            loading={myQ.isLoading}
            columns={studentColumns}
            locale={{ emptyText: <Empty description="Arizalaringiz yo'q" /> }}
            expandable={{
              expandedRowRender: (r) => <div style={{ padding: 16, background: '#fafafa' }}>{r.body}</div>,
            }}
          />
        </Card>
      )}

      {isDean && (
        <Card title="Barcha arizalar">
          <Table
            dataSource={allQ.data?.items}
            rowKey="id"
            loading={allQ.isLoading}
            columns={deanColumns}
            expandable={{
              expandedRowRender: (r) => (
                <div style={{ padding: 16, background: '#fafafa' }}>
                  <strong>Tafsilot:</strong>
                  <p>{r.body}</p>
                  {r.response && (
                    <>
                      <strong>Javob:</strong>
                      <p>{r.response}</p>
                    </>
                  )}
                </div>
              ),
            }}
          />
        </Card>
      )}

      {/* Yangi ariza modal */}
      <Modal
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        title="Yangi ariza yuborish"
        onOk={() => createForm.submit()}
        confirmLoading={submitM.isPending}
        width={600}
      >
        <Form form={createForm} layout="vertical" onFinish={(v) => submitM.mutate(v)}>
          <Form.Item label="Ariza turi" name="application_type" rules={[{ required: true }]}>
            <Select
              options={typesQ.data?.map((t: any) => ({ value: t.value, label: t.label }))}
            />
          </Form.Item>
          <Form.Item label="Sarlavha" name="subject" rules={[{ required: true }]}>
            <Input placeholder="Masalan: Matematika fanidan qayta topshirish" />
          </Form.Item>
          <Form.Item label="Tafsilot" name="body" rules={[{ required: true }]}>
            <Input.TextArea rows={6} placeholder="Arizangiz mazmunini batafsil yozing" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Review modal */}
      <Modal
        open={!!reviewOpen}
        onCancel={() => setReviewOpen(null)}
        title="Arizani ko'rib chiqish"
        footer={null}
        width={600}
      >
        {reviewOpen && (
          <>
            <p>
              <strong>{reviewOpen.student_name}</strong> ({reviewOpen.student_code})
            </p>
            <p>
              <Tag>{labelType(reviewOpen.application_type)}</Tag>
            </p>
            <p><strong>{reviewOpen.subject}</strong></p>
            <p style={{ background: '#fafafa', padding: 12, borderRadius: 4 }}>{reviewOpen.body}</p>

            <Form
              form={reviewForm}
              layout="vertical"
              onFinish={(v) => reviewM.mutate({ id: reviewOpen.id, payload: v })}
            >
              <Form.Item label="Javob" name="response" rules={[{ required: true }]}>
                <Input.TextArea rows={4} />
              </Form.Item>
              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={() =>
                      reviewForm.validateFields().then((v) =>
                        reviewM.mutate({ id: reviewOpen.id, payload: { ...v, status: 'approved' } })
                      )
                    }
                    loading={reviewM.isPending}
                  >
                    Tasdiqlash
                  </Button>
                  <Button
                    danger
                    icon={<CloseOutlined />}
                    onClick={() =>
                      reviewForm.validateFields().then((v) =>
                        reviewM.mutate({ id: reviewOpen.id, payload: { ...v, status: 'rejected' } })
                      )
                    }
                    loading={reviewM.isPending}
                  >
                    Rad etish
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </>
        )}
      </Modal>
    </div>
  );
}
