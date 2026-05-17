import { Card, Table, Tag, Input, Row, Col, Statistic } from 'antd';
import { AuditOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { auditService } from '@/services/notificationService';

export function AuditPage() {
  const [filters, setFilters] = useState<any>({});

  const logsQ = useQuery({
    queryKey: ['audit', 'logs', filters],
    queryFn: () => auditService.list(filters),
  });

  const statsQ = useQuery({ queryKey: ['audit', 'stats'], queryFn: auditService.stats });

  return (
    <div className="olap-page">
      <h1>
        <AuditOutlined /> Audit log
      </h1>
      <p style={{ color: '#666' }}>Tizimda kim qachon nima o'zgartirgan — barchasi qayd qilinadi.</p>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="Jami yozuvlar" value={statsQ.data?.total || 0} />
          </Card>
        </Col>
        <Col xs={24} md={16}>
          <Card title="Eng faol foydalanuvchilar">
            {Object.entries(statsQ.data?.by_user || {}).map(([u, c]: any) => (
              <Tag key={u} color="blue" style={{ margin: 4 }}>
                {u}: {c}
              </Tag>
            ))}
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <Row gutter={8} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Input
              placeholder="Filter: resource_type"
              onChange={(e) => setFilters({ ...filters, resource_type: e.target.value || undefined })}
            />
          </Col>
          <Col span={6}>
            <Input
              placeholder="Filter: action"
              onChange={(e) => setFilters({ ...filters, action: e.target.value || undefined })}
            />
          </Col>
        </Row>
        <Table
          dataSource={logsQ.data?.items}
          rowKey="id"
          loading={logsQ.isLoading}
          pagination={{ total: logsQ.data?.total, pageSize: 50 }}
          size="small"
          columns={[
            { title: 'Vaqt', dataIndex: 'created_at', render: (v: string) => dayjs(v).format('YYYY-MM-DD HH:mm'), width: 150 },
            { title: 'User', dataIndex: 'username', width: 100 },
            { title: 'Rol', dataIndex: 'user_role', render: (v: string) => <Tag>{v}</Tag>, width: 80 },
            {
              title: 'Amal',
              dataIndex: 'action',
              render: (v: string) => (
                <Tag color={v === 'DELETE' ? 'red' : v === 'CREATE' ? 'green' : 'blue'}>{v}</Tag>
              ),
            },
            { title: 'Resurs', dataIndex: 'resource_type' },
            { title: 'ID', dataIndex: 'resource_id', width: 80 },
            { title: 'Tavsif', dataIndex: 'description' },
            { title: 'IP', dataIndex: 'ip_address', width: 110 },
          ]}
        />
      </Card>
    </div>
  );
}
