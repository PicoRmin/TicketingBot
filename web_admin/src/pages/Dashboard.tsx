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
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from "@dnd-kit/core";
import { SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { SortableCard } from "../components/dashboard/SortableCard";
import { useDashboardLayout, type DashboardCardId } from "../hooks/useDashboardLayout";
import { BranchStatusBar } from "../components/dashboard/BranchStatusBar";
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
  buildAnimationConfig,
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
  const { cardOrder, saveOrder } = useDashboardLayout();
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

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = cardOrder.indexOf(active.id as DashboardCardId);
      const newIndex = cardOrder.indexOf(over.id as DashboardCardId);
      const newOrder = [...cardOrder];
      newOrder.splice(oldIndex, 1);
      newOrder.splice(newIndex, 0, active.id as DashboardCardId);
      saveOrder(newOrder);
    }
  };
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

  // Animate charts when they load with GSAP fade-in + scale
  useEffect(() => {
    if (chartsGridRef.current && (byStatusData.length > 0 || byDate.length > 0)) {
      const chartCards = chartsGridRef.current.querySelectorAll(".card");
      if (chartCards.length > 0) {
        stagger(
          chartCards,
          (el) => scaleIn(el, { from: 0.85, to: 1, duration: 0.65 }),
          { stagger: 0.12, delay: 0.3 }
        );
      }
    }
  }, [byStatusData.length, byDate.length]);

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
      ...buildAnimationConfig(),
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
    ...buildAnimationConfig(),
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
    ...buildAnimationConfig(),
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
    ...buildAnimationConfig(),
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
      ...buildAnimationConfig(),
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
    ...buildAnimationConfig(),
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
    ...buildAnimationConfig(),
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
      ...buildAnimationConfig(),
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
    ...buildAnimationConfig(),
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

  // Helper function to render card content by ID
  const renderCardContent = (cardId: DashboardCardId) => {
    switch (cardId) {
      case "kpi-cards":
        return (
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
        );
      case "response-time":
        return (
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
        );
      case "notifications":
        return (
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
        );
      case "status-bar":
        return (
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
        );
      case "status-pie":
        return (
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
        );
      case "date-trend":
        return (
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
        );
      case "priority-bar":
        return byPriorityData.length > 0 ? (
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
              <EChart option={priorityBarOption} height={300} ariaLabel={t("dashboard.charts.priorityBar")} />
            </div>
          </div>
        ) : null;
      case "priority-radar":
        return byPriorityData.length > 0 ? (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">{t("dashboard.charts.priorityComparison")}</h2>
            </div>
            <div style={{ width: "100%", height: 300 }}>
              <EChart option={priorityRadarOption} height={300} ariaLabel={t("dashboard.charts.priorityComparison")} />
            </div>
          </div>
        ) : null;
      case "department-bar":
        return byDepartment.length > 0 ? (
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
              <EChart option={departmentBarOption} height={350} ariaLabel={t("dashboard.charts.department")} />
            </div>
          </div>
        ) : null;
      case "sla-distribution":
        return slaCompliance && slaCompliance.total_tickets_with_sla > 0 ? (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">{t("dashboard.charts.slaDistribution")}</h2>
            </div>
            <div style={{ width: "100%", height: 300 }}>
              <EChart option={slaDistributionOption} height={300} ariaLabel={t("dashboard.charts.slaDistribution")} />
            </div>
          </div>
        ) : null;
      case "sla-by-priority":
        return slaByPriority.length > 0 ? (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">{t("dashboard.charts.slaByPriority")}</h2>
            </div>
            <div style={{ width: "100%", height: 300 }}>
              <EChart option={slaByPriorityOption} height={300} ariaLabel={t("dashboard.charts.slaByPriority")} />
            </div>
          </div>
        ) : null;
      case "branch-bar":
        return byBranch.length > 0 ? (
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
              <EChart option={branchBarOption} height={350} ariaLabel={t("dashboard.charts.branch")} />
            </div>
          </div>
        ) : null;
      default:
        return null;
    }
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
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
        <SortableContext items={cardOrder} strategy={verticalListSortingStrategy}>
          <div ref={chartsGridRef}>
            {cardOrder.map((cardId) => {
              const content = renderCardContent(cardId);
              if (!content) return null;
              
              // Special handling for cards that should be in a grid
              if (cardId === "response-time" || cardId === "notifications") {
                return (
                  <div key={cardId} className="dashboard-grid dashboard-grid--two" style={{ marginBottom: 24 }}>
                    {cardId === "response-time" && (
                      <SortableCard id={cardId}>{renderCardContent("response-time")}</SortableCard>
                    )}
                    {cardId === "notifications" && (
                      <SortableCard id={cardId}>{renderCardContent("notifications")}</SortableCard>
                    )}
                  </div>
                );
              }
              
              if (cardId === "status-bar" || cardId === "status-pie") {
                return (
                  <div key={`grid-${cardId}`} className="grid grid-cols-1 lg:grid-cols-2" style={{ gap: 24, marginBottom: 24 }}>
                    {cardId === "status-bar" && (
                      <SortableCard id={cardId}>{renderCardContent("status-bar")}</SortableCard>
                    )}
                    {cardId === "status-pie" && (
                      <SortableCard id={cardId}>{renderCardContent("status-pie")}</SortableCard>
                    )}
                  </div>
                );
              }
              
              if (cardId === "priority-bar" || cardId === "priority-radar") {
                return byPriorityData.length > 0 ? (
                  <div key={`grid-${cardId}`} className="grid grid-cols-1 lg:grid-cols-2" style={{ gap: 24, marginBottom: 24 }}>
                    {cardId === "priority-bar" && (
                      <SortableCard id={cardId}>{renderCardContent("priority-bar")}</SortableCard>
                    )}
                    {cardId === "priority-radar" && (
                      <SortableCard id={cardId}>{renderCardContent("priority-radar")}</SortableCard>
                    )}
                  </div>
                ) : null;
              }
              
              return <SortableCard key={cardId} id={cardId}>{content}</SortableCard>;
            })}
          </div>
        </SortableContext>
      )}
        {/* Live Branch Status Bar */}
        <BranchStatusBar enabled={authed} />
      </div>
    </DndContext>
  );
}
