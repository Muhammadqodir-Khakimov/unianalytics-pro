import { Card, Row, Col, Input, Select, Tag, Button, message, Modal, Empty, Table } from 'antd';
import { BookOutlined, SearchOutlined, ReadOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { libraryService } from '@/services/hemisService';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';
import { useAuthStore } from '@/store/authStore';

export function LibraryPage() {
  const currentUserId = useAuthStore((s) => s.user?.id ?? 1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string | undefined>();
  const [availableOnly, setAvailableOnly] = useState(false);
  const [loanOpen, setLoanOpen] = useState<any>(null);
  const qc = useQueryClient();

  const booksQ = useQuery({
    queryKey: ['library', 'books', { search, category, availableOnly }],
    queryFn: () => libraryService.listBooks({ search, category, available_only: availableOnly, page_size: 30 }),
  });

  const myLoansQ = useQuery({ queryKey: ['library', 'my-loans'], queryFn: libraryService.myLoans });

  const loanM = useMutation({
    mutationFn: libraryService.loanBook,
    onSuccess: () => {
      message.success('Kitob ijaraga olindi');
      setLoanOpen(null);
      qc.invalidateQueries({ queryKey: ['library'] });
    },
  });

  return (
    <div className="olap-page">
      <PageHeader title="Kutubxona" subtitle="Kitoblar katalogi va shaxsiy ijara" icon={<BookOutlined />} />

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col flex="auto">
          <Input
            prefix={<SearchOutlined />}
            placeholder="Kitob nomi yoki muallifi..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
            size="large"
          />
        </Col>
        <Col>
          <Select
            placeholder="Kategoriya"
            value={category}
            onChange={setCategory}
            allowClear
            style={{ width: 180 }}
            size="large"
            options={[
              { value: 'textbook', label: 'Darslik' },
              { value: 'scientific', label: 'Ilmiy' },
              { value: 'fiction', label: 'Badiiy' },
              { value: 'reference', label: "Ma'lumotnoma" },
              { value: 'journal', label: 'Jurnal' },
            ]}
          />
        </Col>
        <Col>
          <Button
            type={availableOnly ? 'primary' : 'default'}
            size="large"
            onClick={() => setAvailableOnly(!availableOnly)}
          >
            Faqat mavjud
          </Button>
        </Col>
      </Row>

      {myLoansQ.data?.length > 0 && (
        <Card title={<><ReadOutlined /> Mening ijara olgan kitoblarim</>} style={{ marginBottom: 16 }}>
          <Table
            size="small"
            dataSource={myLoansQ.data}
            rowKey="id"
            pagination={false}
            columns={[
              { title: 'Kitob', dataIndex: 'book_title' },
              { title: 'Olgan sana', dataIndex: 'loan_date' },
              {
                title: 'Qaytarish muddati',
                dataIndex: 'due_date',
                render: (v: string) => {
                  const overdue = dayjs(v).isBefore(dayjs(), 'day');
                  return <Tag color={overdue ? 'red' : 'green'}>{v}</Tag>;
                },
              },
              { title: 'Holat', dataIndex: 'status', render: (v: string) => <Tag>{v}</Tag> },
            ]}
          />
        </Card>
      )}

      {booksQ.data?.items?.length === 0 ? (
        <Card><EmptyState type="no-results" title="Kitob topilmadi" description="Boshqa kalit so'z bilan qidiring" /></Card>
      ) : (
        <Row gutter={[16, 16]}>
          {(booksQ.data?.items || []).map((b: any) => (
            <Col xs={24} sm={12} md={8} lg={6} key={b.id}>
              <Card
                hoverable
                cover={
                  b.cover_url ? (
                    <img src={b.cover_url} alt={b.title} style={{ height: 200, objectFit: 'cover' }} />
                  ) : (
                    <div style={{
                      height: 200,
                      background: 'linear-gradient(135deg, #667eea, #764ba2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: 48,
                    }}>📚</div>
                  )
                }
                actions={[
                  b.available_copies > 0 ? (
                    <Button type="primary" onClick={() => setLoanOpen(b)} key="loan">
                      Ijaraga olish
                    </Button>
                  ) : (
                    <Tag color="red" key="x">Mavjud emas</Tag>
                  ),
                ]}
              >
                <Card.Meta
                  title={<div style={{ fontSize: 14, fontWeight: 600 }}>{b.title}</div>}
                  description={
                    <>
                      <div style={{ color: '#666' }}>{b.author}</div>
                      <div style={{ marginTop: 8 }}>
                        <Tag color="blue">{b.category}</Tag>
                        <Tag>{b.available_copies}/{b.total_copies}</Tag>
                      </div>
                    </>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal
        open={!!loanOpen}
        onCancel={() => setLoanOpen(null)}
        title="Kitobni ijaraga olish"
        onOk={() =>
          loanM.mutate({
            book_id: loanOpen.id,
            student_id: currentUserId,
            days: 14,
          })
        }
        confirmLoading={loanM.isPending}
      >
        {loanOpen && (
          <>
            <p><strong>{loanOpen.title}</strong> — {loanOpen.author}</p>
            <p>Standart muddat: 14 kun</p>
          </>
        )}
      </Modal>
    </div>
  );
}
