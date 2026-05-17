import { ReactNode } from 'react';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

interface KpiCardProps {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'purple' | 'pink';
  delta?: number;
  deltaLabel?: string;
  loading?: boolean;
  onClick?: () => void;
}

export function KpiCard({
  label,
  value,
  icon,
  variant = 'primary',
  delta,
  deltaLabel,
  loading,
  onClick,
}: KpiCardProps) {
  return (
    <div
      className={`kpi-card ${variant}`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {icon && <div className={`kpi-icon ${variant}`}>{icon}</div>}
      <div className="kpi-label">{label}</div>
      {loading ? (
        <div className="skeleton-shimmer" style={{ height: 32, width: '60%', marginTop: 6 }} />
      ) : (
        <div className="kpi-value">{value}</div>
      )}
      {delta !== undefined && !loading && (
        <div className={`kpi-delta ${delta >= 0 ? 'positive' : 'negative'}`}>
          {delta >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />} {Math.abs(delta)}
          {deltaLabel ? ` ${deltaLabel}` : ' %'}
        </div>
      )}
    </div>
  );
}
