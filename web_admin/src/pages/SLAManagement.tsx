import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiGet, apiPost, apiPut, apiDelete, isAuthenticated, getStoredProfile } from "../services/api";
import type { EChartsOption } from "echarts";
import { useChartTheme } from "../hooks/useChartTheme";
import { EChart } from "../components/charts/EChart";
import { buildGrid, buildLegend, buildTooltip, buildCategoryAxis, buildValueAxis } from "../lib/echartsConfig";

type SLARule = {
  id: number;
  name: string;
  description?: string | null;
  priority?: string | null;
  category?: string | null;
  department_id?: number | null;
  response_time_minutes: number;
  resolution_time_minutes: number;
  response_warning_minutes: number;
  resolution_warning_minutes: number;
  escalation_enabled: boolean;
  escalation_after_minutes?: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

type SLAPayload = {
  name: string;
  description: string | null;
  priority: string | null;
  category: string | null;
  department_id: number | null;
  response_time_minutes: number;
  resolution_time_minutes: number;
  response_warning_minutes: number;
  resolution_warning_minutes: number;
  escalation_enabled: boolean;
  escalation_after_minutes: number | null;
  is_active: boolean;
};

type SLALogStatus = "on_time" | "warning" | "breached" | null;

type SLALog = {
  id: number;
  ticket_id: number;
  ticket_number?: string;
  sla_rule_name?: string;
  sla_rule_id?: number;
  response_status: SLALogStatus;
  resolution_status: SLALogStatus;
  target_response_time: string;
  target_resolution_time: string;
  actual_response_time?: string | null;
  actual_resolution_time?: string | null;
  escalated: boolean;
  escalated_at?: string | null;
};

type SLAStatsSummary = {
  total_logs: number;
  response_on_time: number;
  response_warning: number;
  response_breached: number;
  resolution_on_time: number;
  resolution_warning: number;
  resolution_breached: number;
  escalated_count: number;
  response_compliance_rate: number;
  resolution_compliance_rate: number;
};

type LogFilters = {
  response_status: "" | Exclude<SLALogStatus, null>;
  resolution_status: "" | Exclude<SLALogStatus, null>;
  escalated: "" | "true" | "false";
};

const EMPTY_FORM = {
  name: "",
  description: "",
  priority: "",
  category: "",
  department_id: "",
  response_time_minutes: 60,
  resolution_time_minutes: 240,
  response_warning_minutes: 30,
  resolution_warning_minutes: 60,
  escalation_enabled: false,
  escalation_after_minutes: "",
  is_active: true,
};

const PRIORITIES = [
  { value: "", label: "همه اولویت‌ها" },
  { value: "critical", label: "🔴 بحرانی" },
  { value: "high", label: "🟠 بالا" },
  { value: "medium", label: "🟡 متوسط" },
  { value: "low", label: "🟢 پایین" },
];

const CATEGORIES = [
  { value: "", label: "همه دسته‌بندی‌ها" },
  { value: "internet", label: "اینترنت" },
  { value: "equipment", label: "تجهیزات" },
  { value: "software", label: "نرم‌افزار" },
  { value: "other", label: "سایر" },
];

export default function SLAManagement() {
  const navigate = useNavigate();
  const chartTheme = useChartTheme();
  const profile = useMemo(() => getStoredProfile(), []);
  const [rules, setRules] = useState<SLARule[]>([]);
  const [departments, setDepartments] = useState<{ id: number; name: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [filterActive, setFilterActive] = useState<string>("");
  
  // SLA Logs states
  const [slaLogs, setSlaLogs] = useState<SLALog[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [logsPage, setLogsPage] = useState(1);
  const [logsTotalPages, setLogsTotalPages] = useState(1);
  const [showLogs, setShowLogs] = useState(false);
  const [logFilters, setLogFilters] = useState<LogFilters>({
    response_status: "",
    resolution_status: "",
    escalated: "",
  });
  
  // SLA Statistics states
  const [slaStats, setSlaStats] = useState<SLAStatsSummary | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  const responseStatusOption = useMemo<EChartsOption>(() => ({
    tooltip: buildTooltip(chartTheme, { trigger: "item", formatter: "{b}: {c} ({d}%)" }),
    legend: buildLegend(chartTheme, { bottom: 0 }),
    series: [
      {
        type: "pie",
        radius: ["35%", "70%"],
        label: { formatter: "{b}\n{d}%", color: chartTheme.foreground },
        data: [
          { value: slaStats?.response_on_time || 0, name: "در مهلت", itemStyle: { color: chartTheme.success } },
          { value: slaStats?.response_warning || 0, name: "هشدار", itemStyle: { color: chartTheme.warning } },
          { value: slaStats?.response_breached || 0, name: "نقض شده", itemStyle: { color: chartTheme.danger } },
        ],
      },
    ],
  }), [slaStats, chartTheme]);

  const resolutionStatusOption = useMemo<EChartsOption>(() => ({
    tooltip: buildTooltip(chartTheme, { trigger: "item", formatter: "{b}: {c} ({d}%)" }),
    legend: buildLegend(chartTheme, { bottom: 0 }),
    series: [
      {
        type: "pie",
        radius: ["35%", "70%"],
        label: { formatter: "{b}\n{d}%", color: chartTheme.foreground },
        data: [
          { value: slaStats?.resolution_on_time || 0, name: "در مهلت", itemStyle: { color: chartTheme.success } },
          { value: slaStats?.resolution_warning || 0, name: "هشدار", itemStyle: { color: chartTheme.warning } },
          { value: slaStats?.resolution_breached || 0, name: "نقض شده", itemStyle: { color: chartTheme.danger } },
        ],
      },
    ],
  }), [slaStats, chartTheme]);

  const responseVsResolutionOption = useMemo<EChartsOption>(() => ({
    grid: buildGrid(),
    tooltip: buildTooltip(chartTheme),
    legend: buildLegend(chartTheme, { top: 0 }),
    xAxis: buildCategoryAxis(["در مهلت", "هشدار", "نقض شده"], chartTheme),
    yAxis: buildValueAxis(chartTheme),
    series: [
      {
        name: "پاسخ",
        type: "bar",
        data: [slaStats?.response_on_time || 0, slaStats?.response_warning || 0, slaStats?.response_breached || 0],
        itemStyle: { color: chartTheme.palette[0] },
      },
      {
        name: "حل",
        type: "bar",
        data: [slaStats?.resolution_on_time || 0, slaStats?.resolution_warning || 0, slaStats?.resolution_breached || 0],
        itemStyle: { color: chartTheme.palette[1] },
      },
    ],
  }), [slaStats, chartTheme]);

  const loadDepartments = useCallback(async () => {
    try {
      const depts = (await apiGet("/api/departments?page_size=100")) as { id: number; name: string }[];
      setDepartments(depts);
    } catch (error) {
      console.error("Error loading departments:", error);
    }
  }, []);

  const loadRules = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterActive) params.set("is_active", filterActive);
      const query = params.toString() ? `?${params.toString()}` : "";
      const res = (await apiGet(`/api/sla${query}`)) as SLARule[];
      setRules(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در دریافت قوانین SLA");
    } finally {
      setLoading(false);
    }
  }, [filterActive]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    if (!profile || !["admin", "central_admin"].includes(profile.role)) {
      navigate("/");
      return;
    }
    loadDepartments();
    loadRules();
  }, [navigate, profile, loadDepartments, loadRules]);

  const startEdit = (rule: SLARule) => {
    setEditingId(rule.id);
    setForm({
      name: rule.name,
      description: rule.description || "",
      priority: rule.priority || "",
      category: rule.category || "",
      department_id: rule.department_id ? String(rule.department_id) : "",
      response_time_minutes: rule.response_time_minutes,
      resolution_time_minutes: rule.resolution_time_minutes,
      response_warning_minutes: rule.response_warning_minutes,
      resolution_warning_minutes: rule.resolution_warning_minutes,
      escalation_enabled: rule.escalation_enabled,
      escalation_after_minutes: rule.escalation_after_minutes ? String(rule.escalation_after_minutes) : "",
      is_active: rule.is_active,
    });
    setSuccess(null);
    setError(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setError(null);
    setSuccess(null);
  };

  const submit = async () => {
    if (!form.name || !form.response_time_minutes || !form.resolution_time_minutes) {
      setError("نام، زمان پاسخ و زمان حل الزامی است.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const payload: SLAPayload = {
        name: form.name,
        description: form.description || null,
        priority: form.priority || null,
        category: form.category || null,
        department_id: form.department_id ? Number(form.department_id) : null,
        response_time_minutes: form.response_time_minutes,
        resolution_time_minutes: form.resolution_time_minutes,
        response_warning_minutes: form.response_warning_minutes,
        resolution_warning_minutes: form.resolution_warning_minutes,
        escalation_enabled: form.escalation_enabled,
        escalation_after_minutes: form.escalation_after_minutes ? Number(form.escalation_after_minutes) : null,
        is_active: form.is_active,
      };

      if (editingId) {
        await apiPut(`/api/sla/${editingId}`, payload);
        setSuccess("قانون SLA با موفقیت به‌روزرسانی شد.");
      } else {
        await apiPost("/api/sla", payload);
        setSuccess("قانون SLA جدید با موفقیت ایجاد شد.");
      }
      cancelEdit();
      await loadRules();
    } catch (error) {
      setError(error instanceof Error ? error.message : "خطا در ذخیره قانون SLA.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("آیا از حذف این قانون SLA مطمئن هستید؟")) {
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await apiDelete(`/api/sla/${id}`);
      setSuccess("قانون SLA با موفقیت حذف شد.");
      await loadRules();
    } catch (error) {
      setError(error instanceof Error ? error.message : "خطا در حذف قانون SLA.");
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (rule: SLARule) => {
    setLoading(true);
    setError(null);
    try {
      await apiPut(`/api/sla/${rule.id}`, { is_active: !rule.is_active });
      await loadRules();
    } catch (error) {
      setError(error instanceof Error ? error.message : "خطا در تغییر وضعیت قانون.");
    } finally {
      setLoading(false);
    }
  };

  const getPriorityLabel = (priority?: string | null) => {
    if (!priority) return "همه اولویت‌ها";
    return PRIORITIES.find((p) => p.value === priority)?.label || priority;
  };

  const getCategoryLabel = (category?: string | null) => {
    if (!category) return "همه دسته‌بندی‌ها";
    return CATEGORIES.find((c) => c.value === category)?.label || category;
  };

  const formatMinutes = (minutes: number) => {
    if (minutes < 60) return `${minutes} دقیقه`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (mins === 0) return `${hours} ساعت`;
    return `${hours} ساعت و ${mins} دقیقه`;
  };

  /**
   * بارگذاری لاگ‌های SLA
   * Load SLA logs
   */
  const loadSlaLogs = useCallback(async () => {
    setLogsLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", String(logsPage));
      params.set("page_size", "20");
      if (logFilters.response_status) params.set("response_status", logFilters.response_status);
      if (logFilters.resolution_status) params.set("resolution_status", logFilters.resolution_status);
      if (logFilters.escalated) params.set("escalated", logFilters.escalated);
      
      const logs = (await apiGet(`/api/sla/logs?${params.toString()}`)) as SLALog[];
      setSlaLogs(logs);
      setLogsTotalPages(Math.ceil(logs.length / 20) || 1);
    } catch (error) {
      console.error("Error loading SLA logs:", error);
    } finally {
      setLogsLoading(false);
    }
  }, [logFilters, logsPage]);

  /**
   * بارگذاری آمار SLA
   * Load SLA statistics
   */
  const loadSlaStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const stats = (await apiGet("/api/reports/sla-compliance")) as {
        total_tickets_with_sla?: number;
        response_on_time?: number;
        response_warning?: number;
        response_breached?: number;
        resolution_on_time?: number;
        resolution_warning?: number;
        resolution_breached?: number;
        escalated_count?: number;
        response_compliance_rate?: number;
        resolution_compliance_rate?: number;
      };
      setSlaStats({
        total_logs: stats.total_tickets_with_sla || 0,
        response_on_time: stats.response_on_time || 0,
        response_warning: stats.response_warning || 0,
        response_breached: stats.response_breached || 0,
        resolution_on_time: stats.resolution_on_time || 0,
        resolution_warning: stats.resolution_warning || 0,
        resolution_breached: stats.resolution_breached || 0,
        escalated_count: stats.escalated_count || 0,
        response_compliance_rate: stats.response_compliance_rate || 0,
        resolution_compliance_rate: stats.resolution_compliance_rate || 0,
      });
    } catch (error) {
      console.error("Error loading SLA stats:", error);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (showLogs) {
      loadSlaLogs();
    }
  }, [showLogs, loadSlaLogs]);

  useEffect(() => {
    loadSlaStats();
  }, [loadSlaStats]);

  /**
   * تابع برای نمایش وضعیت SLA
   * Function to display SLA status badge
   */
  const getStatusBadge = (status: string | null) => {
    if (!status) return <span className="badge secondary">نامشخص</span>;
    const statusMap: Record<string, { text: string; class: string; emoji: string }> = {
      on_time: { text: "در مهلت", class: "success", emoji: "✅" },
      warning: { text: "هشدار", class: "warning", emoji: "⚠️" },
      breached: { text: "نقض شده", class: "danger", emoji: "🔴" },
    };
    const s = statusMap[status] || { text: status, class: "secondary", emoji: "❓" };
    return <span className={`badge ${s.class}`}>{s.emoji} {s.text}</span>;
  };

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="page-title">⏱️ مدیریت قوانین SLA</h1>
        <div style={{ display: "flex", gap: 12 }}>
          <button
            onClick={() => {
              setShowLogs(!showLogs);
              if (!showLogs) {
                loadSlaLogs();
              }
            }}
            className={showLogs ? "secondary" : ""}
            style={{ padding: "10px 20px" }}
          >
            {showLogs ? "📋 مخفی کردن لاگ‌ها" : "📋 نمایش لاگ‌های SLA"}
          </button>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">{editingId ? "✏️ ویرایش قانون SLA" : "➕ ایجاد قانون SLA جدید"}</h2>
        </div>
        {error && <div className="alert error fade-in">{error}</div>}
        {success && <div className="alert success fade-in">{success}</div>}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submit();
          }}
        >
          <label>
            نام قانون:
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              placeholder="مثال: SLA تیکت‌های بحرانی IT"
            />
          </label>
          <label>
            توضیحات:
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={2}
              placeholder="توضیحات اختیاری"
            ></textarea>
          </label>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginTop: 16 }}>
            <label>
              اولویت:
              <select
                value={form.priority}
                onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
              >
                {PRIORITIES.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              دسته‌بندی:
              <select
                value={form.category}
                onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              دپارتمان:
              <select
                value={form.department_id}
                onChange={(e) => setForm((f) => ({ ...f, department_id: e.target.value }))}
              >
                <option value="">همه دپارتمان‌ها</option>
                {departments.map((d) => (
                  <option key={d.id} value={String(d.id)}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>زمان‌های هدف</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <label>
                زمان پاسخ هدف (دقیقه):
                <input
                  type="number"
                  value={form.response_time_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, response_time_minutes: Number(e.target.value) }))}
                  min={1}
                  required
                  placeholder="مثال: 60"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.response_time_minutes)})
                </div>
              </label>
              <label>
                زمان حل هدف (دقیقه):
                <input
                  type="number"
                  value={form.resolution_time_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, resolution_time_minutes: Number(e.target.value) }))}
                  min={1}
                  required
                  placeholder="مثال: 240"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.resolution_time_minutes)})
                </div>
              </label>
            </div>
          </div>

          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>هشدارها</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <label>
                هشدار قبل از مهلت پاسخ (دقیقه):
                <input
                  type="number"
                  value={form.response_warning_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, response_warning_minutes: Number(e.target.value) }))}
                  min={0}
                  required
                  placeholder="مثال: 30"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.response_warning_minutes)})
                </div>
              </label>
              <label>
                هشدار قبل از مهلت حل (دقیقه):
                <input
                  type="number"
                  value={form.resolution_warning_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, resolution_warning_minutes: Number(e.target.value) }))}
                  min={0}
                  required
                  placeholder="مثال: 60"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.resolution_warning_minutes)})
                </div>
              </label>
            </div>
          </div>

          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>Escalation</h3>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.escalation_enabled}
                onChange={(e) => setForm((f) => ({ ...f, escalation_enabled: e.target.checked }))}
              />
              فعال کردن Escalation
            </label>
            {form.escalation_enabled && (
              <label style={{ marginTop: 12 }}>
                Escalation بعد از (دقیقه):
                <input
                  type="number"
                  value={form.escalation_after_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, escalation_after_minutes: e.target.value }))}
                  min={1}
                  placeholder="مثال: 120"
                />
                {form.escalation_after_minutes && (
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                    ({formatMinutes(Number(form.escalation_after_minutes))})
                  </div>
                )}
              </label>
            )}
          </div>

          <label className="checkbox-label" style={{ marginTop: 16 }}>
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
            />
            فعال
          </label>
          <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
            <button type="submit" disabled={loading}>
              {loading ? "⏳ در حال ذخیره..." : "💾 ذخیره"}
            </button>
            {editingId && (
              <button type="button" className="secondary" onClick={cancelEdit} disabled={loading}>
                انصراف
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">لیست قوانین SLA</h2>
        </div>
        <div className="filters" style={{ marginBottom: 16 }}>
          <select
            value={filterActive}
            onChange={(e) => setFilterActive(e.target.value)}
            style={{ flex: 1 }}
          >
            <option value="">همه وضعیت‌ها</option>
            <option value="true">فعال</option>
            <option value="false">غیرفعال</option>
          </select>
        </div>
        {loading && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <div className="loading" style={{ margin: "0 auto" }}></div>
            <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
          </div>
        )}
        {!loading && rules.length === 0 && (
          <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
            هیچ قانون SLA یافت نشد.
          </div>
        )}
        {!loading && rules.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>نام</th>
                  <th>اولویت</th>
                  <th>دسته‌بندی</th>
                  <th>دپارتمان</th>
                  <th>زمان پاسخ</th>
                  <th>زمان حل</th>
                  <th>Escalation</th>
                  <th>وضعیت</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {rules.map((rule) => (
                  <tr key={rule.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{rule.name}</div>
                      {rule.description && (
                        <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                          {rule.description}
                        </div>
                      )}
                    </td>
                    <td>{getPriorityLabel(rule.priority)}</td>
                    <td>{getCategoryLabel(rule.category)}</td>
                    <td>
                      {rule.department_id
                        ? departments.find((d) => d.id === rule.department_id)?.name || `ID: ${rule.department_id}`
                        : "همه"}
                    </td>
                    <td>
                      <div style={{ fontSize: 14 }}>{formatMinutes(rule.response_time_minutes)}</div>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                        هشدار: {formatMinutes(rule.response_warning_minutes)} قبل
                      </div>
                    </td>
                    <td>
                      <div style={{ fontSize: 14 }}>{formatMinutes(rule.resolution_time_minutes)}</div>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                        هشدار: {formatMinutes(rule.resolution_warning_minutes)} قبل
                      </div>
                    </td>
                    <td>
                      {rule.escalation_enabled ? (
                        <div>
                          <span className="badge success">فعال</span>
                          {rule.escalation_after_minutes && (
                            <div style={{ fontSize: 12, marginTop: 4 }}>
                              بعد از {formatMinutes(rule.escalation_after_minutes)}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="badge secondary">غیرفعال</span>
                      )}
                    </td>
                    <td>
                      {rule.is_active ? (
                        <span className="badge success">فعال</span>
                      ) : (
                        <span className="badge danger">غیرفعال</span>
                      )}
                    </td>
                    <td>
                      <button
                        className="secondary small"
                        onClick={() => toggleActive(rule)}
                        disabled={loading}
                        title={rule.is_active ? "غیرفعال کردن" : "فعال کردن"}
                      >
                        {rule.is_active ? "⏸️" : "▶️"}
                      </button>
                      <button
                        className="secondary small"
                        onClick={() => startEdit(rule)}
                        style={{ marginLeft: 8 }}
                      >
                        ✏️ ویرایش
                      </button>
                      <button
                        className="danger small"
                        onClick={() => handleDelete(rule.id)}
                        style={{ marginLeft: 8 }}
                      >
                        🗑️ حذف
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* آمار و نمودارهای SLA */}
      {slaStats && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h2 className="card-title">📊 آمار و نمودارهای SLA</h2>
          </div>
          {statsLoading ? (
            <div style={{ textAlign: "center", padding: 40 }}>
              <div className="loading" style={{ margin: "0 auto" }}></div>
              <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری آمار...</p>
            </div>
          ) : (
            <div style={{ padding: 20 }}>
              {/* کارت‌های آماری */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 30 }}>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "var(--accent)", marginBottom: 8 }}>
                    {slaStats.total_logs || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>کل لاگ‌های SLA</div>
                </div>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "#28a745", marginBottom: 8 }}>
                    {slaStats.response_on_time || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>پاسخ در مهلت</div>
                </div>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "#ffc107", marginBottom: 8 }}>
                    {slaStats.response_warning || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>هشدار پاسخ</div>
                </div>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "#dc3545", marginBottom: 8 }}>
                    {slaStats.response_breached || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>نقض پاسخ</div>
                </div>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "#28a745", marginBottom: 8 }}>
                    {slaStats.resolution_on_time || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>حل در مهلت</div>
                </div>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "#ffc107", marginBottom: 8 }}>
                    {slaStats.resolution_warning || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>هشدار حل</div>
                </div>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "#dc3545", marginBottom: 8 }}>
                    {slaStats.resolution_breached || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>نقض حل</div>
                </div>
                <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: "bold", color: "#ff6b6b", marginBottom: 8 }}>
                    {slaStats.escalated_count || 0}
                  </div>
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>Escalated</div>
                </div>
              </div>

              {/* نمودارهای SLA */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: 20 }}>
                {/* نمودار وضعیت پاسخ */}
                <div style={{ background: "var(--bg-primary)", padding: 20, borderRadius: "var(--radius)", border: "1px solid var(--border)" }}>
                  <h3 style={{ marginBottom: 20, fontSize: 18, fontWeight: 600 }}>📊 وضعیت پاسخ</h3>
                  <EChart option={responseStatusOption} height={300} ariaLabel="وضعیت پاسخ SLA" />
                </div>

                {/* نمودار وضعیت حل */}
                <div style={{ background: "var(--bg-primary)", padding: 20, borderRadius: "var(--radius)", border: "1px solid var(--border)" }}>
                  <h3 style={{ marginBottom: 20, fontSize: 18, fontWeight: 600 }}>📊 وضعیت حل</h3>
                  <EChart option={resolutionStatusOption} height={300} ariaLabel="وضعیت حل SLA" />
                </div>

                {/* نمودار مقایسه‌ای پاسخ و حل */}
                <div style={{ background: "var(--bg-primary)", padding: 20, borderRadius: "var(--radius)", border: "1px solid var(--border)", gridColumn: "1 / -1" }}>
                  <h3 style={{ marginBottom: 20, fontSize: 18, fontWeight: 600 }}>📊 مقایسه وضعیت پاسخ و حل</h3>
                  <EChart option={responseVsResolutionOption} height={300} ariaLabel="مقایسه وضعیت پاسخ و حل SLA" />
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* لاگ‌های SLA */}
      {showLogs && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">📋 لاگ‌های SLA</h2>
          </div>
          
          {/* فیلترهای لاگ */}
          <div className="filters" style={{ marginBottom: 16 }}>
            <select
              value={logFilters.response_status}
              onChange={(e) =>
                setLogFilters({
                  ...logFilters,
                  response_status: e.target.value as LogFilters["response_status"],
                })
              }
              style={{ flex: 1 }}
            >
              <option value="">همه وضعیت‌های پاسخ</option>
              <option value="on_time">✅ در مهلت</option>
              <option value="warning">⚠️ هشدار</option>
              <option value="breached">🔴 نقض شده</option>
            </select>
            <select
              value={logFilters.resolution_status}
              onChange={(e) =>
                setLogFilters({
                  ...logFilters,
                  resolution_status: e.target.value as LogFilters["resolution_status"],
                })
              }
              style={{ flex: 1 }}
            >
              <option value="">همه وضعیت‌های حل</option>
              <option value="on_time">✅ در مهلت</option>
              <option value="warning">⚠️ هشدار</option>
              <option value="breached">🔴 نقض شده</option>
            </select>
            <select
              value={logFilters.escalated}
              onChange={(e) =>
                setLogFilters({
                  ...logFilters,
                  escalated: e.target.value as LogFilters["escalated"],
                })
              }
              style={{ flex: 1 }}
            >
              <option value="">همه Escalation</option>
              <option value="true">Escalated</option>
              <option value="false">Not Escalated</option>
            </select>
          </div>

          {logsLoading ? (
            <div style={{ textAlign: "center", padding: 40 }}>
              <div className="loading" style={{ margin: "0 auto" }}></div>
              <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری لاگ‌ها...</p>
            </div>
          ) : slaLogs.length === 0 ? (
            <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
              هیچ لاگ SLA یافت نشد.
            </div>
          ) : (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>شماره تیکت</th>
                      <th>قانون SLA</th>
                      <th>وضعیت پاسخ</th>
                      <th>وضعیت حل</th>
                      <th>مهلت پاسخ</th>
                      <th>مهلت حل</th>
                      <th>Escalated</th>
                      <th>عملیات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {slaLogs.map((log) => (
                      <tr key={log.id}>
                        <td>
                          <Link to={`/tickets/${log.ticket_id}`} style={{ color: "var(--accent)", textDecoration: "none" }}>
                            {log.ticket_number || `#${log.ticket_id}`}
                          </Link>
                        </td>
                        <td>{log.sla_rule_name || `قانون #${log.sla_rule_id}`}</td>
                        <td>{getStatusBadge(log.response_status)}</td>
                        <td>{getStatusBadge(log.resolution_status)}</td>
                        <td style={{ fontSize: 12 }}>
                          {new Date(log.target_response_time).toLocaleString("fa-IR")}
                          {log.actual_response_time && (
                            <div style={{ color: "var(--fg-secondary)", marginTop: 4 }}>
                              واقعی: {new Date(log.actual_response_time).toLocaleString("fa-IR")}
                            </div>
                          )}
                        </td>
                        <td style={{ fontSize: 12 }}>
                          {new Date(log.target_resolution_time).toLocaleString("fa-IR")}
                          {log.actual_resolution_time && (
                            <div style={{ color: "var(--fg-secondary)", marginTop: 4 }}>
                              واقعی: {new Date(log.actual_resolution_time).toLocaleString("fa-IR")}
                            </div>
                          )}
                        </td>
                        <td>
                          {log.escalated ? (
                            <span className="badge danger">
                              ⚠️ Escalated
                              {log.escalated_at && (
                                <div style={{ fontSize: 11, marginTop: 4 }}>
                                  {new Date(log.escalated_at).toLocaleString("fa-IR")}
                                </div>
                              )}
                            </span>
                          ) : (
                            <span className="badge secondary">-</span>
                          )}
                        </td>
                        <td>
                          <Link to={`/tickets/${log.ticket_id}`}>
                            <button className="secondary small">مشاهده تیکت</button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Pagination */}
              {logsTotalPages > 1 && (
                <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 20 }}>
                  <button
                    onClick={() => setLogsPage((p) => Math.max(1, p - 1))}
                    disabled={logsPage === 1}
                    className="secondary"
                  >
                    قبلی
                  </button>
                  <span style={{ padding: "8px 16px", display: "flex", alignItems: "center" }}>
                    صفحه {logsPage} از {logsTotalPages}
                  </span>
                  <button
                    onClick={() => setLogsPage((p) => Math.min(logsTotalPages, p + 1))}
                    disabled={logsPage === logsTotalPages}
                    className="secondary"
                  >
                    بعدی
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

