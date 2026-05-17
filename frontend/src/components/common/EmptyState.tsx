import { ReactNode } from 'react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: ReactNode;
  type?: 'no-data' | 'no-results' | 'no-notifications' | 'no-access' | 'error';
}

const ILLUSTRATIONS: Record<string, JSX.Element> = {
  'no-data': (
    <svg width="180" height="160" viewBox="0 0 200 180" fill="none">
      <defs>
        <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#667eea" stopOpacity="0.1" />
          <stop offset="100%" stopColor="#764ba2" stopOpacity="0.2" />
        </linearGradient>
      </defs>
      <circle cx="100" cy="90" r="70" fill="url(#g1)" />
      <rect x="60" y="60" width="80" height="60" rx="8" fill="white" stroke="#cbd5e1" strokeWidth="2" />
      <rect x="70" y="72" width="60" height="4" rx="2" fill="#cbd5e1" />
      <rect x="70" y="84" width="40" height="4" rx="2" fill="#cbd5e1" />
      <rect x="70" y="96" width="50" height="4" rx="2" fill="#cbd5e1" />
      <circle cx="140" cy="135" r="22" fill="#667eea" />
      <text x="140" y="142" textAnchor="middle" fill="white" fontSize="20" fontWeight="bold">?</text>
    </svg>
  ),
  'no-results': (
    <svg width="180" height="160" viewBox="0 0 200 180" fill="none">
      <circle cx="100" cy="90" r="70" fill="#f1f5f9" />
      <circle cx="90" cy="80" r="30" stroke="#94a3b8" strokeWidth="4" fill="none" />
      <line x1="110" y1="100" x2="130" y2="120" stroke="#94a3b8" strokeWidth="4" strokeLinecap="round" />
      <line x1="76" y1="80" x2="104" y2="80" stroke="#cbd5e1" strokeWidth="2" />
    </svg>
  ),
  'no-notifications': (
    <svg width="180" height="160" viewBox="0 0 200 180" fill="none">
      <circle cx="100" cy="90" r="70" fill="#fef3c7" />
      <path
        d="M100 50c-15 0-25 10-25 25v15l-10 15h70l-10-15V75c0-15-10-25-25-25z"
        fill="white"
        stroke="#f59e0b"
        strokeWidth="3"
      />
      <circle cx="100" cy="115" r="5" fill="#f59e0b" />
    </svg>
  ),
  'no-access': (
    <svg width="180" height="160" viewBox="0 0 200 180" fill="none">
      <circle cx="100" cy="90" r="70" fill="#fee2e2" />
      <rect x="80" y="80" width="40" height="40" rx="4" fill="white" stroke="#ef4444" strokeWidth="3" />
      <path d="M88 80V70a12 12 0 0124 0v10" stroke="#ef4444" strokeWidth="3" fill="none" />
      <circle cx="100" cy="100" r="4" fill="#ef4444" />
    </svg>
  ),
  error: (
    <svg width="180" height="160" viewBox="0 0 200 180" fill="none">
      <circle cx="100" cy="90" r="70" fill="#fee2e2" />
      <circle cx="100" cy="90" r="40" fill="white" stroke="#ef4444" strokeWidth="4" />
      <path d="M85 75l30 30M115 75l-30 30" stroke="#ef4444" strokeWidth="4" strokeLinecap="round" />
    </svg>
  ),
};

export function EmptyState({
  title = "Ma'lumot yo'q",
  description,
  action,
  type = 'no-data',
}: EmptyStateProps) {
  return (
    <div style={{ textAlign: 'center', padding: '40px 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
        {ILLUSTRATIONS[type]}
      </div>
      <h3 style={{ margin: '8px 0', fontWeight: 600 }}>{title}</h3>
      {description && (
        <p style={{ color: 'rgba(0,0,0,0.55)', fontSize: 14, maxWidth: 360, margin: '0 auto 16px' }}>
          {description}
        </p>
      )}
      {action && <div>{action}</div>}
    </div>
  );
}
