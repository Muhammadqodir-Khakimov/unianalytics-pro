import { api } from './api';
import { PaginatedResponse } from '@/types';

export function createCrudService<T>(resource: string) {
  return {
    list: (params?: Record<string, any>): Promise<PaginatedResponse<T>> =>
      api.get(`/${resource}`, { params }).then((r) => r.data),
    get: (id: number): Promise<T> => api.get(`/${resource}/${id}`).then((r) => r.data),
    create: (payload: any): Promise<T> => api.post(`/${resource}`, payload).then((r) => r.data),
    update: (id: number, payload: any): Promise<T> =>
      api.put(`/${resource}/${id}`, payload).then((r) => r.data),
    remove: (id: number) => api.delete(`/${resource}/${id}`).then((r) => r.data),
  };
}

export const studentService = createCrudService('students');
export const teacherService = createCrudService('teachers');
export const subjectService = createCrudService('subjects');
export const gradeService = createCrudService('grades');
export const facultyService = createCrudService('faculties');
