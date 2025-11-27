import { useEffect, useMemo, useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, API_BASE_URL, isAuthenticated } from "../services/api";
import { useTranslation } from "react-i18next";
import { stagger, scaleIn } from "../lib/gsap";
import type { EChartsOption } from "echarts";
import type { CallbackDataParams, TopLevelFormatterParams } from "echarts/types/dist/shared";
import { useNotificationsQuery, type NotificationItem } from "../hooks/useNotificationsQuery";
import { useChartTheme } from "../hooks/useChartTheme";
import { EChart } from "../components/charts/EChart";
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

type OverviewReport = {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
};

type BranchCount = { branch_name: string; count: number };
type DepartmentCount = { department_name: string; count: number };
type Branch = { id: number; name: string; code: string };
type Department = { id: number; name: string; code?: string };
type TrendPoint = { date: string; count: number };

type SlaCompliance = {
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

type SlaPriorityItem = {
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

type ChartMode = "count" | "percent";

export default function Dashboard() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const chartTheme = useChartTheme();
  const [overview, setOverview] = useState<OverviewReport | null>(null);
  const [byStatus, setByStatus] = useState<Record<string, number>>({});
  const [byDate, setByDate] = useState<TrendPoint[]>([]);
  const [byBranch, setByBranch] = useState<BranchCount[]>([]);
  const [byPriority, setByPriority] = useState<Record<string, number>>({});
  const [byDepartment, setByDepartment] = useState<DepartmentCount[]>([]);
  const [slaCompliance, setSlaCompliance] = useState<SlaCompliance | null>(null);
  const [slaByPriority, setSlaByPriority] = useState<SlaPriorityItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [branchFilter, setBranchFilter] = useState<string>("");
  const [departmentFilter, setDepartmentFilter] = useState<string>("");
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [branches, setBranches] = useState<Branch[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [responseHours, setResponseHours] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [chartMode, setChartMode] = useState<ChartMode>("count");
  const {
    notifications: latestNotifications,
    unreadCount,
    loading: notificationsLoading,
    refresh: refreshNotifications,
  } = useNotificationsQuery(120000);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
  }, [navigate]);

  const loadReports = useCallback(async () => {
    if (!isAuthenticated()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const df = new URLSearchParams();
      if (dateFrom) df.set("date_from", dateFrom);
      if (dateTo) df.set("date_to", dateTo);
      if (branchFilter) df.set("branch_id", branchFilter);
      if (departmentFilter) df.set("department_id", departmentFilter);
      if (priorityFilter) df.set("priority", priorityFilter);
      const query = df.toString();
      const filterSuffix = query ? `?${query}` : "";

      const [
        ov,
        bs,
        bd,
        bb,
        bp,
        bdpt,
        sla,
        slaP,
        rt,
      ] = await Promise.all([
        apiGet("/api/reports/overview") as Promise<OverviewReport>,
        apiGet("/api/reports/by-status") as Promise<Record<string, number>>,
        apiGet(`/api/reports/by-date${filterSuffix}`) as Promise<TrendPoint[]>,
        apiGet(`/api/reports/by-branch${filterSuffix}`) as Promise<BranchCount[]>,
        apiGet(`/api/reports/by-priority${filterSuffix}`) as Promise<Record<string, number>>,
        apiGet(`/api/reports/by-department${filterSuffix}`) as Promise<DepartmentCount[]>,
        apiGet(`/api/reports/sla-compliance`) as Promise<SlaCompliance>,
        apiGet(`/api/reports/sla-by-priority`) as Promise<SlaPriorityItem[]>,
        apiGet(`/api/reports/response-time`) as Promise<{ average_response_time_hours?: number }>,
      ]);

      setOverview(ov);
      setByStatus(bs);
      setByDate(bd);
      setByBranch(bb);
      setByPriority(bp);
      setByDepartment(bdpt);
      setSlaCompliance(sla);
      setSlaByPriority(slaP);
      setResponseHours(rt?.average_response_time_hours ?? null);
    } catch (e) {
      console.error("Dashboard error:", e);
      setError(e instanceof Error ? e.message : t("dashboard.errors.fetch"));
    } finally {
      setLoading(false);
    }
  }, [branchFilter, dateFrom, dateTo, departmentFilter, priorityFilter, t]);

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

  useEffect(() => {
    if (isAuthenticated()) {
      loadBranchesAndDepartments();
    }
  }, [loadBranchesAndDepartments]);

  useEffect(() => {
    if (isAuthenticated()) {
      loadReports();
    }
  }, [loadReports]);

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

  // Animate charts when they load - moved after byStatusData definition

  const getPriorityLabel = useCallback(
    (priority: string) => t(`dashboard.priority.${priority}`, { defaultValue: priority }),
    [t]
  );

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

  if (!isAuthenticated()) {
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
        <button onClick={loadReports} disabled={loading} className="secondary">
          {loading ? t("dashboard.buttons.loading") : t("dashboard.buttons.refresh")}
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

      {loading && !overview && (
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
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}>
              <div className="stat-label">{t("dashboard.stats.total")}</div>
              <div className="stat-value">{overview.total || 0}</div>
            </div>
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)" }}>
              <div className="stat-label">{t("dashboard.status.pending")}</div>
              <div className="stat-value">{overview.pending || 0}</div>
            </div>
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)" }}>
              <div className="stat-label">{t("dashboard.status.in_progress")}</div>
              <div className="stat-value">{overview.in_progress || 0}</div>
            </div>
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)" }}>
              <div className="stat-label">{t("dashboard.status.resolved")}</div>
              <div className="stat-value">{overview.resolved || 0}</div>
            </div>
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
