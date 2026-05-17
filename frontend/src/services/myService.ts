import { api } from './api';

export const myService = {
  dashboard: () => api.get('/my/dashboard').then((r) => r.data),
};
