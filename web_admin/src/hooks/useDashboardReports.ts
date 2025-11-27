import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { apiGet, isAuthenticated } from "../services/api";

export type OverviewReport = {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
};

export type BranchCount = { branch_name: string; count: number };
export type DepartmentCount = { department_name: string; count: number };
export type TrendPoint = { date: string; count: number };

export type SlaCompliance = {
  total_tickets_with_sla: number;
  escalated_count: number;
  response_compliance_rate: number;
  resolution_compliance_rate: number;
  response_on_time: number;
  response_warning: number;
  response_breached: number;
  resolution_on_time: number;
  resolution_warning: number;
  resolution_breached: number;
};

export type SlaPriorityItem = {
  priority: string;
  total_tickets: number;
  response_compliance_rate: number;
  resolution_compliance_rate: number;
  response_on_time: number;
  response_warning: number;
  response_breached: number;
  resolution_on_time: number;
  resolution_warning: number;
  resolution_breached: number;
};

export type DashboardFilterState = {
  dateFrom?: string;
  dateTo?: string;
  branchId?: string;
  departmentId?: string;
  priority?: string;
};

export type DashboardReports = {
  overview: OverviewReport | null;
  byStatus: Record<string, number>;
  byDate: TrendPoint[];
  byBranch: BranchCount[];
  byPriority: Record<string, number>;
  byDepartment: DepartmentCount[];
  slaCompliance: SlaCompliance | null;
  slaByPriority: SlaPriorityItem[];
  responseHours: number | null;
};

async function fetchDashboardReports(filters: DashboardFilterState): Promise<DashboardReports> {
  const params = new URLSearchParams();
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
  if (filters.branchId) params.set("branch_id", filters.branchId);
  if (filters.departmentId) params.set("department_id", filters.departmentId);
  if (filters.priority) params.set("priority", filters.priority);
  const suffix = params.toString() ? `?${params.toString()}` : "";

  const [
    overview,
    byStatus,
    byDate,
    byBranch,
    byPriority,
    byDepartment,
    slaCompliance,
    slaByPriority,
    responseTime,
  ] = await Promise.all([
    apiGet("/api/reports/overview") as Promise<OverviewReport>,
    apiGet("/api/reports/by-status") as Promise<Record<string, number>>,
    apiGet(`/api/reports/by-date${suffix}`) as Promise<TrendPoint[]>,
    apiGet(`/api/reports/by-branch${suffix}`) as Promise<BranchCount[]>,
    apiGet(`/api/reports/by-priority${suffix}`) as Promise<Record<string, number>>,
    apiGet(`/api/reports/by-department${suffix}`) as Promise<DepartmentCount[]>,
    apiGet("/api/reports/sla-compliance") as Promise<SlaCompliance>,
    apiGet("/api/reports/sla-by-priority") as Promise<SlaPriorityItem[]>,
    apiGet("/api/reports/response-time") as Promise<{ average_response_time_hours?: number }>,
  ]);

  return {
    overview: overview ?? null,
    byStatus,
    byDate,
    byBranch,
    byPriority,
    byDepartment,
    slaCompliance: slaCompliance ?? null,
    slaByPriority,
    responseHours: responseTime?.average_response_time_hours ?? null,
  };
}

export function useDashboardReports(
  filters: DashboardFilterState,
  enabled: boolean
): UseQueryResult<DashboardReports> {
  return useQuery({
    queryKey: [
      "dashboardReports",
      filters.dateFrom ?? "",
      filters.dateTo ?? "",
      filters.branchId ?? "",
      filters.departmentId ?? "",
      filters.priority ?? "",
    ],
    queryFn: () => fetchDashboardReports(filters),
    staleTime: 60_000,
    refetchInterval: 120_000,
    enabled: enabled && isAuthenticated(),
  });
}

