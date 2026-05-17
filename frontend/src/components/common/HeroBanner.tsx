import { ReactNode } from 'react';
import dayjs from 'dayjs';

interface HeroBannerProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  gradient?: 'primary' | 'success' | 'warning' | 'sunset' | 'ocean' | 'purple' | 'pink';
}

const GRADIENTS: Record<string, string> = {
  primary: 'var(--gradient-primary)',
  success: 'var(--gradient-success)',
  warning: 'var(--gradient-warning)',
  sunset: 'var(--gradient-sunset)',
  ocean: 'var(--gradient-ocean)',
  purple: 'var(--gradient-purple)',
  pink: 'var(--gradient-pink)',
};

const GREETINGS = ["Xayrli tong", "Xayrli kun", "Xayrli oqshom", "Xayrli tun"];
function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return GREETINGS[0];
  if (h < 17) return GREETINGS[1];
  if (h < 22) return GREETINGS[2];
  return GREETINGS[3];
}

const WEEKDAYS = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba'];
const MONTHS = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentyabr', 'oktyabr', 'noyabr', 'dekabr'];

export function HeroBanner({ title, subtitle, actions, gradient = 'primary' }: HeroBannerProps) {
  const now = dayjs();
  const dateStr = `${WEEKDAYS[now.day()]}, ${now.date()}-${MONTHS[now.month()]} ${now.year()}-yil`;

  return (
    <div className="hero-banner" style={{ background: GRADIENTS[gradient] }}>
      <div style={{ position: 'relative', zIndex: 2 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ fontSize: 13, opacity: 0.8, fontWeight: 500, marginBottom: 4 }}>
              {getGreeting()} • {dateStr}
            </div>
            <h1 className="hero-title">{title}</h1>
            {subtitle && <div className="hero-subtitle">{subtitle}</div>}
          </div>
          {actions && <div>{actions}</div>}
        </div>
      </div>
    </div>
  );
}

export function HeroGreeting({ name, role, extras }: { name: string; role: string; extras?: ReactNode }) {
  return (
    <HeroBanner
      title={`${getGreeting()}, ${name}! 👋`}
      subtitle={`${role} hisobingizdan foydalanmoqdasiz`}
      actions={extras}
      gradient="primary"
    />
  );
}
