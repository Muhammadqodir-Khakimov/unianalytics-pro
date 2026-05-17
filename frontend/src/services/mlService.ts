import { api } from './api';

export const mlService = {
  // Drop-out (XGBoost)
  trainDropout: () => api.post('/ml/dropout/train').then((r) => r.data),
  dropoutStatus: () => api.get('/ml/dropout/status').then((r) => r.data),
  dropoutForStudent: (id: number) => api.get(`/ml/dropout/student/${id}`).then((r) => r.data),
  dropoutAtRisk: (topN = 50) =>
    api.get('/ml/dropout/at-risk', { params: { top_n: topN } }).then((r) => r.data),

  // Clustering
  trainClusters: (n = 5) => api.post(`/ml/clustering/train?n_clusters=${n}`).then((r) => r.data),
  clusterForStudent: (id: number) => api.get(`/ml/clustering/student/${id}`).then((r) => r.data),
  allClusters: () => api.get('/ml/clustering/all').then((r) => r.data),

  // Forecasting
  forecastStudent: (id: number, horizon = 3) =>
    api.get(`/ml/forecast/student/${id}`, { params: { horizon } }).then((r) => r.data),
  forecastFaculty: (name: string) =>
    api.get(`/ml/forecast/faculty/${encodeURIComponent(name)}`).then((r) => r.data),
  forecastEnrollment: () => api.get('/ml/forecast/enrollment').then((r) => r.data),

  // Anomaly
  anomaliesStudents: () => api.get('/ml/anomalies/students').then((r) => r.data),
  anomaliesTeachers: () => api.get('/ml/anomalies/teachers').then((r) => r.data),
  subjectsDifficulty: () => api.get('/ml/anomalies/subjects').then((r) => r.data),

  // AI Tutor
  tutorChat: (message: string, history: any[] = []) =>
    api.post('/ml/tutor/chat', { message, history }).then((r) => r.data),
};
