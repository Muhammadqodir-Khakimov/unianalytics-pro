import { api } from './api';

export const notificationService = {
  list: (unreadOnly = false, limit = 50) =>
    api.get('/notifications', { params: { unread_only: unreadOnly, limit } }).then((r) => r.data),
  markRead: (id: number) => api.post(`/notifications/${id}/read`).then((r) => r.data),
  markAllRead: () => api.post('/notifications/mark-all-read').then((r) => r.data),
};

export const scheduleService = {
  list: (params?: any) => api.get('/schedule', { params }).then((r) => r.data),
  create: (payload: any) => api.post('/schedule', payload).then((r) => r.data),
  delete: (id: number) => api.delete(`/schedule/${id}`).then((r) => r.data),
  attendance: (params?: any) => api.get('/schedule/attendance', { params }).then((r) => r.data),
  markAttendance: (payload: any) => api.post('/schedule/attendance/bulk', payload).then((r) => r.data),
  studentAttendanceStats: (studentId: number) =>
    api.get(`/schedule/attendance/student/${studentId}/stats`).then((r) => r.data),
};

export const applicationService = {
  submit: (payload: any) => api.post('/applications', payload).then((r) => r.data),
  my: () => api.get('/applications/my').then((r) => r.data),
  list: (params?: any) => api.get('/applications', { params }).then((r) => r.data),
  get: (id: number) => api.get(`/applications/${id}`).then((r) => r.data),
  review: (id: number, payload: any) =>
    api.put(`/applications/${id}/review`, payload).then((r) => r.data),
  types: () => api.get('/applications/types/all').then((r) => r.data),
};

export const scholarshipService = {
  student: (studentId: number) => api.get(`/scholarship/student/${studentId}`).then((r) => r.data),
  group: (groupName: string) =>
    api.get(`/scholarship/group/${encodeURIComponent(groupName)}`).then((r) => r.data),
  summary: () => api.get('/scholarship/summary').then((r) => r.data),
};

export const auditService = {
  list: (params?: any) => api.get('/audit/logs', { params }).then((r) => r.data),
  stats: () => api.get('/audit/stats').then((r) => r.data),
};

export const certificateService = {
  download: async (studentId: number, name: string) => {
    const r = await api.get(`/certificate/student/${studentId}`, { responseType: 'blob' });
    const url = URL.createObjectURL(new Blob([r.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `certificate_${name.replace(/\s+/g, '_')}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  },
};
