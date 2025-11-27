/**
 * Custom Hook برای استفاده از React Query Mutations با API calls
 * 
 * این hook یک wrapper برای useMutation است که با API service ما کار می‌کند.
 */

import {
  useMutation,
  UseMutationOptions,
  UseMutationResult,
  useQueryClient,
} from "@tanstack/react-query";
import { apiPost, apiPatch, apiPut, apiDelete } from "../services/api";

/**
 * Generic type برای API response
 */
type ApiResponse<T> = T;

/**
 * Options برای useApiMutation
 */
interface UseApiMutationOptions<TData, TVariables, TError = Error>
  extends Omit<UseMutationOptions<ApiResponse<TData>, TError, TVariables>, "mutationFn"> {
  method?: "POST" | "PATCH" | "PUT" | "DELETE";
  endpoint: string | ((variables: TVariables) => string);
  invalidateQueries?: string[][]; // Array of query keys to invalidate after mutation
}

/**
 * Custom hook برای mutations (POST, PATCH, PUT, DELETE) با React Query
 * 
 * @example
 * const { mutate, isPending } = useApiMutation<Ticket, CreateTicketData>({
 *   method: 'POST',
 *   endpoint: '/api/tickets',
 *   invalidateQueries: [['tickets']],
 * });
 * 
 * mutate({ title: 'New Ticket', description: '...' });
 * 
 * @example با dynamic endpoint
 * const { mutate } = useApiMutation<Ticket, { id: number; status: string }>({
 *   method: 'PATCH',
 *   endpoint: (vars) => `/api/tickets/${vars.id}/status`,
 *   invalidateQueries: [['tickets'], ['tickets', vars => vars.id]],
 * });
 */
export function useApiMutation<TData = unknown, TVariables = unknown, TError = Error>(
  options: UseApiMutationOptions<TData, TVariables, TError>
): UseMutationResult<ApiResponse<TData>, TError, TVariables> {
  const { method = "POST", endpoint, invalidateQueries = [], ...mutationOptions } = options;
  const queryClient = useQueryClient();

  return useMutation<ApiResponse<TData>, TError, TVariables>({
    ...mutationOptions,
    mutationFn: async (variables: TVariables) => {
      const url = typeof endpoint === "function" ? endpoint(variables) : endpoint;
      
      let data: ApiResponse<TData>;
      
      switch (method) {
        case "POST":
          data = await apiPost(url, variables);
          break;
        case "PATCH":
          data = await apiPatch(url, variables);
          break;
        case "PUT":
          data = await apiPut(url, variables);
          break;
        case "DELETE":
          data = await apiDelete(url);
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }
      
      return data;
    },
    onSuccess: (data, variables, context) => {
      // Invalidate queries after successful mutation
      invalidateQueries.forEach((queryKey) => {
        // اگر queryKey یک function باشد، با variables اجرا کن
        const finalQueryKey = typeof queryKey === "function" 
          ? queryKey(variables) 
          : queryKey;
        queryClient.invalidateQueries({ queryKey: finalQueryKey });
      });
      
      // Call custom onSuccess if provided
      if (mutationOptions.onSuccess) {
        mutationOptions.onSuccess(data, variables, context);
      }
    },
  });
}

