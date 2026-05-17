import { Card, Input, Button, Avatar, Spin, message, Tag, Space, Alert } from 'antd';
import {
  RobotOutlined,
  UserOutlined,
  SendOutlined,
  ExperimentOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { mlService } from '@/services/mlService';
import { PageHeader } from '@/components/common/PageHeader';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  provider?: string;
}

const SUGGESTIONS = [
  'Mening eng kuchsiz fanim qaysi?',
  'GPA ni qanday oshiraman?',
  'Stipendiya olish uchun nima kerak?',
  'Davomatim qancha?',
  'Kelgusi semestr qaysi fanlarni olsam yaxshi?',
];

export function AITutorPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Salom! Men sizning AI tutoringizman. Akademik savollaringizga javob beraman. Quyidagi tavsiyalardan tanlang yoki o\'zingiz yozing.',
    },
  ]);
  const [input, setInput] = useState('');
  const listRef = useRef<HTMLDivElement>(null);

  const chatM = useMutation({
    mutationFn: ({ msg, history }: any) => mlService.tutorChat(msg, history),
    onSuccess: (data, vars) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response, provider: data.provider },
      ]);
    },
    onError: () => message.error('AI bilan bog\'lanishda xato'),
  });

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const send = (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg) return;
    const history = messages.slice(1).map(({ role, content }) => ({ role, content }));
    setMessages((prev) => [...prev, { role: 'user', content: msg }]);
    setInput('');
    chatM.mutate({ msg, history });
  };

  return (
    <div className="olap-page">
      <PageHeader
        title="AI Tutor"
        subtitle="Sun'iy intellekt asosida shaxsiy akademik yordamchi"
        icon={<RobotOutlined />}
        actions={
          <Button
            icon={<ClearOutlined />}
            onClick={() => setMessages([{ role: 'assistant', content: 'Yangi suhbat boshlandi. Savol bering.' }])}
          >
            Suhbatni tozalash
          </Button>
        }
      />

      <Alert
        type="info"
        message="AI Tutor"
        description="Sizning akademik ma'lumotlaringizni bilgan holda javob beradi (GPA, baholar, davomat). Demo rejimda ishlayapti — real Claude/OpenAI API uchun ANTHROPIC_API_KEY o'rnating."
        showIcon
        icon={<ExperimentOutlined />}
        style={{ marginBottom: 16, borderRadius: 12 }}
      />

      <Card styles={{ body: { padding: 0 } }}>
        <div
          ref={listRef}
          style={{ height: '60vh', overflowY: 'auto', padding: 24, background: '#f5f7fa' }}
        >
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: 12,
                marginBottom: 16,
                flexDirection: m.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <Avatar
                icon={m.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                style={{ background: m.role === 'user' ? '#1677ff' : '#722ed1', flexShrink: 0 }}
              />
              <div
                style={{
                  background: m.role === 'user' ? '#1677ff' : '#fff',
                  color: m.role === 'user' ? '#fff' : '#000',
                  padding: '12px 16px',
                  borderRadius: 12,
                  maxWidth: '70%',
                  whiteSpace: 'pre-wrap',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.06)',
                }}
              >
                {m.content}
                {m.provider && (
                  <div style={{ marginTop: 6, fontSize: 11, opacity: 0.7 }}>
                    <Tag>{m.provider}</Tag>
                  </div>
                )}
              </div>
            </div>
          ))}
          {chatM.isPending && (
            <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
              <Avatar icon={<RobotOutlined />} style={{ background: '#722ed1' }} />
              <div style={{ background: '#fff', padding: '12px 16px', borderRadius: 12 }}>
                <Spin size="small" /> AI o'ylayapti...
              </div>
            </div>
          )}
        </div>

        {messages.length <= 2 && (
          <div style={{ padding: '0 24px 12px', background: '#f5f7fa' }}>
            <small style={{ color: '#666' }}>Tavsiyalar:</small>
            <Space wrap style={{ marginTop: 8 }}>
              {SUGGESTIONS.map((s, i) => (
                <Button key={i} size="small" onClick={() => send(s)}>
                  {s}
                </Button>
              ))}
            </Space>
          </div>
        )}

        <div style={{ padding: 16, display: 'flex', gap: 8, background: '#fff', borderTop: '1px solid #eee' }}>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={() => send()}
            placeholder="AI ga savol bering..."
            size="large"
            disabled={chatM.isPending}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={() => send()}
            loading={chatM.isPending}
            size="large"
          >
            Yuborish
          </Button>
        </div>
      </Card>
    </div>
  );
}
