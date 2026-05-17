import { Card, Tag, Button, Modal, Form, Input, Select, Switch, message, Empty } from 'antd';
import { NotificationOutlined, PlusOutlined, PushpinFilled } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { announcementService } from '@/services/hemisService';
import { useAuthStore } from '@/store/authStore';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';
import { StaggerChildren, StaggerItem } from '@/components/common/PageTransition';

export function AnnouncementsPage() {
  const user = useAuthStore((s) => s.user);
  const isDean = user?.role === 'dekan' || user?.role === 'admin';
  const qc = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const annQ = useQuery({ queryKey: ['announcements'], queryFn: () => announcementService.list({ limit: 50 }) });

  const createM = useMutation({
    mutationFn: announcementService.create,
    onSuccess: () => {
      message.success("E'lon yaratildi");
      setModalOpen(false);
      form.resetFields();
      qc.invalidateQueries({ queryKey: ['announcements'] });
    },
  });

  const deleteM = useMutation({
    mutationFn: announcementService.remove,
    onSuccess: () => {
      message.success("O'chirildi");
      qc.invalidateQueries({ queryKey: ['announcements'] });
    },
  });

  const priorityColor = (p: string) => (p === 'urgent' ? 'red' : p === 'high' ? 'orange' : 'blue');
  const priorityIcon = (p: string) => (p === 'urgent' ? '🚨' : p === 'high' ? '⚠️' : '📢');

  return (
    <div className="olap-page">
      <PageHeader
        title="E'lonlar"
        subtitle="Universitet va fakultet xabarlari"
        icon={<NotificationOutlined />}
        actions={
          isDean && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
              Yangi e'lon
            </Button>
          )
        }
      />

      {annQ.isLoading ? (
        <Card><div className="skeleton-shimmer" style={{ height: 200 }} /></Card>
      ) : annQ.data?.length === 0 ? (
        <EmptyState title="E'lonlar yo'q" description="Hozircha yangi e'lonlar mavjud emas" />
      ) : (
        <StaggerChildren>
          {(annQ.data || []).map((ann: any) => (
            <StaggerItem key={ann.id}>
              <Card
                style={{
                  marginBottom: 12,
                  borderLeft: `4px solid ${
                    ann.priority === 'urgent' ? '#ef4444' : ann.priority === 'high' ? '#f59e0b' : '#3b82f6'
                  }`,
                }}
                title={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {ann.is_pinned && <PushpinFilled style={{ color: '#f59e0b' }} />}
                    <span style={{ fontSize: 20 }}>{priorityIcon(ann.priority)}</span>
                    <strong>{ann.title}</strong>
                  </div>
                }
                extra={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Tag color={priorityColor(ann.priority)}>{ann.priority}</Tag>
                    <Tag>{ann.audience}</Tag>
                    {isDean && (
                      <Button size="small" danger onClick={() => deleteM.mutate(ann.id)}>
                        O'chirish
                      </Button>
                    )}
                  </div>
                }
              >
                <div style={{ whiteSpace: 'pre-line', marginBottom: 8 }}>{ann.body}</div>
                {ann.image_url && (
                  <img src={ann.image_url} alt="" style={{ maxWidth: '100%', borderRadius: 8 }} />
                )}
                <div style={{ color: '#999', fontSize: 12, marginTop: 8 }}>
                  {dayjs(ann.published_at).format('YYYY-MM-DD HH:mm')}
                </div>
              </Card>
            </StaggerItem>
          ))}
        </StaggerChildren>
      )}

      <Modal
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        title="Yangi e'lon"
        onOk={() => form.submit()}
        confirmLoading={createM.isPending}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={(v) => createM.mutate(v)}>
          <Form.Item label="Sarlavha" name="title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Matn" name="body" rules={[{ required: true }]}>
            <Input.TextArea rows={5} />
          </Form.Item>
          <Form.Item label="Kim uchun" name="audience" initialValue="all">
            <Select options={[
              { value: 'all', label: 'Hammaga' },
              { value: 'students', label: 'Talabalar' },
              { value: 'teachers', label: "O'qituvchilar" },
            ]} />
          </Form.Item>
          <Form.Item label="Prioritet" name="priority" initialValue="normal">
            <Select options={[
              { value: 'normal', label: 'Oddiy' },
              { value: 'high', label: 'Yuqori' },
              { value: 'urgent', label: 'Shoshilinch' },
            ]} />
          </Form.Item>
          <Form.Item label="Pin qilingan" name="is_pinned" valuePropName="checked" initialValue={false}>
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
