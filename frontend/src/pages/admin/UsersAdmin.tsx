import { Card, Table, Tag, Button, Select, Switch, Modal, Form, Input, message, Space } from 'antd';
import { LinkOutlined, UserOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '@/services/userService';

export function UsersAdmin() {
  const [linkOpen, setLinkOpen] = useState(false);
  const [linkForm] = Form.useForm();
  const qc = useQueryClient();

  const usersQ = useQuery({ queryKey: ['admin', 'users'], queryFn: userService.list });
  const unlinkedQ = useQuery({
    queryKey: ['admin', 'unlinked'],
    queryFn: () => userService['list'].name && fetch('/api/v1/users/unlinked', {
      headers: { Authorization: `Bearer ${JSON.parse(localStorage.getItem('auth-storage') || '{}')?.state?.accessToken}` },
    }).then((r) => r.json()),
  });

  const roleM = useMutation({
    mutationFn: ({ id, role }: any) => userService.changeRole(id, role),
    onSuccess: () => {
      message.success('Rol o\'zgartirildi');
      qc.invalidateQueries({ queryKey: ['admin'] });
    },
  });

  const activeM = useMutation({
    mutationFn: ({ id, is_active }: any) => userService.toggleActive(id, is_active),
    onSuccess: () => {
      message.success('Holat o\'zgartirildi');
      qc.invalidateQueries({ queryKey: ['admin'] });
    },
  });

  return (
    <div className="olap-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>
          <UserOutlined /> Foydalanuvchilar boshqaruvi
        </h1>
        <Button type="primary" icon={<LinkOutlined />} onClick={() => setLinkOpen(true)}>
          User ni talaba/o'qituvchi bilan bog'lash
        </Button>
      </div>

      <Card>
        <Table
          dataSource={usersQ.data || []}
          rowKey="id"
          loading={usersQ.isLoading}
          columns={[
            { title: 'ID', dataIndex: 'id', width: 60 },
            { title: 'Username', dataIndex: 'username' },
            { title: 'F.I.Sh.', dataIndex: 'full_name' },
            { title: 'Email', dataIndex: 'email' },
            {
              title: 'Rol',
              dataIndex: 'role',
              render: (v: string, r: any) => (
                <Select
                  value={v}
                  onChange={(role) => roleM.mutate({ id: r.id, role })}
                  size="small"
                  style={{ width: 120 }}
                  options={[
                    { value: 'admin', label: 'Admin' },
                    { value: 'dekan', label: 'Dekan' },
                    { value: 'teacher', label: "O'qituvchi" },
                    { value: 'student', label: 'Talaba' },
                  ]}
                />
              ),
            },
            {
              title: 'Faol',
              dataIndex: 'is_active',
              render: (v: boolean, r: any) => (
                <Switch
                  checked={v}
                  onChange={(checked) => activeM.mutate({ id: r.id, is_active: checked })}
                />
              ),
            },
            {
              title: 'Tasdiqlangan',
              dataIndex: 'is_verified',
              render: (v: boolean) => (v ? <Tag color="green">Ha</Tag> : <Tag>Yo'q</Tag>),
            },
          ]}
        />
      </Card>

      <Modal
        open={linkOpen}
        onCancel={() => setLinkOpen(false)}
        title="User ni real hisob bilan bog'lash"
        footer={null}
        width={600}
      >
        <p style={{ color: '#666' }}>
          Bu yerda user hisobini real talaba yoki o'qituvchi bilan bog'lash mumkin.
        </p>
        <p>
          <strong>Bog'lanmaganlar:</strong>
        </p>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Card size="small" title="Bog'lanmagan user lar">
            {(unlinkedQ.data?.free_users || []).map((u: any) => (
              <Tag key={u.id} color="blue" style={{ margin: 4 }}>
                {u.username} ({u.role})
              </Tag>
            ))}
          </Card>
          <Card size="small" title="Bog'lanmagan talabalar (top 50)">
            {(unlinkedQ.data?.unlinked_students || []).slice(0, 10).map((s: any) => (
              <Tag key={s.id} style={{ margin: 4 }}>
                {s.student_id}: {s.full_name}
              </Tag>
            ))}
          </Card>
        </Space>
      </Modal>
    </div>
  );
}
