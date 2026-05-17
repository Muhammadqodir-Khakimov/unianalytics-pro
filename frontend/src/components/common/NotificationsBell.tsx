import { Badge, Dropdown, Button, List, Empty, Tag, Tooltip } from 'antd';
import { BellOutlined, CheckCircleOutlined, WarningOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { notificationService } from '@/services/notificationService';
import dayjs from 'dayjs';

const TYPE_ICONS: Record<string, any> = {
  success: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  warning: <WarningOutlined style={{ color: '#fa8c16' }} />,
  error: <WarningOutlined style={{ color: '#ff4d4f' }} />,
  info: <InfoCircleOutlined style={{ color: '#1677ff' }} />,
};

export function NotificationsBell() {
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationService.list(false, 20),
    refetchInterval: 30000,
  });

  const markReadM = useMutation({
    mutationFn: (id: number) => notificationService.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const markAllM = useMutation({
    mutationFn: notificationService.markAllRead,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const items = data?.items || [];
  const unread = data?.total_unread || 0;

  const dropdown = (
    <div style={{ width: 400, maxHeight: 500, overflow: 'auto', background: '#fff', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', borderRadius: 8 }}>
      <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f0f0f0' }}>
        <strong>Xabarlar ({unread} o'qilmagan)</strong>
        {unread > 0 && (
          <Button size="small" type="link" onClick={() => markAllM.mutate()}>
            Hammasini o'qilgan deb belgilash
          </Button>
        )}
      </div>
      {items.length === 0 ? (
        <Empty description="Xabarlar yo'q" style={{ padding: 24 }} />
      ) : (
        <List
          dataSource={items}
          renderItem={(n: any) => (
            <List.Item
              style={{ padding: '12px 16px', cursor: 'pointer', background: n.is_read ? 'transparent' : '#e6f4ff' }}
              onClick={() => {
                if (!n.is_read) markReadM.mutate(n.id);
                if (n.link) navigate(n.link);
              }}
            >
              <List.Item.Meta
                avatar={TYPE_ICONS[n.type] || TYPE_ICONS.info}
                title={
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{n.title}</span>
                    {!n.is_read && <Tag color="blue">Yangi</Tag>}
                  </div>
                }
                description={
                  <>
                    <div style={{ color: '#444' }}>{n.message}</div>
                    <small style={{ color: '#999' }}>{dayjs(n.created_at).format('YYYY-MM-DD HH:mm')}</small>
                  </>
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  );

  return (
    <Dropdown popupRender={() => dropdown} placement="bottomRight" trigger={['click']}>
      <Tooltip title="Xabarlar">
        <Badge count={unread} size="small">
          <Button shape="circle" icon={<BellOutlined />} />
        </Badge>
      </Tooltip>
    </Dropdown>
  );
}
