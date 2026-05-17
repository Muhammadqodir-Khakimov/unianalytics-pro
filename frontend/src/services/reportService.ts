import { api } from './api';

export const reportService = {
  listTemplates: () => api.get('/reports/templates').then((r) => r.data),

  generate: async (payload: {
    title: string;
    format: 'pdf' | 'excel';
    query: any;
  }) => {
    const response = await api.post('/reports/generate', payload, { responseType: 'blob' });
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const ext = payload.format === 'pdf' ? 'pdf' : 'xlsx';
    a.download = `${payload.title}.${ext}`;
    a.click();
    window.URL.revokeObjectURL(url);
  },
};
