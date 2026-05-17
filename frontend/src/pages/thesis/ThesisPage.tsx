import { Card, Table, Tag, Button, Modal, Form, Input, Select, message } from 'antd';
import { ExperimentOutlined, PlusOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { thesisService } from '@/services/hemisService';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  draft: { label: 'Loyiha', color: 'default' },
  approved: { label: 'Tasdiqlangan', color: 'blue' },
  in_progress: { label: 'Yozilmoqda', color: 'cyan' },
  submitted: { label: 'Topshirilgan', color: 'gold' },
  defended: { label: 'Himoya qilindi', color: 'green' },
  rejected: { label: 'Rad etilgan', color: 'red' },
};

export function ThesisPage() {
  const qc = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const { data, isLoading } = useQuery({ queryKey: ['theses'], queryFn: () => thesisService.list() });

  const createM = useMutation({
    mutationFn: thesisService.create,
    onSuccess: () => {
      message.success('Bitiruv ishi qo\'shildi');
      setModalOpen(false);
      form.resetFields();
      qc.invalidateQueries({ queryKey: ['theses'] });
    },
  });

  return (
    <div className="olap-page">
      <PageHeader
        title="Bitiruv ishlari"
        subtitle="Diplom va kurs ishlari boshqaruvi"
        icon={<ExperimentOutlined />}
        actions={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Yangi
          </Button>
        }
      />

      <Card>
        {data?.length === 0 ? (
          <EmptyState title="Bitiruv ishlari yo'q" />
        ) : (
          <Table
            dataSource={data}
            rowKey="id"
            loading={isLoading}
            columns={[
              { title: 'Talaba', dataIndex: 'student_name' },
              { title: 'Mavzu', dataIndex: 'title', render: (v: string) => <strong>{v}</strong> },
              { title: 'Rahbar', dataIndex: 'supervisor_name' },
              {
                title: 'Holat',
                dataIndex: 'status',
                render: (v: string) => <Tag color={STATUS_LABELS[v]?.color}>{STATUS_LABELS[v]?.label || v}</Tag>,
              },
              { title: 'Himoya', dataIndex: 'defense_date' },
              { title: 'Baho', dataIndex: 'defense_grade', render: (v: number) => v && <strong>{v}</strong> },
            ]}
          />
        )}
      </Card>

      <Modal
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        title="Bitiruv ishi qo'shish"
        onOk={() => form.submit()}
        confirmLoading={createM.isPending}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={(v) => createM.mutate(v)}>
          <Form.Item label="Talaba ID" name="student_id" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item label="Rahbar ID (o'qituvchi)" name="supervisor_id" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item label="Mavzu" name="title" rules={[{ required: true }]}>
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item label="Annotatsiya" name="abstract">
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item label="Kalit so'zlar" name="keywords">
            <Input placeholder="vergul bilan ajrating" />
          </Form.Item>
          <Form.Item label="O'quv yili" name="academic_year" initialValue="2024-2025" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
