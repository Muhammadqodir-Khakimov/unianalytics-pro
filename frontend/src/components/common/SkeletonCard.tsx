interface SkeletonCardProps {
  rows?: number;
  height?: number;
}

export function SkeletonCard({ rows = 3, height = 16 }: SkeletonCardProps) {
  return (
    <div style={{ padding: 24 }}>
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="skeleton-shimmer"
          style={{
            height,
            width: i === rows - 1 ? '60%' : `${100 - i * 10}%`,
            marginBottom: 8,
          }}
        />
      ))}
    </div>
  );
}

export function SkeletonKpi() {
  return (
    <div className="kpi-card">
      <div className="skeleton-shimmer" style={{ width: 48, height: 48, borderRadius: 10, marginBottom: 12 }} />
      <div className="skeleton-shimmer" style={{ height: 12, width: '50%', marginBottom: 8 }} />
      <div className="skeleton-shimmer" style={{ height: 28, width: '70%' }} />
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div style={{ padding: 20 }}>
      <div className="skeleton-shimmer" style={{ height: 16, width: '40%', marginBottom: 20 }} />
      <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', height: 250 }}>
        {[60, 80, 45, 90, 70, 100, 55].map((h, i) => (
          <div
            key={i}
            className="skeleton-shimmer"
            style={{ flex: 1, height: `${h}%`, borderRadius: '6px 6px 0 0' }}
          />
        ))}
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="skeleton-shimmer" style={{ flex: 1, height: 14 }} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} style={{ display: 'flex', gap: 12, marginBottom: 10 }}>
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="skeleton-shimmer" style={{ flex: 1, height: 12 }} />
          ))}
        </div>
      ))}
    </div>
  );
}
