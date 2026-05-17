import { Card, Upload, message, List, Tag, Button, Modal, Form, Input, Select } from 'antd';
import { FileTextOutlined, UploadOutlined, DeleteOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { documentService, uploadService } from '@/services/hemisService';
import { PageHeader } from '@/components/common/PageHeader';
import { EmptyState } from '@/components/common/EmptyState';

const TYPE_LABELS: Record<string, string> = {
  passport: '🪪 Pasport',
  attestat: '📜 Attestat',
  diploma: '🎓 Diplom',
  certificate: '📋 Sertifikat',
  medical: '🏥 Tibbiy ma\'lumotnoma',
  other: '📄 Boshqa',
};

export function DocumentsPage() {
  const qc = useQueryClient();
  const [uploadOpen, setUploadOpen] = useState(false);
  const [form] = Form.useForm();

  const docsQ = useQuery({ queryKey: ['documents', 'my'], queryFn: documentService.my });

  const registerM = useMutation({
    mutationFn: documentService.register,
    onSuccess: () => {
      message.success('Hujjat qo\'shildi');
      setUploadOpen(false);
      form.resetFields();
      qc.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  const deleteM = useMutation({
    mutationFn: documentService.remove,
    onSuccess: () => {
      message.success("O'chirildi");
      qc.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  return (
    <div className="olap-page">
      <PageHeader
        title="Mening hujjatlarim"
        subtitle="Shaxsiy hujjatlar arxivi"
        icon={<FileTextOutlined />}
        actions={
          <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadOpen(true)}>
            Hujjat qo'shish
          </Button>
        }
      />

      <Card>
        {!docsQ.data?.length ? (
          <EmptyState title="Hujjatlar yo'q" description="Yuqori o'ng tugma orqali hujjat qo'shing" />
        ) : (
          <List
            dataSource={docsQ.data}
            renderItem={(d: any) => (
              <List.Item
                actions={[
                  <Button key="view" type="link" onClick={() => window.open(d.file_url, '_blank')}>
                    Ko'rish
                  </Button>,
                  <Button key="del" type="link" danger icon={<DeleteOutlined />} onClick={() => deleteM.mutate(d.id)} />,
                ]}
              >
                <List.Item.Meta
                  title={
                    <div>
                      <strong>{d.title}</strong> {d.is_verified && <Tag color="green">Tasdiqlangan</Tag>}
                    </div>
                  }
                  description={
                    <>
                      <Tag>{TYPE_LABELS[d.document_type] || d.document_type}</Tag>
                      <span style={{ color: '#999' }}>{dayjs(d.uploaded_at).format('YYYY-MM-DD HH:mm')}</span>
                    </>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>

      <Modal
        open={uploadOpen}
        onCancel={() => setUploadOpen(false)}
        title="Hujjat qo'shish"
        onOk={() => form.submit()}
        confirmLoading={registerM.isPending}
      >
        <Form form={form} layout="vertical" onFinish={(v) => registerM.mutate(v)}>
          <Form.Item label="Hujjat turi" name="document_type" rules={[{ required: true }]}>
            <Select
              options={Object.entries(TYPE_LABELS).map(([k, v]) => ({ value: k, label: v }))}
            />
          </Form.Item>
          <Form.Item label="Sarlavha" name="title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Fayl" required>
            <Upload
              maxCount={1}
              beforeUpload={async (file) => {
                try {
                  const res = await uploadService.document(file, 'general');
                  form.setFieldValue('file_url', res.url);
                  message.success(`${file.name} yuklandi`);
                } catch (e) {
                  message.error('Yuklashda xato');
                }
                return false;
              }}
            >
              <Button icon={<UploadOutlined />}>Tanlash</Button>
            </Upload>
          </Form.Item>
          <Form.Item name="file_url" hidden>
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
