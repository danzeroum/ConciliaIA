/**
 * @deprecated Use `@/api/axios-config` directly.
 *
 * This module previously created a second, independent axios instance with a
 * different base URL and no token-refresh handling. It now re-exports the single
 * unified client so any remaining import keeps working while pointing at the
 * same instance (request auth + 401 refresh interceptor).
 */
import { apiClient } from '@/api/axios-config';

export { apiClient };
export default apiClient;
