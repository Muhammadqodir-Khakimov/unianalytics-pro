import { Table, Button, Space, Popconfirm, Modal, Form, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useState, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

interface CrudTableProps<T> {
  resource: string;
  service: {
    list: (params?: any) => Promise<{ items: T[]; total: number; page: number; page_size: number }>;
    create: (payload: any) => Promise<T>;
    update: (id: number, payload: any) => Promise<T>;
    remove: (id: number) => Promise<any>;
  };
  columns: any[];
  FormFields: ReactNode | ((form: any) => ReactNode);
  rowKey?: string;
  initialValues?: any;
  canEdit?: boolean;
  title?: string;
}

export function CrudTable<T extends { id: number }>({
  resource,
  service,
  columns,
  FormFields,
  rowKey = 'id',
  initialValues = {},
  canEdit = true,
  title,
}: CrudTableProps<T>) {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<T | null>(null);
  const [form] = Form.useForm();
  const qc = useQueryClient();

  const listQ = useQuery({
    queryKey: [resource, 'list', page, pageSize],
    queryFn: () => service.list({ page, page_size: pageSize }),
  });

  const createM = useMutation({
    mutationFn: service.create,
    onSuccess: () => {
      message.success("Yaratildi");
      qc.invalidateQueries({ queryKey: [resource] });
      setModalOpen(false);
      form.resetFields();
    },
  });

  const updateM = useMutation({
    mutationFn: ({ id, payload }: any) => service.update(id, payload),
    onSuccess: () => {
      message.success("Yangilandi");
      qc.invalidateQueries({ queryKey: [resource] });
      setModalOpen(false);
      setEditing(null);
      form.resetFields();
    },
  });

  const deleteM = useMutation({
    mutationFn: service.remove,
    onSuccess: () => {
      message.success("O'chirildi");
      qc.invalidateQueries({ queryKey: [resource] });
    },
  });

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    form.setFieldsValue(initialValues);
    setModalOpen(true);
  };

  const openEdit = (record: T) => {
    setEditing(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const handleSubmit = (values: any) => {
    if (editing) {
      updateM.mutate({ id: editing.id, payload: values });
    } else {
      createM.mutate(values);
    }
  };

  const actionColumn = canEdit
    ? [
        {
          title: t('common.actions'),
          width: 140,
          fixed: 'right' as const,
          render: (_: any, record: T) => (
            <Space>
              <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
              <Popconfirm
                title="O'chirishni tasdiqlaysizmi?"
                onConfirm={() => deleteM.mutate(record.id)}
              >
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </Space>
          ),
        },
      ]
    : [];

  return (
    <div className="olap-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h1>{title || resource}</h1>
        {canEdit && (
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            {t('common.create')}
          </Button>
        )}
      </div>

      <Table
        loading={listQ.isLoading}
        rowKey={rowKey}
        dataSource={listQ.data?.items || []}
        columns={[...columns, ...actionColumn]}
        scroll={{ x: 'max-content' }}
        pagination={{
          current: page,
          pageSize,
          total: listQ.data?.total,
          showSizeChanger: true,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
        }}
      />

      <Modal
        open={modalOpen}
        title={editing ? t('common.edit') : t('common.create')}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={createM.isPending || updateM.isPending}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          {typeof FormFields === 'function' ? FormFields(form) : FormFields}
        </Form>
      </Modal>
    </div>
  );
}
