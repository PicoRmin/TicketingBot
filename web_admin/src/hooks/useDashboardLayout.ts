import { useState, useCallback } from "react";

export type DashboardCardId =
  | "kpi-cards"
  | "response-time"
  | "notifications"
  | "status-bar"
  | "status-pie"
  | "date-trend"
  | "priority-bar"
  | "priority-radar"
  | "department-bar"
  | "sla-distribution"
  | "sla-by-priority"
  | "branch-bar";

const DEFAULT_ORDER: DashboardCardId[] = [
  "kpi-cards",
  "response-time",
  "notifications",
  "status-bar",
  "status-pie",
  "date-trend",
  "priority-bar",
  "priority-radar",
  "department-bar",
  "sla-distribution",
  "sla-by-priority",
  "branch-bar",
];

const STORAGE_KEY = "imehr_dashboard_layout";

export function useDashboardLayout() {
  const [cardOrder, setCardOrder] = useState<DashboardCardId[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as DashboardCardId[];
        // Validate: ensure all default cards are present
        const validOrder = DEFAULT_ORDER.filter((id) => parsed.includes(id));
        const missing = DEFAULT_ORDER.filter((id) => !parsed.includes(id));
        return [...validOrder, ...missing];
      }
    } catch {
      // ignore
    }
    return DEFAULT_ORDER;
  });

  const saveOrder = useCallback((newOrder: DashboardCardId[]) => {
    setCardOrder(newOrder);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newOrder));
    } catch {
      // ignore
    }
  }, []);

  const resetOrder = useCallback(() => {
    setCardOrder(DEFAULT_ORDER);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  }, []);

  return {
    cardOrder,
    saveOrder,
    resetOrder,
  };
}

