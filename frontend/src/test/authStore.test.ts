import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '@/store/authStore';

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
  });

  it('starts unauthenticated', () => {
    expect(useAuthStore.getState().isAuthenticated()).toBe(false);
  });

  it('becomes authenticated after setTokens', () => {
    useAuthStore.getState().setTokens('access', 'refresh');
    expect(useAuthStore.getState().isAuthenticated()).toBe(true);
  });

  it('logout clears state', () => {
    useAuthStore.getState().setTokens('a', 'b');
    useAuthStore.getState().logout();
    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
  });
});
