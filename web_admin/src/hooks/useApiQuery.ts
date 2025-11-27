/**
 * Custom Hook برای استفاده از React Query با API calls
 * 
 * این hook یک wrapper برای useQuery است که با API service ما کار می‌کند.
 */

import { useQuery, UseQueryOptions, UseQueryResult } from "@tanstack/react-query";
import { apiGet } from "../services/api";

/**
 * Generic type برای API response
 */
type ApiResponse<T> = T;

/**
 * Options برای useApiQuery
 */
interface UseApiQueryOptions<TData, TError = Error> extends Omit<UseQueryOptions<ApiResponse<TData>, TError>, "queryFn"> {
  endpoint: string;
  enabled?: boolean;
  refetchInterval?: number | false;
}

/**
 * Custom hook برای fetch کردن data از API با React Query
 * 
 * @example
 * const { data, isLoading, error } = useApiQuery<Ticket[]>({
 *   endpoint: '/api/tickets',
 *   queryKey: ['tickets'],
 * });
 * 
 * @example با فیلتر
 * const { data } = useApiQuery<Ticket[]>({
 *   endpoint: `/api/tickets?status=${status}`,
 *   queryKey: ['tickets', status],
 * });
 * 
 * @example با refetch interval
 * const { data } = useApiQuery<Notification[]>({
 *   endpoint: '/api/notifications',
 *   queryKey: ['notifications'],
 *   refetchInterval: 60000, // هر 60 ثانیه
 * });
 */
export function useApiQuery<TData = unknown, TError = Error>(
  options: UseApiQueryOptions<TData, TError>
): UseQueryResult<ApiResponse<TData>, TError> {
  const { endpoint, enabled = true, refetchInterval, placeholderData, ...queryOptions } = options;

  return useQuery<ApiResponse<TData>, TError>({
    ...queryOptions,
    queryFn: async () => {
      const data = await apiGet(endpoint);
      return data as ApiResponse<TData>;
    },
    enabled,
    refetchInterval: refetchInterval || false,
    placeholderData: placeholderData ? (typeof placeholderData === "function" ? placeholderData() : placeholderData) as ApiResponse<TData> : undefined,
  });
}

