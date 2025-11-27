/**
 * React Query version of useNotifications hook
 * 
 * این hook از React Query برای مدیریت notifications استفاده می‌کند.
 */

import { useMemo } from "react";
import { useApiQuery } from "./useApiQuery";
import { useApiMutation } from "./useApiMutation";
import { useQueryClient } from "@tanstack/react-query";

export type NotificationItem = {
  id: string | number;
  title: string;
  body: string;
  created_at: string;
  read?: boolean;
  severity?: "info" | "warning" | "critical";
};

const FALLBACK_STORAGE_KEY = "imehr_notification_samples";

function buildFallbackNotifications(): NotificationItem[] {
  if (typeof window === "undefined") {
    return [];
  }
  const stored = localStorage.getItem(FALLBACK_STORAGE_KEY);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      /* ignore */
    }
  }
  const now = new Date();
  const base: NotificationItem[] = [
    {
      id: "sample-1",
      title: "اینترنت شعبه ونک",
      body: "کیفیت لینک افزایش یافت. مانیتورینگ طی ۲۴ ساعت پایدار بوده است.",
      created_at: new Date(now.getTime() - 1000 * 60 * 30).toISOString(),
      severity: "info",
    },
    {
      id: "sample-2",
      title: "هشدار SLA",
      body: "تیکت T-20251126-0043 در آستانه نقض SLA پاسخ است.",
      created_at: new Date(now.getTime() - 1000 * 60 * 90).toISOString(),
      severity: "warning",
    },
    {
      id: "sample-3",
      title: "VoIP شمال‌شرق",
      body: "ثبت‌نام SIP دو دستگاه در شعبه شرق با خطا مواجه شد.",
      created_at: new Date(now.getTime() - 1000 * 60 * 180).toISOString(),
      severity: "critical",
    },
  ];
  localStorage.setItem(FALLBACK_STORAGE_KEY, JSON.stringify(base));
  return base;
}

/**
 * Hook برای دریافت notifications با React Query
 * 
 * @param pollInterval - فاصله زمانی برای refetch (به میلی‌ثانیه). اگر 0 یا false باشد، polling غیرفعال است.
 * 
 * @example
 * const { notifications, unreadCount, isLoading, error, markAllAsRead } = useNotificationsQuery(60000);
 */
export function useNotificationsQuery(pollInterval: number | false = 60000) {
  const queryClient = useQueryClient();

  // Fetch notifications
  const {
    data: notificationsData,
    isLoading,
    error,
    refetch,
  } = useApiQuery<NotificationItem[]>({
    endpoint: "/api/notifications?limit=5",
    queryKey: ["notifications"],
    refetchInterval: pollInterval || false,
    // Fallback data در صورت خطا
    placeholderData: buildFallbackNotifications() as NotificationItem[],
  });

  // Process notifications data
  const notifications = useMemo(() => {
    if (notificationsData) {
      if (Array.isArray(notificationsData)) {
        return notificationsData;
      } else if (notificationsData && typeof notificationsData === "object" && "items" in notificationsData) {
        return (notificationsData as any).items || [];
      }
    }
    return buildFallbackNotifications();
  }, [notificationsData]);

  // Calculate unread count
  const unreadCount = useMemo(
    () => notifications.filter((n: NotificationItem) => !n.read).length,
    [notifications]
  );

  // Mark all as read mutation
  const markAllAsReadMutation = useApiMutation<{ success: boolean }, void>({
    method: "POST",
    endpoint: "/api/notifications/mark-read",
    invalidateQueries: [["notifications"]],
  });

  const markAllAsRead = async () => {
    try {
      await markAllAsReadMutation.mutateAsync(undefined);
      // Optimistic update: همه notifications را به عنوان خوانده شده علامت بزن
      queryClient.setQueryData<NotificationItem[]>(["notifications"], (old) => {
        if (!old) return old;
        return old.map((item) => ({ ...item, read: true }));
      });
    } catch (err: any) {
      // Error handling در mutation انجام می‌شود
      throw err;
    }
  };

  return {
    notifications,
    unreadCount,
    loading: isLoading,
    error: error ? (error as any)?.message || "خطا در دریافت اعلان‌ها" : null,
    refresh: refetch,
    markAllAsRead,
    isMarkingAsRead: markAllAsReadMutation.isPending,
  };
}

