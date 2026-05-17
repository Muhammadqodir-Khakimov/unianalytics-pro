import { useState, useEffect } from 'react';
import { Modal, Button, Steps } from 'antd';
import {
  RocketOutlined,
  DashboardOutlined,
  ExperimentOutlined,
  SearchOutlined,
  BellOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/store/authStore';

const ONBOARDING_KEY = 'onboarding-completed';

export function OnboardingTour() {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    if (user && !localStorage.getItem(ONBOARDING_KEY)) {
      const timer = setTimeout(() => setOpen(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [user]);

  const steps = [
    {
      title: 'Xush kelibsiz!',
      icon: <RocketOutlined />,
      content: (
        <div style={{ textAlign: 'center', padding: 24 }}>
          <div style={{ fontSize: 64, marginBottom: 16 }}>🎓</div>
          <h2 style={{ marginBottom: 12 }}>Student Rating OLAP ga xush kelibsiz!</h2>
          <p style={{ color: '#666', fontSize: 15, lineHeight: 1.6 }}>
            Bu — talabalar reyting tizimini boshqarish va OLAP tahlil qilish uchun zamonaviy platforma.
            Sizning roli{user?.role === 'student' ? 'ngiz' : 'ngiz'} <strong>{user?.role}</strong>.
          </p>
        </div>
      ),
    },
    {
      title: 'Dashboard',
      icon: <DashboardOutlined />,
      content: (
        <div style={{ padding: 24 }}>
          <h3>📊 Boshqaruv paneli</h3>
          <p>Dashboard sahifasida sizning roli{user?.role === 'student' ? 'ngiz' : 'ngiz'}ga moslangan ma'lumotlar:</p>
          <ul style={{ lineHeight: 1.8 }}>
            {user?.role === 'student' && (
              <>
                <li>O'z GPA va o'rtacha ballingiz</li>
                <li>Guruh ichidagi reytingingiz</li>
                <li>Fanlar bo'yicha natijalar</li>
                <li>AI prognoz va tavsiyalar</li>
              </>
            )}
            {user?.role === 'teacher' && (
              <>
                <li>O'z fanlaringiz bo'yicha statistika</li>
                <li>Talabalar ro'yxati</li>
                <li>So'nggi kiritgan baholar</li>
              </>
            )}
            {(user?.role === 'admin' || user?.role === 'dekan') && (
              <>
                <li>Umumiy tizim ko'rsatkichlari</li>
                <li>Fakultetlar bo'yicha solishtirma</li>
                <li>Eng yaxshi talabalar</li>
                <li>OLAP tahlil va AI insights</li>
              </>
            )}
          </ul>
        </div>
      ),
    },
    {
      title: 'OLAP tahlil',
      icon: <ExperimentOutlined />,
      content: (
        <div style={{ padding: 24 }}>
          <h3>🔬 OLAP Cube va AI</h3>
          <p>Tizimning eng kuchli imkoniyatlari:</p>
          <ul style={{ lineHeight: 1.8 }}>
            <li><strong>Cube Explorer</strong> — ko'p o'lchovli tahlil (drill-down/roll-up)</li>
            <li><strong>Pivot Table</strong> — qator/ustun matritsasi</li>
            <li><strong>AI Analitika</strong> — talaba GPA prognozi, xavf zonasi</li>
            <li><strong>Tavsiyalar</strong> — sun'iy intellekt asosida</li>
          </ul>
        </div>
      ),
    },
    {
      title: 'Tezkor qidiruv',
      icon: <SearchOutlined />,
      content: (
        <div style={{ padding: 24 }}>
          <h3>🔎 Global qidiruv</h3>
          <p>
            Sahifa yuqorisidagi qidiruv yoki <kbd>Ctrl+K</kbd> (yoki <kbd>⌘K</kbd>) bosib
            tezda istalgan talaba, o'qituvchi, fan yoki sahifani toping.
          </p>
          <div style={{ background: '#f5f5f5', padding: 12, borderRadius: 8, marginTop: 12 }}>
            <code>Ctrl+K</code> — buyruq paneli (Command Palette)
          </div>
        </div>
      ),
    },
    {
      title: 'Xabarlar',
      icon: <BellOutlined />,
      content: (
        <div style={{ padding: 24 }}>
          <h3>🔔 Xabarlar va sozlamalar</h3>
          <p>
            Header dagi <strong>qo'ng'iroq ikonkasi</strong> orqali yangi xabarlarni ko'rasiz:
          </p>
          <ul style={{ lineHeight: 1.8 }}>
            <li>Yangi baholar haqida xabar</li>
            <li>Past GPA ogohlantirishlari</li>
            <li>Ariza javoblari</li>
            <li>Tizim e'lonlari</li>
          </ul>
          <p style={{ marginTop: 12 }}>
            Sozlamalar (oy/quyosh ikonkasi) — tungi rejim, til, rang sxemasi.
          </p>
        </div>
      ),
    },
  ];

  const complete = () => {
    localStorage.setItem(ONBOARDING_KEY, '1');
    setOpen(false);
  };

  return (
    <Modal
      open={open}
      onCancel={complete}
      footer={null}
      width={600}
      closable={false}
      maskClosable={false}
    >
      <Steps current={step} items={steps.map((s) => ({ title: s.title, icon: s.icon }))} />
      <div style={{ minHeight: 280, marginTop: 24 }}>{steps[step].content}</div>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button onClick={complete}>O'tkazib yuborish</Button>
        <div style={{ display: 'flex', gap: 8 }}>
          {step > 0 && <Button onClick={() => setStep(step - 1)}>Orqaga</Button>}
          {step < steps.length - 1 ? (
            <Button type="primary" onClick={() => setStep(step + 1)}>
              Keyingisi
            </Button>
          ) : (
            <Button type="primary" onClick={complete}>
              Boshlash 🚀
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
