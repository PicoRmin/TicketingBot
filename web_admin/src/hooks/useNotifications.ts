import { useCallback, useEffect, useMemo, useState } from "react";
import { apiGet, apiPost } from "../services/api";

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

export function useNotifications(pollInterval = 60000) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet("/api/notifications?limit=5");
      if (Array.isArray(data)) {
        setNotifications(data);
      } else if (data?.items) {
        setNotifications(data.items);
      } else {
        setNotifications([]);
      }
      setError(null);
    } catch (err) {
      setNotifications(buildFallbackNotifications());
      const errorMessage = err instanceof Error ? err.message : "عدم دسترسی به سرویس اعلان‌ها";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    if (pollInterval <= 0) {
      return;
    }
    const id = window.setInterval(fetchNotifications, pollInterval);
    return () => window.clearInterval(id);
  }, [fetchNotifications, pollInterval]);

  const unreadCount = useMemo(() => notifications.filter((n) => !n.read).length, [notifications]);

  const markAllAsRead = useCallback(async () => {
    try {
      await apiPost("/api/notifications/mark-read", {});
      setNotifications((prev) => prev.map((item) => ({ ...item, read: true })));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "خطا در به‌روزرسانی اعلان‌ها";
      setError(errorMessage);
    }
  }, []);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    refresh: fetchNotifications,
    markAllAsRead,
  };
}

