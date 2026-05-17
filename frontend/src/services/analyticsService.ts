import { api } from './api';

export const analyticsService = {
  studentPrediction: (id: number) => api.get(`/analytics/student/${id}/prediction`).then((r) => r.data),
  atRisk: (threshold = 2.0, limit = 50) =>
    api.get('/analytics/at-risk', { params: { threshold, limit } }).then((r) => r.data),
  topPerformers: (limit = 20) =>
    api.get('/analytics/top-performers', { params: { limit } }).then((r) => r.data),
  anomalies: () => api.get('/analytics/anomalies').then((r) => r.data),
  facultyInsights: (facultyName: string) =>
    api.get(`/analytics/faculty-insights/${encodeURIComponent(facultyName)}`).then((r) => r.data),
};
