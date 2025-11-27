/**
 * React Query Provider Component
 * 
 * این کامپوننت QueryClientProvider را برای کل اپلیکیشن فراهم می‌کند.
 */

import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { queryClient } from "../lib/queryClient";
import { ReactNode } from "react";

interface QueryProviderProps {
  children: ReactNode;
}

/**
 * QueryProvider component
 * 
 * این کامپوننت QueryClientProvider و ReactQueryDevtools را wrap می‌کند.
 * 
 * @param children - React children
 */
export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* React Query DevTools - فقط در development */}
      {import.meta.env.DEV && (
        <ReactQueryDevtools
          initialIsOpen={false}
          position="bottom-right"
          buttonPosition="bottom-right"
        />
      )}
    </QueryClientProvider>
  );
}

