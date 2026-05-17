import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { RightOutlined, HomeOutlined } from '@ant-design/icons';

interface PageHeaderProps {
  title: ReactNode;
  subtitle?: ReactNode;
  icon?: ReactNode;
  actions?: ReactNode;
  breadcrumbs?: { label: string; to?: string }[];
  sticky?: boolean;
}

const ROUTE_LABELS: Record<string, string> = {
  dashboard: 'Dashboard',
  olap: 'OLAP',
  cube: 'Kub tahlili',
  pivot: 'Pivot',
  analytics: 'AI Analitika',
  'grade-entry': 'Baho kiritish',
  schedule: 'Jadval',
  applications: 'Arizalar',
  scholarship: 'Stipendiya',
  students: 'Talabalar',
  teachers: "O'qituvchilar",
  subjects: 'Fanlar',
  grades: 'Baholar',
  faculties: 'Fakultetlar',
  reports: 'Hisobotlar',
  settings: 'Sozlamalar',
  admin: 'Admin',
  users: 'Foydalanuvchilar',
  audit: 'Audit',
};

export function PageHeader({ title, subtitle, icon, actions, breadcrumbs, sticky }: PageHeaderProps) {
  const location = useLocation();

  // Auto-build breadcrumbs from URL if not provided
  const autoBreadcrumbs = breadcrumbs || location.pathname
    .split('/')
    .filter(Boolean)
    .map((seg, idx, all) => ({
      label: ROUTE_LABELS[seg] || seg,
      to: idx === all.length - 1 ? undefined : '/' + all.slice(0, idx + 1).join('/'),
    }));

  return (
    <div
      className="page-header"
      style={sticky ? { position: 'sticky', top: 64, zIndex: 5, background: 'inherit' } : {}}
    >
      <div>
        {autoBreadcrumbs.length > 0 && (
          <div className="modern-breadcrumb" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Link to="/dashboard"><HomeOutlined /></Link>
            {autoBreadcrumbs.map((b, i) => (
              <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <RightOutlined style={{ fontSize: 10, opacity: 0.5 }} />
                {b.to ? <Link to={b.to}>{b.label}</Link> : <span>{b.label}</span>}
              </span>
            ))}
          </div>
        )}
        <h1 className="page-title">
          {icon}
          {title}
        </h1>
        {subtitle && <div className="page-subtitle">{subtitle}</div>}
      </div>
      {actions && <div>{actions}</div>}
    </div>
  );
}
