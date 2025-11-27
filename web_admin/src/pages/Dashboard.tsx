import { useEffect, useMemo, useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, API_BASE_URL, isAuthenticated } from "../services/api";
import { useTranslation } from "react-i18next";
import { stagger, scaleIn } from "../lib/gsap";
import { motion } from "framer-motion";
import type { EChartsOption } from "echarts";
import type { CallbackDataParams, TopLevelFormatterParams } from "echarts/types/dist/shared";
import { useNotificationsQuery, type NotificationItem } from "../hooks/useNotificationsQuery";
import { useChartTheme } from "../hooks/useChartTheme";
import { EChart } from "../components/charts/EChart";
import {
  useDashboardReports,
  type OverviewReport,
  type BranchCount,
  type DepartmentCount,
  type TrendPoint,
  type SlaPriorityItem,
} from "../hooks/useDashboardReports";
import { useAnimatedNumber } from "../hooks/useAnimatedNumber";
import {
  buildCategoryAxis,
  buildGrid,
  buildLegend,
  buildLinearGradient,
  buildTooltip,
  buildValueAxis,
  buildValueXAxis,
  buildToolbox,
  buildHorizontalZoom,
} from "../lib/echartsConfig";

type Branch = { id: number; name: string; code: string };
type Department = { id: number; name: string; code?: string };
type ChartMode = "count" | "percent";
const EMPTY_STATUS: Record<string, number> = {};
const EMPTY_PRIORITY: Record<string, number> = {};
const EMPTY_TRENDS: TrendPoint[] = [];
const EMPTY_BRANCH_COUNTS: BranchCount[] = [];
const EMPTY_DEPARTMENT_COUNTS: DepartmentCount[] = [];
const EMPTY_SLA_PRIORITY: SlaPriorityItem[] = [];

export default function Dashboard() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const chartTheme = useChartTheme();
  const authed = isAuthenticated();
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [branchFilter, setBranchFilter] = useState<string>("");
  const [departmentFilter, setDepartmentFilter] = useState<string>("");
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [branches, setBranches] = useState<Branch[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [chartMode, setChartMode] = useState<ChartMode>("count");
  const [overviewTrend, setOverviewTrend] = useState({
    total: 0,
    pending: 0,
    in_progress: 0,
    resolved: 0,
  });
  const dashboardFilters = useMemo(
    () => ({
      dateFrom: dateFrom || undefined,
      dateTo: dateTo || undefined,
      branchId: branchFilter || undefined,
      departmentId: departmentFilter || undefined,
      priority: priorityFilter || undefined,
    }),
    [branchFilter, dateFrom, dateTo, departmentFilter, priorityFilter]
  );

  const {
    data: reports,
    isLoading: reportsLoading,
    isFetching: reportsFetching,
    error: reportsError,
    refetch: refetchReports,
  } = useDashboardReports(dashboardFilters, authed);

  const {
    notifications: latestNotifications,
    unreadCount,
    loading: notificationsLoading,
    refresh: refreshNotifications,
  } = useNotificationsQuery(120000);

  const overview = reports?.overview ?? null;
  const byStatus = reports?.byStatus ?? EMPTY_STATUS;
  const byDate = reports?.byDate ?? EMPTY_TRENDS;
  const byBranch = reports?.byBranch ?? EMPTY_BRANCH_COUNTS;
  const byPriority = reports?.byPriority ?? EMPTY_PRIORITY;
  const byDepartment = reports?.byDepartment ?? EMPTY_DEPARTMENT_COUNTS;
  const slaCompliance = reports?.slaCompliance ?? null;
  const slaByPriority = reports?.slaByPriority ?? EMPTY_SLA_PRIORITY;
  const responseHours = reports?.responseHours ?? null;
  const error = reportsError instanceof Error ? reportsError.message : null;
  const isInitialLoading = reportsLoading && !overview;
  const isRefreshing = reportsFetching && !!overview;

  useEffect(() => {
    if (!authed) {
      navigate("/login");
    }
  }, [navigate, authed]);

  const loadBranchesAndDepartments = useCallback(async () => {
    try {
      const [branchResponse, departmentResponse] = await Promise.all([
        apiGet(`/api/branches`) as Promise<Branch[]>,
        apiGet(`/api/departments?page_size=100`) as Promise<Department[]>,
      ]);
      setBranches(branchResponse);
      setDepartments(departmentResponse);
    } catch {
      // ignore
    }
  }, []);

  const statsGridRef = useRef<HTMLDivElement>(null);
  const chartsGridRef = useRef<HTMLDivElement>(null);
  const previousOverviewRef = useRef<OverviewReport | null>(null);

  useEffect(() => {
    if (authed) {
      loadBranchesAndDepartments();
    }
  }, [authed, loadBranchesAndDepartments]);

  // Animate stats cards when data loads
  useEffect(() => {
    if (overview && statsGridRef.current) {
      stagger(
        ".stat-card",
        (el) => scaleIn(el, { from: 0.8, to: 1, duration: 0.6 }),
        { stagger: 0.1, delay: 0.2 }
      );
    }
  }, [overview]);

  useEffect(() => {
    if (!overview) {
      return;
    }
    const previous = previousOverviewRef.current;
    if (!previous) {
      previousOverviewRef.current = overview;
      setOverviewTrend({ total: 0, pending: 0, in_progress: 0, resolved: 0 });
      return;
    }
    setOverviewTrend({
      total: overview.total - previous.total,
      pending: overview.pending - previous.pending,
      in_progress: overview.in_progress - previous.in_progress,
      resolved: overview.resolved - previous.resolved,
    });
    previousOverviewRef.current = overview;
  }, [overview]);

  // Animate charts when they load - moved after byStatusData definition

  const getPriorityLabel = useCallback(
    (priority: string) => t(`dashboard.priority.${priority}`, { defaultValue: priority }),
    [t]
  );

  const animatedTotal = useAnimatedNumber(overview?.total ?? 0, { duration: 700 });
  const animatedPending = useAnimatedNumber(overview?.pending ?? 0, { duration: 700 });
  const animatedInProgress = useAnimatedNumber(overview?.in_progress ?? 0, { duration: 700 });
  const animatedResolved = useAnimatedNumber(overview?.resolved ?? 0, { duration: 700 });
  const totalTickets = overview?.total ?? 0;
  const shareLabel = (raw: number) =>
    totalTickets > 0 ? `${((raw / totalTickets) * 100).toFixed(1)}% ${t("dashboard.labels.percent")}` : t("dashboard.labels.count");
  const pendingRatio = totalTickets > 0 ? (overview?.pending ?? 0) / totalTickets : 0;
  const kpiCards = [
    {
      id: "total",
      label: t("dashboard.stats.total"),
      value: animatedTotal,
      raw: overview?.total ?? 0,
      trend: overviewTrend.total,
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      icon: "📈",
      secondary: totalTickets
        ? `${totalTickets.toLocaleString()} ${t("dashboard.labels.count")}`
        : t("dashboard.noData"),
    },
    {
      id: "pending",
      label: t("dashboard.status.pending"),
      value: animatedPending,
      raw: overview?.pending ?? 0,
      trend: overviewTrend.pending,
      gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
      icon: "⏳",
      secondary: shareLabel(overview?.pending ?? 0),
      alert: pendingRatio >= 0.35,
    },
    {
      id: "in_progress",
      label: t("dashboard.status.in_progress"),
      value: animatedInProgress,
      raw: overview?.in_progress ?? 0,
      trend: overviewTrend.in_progress,
      gradient: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
      icon: "⚙️",
      secondary: shareLabel(overview?.in_progress ?? 0),
    },
    {
      id: "resolved",
      label: t("dashboard.status.resolved"),
      value: animatedResolved,
      raw: overview?.resolved ?? 0,
      trend: overviewTrend.resolved,
      gradient: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
      icon: "✅",
      secondary: shareLabel(overview?.resolved ?? 0),
      tone: "success",
    },
  ];

  const isPercentMode = chartMode === "percent";

  const statusTotal = useMemo(() => Object.values(byStatus).reduce((sum, value) => sum + value, 0), [byStatus]);
  const priorityTotal = useMemo(() => Object.values(byPriority).reduce((sum, value) => sum + value, 0), [byPriority]);

  const formatValue = useCallback(
    (value: number, total: number) => {
      if (!isPercentMode || total === 0) {
        return value;
      }
      return Number(((value / total) * 100).toFixed(2));
    },
    [isPercentMode]
  );

  const singleTooltipParam = useCallback(
    (params: TopLevelFormatterParams): CallbackDataParams | undefined =>
      Array.isArray(params) ? params[0] : params,
    []
  );

  const byStatusData = useMemo(
    () =>
      Object.entries(byStatus).map(([status, count]) => ({
      status: t(`dashboard.status.${status}`, { defaultValue: status }),
        value: formatValue(count, statusTotal),
        raw: count,
        percent: statusTotal ? (count / statusTotal) * 100 : 0,
    })),
    [byStatus, formatValue, statusTotal, t]
  );

  const byPriorityData = useMemo(
    () =>
      Object.entries(byPriority).map(([priority, count]) => ({
      priority: getPriorityLabel(priority),
        value: formatValue(count, priorityTotal),
        raw: count,
        percent: priorityTotal ? (count / priorityTotal) * 100 : 0,
      })),
    [byPriority, formatValue, getPriorityLabel, priorityTotal]
  );

  const renderNoData = (height = 260) => (
    <div
      style={{
        height,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "var(--fg-secondary)",
        fontSize: 14,
      }}
    >
      {t("dashboard.noData")}
    </div>
  );

  const renderTrendBadge = (diff: number) => {
    if (diff === 0) {
      return <span className="stat-trend neutral">= 0</span>;
    }
    const positive = diff > 0;
    return (
      <span className={`stat-trend ${positive ? "up" : "down"}`}>
        {positive ? "▲" : "▼"} {Math.abs(diff)}
      </span>
    );
  };

  const statusBarOption = useMemo<EChartsOption>(() => {
    const categories = byStatusData.map((d) => d.status);
    const values = byStatusData.map((d) => d.value);
    return {
      grid: buildGrid(),
      tooltip: buildTooltip(chartTheme, {
        formatter: (params: TopLevelFormatterParams) => {
          const single = singleTooltipParam(params);
          if (!single || typeof single.dataIndex !== "number") {
            return "";
          }
          const datum = byStatusData[single.dataIndex];
          if (!datum) return "";
          return `${datum.status}: ${datum.value}${isPercentMode ? "%" : ""} (${datum.raw})`;
        },
      }),
      toolbox: buildToolbox(chartTheme),
      xAxis: buildCategoryAxis(categories, chartTheme),
      yAxis: buildValueAxis(chartTheme, isPercentMode ? { max: 100, axisLabel: { formatter: "{value}%" } } : {}),
      series: [
        {
          type: "bar",
          barWidth: 32,
          data: values,
          itemStyle: {
            borderRadius: [12, 12, 4, 4],
            color: buildLinearGradient([chartTheme.palette[0], chartTheme.palette[1]]),
            shadowBlur: 10,
            shadowColor: "rgba(15,23,42,0.15)",
          },
        },
      ],
    };
  }, [byStatusData, chartTheme, isPercentMode, singleTooltipParam]);

  const statusPieOption = useMemo<EChartsOption>(() => ({
    tooltip: buildTooltip(chartTheme, {
      trigger: "item",
      formatter: (params: TopLevelFormatterParams) => {
        const single = singleTooltipParam(params);
        if (!single || typeof single.dataIndex !== "number") {
          return Array.isArray(params) ? "" : params.name || "";
        }
        const datum = byStatusData[single.dataIndex];
        if (!datum) {
          return single.name || "";
        }
        return `${datum.status}: ${datum.raw} (${datum.percent.toFixed(1)}%)`;
      },
    }),
    legend: buildLegend(chartTheme, { bottom: 0 }),
    toolbox: buildToolbox(chartTheme),
    series: [
      {
        name: t("dashboard.charts.statusPie"),
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        labelLine: { smooth: true, lineStyle: { color: chartTheme.border } },
        label: {
          formatter: (params: CallbackDataParams) => {
            const rawValue =
              typeof params.value === "number"
                ? params.value
                : Array.isArray(params.value)
                ? params.value[0]
                : params.value ?? 0;
            const meta = Array.isArray(params.data)
              ? (params.data[0] as { percent?: number })
              : (params.data as { percent?: number } | undefined);
            const pct = typeof meta?.percent === "number" ? meta.percent : params.percent ?? 0;
            return `${params.name}\n${rawValue} (${pct.toFixed(1)}%)`;
          },
          color: chartTheme.foreground,
        },
        data: byStatusData.map((item, index) => ({
          value: item.raw,
          raw: item.raw,
          percent: item.percent,
          name: item.status,
          itemStyle: { color: chartTheme.palette[index % chartTheme.palette.length] },
        })),
      },
    ],
  }), [byStatusData, chartTheme, singleTooltipParam, t]);

  const dateTrendOption = useMemo<EChartsOption>(() => ({
    grid: buildGrid({ bottom: 70 }),
    tooltip: buildTooltip(chartTheme),
    toolbox: buildToolbox(chartTheme),
    xAxis: buildCategoryAxis(
      byDate.map((d) => d.date),
      chartTheme,
      {
        boundaryGap: false,
        axisLabel: { rotate: 45, fontSize: 11, color: chartTheme.muted },
      }
    ),
    yAxis: buildValueAxis(chartTheme),
    dataZoom: buildHorizontalZoom(),
    series: [
      {
        type: "line",
        data: byDate.map((d) => d.count),
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { width: 3, color: chartTheme.palette[1] },
        itemStyle: { color: chartTheme.palette[1] },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: chartTheme.palette[1] },
              { offset: 1, color: "rgba(34,197,94,0.05)" },
            ],
          },
        },
      },
    ],
  }), [byDate, chartTheme]);

  const priorityBarOption = useMemo<EChartsOption>(() => ({
    grid: buildGrid(),
    tooltip: buildTooltip(chartTheme, {
      formatter: (params: TopLevelFormatterParams) => {
        const single = singleTooltipParam(params);
        if (!single || typeof single.dataIndex !== "number") {
          return "";
        }
        const datum = byPriorityData[single.dataIndex];
        if (!datum) return "";
        return `${datum.priority}: ${datum.value}${isPercentMode ? "%" : ""} (${datum.raw})`;
      },
    }),
    toolbox: buildToolbox(chartTheme),
    xAxis: buildCategoryAxis(byPriorityData.map((d) => d.priority), chartTheme),
    yAxis: buildValueAxis(
      chartTheme,
      isPercentMode ? { max: 100, axisLabel: { formatter: "{value}%" } } : {}
    ),
    series: [
      {
        type: "bar",
        data: byPriorityData.map((d) => d.value),
        itemStyle: {
          borderRadius: [12, 12, 0, 0],
          color: (params: CallbackDataParams) => chartTheme.palette[params.dataIndex % chartTheme.palette.length],
        },
      },
    ],
  }), [byPriorityData, chartTheme, isPercentMode, singleTooltipParam]);

  const priorityRadarOption = useMemo<EChartsOption>(() => {
    if (byPriorityData.length === 0) {
      return { series: [] };
    }
    const maxValue = Math.max(...byPriorityData.map((d) => d.value), 10);
    return {
      tooltip: buildTooltip(chartTheme, {
        trigger: "item",
        formatter: (params: TopLevelFormatterParams) => {
          const single = singleTooltipParam(params);
          if (!single || typeof single.dataIndex !== "number") {
            return "";
          }
          const datum = byPriorityData[single.dataIndex];
          if (!datum) return "";
          return `${datum.priority}: ${datum.value}${isPercentMode ? "%" : ""} (${datum.raw})`;
        },
      }),
      toolbox: buildToolbox(chartTheme),
      radar: {
        indicator: byPriorityData.map((item) => ({
          name: item.priority,
          max: Math.ceil(maxValue * 1.2),
        })),
        splitLine: { lineStyle: { color: ["rgba(99,102,241,0.3)", "rgba(99,102,241,0.15)"] } },
        splitArea: { areaStyle: { color: ["rgba(99,102,241,0.12)", "rgba(99,102,241,0.04)"] } },
        axisName: { color: chartTheme.muted },
        axisLine: { lineStyle: { color: chartTheme.grid } },
      },
      series: [
        {
          type: "radar",
          areaStyle: { color: "rgba(99,102,241,0.4)" },
          lineStyle: { color: chartTheme.palette[0], width: 2 },
          data: [
            {
              value: byPriorityData.map((d) => d.value),
              name: isPercentMode ? t("dashboard.labels.percent") : t("dashboard.labels.count"),
            },
          ],
        },
      ],
    };
  }, [byPriorityData, chartTheme, isPercentMode, singleTooltipParam, t]);

  const departmentBarOption = useMemo<EChartsOption>(() => ({
    grid: buildGrid({ left: 150, bottom: 20 }),
    tooltip: buildTooltip(chartTheme),
    toolbox: buildToolbox(chartTheme),
    xAxis: buildValueXAxis(chartTheme),
    yAxis: {
      type: "category",
      data: byDepartment.map((d) => d.department_name),
      axisLabel: { color: chartTheme.muted },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: chartTheme.border } },
    },
    series: [
      {
        type: "bar",
        data: byDepartment.map((d) => d.count),
        barWidth: 18,
        itemStyle: {
          borderRadius: [0, 12, 12, 0],
          color: buildLinearGradient([chartTheme.palette[2], chartTheme.palette[3]]),
        },
      },
    ],
  }), [byDepartment, chartTheme]);

  const branchBarOption = useMemo<EChartsOption>(() => ({
    grid: buildGrid({ bottom: 80 }),
    tooltip: buildTooltip(chartTheme),
    toolbox: buildToolbox(chartTheme),
    xAxis: buildCategoryAxis(
      byBranch.map((d) => d.branch_name),
      chartTheme,
      {
        axisLabel: { rotate: 35, fontSize: 11, color: chartTheme.muted },
      }
    ),
    yAxis: buildValueAxis(chartTheme),
    series: [
      {
        type: "bar",
        data: byBranch.map((d) => d.count),
        itemStyle: {
          borderRadius: [10, 10, 0, 0],
          color: buildLinearGradient(["#f59e0b", "#d97706"]),
        },
      },
    ],
  }), [byBranch, chartTheme]);

  const slaDistributionOption = useMemo<EChartsOption>(() => {
    if (!slaCompliance) {
      return { series: [] };
    }
    const pieData = [
      { name: t("dashboard.slaPie.onTime"), value: (slaCompliance.response_on_time || 0) + (slaCompliance.resolution_on_time || 0), color: chartTheme.success },
      { name: t("dashboard.slaPie.warning"), value: (slaCompliance.response_warning || 0) + (slaCompliance.resolution_warning || 0), color: chartTheme.warning },
      { name: t("dashboard.slaPie.breached"), value: (slaCompliance.response_breached || 0) + (slaCompliance.resolution_breached || 0), color: chartTheme.danger },
    ];
    return {
    tooltip: buildTooltip(chartTheme, { trigger: "item", formatter: "{b}: {c} ({d}%)" }),
      legend: buildLegend(chartTheme, { bottom: 0 }),
    toolbox: buildToolbox(chartTheme),
      series: [
        {
          type: "pie",
          radius: ["45%", "70%"],
          label: { formatter: "{b}\n{d}%", color: chartTheme.foreground },
          labelLine: { length: 15, length2: 10 },
          data: pieData.map((item) => ({
            value: item.value,
            name: item.name,
            itemStyle: { color: item.color },
          })),
        },
      ],
    };
  }, [slaCompliance, chartTheme, t]);

  const slaByPriorityOption = useMemo<EChartsOption>(() => ({
    grid: buildGrid(),
    tooltip: buildTooltip(chartTheme),
    toolbox: buildToolbox(chartTheme),
    legend: buildLegend(chartTheme, { top: 0 }),
    xAxis: buildCategoryAxis(
      slaByPriority.map((item) => getPriorityLabel(item.priority)),
      chartTheme
    ),
    yAxis: buildValueAxis(chartTheme, { max: 100 }),
    series: [
      {
        name: t("dashboard.slaCards.responseRate"),
        type: "bar",
        data: slaByPriority.map((item) => item.response_compliance_rate || 0),
        itemStyle: { color: chartTheme.palette[0] },
      },
      {
        name: t("dashboard.slaCards.resolutionRate"),
        type: "bar",
        data: slaByPriority.map((item) => item.resolution_compliance_rate || 0),
        itemStyle: { color: chartTheme.palette[1] },
      },
    ],
  }), [slaByPriority, chartTheme, t, getPriorityLabel]);

  if (!authed) {
    return null;
  }

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>{t("dashboard.title")}</h1>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              onClick={() => setChartMode((mode) => (mode === "count" ? "percent" : "count"))}
              className={isPercentMode ? "primary" : "secondary"}
              style={{ padding: "8px 16px" }}
              aria-pressed={isPercentMode}
              title={isPercentMode ? t("dashboard.modes.count") : t("dashboard.modes.percent")}
            >
              {isPercentMode ? t("dashboard.modes.count") : t("dashboard.modes.percent")}
            </button>
          <button 
            onClick={() => setShowFilters(!showFilters)} 
            className="secondary"
            style={{ padding: "8px 16px" }}
          >
            {showFilters ? t("dashboard.buttons.closeFilters") : t("dashboard.buttons.openFilters")}
          </button>
        <button
          onClick={() => void refetchReports()}
          disabled={isInitialLoading || isRefreshing}
          className="secondary"
        >
          {isInitialLoading || isRefreshing ? t("dashboard.buttons.loading") : t("dashboard.buttons.refresh")}
        </button>
          <button 
            onClick={async () => {
              try {
                const params = new URLSearchParams();
                if (dateFrom) params.set("date_from", dateFrom);
                if (dateTo) params.set("date_to", dateTo);
                if (branchFilter) params.set("branch_id", branchFilter);
                if (departmentFilter) params.set("department_id", departmentFilter);
                if (priorityFilter) params.set("priority", priorityFilter);
                
                const token = localStorage.getItem('imehr_token');
                const response = await fetch(`${API_BASE_URL}/api/reports/export-pdf?${params.toString()}`, {
                  headers: {
                    'Authorization': `Bearer ${token}`
                  }
                });
                if (response.ok) {
                  const blob = await response.blob();
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `dashboard-report-${new Date().toISOString().split('T')[0]}.pdf`;
                  document.body.appendChild(a);
                  a.click();
                  window.URL.revokeObjectURL(url);
                  document.body.removeChild(a);
                } else {
                  alert(t("dashboard.errors.pdf"));
                }
              } catch (e) {
                alert(t("dashboard.errors.pdf"));
              }
            }}
            className="primary"
            style={{ padding: "8px 16px" }}
          >
            {t("dashboard.buttons.exportPdf")}
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="card" style={{ marginBottom: 24, background: "var(--bg-secondary)" }}>
          <div className="card-header">
            <h2 className="card-title" style={{ fontSize: 18 }}>{t("dashboard.filters.title")}</h2>
          </div>
          <div className="filters" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 500 }}>{t("dashboard.filters.dateFrom")}</label>
              <input 
                type="date" 
                value={dateFrom} 
                onChange={(e) => setDateFrom(e.target.value)}
                style={{ width: "100%" }}
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 500 }}>{t("dashboard.filters.dateTo")}</label>
              <input 
                type="date" 
                value={dateTo} 
                onChange={(e) => setDateTo(e.target.value)}
                style={{ width: "100%" }}
              />
            </div>
            {branches.length > 0 && (
              <div>
                <label style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 500 }}>{t("dashboard.filters.branch")}</label>
                <select
                  value={branchFilter}
                  onChange={(e) => setBranchFilter(e.target.value)}
                  style={{ width: "100%" }}
                >
                  <option value="">{t("dashboard.filters.allBranches")}</option>
                  {branches.map((b) => (
                    <option key={b.id} value={String(b.id)}>
                      {b.name} ({b.code})
                    </option>
                  ))}
                </select>
              </div>
            )}
            {departments.length > 0 && (
              <div>
                <label style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 500 }}>{t("dashboard.filters.department")}</label>
                <select
                  value={departmentFilter}
                  onChange={(e) => setDepartmentFilter(e.target.value)}
                  style={{ width: "100%" }}
                >
                  <option value="">{t("dashboard.filters.allDepartments")}</option>
                  {departments.map((d) => (
                    <option key={d.id} value={String(d.id)}>
                      {d.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 500 }}>{t("dashboard.filters.priority")}</label>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                style={{ width: "100%" }}
              >
                <option value="">{t("dashboard.filters.allPriorities")}</option>
                <option value="critical">{t("dashboard.priority.critical")}</option>
                <option value="high">{t("dashboard.priority.high")}</option>
                <option value="medium">{t("dashboard.priority.medium")}</option>
                <option value="low">{t("dashboard.priority.low")}</option>
              </select>
            </div>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 8 }}>
              <button
                onClick={() => {
                  setDateFrom("");
                  setDateTo("");
                  setBranchFilter("");
                  setDepartmentFilter("");
                  setPriorityFilter("");
                }}
                className="secondary"
                style={{ padding: "8px 16px" }}
              >
                {t("dashboard.filters.clear")}
              </button>
            </div>
          </div>
        </div>
      )}

      {isInitialLoading && (
        <div style={{ textAlign: "center", padding: 40 }}>
          <div className="loading" style={{ margin: "0 auto" }}></div>
          <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>{t("dashboard.loading")}</p>
        </div>
      )}

      {error && (
        <div className="alert error fade-in">
          <strong>{t("dashboard.errorLabel")} </strong> {error}
        </div>
      )}

      {overview && (
        <>
          {/* Stats Cards */}
          <div ref={statsGridRef} className="dashboard-grid dashboard-grid--stats" style={{ marginBottom: 24 }}>
            {kpiCards.map((card) => {
              const classes = ["stat-card"];
              if (card.alert) classes.push("stat-card--alert");
              if (card.tone === "success") classes.push("stat-card--success");
              return (
                <motion.div
                  key={card.id}
                  className={classes.join(" ")}
                  style={{ background: card.gradient }}
                  whileHover={{ translateY: -6, scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 260, damping: 20 }}
                >
                  <div className="stat-card__icon" aria-hidden="true">
                    {card.icon}
                  </div>
                  <div className="stat-label">{card.label}</div>
                  <div className="stat-value">{card.value.toLocaleString()}</div>
                  <div className="stat-card__meta">
                    {renderTrendBadge(card.trend)}
                    <span className="stat-card__hint">{card.secondary}</span>
                  </div>
                </motion.div>
              );
            })}
          </div>

          <div className="dashboard-grid dashboard-grid--two" style={{ marginBottom: 24 }}>
            <div className="card" style={{ minHeight: 180 }}>
              <div className="card-header">
                <h2 className="card-title">{t("dashboard.cards.responseTime")}</h2>
              </div>
              <div style={{ fontSize: 48, fontWeight: 700, color: "var(--primary)", textAlign: "center", padding: "20px 0" }}>
                {responseHours !== null ? (
                  <>
                    {responseHours.toFixed(2)} <span style={{ fontSize: 24, color: "var(--fg-secondary)" }}>{t("dashboard.cards.hours")}</span>
                  </>
                ) : (
                  <span style={{ fontSize: 18, color: "var(--fg-secondary)" }}>داده‌ای موجود نیست</span>
                )}
              </div>
            </div>
            <div className="card notifications-card">
              <div className="card-header">
                <h2 className="card-title">اعلان‌ها</h2>
                <button
                  className="secondary"
                  style={{ padding: "6px 12px" }}
                  onClick={() => void refreshNotifications()}
                  disabled={notificationsLoading}
                >
                  {notificationsLoading ? t("dashboard.buttons.loading") : t("dashboard.buttons.refresh")}
                </button>
              </div>
              <div className="notifications-panel">
                {notificationsLoading && (
                  <div className="notification-bell__loading">
                    <div className="loading" />
                  </div>
                )}
                {!notificationsLoading && latestNotifications.length === 0 && (
                  <p className="notification-bell__empty">اعلان فعالی وجود ندارد.</p>
                )}
                {latestNotifications.slice(0, 4).map((notif: NotificationItem) => (
                  <div key={notif.id} className={`notification-item notification-item--${notif.severity || "info"}`}>
                    <div className="notification-item__title">
                      {notif.title}
                      {!notif.read && <span className="notification-item__dot" />}
                    </div>
                    <div className="notification-item__body">{notif.body}</div>
                    <div className="notification-item__time">
                      {new Date(notif.created_at).toLocaleString("fa-IR", { hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>
                ))}
                {unreadCount > 0 && (
                  <div className="notification-panel__footer">
                    <span>{unreadCount} اعلان خوانده‌نشده</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Status Charts - Bar and Pie */}
          <div ref={chartsGridRef} className="grid grid-cols-1 lg:grid-cols-2" style={{ gap: 24, marginBottom: 24 }}>
            {/* Bar Chart */}
            <div className="card">
            <div className="card-header">
              <h2 className="card-title">{t("dashboard.charts.statusTitle")}</h2>
              <a 
                href={`${API_BASE_URL}/api/reports/export?kind=by-status`} 
                target="_blank" 
                rel="noreferrer"
                style={{ fontSize: 14 }}
              >
                {t("dashboard.actions.exportCsv")}
              </a>
            </div>
            <div style={{ width: "100%", height: 300 }}>
              {byStatusData.length > 0 ? (
                <EChart option={statusBarOption} height={300} ariaLabel={t("dashboard.charts.statusTitle")} />
              ) : (
                renderNoData(300)
              )}
            </div>
          </div>

            {/* Pie Chart */}
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">{t("dashboard.charts.statusPie")}</h2>
              </div>
              <div style={{ width: "100%", height: 300 }}>
                {byStatusData.length > 0 ? (
                  <EChart option={statusPieOption} height={300} ariaLabel={t("dashboard.charts.statusPie")} />
                ) : (
                  renderNoData(300)
                )}
              </div>
            </div>
          </div>

          {/* Date Chart - Area and Line */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <h2 className="card-title">{t("dashboard.charts.dateTrend")}</h2>
              <a 
                href={`${API_BASE_URL}/api/reports/export?kind=by-date`} 
                target="_blank" 
                rel="noreferrer"
                style={{ fontSize: 14 }}
              >
                {t("dashboard.actions.exportCsv")}
              </a>
            </div>
            <div style={{ width: "100%", height: 350 }}>
              {byDate.length > 0 ? (
                <EChart option={dateTrendOption} height={350} ariaLabel={t("dashboard.charts.dateTrend")} />
              ) : (
                renderNoData(350)
              )}
            </div>
          </div>

          {/* Priority Charts - Bar and Radar */}
          {byPriorityData.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2" style={{ gap: 24, marginBottom: 24 }}>
              {/* Bar Chart */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">{t("dashboard.charts.priorityBar")}</h2>
                  <a 
                    href={`${API_BASE_URL}/api/reports/export?kind=by-priority`} 
                    target="_blank" 
                    rel="noreferrer"
                    style={{ fontSize: 14 }}
                  >
                    {t("dashboard.actions.exportCsv")}
                  </a>
                </div>
                <div style={{ width: "100%", height: 300 }}>
                {byPriorityData.length > 0 ? (
                  <EChart option={priorityBarOption} height={300} ariaLabel={t("dashboard.charts.priorityBar")} />
                ) : (
                  renderNoData(300)
                )}
                </div>
              </div>

              {/* Radar Chart */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">{t("dashboard.charts.priorityComparison")}</h2>
                </div>
                <div style={{ width: "100%", height: 300 }}>
                  {byPriorityData.length > 0 ? (
                    <EChart option={priorityRadarOption} height={300} ariaLabel={t("dashboard.charts.priorityComparison")} />
                  ) : (
                    renderNoData(300)
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Department Chart */}
          {byDepartment.length > 0 && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">{t("dashboard.charts.department")}</h2>
                <a 
                  href={`${API_BASE_URL}/api/reports/export?kind=by-department`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ fontSize: 14 }}
                >
                  {t("dashboard.actions.exportCsv")}
                </a>
              </div>
              <div style={{ width: "100%", height: 350 }}>
                {byDepartment.length > 0 ? (
                  <EChart option={departmentBarOption} height={350} ariaLabel={t("dashboard.charts.department")} />
                ) : (
                  renderNoData(350)
                )}
              </div>
            </div>
          )}

          {/* SLA Compliance Card with Charts */}
          {slaCompliance && slaCompliance.total_tickets_with_sla > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2" style={{ gap: 24, marginBottom: 24 }}>
              {/* SLA Stats */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">{t("dashboard.charts.slaCompliance")}</h2>
                  <a 
                    href={`${API_BASE_URL}/api/reports/export?kind=sla-compliance`} 
                    target="_blank" 
                    rel="noreferrer"
                    style={{ fontSize: 14 }}
                  >
                    {t("dashboard.actions.exportCsv")}
                  </a>
                </div>
                <div className="grid grid-cols-2" style={{ gap: 16, marginBottom: 16 }}>
                  <div style={{ 
                    padding: 16, 
                    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    borderRadius: "var(--radius)",
                    color: "white"
                  }}>
                    <div style={{ fontSize: 12, opacity: 0.9, marginBottom: 4 }}>{t("dashboard.slaCards.totalSla")}</div>
                    <div style={{ fontSize: 28, fontWeight: 700 }}>{slaCompliance.total_tickets_with_sla}</div>
                  </div>
                  <div style={{ 
                    padding: 16, 
                    background: slaCompliance.escalated_count > 0 
                      ? "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
                      : "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                    borderRadius: "var(--radius)",
                    color: "white"
                  }}>
                    <div style={{ fontSize: 12, opacity: 0.9, marginBottom: 4 }}>{t("dashboard.slaCards.escalated")}</div>
                    <div style={{ fontSize: 28, fontWeight: 700 }}>
                      {slaCompliance.escalated_count}
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2" style={{ gap: 16 }}>
                  <div style={{ 
                    padding: 12, 
                    background: "var(--bg-secondary)", 
                    borderRadius: "var(--radius)",
                    border: "2px solid",
                    borderColor: slaCompliance.response_compliance_rate >= 80 ? "var(--success)" : "var(--warning)"
                  }}>
                    <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>{t("dashboard.slaCards.responseRate")}</div>
                    <div style={{ fontSize: 24, fontWeight: 700, color: slaCompliance.response_compliance_rate >= 80 ? "var(--success)" : "var(--warning)" }}>
                      {slaCompliance.response_compliance_rate}%
                    </div>
                    <div style={{ fontSize: 11, color: "var(--fg-secondary)", marginTop: 4 }}>
                      ✅ {slaCompliance.response_on_time || 0} | ⚠️ {slaCompliance.response_warning || 0} | ❌ {slaCompliance.response_breached || 0}
                    </div>
                  </div>
                  <div style={{ 
                    padding: 12, 
                    background: "var(--bg-secondary)", 
                    borderRadius: "var(--radius)",
                    border: "2px solid",
                    borderColor: slaCompliance.resolution_compliance_rate >= 80 ? "var(--success)" : "var(--warning)"
                  }}>
                    <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>{t("dashboard.slaCards.resolutionRate")}</div>
                    <div style={{ fontSize: 24, fontWeight: 700, color: slaCompliance.resolution_compliance_rate >= 80 ? "var(--success)" : "var(--warning)" }}>
                      {slaCompliance.resolution_compliance_rate}%
                    </div>
                    <div style={{ fontSize: 11, color: "var(--fg-secondary)", marginTop: 4 }}>
                      ✅ {slaCompliance.resolution_on_time || 0} | ⚠️ {slaCompliance.resolution_warning || 0} | ❌ {slaCompliance.resolution_breached || 0}
                    </div>
                  </div>
                </div>
              </div>

              {/* SLA Pie Chart */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">{t("dashboard.charts.slaDistribution")}</h2>
                </div>
                <div style={{ width: "100%", height: 300 }}>
                  {slaCompliance ? (
                    <EChart option={slaDistributionOption} height={300} ariaLabel={t("dashboard.charts.slaDistribution")} />
                  ) : (
                    renderNoData(300)
                  )}
                </div>
              </div>
            </div>
          )}

          {/* SLA by Priority - Chart and Table */}
          {slaByPriority.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2" style={{ gap: 24, marginBottom: 24 }}>
              {/* Chart */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">{t("dashboard.charts.slaByPriority")}</h2>
                </div>
                <div style={{ width: "100%", height: 300 }}>
                {slaByPriority.length > 0 ? (
                  <EChart option={slaByPriorityOption} height={300} ariaLabel={t("dashboard.charts.slaByPriority")} />
                ) : (
                  renderNoData(300)
                )}
            </div>
          </div>

              {/* Table */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">{t("dashboard.charts.slaTable")}</h2>
                </div>
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%" }}>
                    <thead>
                      <tr>
                        <th>{t("dashboard.table.priority")}</th>
                        <th>{t("dashboard.table.count")}</th>
                        <th>{t("dashboard.table.responseRate")}</th>
                        <th>{t("dashboard.table.resolutionRate")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {slaByPriority.map((item, idx) => (
                        <tr key={idx}>
                          <td>
                            {getPriorityLabel(item.priority)}
                          </td>
                          <td style={{ fontWeight: 600 }}>{item.total_tickets}</td>
                          <td>
                            <span style={{ 
                              color: item.response_compliance_rate >= 80 ? "var(--success)" : "var(--warning)",
                              fontWeight: 600
                            }}>
                              {item.response_compliance_rate}%
                            </span>
                            <div style={{ fontSize: 10, color: "var(--fg-secondary)", marginTop: 2 }}>
                              ✅{item.response_on_time} ⚠️{item.response_warning || 0} ❌{item.response_breached}
                            </div>
                          </td>
                          <td>
                            <span style={{ 
                              color: item.resolution_compliance_rate >= 80 ? "var(--success)" : "var(--warning)",
                              fontWeight: 600
                            }}>
                              {item.resolution_compliance_rate}%
                            </span>
                            <div style={{ fontSize: 10, color: "var(--fg-secondary)", marginTop: 2 }}>
                              ✅{item.resolution_on_time} ⚠️{item.resolution_warning || 0} ❌{item.resolution_breached}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Branch Chart */}
          {byBranch.length > 0 && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">{t("dashboard.charts.branch")}</h2>
                <a 
                  href={`${API_BASE_URL}/api/reports/export?kind=by-branch`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ fontSize: 14 }}
                >
                  {t("dashboard.actions.exportCsv")}
                </a>
              </div>
              <div style={{ width: "100%", height: 350 }}>
                {byBranch.length > 0 ? (
                  <EChart option={branchBarOption} height={350} ariaLabel={t("dashboard.charts.branch")} />
                ) : (
                  renderNoData(350)
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
