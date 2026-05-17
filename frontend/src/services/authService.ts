import { api } from './api';
import { User, TokenResponse } from '@/types';

export const authService = {
  async login(username: string, password: string): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const { data } = await api.post<TokenResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },

  async register(payload: {
    username: string;
    email: string;
    full_name: string;
    password: string;
    role?: string;
  }): Promise<User> {
    const { data } = await api.post<User>('/auth/register', payload);
    return data;
  },

  async me(): Promise<User> {
    const { data } = await api.get<User>('/auth/me');
    return data;
  },
};
