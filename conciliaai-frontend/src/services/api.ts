import axios, {
  AxiosError,
  AxiosHeaders,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
} from 'axios';
import type { ApiResponse } from './types';

type RefreshResponse = ApiResponse<{
  access_token: string;
  refresh_token: string;
  expires_in?: number;
}>;

type RequestConfig = AxiosRequestConfig & { _retry?: boolean };

type ErrorResponseBody = {
  message?: string;
  detail?: string;
  error?: string;
};

const resolveBaseUrl = (): string => {
  const importMetaUrl = typeof import.meta !== 'undefined' ? import.meta.env?.VITE_API_URL : undefined;
  const processUrl = typeof process !== 'undefined' ? process.env?.VITE_API_URL : undefined;

  return importMetaUrl || processUrl || 'http://localhost:3000/api';
};

const BASE_URL = resolveBaseUrl();
const DEFAULT_TIMEOUT = 10_000;
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

const toPlainHeaders = (
  headers?: AxiosRequestConfig['headers'],
): Record<string, string> => {
  if (!headers) {
    return {};
  }

  if (headers instanceof AxiosHeaders) {
    return headers.toJSON() as Record<string, string>;
  }

  if (Array.isArray(headers)) {
    return Object.fromEntries(headers) as Record<string, string>;
  }

  return { ...(headers as Record<string, string>) };
};

const setAuthorizationHeader = (config: AxiosRequestConfig, token: string): void => {
  const normalizedHeaders = toPlainHeaders(config.headers);

  config.headers = {
    ...normalizedHeaders,
    Authorization: `Bearer ${token}`,
  };
};

const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
};

const getRefreshToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
};

const setTokens = (accessToken: string, refreshToken?: string): void => {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);

  if (refreshToken) {
    window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
};

const clearTokens = (): void => {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
};

export const handleApiError = (error: unknown): Error => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponseBody>;
    const status = axiosError.response?.status;
    const responseData = axiosError.response?.data;

    if (status === 403) {
      return new Error(responseData?.message || 'Acesso negado.');
    }

    if (status && status >= 500) {
      return new Error('Erro no servidor. Tente novamente mais tarde.');
    }

    const detailedMessage =
      responseData?.message || responseData?.detail || responseData?.error;

    return new Error(detailedMessage || axiosError.message || 'Erro na requisição.');
  }

  if (error instanceof Error) {
    return error;
  }

  return new Error('Erro desconhecido.');
};

const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

let refreshPromise: Promise<string | null> | null = null;

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    clearTokens();
    return null;
  }

  try {
    const response: AxiosResponse<RefreshResponse> = await axios.post(
      `${BASE_URL}/auth/refresh`,
      { refresh_token: refreshToken },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: DEFAULT_TIMEOUT,
      },
    );

    if (response.data?.data?.access_token) {
      setTokens(response.data.data.access_token, response.data.data.refresh_token);
      return response.data.data.access_token;
    }

    return null;
  } catch (refreshError) {
    clearTokens();
    throw handleApiError(refreshError);
  }
};

apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

    if (token) {
      setAuthorizationHeader(config, token);
    }

    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.log('[API Request]', config.method?.toUpperCase(), config.url, config);
    }

    return config;
  },
  (error: AxiosError) => Promise.reject(handleApiError(error)),
);

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const status = error.response?.status;
    const originalRequest = error.config as RequestConfig | undefined;

    if (status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      try {
        const newAccessToken = await refreshPromise;

        if (newAccessToken) {
          setAuthorizationHeader(originalRequest, newAccessToken);
          return apiClient(originalRequest);
        }

        return Promise.reject(handleApiError(error));
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }

    if (status === 403) {
      clearTokens();
    }

    if (status === 500) {
      // espaço reservado para integrações futuras de monitoramento
    }

    return Promise.reject(handleApiError(error));
  },
);

export { apiClient };
export default apiClient;
