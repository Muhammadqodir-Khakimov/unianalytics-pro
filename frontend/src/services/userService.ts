import { api } from './api';

export const userService = {
  changePassword: (old_password: string, new_password: string) =>
    api.post('/users/me/change-password', { old_password, new_password }).then((r) => r.data),
  updateProfile: (payload: { full_name?: string; email?: string }) =>
    api.put('/users/me', payload).then((r) => r.data),
  list: () => api.get('/users').then((r) => r.data),
  changeRole: (userId: number, role: string) =>
    api.put(`/users/${userId}/role?role=${role}`).then((r) => r.data),
  toggleActive: (userId: number, is_active: boolean) =>
    api.put(`/users/${userId}/active?is_active=${is_active}`).then((r) => r.data),
};

export const transcriptService = {
  download: async (studentId: number, studentName: string) => {
    const response = await api.get(`/transcript/student/${studentId}`, { responseType: 'blob' });
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${studentName.replace(/\s+/g, '_')}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
  },
};
