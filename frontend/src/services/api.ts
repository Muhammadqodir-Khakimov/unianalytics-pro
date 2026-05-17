import axios, { AxiosError } from 'axios';
import { message } from 'antd';
import { useAuthStore } from '@/store/authStore';

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const api = axios.create({
  baseURL,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<any>) => {
    if (error.response?.status === 401) {
      const original = error.config as any;
      if (!original._retry) {
        original._retry = true;
        try {
          const refreshToken = useAuthStore.getState().refreshToken;
          if (refreshToken) {
            const { data } = await axios.post(`${baseURL}/auth/refresh`, {
              refresh_token: refreshToken,
            });
            useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
            original.headers.Authorization = `Bearer ${data.access_token}`;
            return api(original);
          }
        } catch {
          useAuthStore.getState().logout();
          window.location.href = '/login';
        }
      }
    }

    const detail = error.response?.data?.detail || error.message || 'Xatolik yuz berdi';
    message.error(typeof detail === 'string' ? detail : 'Xatolik yuz berdi');
    return Promise.reject(error);
  }
);
