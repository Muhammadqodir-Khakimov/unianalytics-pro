import { api } from './api';

export const detailService = {
  student: (id: number) => api.get(`/detail/student/${id}`).then((r) => r.data),
  teacher: (id: number) => api.get(`/detail/teacher/${id}`).then((r) => r.data),
  subject: (id: number) => api.get(`/detail/subject/${id}`).then((r) => r.data),
  faculty: (id: number) => api.get(`/detail/faculty/${id}`).then((r) => r.data),
};
