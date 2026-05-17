import { api } from './api';

export const announcementService = {
  list: (params?: any) => api.get('/announcements', { params }).then((r) => r.data),
  create: (payload: any) => api.post('/announcements', payload).then((r) => r.data),
  remove: (id: number) => api.delete(`/announcements/${id}`).then((r) => r.data),
};

export const paymentService = {
  my: () => api.get('/payments/my').then((r) => r.data),
  list: (params?: any) => api.get('/payments', { params }).then((r) => r.data),
  create: (payload: any) => api.post('/payments', payload).then((r) => r.data),
  pay: (id: number, payload: any) => api.post(`/payments/${id}/pay`, payload).then((r) => r.data),
  summary: () => api.get('/payments/summary').then((r) => r.data),
};

export const examService = {
  list: (params?: any) => api.get('/exams', { params }).then((r) => r.data),
  create: (payload: any) => api.post('/exams', payload).then((r) => r.data),
};

export const thesisService = {
  list: (params?: any) => api.get('/theses', { params }).then((r) => r.data),
  create: (payload: any) => api.post('/theses', payload).then((r) => r.data),
  update: (id: number, payload: any) => api.put(`/theses/${id}`, payload).then((r) => r.data),
};

export const libraryService = {
  listBooks: (params?: any) => api.get('/library/books', { params }).then((r) => r.data),
  createBook: (payload: any) => api.post('/library/books', payload).then((r) => r.data),
  loanBook: (payload: any) => api.post('/library/loans', payload).then((r) => r.data),
  returnBook: (loanId: number) => api.post(`/library/loans/${loanId}/return`).then((r) => r.data),
  myLoans: () => api.get('/library/my-loans').then((r) => r.data),
};

export const dormitoryService = {
  rooms: () => api.get('/dormitory/rooms').then((r) => r.data),
  assign: (payload: any) => api.post('/dormitory/assign', payload).then((r) => r.data),
  my: () => api.get('/dormitory/my').then((r) => r.data),
};

export const documentService = {
  my: () => api.get('/documents/my').then((r) => r.data),
  register: (payload: any) => api.post('/documents', payload).then((r) => r.data),
  remove: (id: number) => api.delete(`/documents/${id}`).then((r) => r.data),
};

export const messageService = {
  list: (folder = 'inbox', unread_only = false) =>
    api.get('/messages', { params: { folder, unread_only } }).then((r) => r.data),
  send: (payload: any) => api.post('/messages', payload).then((r) => r.data),
  markRead: (id: number) => api.post(`/messages/${id}/read`).then((r) => r.data),
};

export const calendarService = {
  events: (start: string, end: string) =>
    api.get('/calendar/events', { params: { start, end } }).then((r) => r.data),
};

export const courseService = {
  prerequisites: (subjectId: number) =>
    api.get(`/courses/prerequisites/${subjectId}`).then((r) => r.data),
  addPrerequisite: (payload: any) =>
    api.post('/courses/prerequisites', payload).then((r) => r.data),
};

export const uploadService = {
  avatar: async (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    const r = await api.post('/uploads/avatar', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
    return r.data;
  },
  document: async (file: File, category = 'general') => {
    const fd = new FormData();
    fd.append('file', file);
    const r = await api.post(`/uploads/document?category=${category}`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return r.data;
  },
};
