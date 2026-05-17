/**
 * Sentry client initialization.
 * Configured via Vite env vars:
 *   VITE_SENTRY_DSN
 *   VITE_APP_VERSION  (auto from git sha during CI)
 *   VITE_APP_ENV      (production / staging)
 */

export async function initSentry() {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (!dsn || import.meta.env.DEV) return;

  // Lazy-loaded so dev bundle stays clean
  const Sentry = await import('@sentry/react');
  Sentry.init({
    dsn,
    release: `unianalytics-frontend@${import.meta.env.VITE_APP_VERSION || 'unknown'}`,
    environment: import.meta.env.VITE_APP_ENV || 'production',
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.0,
    replaysOnErrorSampleRate: 1.0,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({ maskAllText: true, blockAllMedia: true }),
    ],
    beforeSend(event) {
      // Strip PII
      if (event.request?.cookies) delete event.request.cookies;
      return event;
    },
  });
}
