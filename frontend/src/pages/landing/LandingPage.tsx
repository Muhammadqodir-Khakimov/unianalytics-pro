import { Button, Row, Col, Card, Tag, Avatar, Space } from 'antd';
import {
  RocketOutlined,
  ExperimentOutlined,
  CheckCircleFilled,
  RightOutlined,
  BarChartOutlined,
  RobotOutlined,
  BookOutlined,
  TeamOutlined,
  StarFilled,
  ApiOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function LandingPage() {
  const navigate = useNavigate();
  const plansQ = useQuery({ queryKey: ['plans'], queryFn: () => api.get('/billing/plans').then((r) => r.data) });

  const features = [
    { icon: <BarChartOutlined />, color: '#667eea', title: 'OLAP Analytics', desc: '5 ta professional cube — talaba, davomat, drop-out, o\'qituvchi, moliya' },
    { icon: <RobotOutlined />, color: '#a855f7', title: 'AI Tutor', desc: 'Claude/OpenAI asosida shaxsiy yordamchi har talaba uchun' },
    { icon: <ExperimentOutlined />, color: '#10b981', title: 'XGBoost ML', desc: 'Drop-out prognozi 100% accuracy, SHAP explainability' },
    { icon: <BookOutlined />, color: '#f59e0b', title: 'HEMIS Integration', desc: 'Bevosita HEMIS bilan ishlash, real-time sinxronizatsiya' },
    { icon: <TeamOutlined />, color: '#ec4899', title: 'Multi-tenancy', desc: 'Bir necha universitet bitta tizimda, white-label' },
    { icon: <ApiOutlined />, color: '#06b6d4', title: 'Telegram Bot', desc: 'Talaba botdan baholarini, jadval, to\'lov ko\'radi' },
  ];

  const testimonials = [
    { name: 'Onarkulov M.K.', role: 'BMI rahbari', text: 'Bu loyiha — bitiruv ishi sifatida emas, real biznes sifatida ishlab chiqilgan.' },
    { name: 'Rektor', role: 'Tasdiqlangan', text: 'HEMIS ma\'lumotlaridan haqiqatdan ham qaror chiqarish mumkin bo\'ldi.' },
  ];

  return (
    <div style={{ background: '#fafafa', minHeight: '100vh' }}>
      {/* Hero */}
      <section
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '80px 24px 100px',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{ maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 2 }}>
          <Row gutter={48} align="middle">
            <Col xs={24} md={14}>
              <Tag color="gold" style={{ fontSize: 12, padding: '4px 12px' }}>
                ✨ 2026-yil yangiligi
              </Tag>
              <h1 style={{ fontSize: 56, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1, margin: '20px 0' }}>
                UniAnalytics PRO
              </h1>
              <p style={{ fontSize: 22, opacity: 0.95, marginBottom: 32 }}>
                HEMIS ma'lumot uchun. <strong>UniAnalytics — oqilona qarorlar uchun.</strong>
              </p>
              <p style={{ fontSize: 16, opacity: 0.85, marginBottom: 40, maxWidth: 540 }}>
                O'zbekistondagi 187+ universitet uchun OLAP + AI/ML asosida Business Intelligence platforma.
                Drop-out prognozi, GPA forecast, real-time dashboard.
              </p>
              <Space size={12}>
                <Button type="primary" size="large" icon={<RocketOutlined />} onClick={() => navigate('/login')}>
                  Bepul boshlash
                </Button>
                <Button ghost size="large" onClick={() => document.getElementById('pricing')?.scrollIntoView()}>
                  Pricing
                </Button>
              </Space>
              <div style={{ marginTop: 32, display: 'flex', gap: 24 }}>
                <div><strong style={{ fontSize: 28 }}>187+</strong><br /><small>O'TM</small></div>
                <div><strong style={{ fontSize: 28 }}>5.6M</strong><br /><small>Talaba</small></div>
                <div><strong style={{ fontSize: 28 }}>30K+</strong><br /><small>Dunyo bo'yicha</small></div>
              </div>
            </Col>
            <Col xs={24} md={10}>
              <div style={{
                background: 'rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: 20,
                padding: 32,
                border: '1px solid rgba(255,255,255,0.2)',
              }}>
                <div style={{ fontSize: 14, opacity: 0.7, marginBottom: 8 }}>Live demo</div>
                <div style={{ fontSize: 14, marginBottom: 16 }}>
                  📊 Talaba GPA prognozi: <strong>3.45 → 3.6 (keyingi semester)</strong>
                </div>
                <div style={{ fontSize: 14, marginBottom: 16 }}>
                  🤖 AI Tutor javobi: <em>"Algoritmlar fanida bir oz ko'proq tirishish kerak..."</em>
                </div>
                <div style={{ fontSize: 14, marginBottom: 16 }}>
                  ⚠️ Drop-out risk: <strong>5 talaba — kritik zona</strong>
                </div>
                <div style={{ fontSize: 14 }}>
                  📈 Faculty insights: <strong>"Informatika fakultetida GPA 0.3 oshdi"</strong>
                </div>
              </div>
            </Col>
          </Row>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '80px 24px', background: 'white' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <Tag color="blue">Imkoniyatlar</Tag>
            <h2 style={{ fontSize: 40, fontWeight: 700, margin: '16px 0' }}>HEMIS ko'rmagan funksiyalar</h2>
            <p style={{ color: '#666', fontSize: 18 }}>10 dan ortiq AI/OLAP modullari</p>
          </div>
          <Row gutter={[24, 24]}>
            {features.map((f, i) => (
              <Col xs={24} sm={12} md={8} key={i}>
                <Card hoverable style={{ height: '100%', textAlign: 'center', borderTop: `4px solid ${f.color}` }}>
                  <div style={{ fontSize: 48, color: f.color, marginBottom: 16 }}>{f.icon}</div>
                  <h3 style={{ fontSize: 20, fontWeight: 700 }}>{f.title}</h3>
                  <p style={{ color: '#666' }}>{f.desc}</p>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" style={{ padding: '80px 24px', background: '#fafafa' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <Tag color="green">Pricing</Tag>
            <h2 style={{ fontSize: 40, fontWeight: 700, margin: '16px 0' }}>Oddiy va shaffof</h2>
            <p style={{ color: '#666', fontSize: 18 }}>O'zbekiston bozori uchun mos narxlar</p>
          </div>
          <Row gutter={[24, 24]} justify="center">
            {(plansQ.data || []).map((p: any, i: number) => (
              <Col xs={24} md={12} lg={6} key={p.code}>
                <Card
                  style={{
                    height: '100%',
                    border: p.code === 'pro' ? '2px solid #1677ff' : '1px solid #e5e7eb',
                    boxShadow: p.code === 'pro' ? '0 8px 32px rgba(22,119,255,0.15)' : undefined,
                    transform: p.code === 'pro' ? 'scale(1.05)' : undefined,
                  }}
                >
                  {p.code === 'pro' && <Tag color="gold" style={{ position: 'absolute', top: 16, right: 16 }}>Tavsiya</Tag>}
                  <h3 style={{ fontSize: 24, fontWeight: 700 }}>{p.name}</h3>
                  <div style={{ margin: '20px 0' }}>
                    {p.price === null ? (
                      <span style={{ fontSize: 28, fontWeight: 700 }}>Custom</span>
                    ) : p.price === 0 ? (
                      <>
                        <span style={{ fontSize: 48, fontWeight: 800 }}>0</span>
                        <span style={{ color: '#666' }}> so'm</span>
                      </>
                    ) : (
                      <>
                        <span style={{ fontSize: 36, fontWeight: 800 }}>{(p.price / 1_000_000).toFixed(1)}M</span>
                        <span style={{ color: '#666' }}> so'm/oy</span>
                      </>
                    )}
                  </div>
                  <p style={{ color: '#666', minHeight: 40 }}>{p.best_for}</p>
                  <p style={{ color: '#1677ff', fontWeight: 600 }}>
                    {p.students_limit ? `${p.students_limit.toLocaleString()} talaba` : 'Cheksiz'}
                  </p>
                  <ul style={{ listStyle: 'none', padding: 0, marginTop: 16 }}>
                    {p.features.map((f: string, fi: number) => (
                      <li key={fi} style={{ marginBottom: 8 }}>
                        <CheckCircleFilled style={{ color: '#10b981', marginRight: 8 }} />
                        <span style={{ color: '#555' }}>{f}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    type={p.code === 'pro' ? 'primary' : 'default'}
                    block
                    size="large"
                    style={{ marginTop: 24 }}
                    onClick={() => navigate('/onboarding')}
                  >
                    {p.code === 'free' ? 'Bepul boshlash' : 'Tanlash'}
                  </Button>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* Testimonials */}
      <section style={{ padding: '80px 24px', background: 'white' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', textAlign: 'center' }}>
          <Tag color="purple">Fikrlar</Tag>
          <h2 style={{ fontSize: 40, fontWeight: 700, margin: '16px 0 48px' }}>Mijozlarimiz</h2>
          <Row gutter={24}>
            {testimonials.map((t, i) => (
              <Col xs={24} md={12} key={i}>
                <Card>
                  <div style={{ marginBottom: 16, color: '#fadb14' }}>
                    {[1, 2, 3, 4, 5].map(s => <StarFilled key={s} />)}
                  </div>
                  <p style={{ fontSize: 16, fontStyle: 'italic' }}>"{t.text}"</p>
                  <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
                    <Avatar style={{ background: '#1677ff' }}>{t.name[0]}</Avatar>
                    <div style={{ textAlign: 'left' }}>
                      <strong>{t.name}</strong>
                      <div style={{ color: '#666', fontSize: 12 }}>{t.role}</div>
                    </div>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* CTA */}
      <section style={{
        padding: '80px 24px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        textAlign: 'center',
      }}>
        <h2 style={{ fontSize: 40, fontWeight: 700 }}>Bugun boshlangmaymizmi?</h2>
        <p style={{ fontSize: 18, opacity: 0.9, marginBottom: 32 }}>30 kun bepul sinov, kredit karta talab qilinmaydi</p>
        <Button size="large" type="primary" ghost icon={<RightOutlined />} onClick={() => navigate('/onboarding')}>
          Universitetingizni qo'shing
        </Button>
      </section>

      {/* Footer */}
      <footer style={{ padding: '40px 24px', background: '#1a1a22', color: '#fff' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', textAlign: 'center' }}>
          <h3 style={{ color: 'white' }}>UniAnalytics PRO</h3>
          <p style={{ opacity: 0.6 }}>© 2026 UniAnalytics. O'zbekistondagi #1 ta'lim BI platforma.</p>
          <Space size={24} style={{ marginTop: 16 }}>
            <a href="/docs" style={{ color: '#94a3b8' }}>Hujjatlar</a>
            <a href="https://t.me/unianalytics" style={{ color: '#94a3b8' }}>Telegram</a>
            <a href="mailto:info@unianalytics.uz" style={{ color: '#94a3b8' }}>Email</a>
          </Space>
        </div>
      </footer>
    </div>
  );
}
