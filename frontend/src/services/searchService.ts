import { api } from './api';

export const searchService = {
  global: (q: string, limit = 5) =>
    api.get('/search', { params: { q, limit } }).then((r) => r.data),
};
