/**
 * Web Vitals tracking — Core Web Vitals va custom metrics.
 *
 * Yuborilishi mumkin:
 *  - Backend `/api/v1/metrics/web-vitals` endpointiga
 *  - Google Analytics 4
 *  - Sentry performance
 */

export interface WebVitalMetric {
  name: 'CLS' | 'FCP' | 'FID' | 'INP' | 'LCP' | 'TTFB';
  value: number;
  delta: number;
  id: string;
  rating?: 'good' | 'needs-improvement' | 'poor';
}

type Reporter = (m: WebVitalMetric) => void;

export async function reportWebVitals(onReport?: Reporter) {
  if (typeof window === 'undefined') return;

  try {
    const { onCLS, onFCP, onINP, onLCP, onTTFB } = await import('web-vitals');
    const reporter: Reporter = onReport || defaultReporter;

    onCLS(reporter as any);
    onFCP(reporter as any);
    onINP(reporter as any);
    onLCP(reporter as any);
    onTTFB(reporter as any);
  } catch (e) {
    console.warn('web-vitals package not installed — npm i web-vitals');
  }
}

function defaultReporter(metric: WebVitalMetric) {
  if (import.meta.env.DEV) {
    console.log(`[WebVital] ${metric.name}: ${metric.value.toFixed(2)} (${metric.rating})`);
    return;
  }

  // Production'da backend'ga yuborish (sendBeacon — sahifa yopilsa ham yuboriladi)
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    id: metric.id,
    url: window.location.pathname,
    timestamp: Date.now(),
  });

  const url = '/api/v1/metrics/web-vitals';
  if (navigator.sendBeacon) {
    navigator.sendBeacon(url, body);
  } else {
    fetch(url, { method: 'POST', body, headers: { 'Content-Type': 'application/json' }, keepalive: true });
  }
}
