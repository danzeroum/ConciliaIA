import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '@/api/auth.api';

interface User {
  id: string;
  email: string;
  name: string;
  roles: string[];
  tenantId: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  updateUser: (user: Partial<User>) => void;
}

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64));
  } catch {
    return {};
  }
}

function userFromToken(token: string, fallbackEmail: string): User {
  const payload = decodeJwtPayload(token);
  return {
    id: (payload.sub as string) || '',
    email: (payload.email as string) || fallbackEmail,
    name: (payload.name as string) || (payload.email as string) || fallbackEmail,
    roles: Array.isArray(payload.roles) ? (payload.roles as string[]) : [],
    tenantId: (payload.tenant_id as string) || '',
  };
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const response = await authApi.login({ email, password });

        const user = userFromToken(response.access_token, email);

        set({
          user,
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
          isAuthenticated: true,
        });
      },

      logout: () => {
        authApi.logout().catch(() => {});

        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      refreshAccessToken: async () => {
        const { refreshToken, user } = get();
        if (!refreshToken) throw new Error('No refresh token');

        const response = await authApi.refresh(refreshToken);
        const updatedUser = userFromToken(response.access_token, user?.email ?? '');
        set({
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
          user: updatedUser,
        });
      },

      updateUser: (userData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }));
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
