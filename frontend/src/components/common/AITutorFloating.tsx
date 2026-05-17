import { Button, Drawer, Input, Avatar, Spin, message, Badge, Tag } from 'antd';
import { RobotOutlined, SendOutlined, CloseOutlined, MessageOutlined, UserOutlined } from '@ant-design/icons';
import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { mlService } from '@/services/mlService';
import { useAuthStore } from '@/store/authStore';

/**
 * Sitewide AI Tutor floating widget.
 * Har sahifaning pastki o'ng burchagida button.
 */
export function AITutorFloating() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([
    { role: 'assistant', content: 'Salom! Men AI tutoringizman. Sahifani tark etmasdan savol bering 🚀' },
  ]);
  const [input, setInput] = useState('');
  const listRef = useRef<HTMLDivElement>(null);
  const user = useAuthStore((s) => s.user);

  // Only show for authenticated users
  if (!user) return null;

  const chatM = useMutation({
    mutationFn: ({ msg, history }: any) => mlService.tutorChat(msg, history),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response, provider: data.provider }]);
    },
    onError: () => message.error('AI bilan bog\'lanishda xato'),
  });

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const send = () => {
    if (!input.trim()) return;
    const history = messages.slice(1).map(({ role, content }) => ({ role, content }));
    setMessages((prev) => [...prev, { role: 'user', content: input }]);
    chatM.mutate({ msg: input, history });
    setInput('');
  };

  return (
    <>
      <div
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 999,
        }}
      >
        <Badge dot color="green">
          <Button
            type="primary"
            shape="circle"
            size="large"
            icon={<RobotOutlined style={{ fontSize: 24 }} />}
            onClick={() => setOpen(true)}
            style={{
              width: 60,
              height: 60,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              boxShadow: '0 4px 20px rgba(118, 75, 162, 0.4)',
              animation: 'float 3s ease-in-out infinite',
            }}
          />
        </Badge>
      </div>

      <Drawer
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Avatar icon={<RobotOutlined />} style={{ background: '#722ed1' }} />
            <span>AI Tutor</span>
            <Tag color="purple">Beta</Tag>
          </div>
        }
        open={open}
        onClose={() => setOpen(false)}
        width={420}
        styles={{ body: { padding: 0, display: 'flex', flexDirection: 'column', height: '100%' } }}
      >
        <div
          ref={listRef}
          style={{ flex: 1, overflowY: 'auto', padding: 16, background: '#f5f7fa' }}
        >
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                gap: 8,
                marginBottom: 12,
                flexDirection: m.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <Avatar
                size="small"
                icon={m.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                style={{ background: m.role === 'user' ? '#1677ff' : '#722ed1', flexShrink: 0 }}
              />
              <div
                style={{
                  background: m.role === 'user' ? '#1677ff' : '#fff',
                  color: m.role === 'user' ? '#fff' : '#000',
                  padding: '8px 12px',
                  borderRadius: 8,
                  maxWidth: '80%',
                  fontSize: 13,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {m.content}
              </div>
            </div>
          ))}
          {chatM.isPending && (
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
              <Avatar size="small" icon={<RobotOutlined />} style={{ background: '#722ed1' }} />
              <div style={{ background: '#fff', padding: '8px 12px', borderRadius: 8 }}>
                <Spin size="small" />
              </div>
            </div>
          )}
        </div>

        <div style={{ padding: 12, borderTop: '1px solid #eee', background: '#fff' }}>
          <div style={{ display: 'flex', gap: 6 }}>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={send}
              placeholder="Savol..."
              disabled={chatM.isPending}
            />
            <Button type="primary" icon={<SendOutlined />} onClick={send} loading={chatM.isPending} />
          </div>
          <div style={{ fontSize: 10, color: '#999', marginTop: 4, textAlign: 'center' }}>
            Sizning ma'lumotlaringizdan foydalanib javob beradi
          </div>
        </div>
      </Drawer>
    </>
  );
}
