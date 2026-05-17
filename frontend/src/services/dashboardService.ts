import { api } from './api';

export const dashboardService = {
  summary: () => api.get('/dashboard/summary').then((r) => r.data),
  gpaTrend: () => api.get('/dashboard/gpa-trend').then((r) => r.data),
  facultyComparison: () => api.get('/dashboard/faculty-comparison').then((r) => r.data),
  topStudents: (limit = 10) =>
    api.get('/dashboard/top-students', { params: { limit } }).then((r) => r.data),
  subjectPerformance: () => api.get('/dashboard/subject-performance').then((r) => r.data),
  genderDistribution: () => api.get('/dashboard/gender-distribution').then((r) => r.data),
  heatmapFacultySemester: () => api.get('/dashboard/heatmap-faculty-semester').then((r) => r.data),
};
