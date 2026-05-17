import { Card, List, Avatar, Button, Modal, Form, Input, message, Tag, Badge, Tabs, Empty } from 'antd';
import { MailOutlined, SendOutlined, PlusOutlined, InboxOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { messageService } from '@/services/hemisService';
import { useAuthStore } from '@/store/authStore';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';
import { userService } from '@/services/userService';

export function MessagesPage() {
  const user = useAuthStore((s) => s.user);
  const qc = useQueryClient();
  const [folder, setFolder] = useState<'inbox' | 'sent'>('inbox');
  const [composeOpen, setComposeOpen] = useState(false);
  const [viewMsg, setViewMsg] = useState<any>(null);
  const [form] = Form.useForm();

  const inboxQ = useQuery({
    queryKey: ['messages', 'inbox'],
    queryFn: () => messageService.list('inbox'),
  });
  const sentQ = useQuery({
    queryKey: ['messages', 'sent'],
    queryFn: () => messageService.list('sent'),
  });
  const usersQ = useQuery({ queryKey: ['users-all'], queryFn: userService.list, enabled: composeOpen });

  const sendM = useMutation({
    mutationFn: messageService.send,
    onSuccess: () => {
      message.success('Xabar yuborildi');
      setComposeOpen(false);
      form.resetFields();
      qc.invalidateQueries({ queryKey: ['messages'] });
    },
  });

  const markReadM = useMutation({
    mutationFn: messageService.markRead,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages'] }),
  });

  const items = folder === 'inbox' ? inboxQ.data : sentQ.data;
  const unread = (inboxQ.data || []).filter((m: any) => !m.is_read).length;

  return (
    <div className="olap-page">
      <PageHeader
        title="Xabarlar"
        subtitle="Talaba, o'qituvchi va dekan o'rtasidagi muloqot"
        icon={<MailOutlined />}
        actions={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setComposeOpen(true)}>
            Yangi xabar
          </Button>
        }
      />

      <Card>
        <Tabs
          activeKey={folder}
          onChange={(k) => setFolder(k as any)}
          items={[
            {
              key: 'inbox',
              label: (
                <span>
                  <InboxOutlined /> Inbox <Badge count={unread} size="small" />
                </span>
              ),
            },
            { key: 'sent', label: <span><SendOutlined /> Yuborilganlar</span> },
          ]}
        />

        {!items?.length ? (
          <EmptyState type="no-notifications" title="Xabarlar yo'q" />
        ) : (
          <List
            dataSource={items}
            renderItem={(m: any) => (
              <List.Item
                style={{
                  cursor: 'pointer',
                  padding: 16,
                  background: !m.is_read && folder === 'inbox' ? '#e6f4ff' : 'transparent',
                  borderRadius: 8,
                }}
                onClick={() => {
                  setViewMsg(m);
                  if (folder === 'inbox' && !m.is_read) markReadM.mutate(m.id);
                }}
              >
                <List.Item.Meta
                  avatar={<Avatar style={{ background: '#1677ff' }}>{(folder === 'inbox' ? m.sender_name : m.recipient_name)?.[0] || '?'}</Avatar>}
                  title={
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong>{folder === 'inbox' ? m.sender_name : `→ ${m.recipient_name}`}</strong>
                      {!m.is_read && folder === 'inbox' && <Tag color="blue">Yangi</Tag>}
                    </div>
                  }
                  description={
                    <>
                      <div style={{ fontWeight: 500 }}>{m.subject || '(mavzu yo\'q)'}</div>
                      <div style={{ color: '#666' }}>{m.body.slice(0, 100)}{m.body.length > 100 && '...'}</div>
                      <small style={{ color: '#999' }}>{dayjs(m.sent_at).format('YYYY-MM-DD HH:mm')}</small>
                    </>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* Compose */}
      <Modal
        open={composeOpen}
        onCancel={() => setComposeOpen(false)}
        title="Yangi xabar"
        onOk={() => form.submit()}
        confirmLoading={sendM.isPending}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={(v) => sendM.mutate(v)}>
          <Form.Item label="Kimga" name="recipient_id" rules={[{ required: true }]}>
            <Form.Item noStyle name="recipient_id">
              <Input.Search
                placeholder="User ID kiriting (yoki ro'yxatdan tanlang)"
                style={{ width: '100%' }}
                type="number"
              />
            </Form.Item>
          </Form.Item>
          <Form.Item label="Mavzu" name="subject">
            <Input />
          </Form.Item>
          <Form.Item label="Xabar" name="body" rules={[{ required: true }]}>
            <Input.TextArea rows={6} />
          </Form.Item>
        </Form>
      </Modal>

      {/* View message */}
      <Modal open={!!viewMsg} onCancel={() => setViewMsg(null)} title={viewMsg?.subject} footer={null} width={600}>
        {viewMsg && (
          <div>
            <p><strong>Kimdan:</strong> {viewMsg.sender_name}</p>
            <p><strong>Sana:</strong> {dayjs(viewMsg.sent_at).format('YYYY-MM-DD HH:mm')}</p>
            <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 8, whiteSpace: 'pre-line', marginTop: 16 }}>
              {viewMsg.body}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
