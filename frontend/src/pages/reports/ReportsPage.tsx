import { Card, Row, Col, Button, message, Tag, Space } from 'antd';
import { FilePdfOutlined, FileExcelOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { reportService } from '@/services/reportService';

export function ReportsPage() {
  const { t } = useTranslation();
  const templatesQ = useQuery({ queryKey: ['reports', 'templates'], queryFn: reportService.listTemplates });

  const generateM = useMutation({
    mutationFn: reportService.generate,
    onSuccess: () => message.success('Hisobot yuklandi'),
    onError: () => message.error('Hisobot generatsiyasida xato'),
  });

  return (
    <div className="olap-page">
      <h1>{t('menu.reports')}</h1>

      <Row gutter={[16, 16]}>
        {(templatesQ.data || []).map((tpl: any) => (
          <Col xs={24} md={12} lg={8} key={tpl.name}>
            <Card title={tpl.title} bordered>
              <p>{tpl.description}</p>
              <div style={{ marginBottom: 12 }}>
                {tpl.query.dimensions?.map((d: any, i: number) => (
                  <Tag key={i} color="blue">
                    {d.dimension}.{d.attribute}
                  </Tag>
                ))}
              </div>
              <div style={{ marginBottom: 12 }}>
                {tpl.query.measures?.map((m: string) => (
                  <Tag key={m} color="green">
                    {m}
                  </Tag>
                ))}
              </div>
              <Space>
                <Button
                  icon={<FileExcelOutlined />}
                  loading={generateM.isPending}
                  onClick={() =>
                    generateM.mutate({
                      title: tpl.title,
                      format: 'excel',
                      query: tpl.query,
                    })
                  }
                >
                  Excel
                </Button>
                <Button
                  icon={<FilePdfOutlined />}
                  loading={generateM.isPending}
                  onClick={() =>
                    generateM.mutate({
                      title: tpl.title,
                      format: 'pdf',
                      query: tpl.query,
                    })
                  }
                >
                  PDF
                </Button>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
