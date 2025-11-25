import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, API_BASE_URL, isAuthenticated } from "../services/api";
import { useTranslation } from "react-i18next";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from "recharts";

export default function Dashboard() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [overview, setOverview] = useState<any | null>(null);
  const [byStatus, setByStatus] = useState<Record<string, number>>({});
  const [byDate, setByDate] = useState<{ date: string; count: number }[]>([]);
  const [byBranch, setByBranch] = useState<{ branch_name: string; count: number }[]>([]);
  const [byPriority, setByPriority] = useState<Record<string, number>>({});
  const [byDepartment, setByDepartment] = useState<{ department_name: string; count: number }[]>([]);
  const [slaCompliance, setSlaCompliance] = useState<any | null>(null);
  const [slaByPriority, setSlaByPriority] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [branchFilter, setBranchFilter] = useState<string>("");
  const [departmentFilter, setDepartmentFilter] = useState<string>("");
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [branches, setBranches] = useState<{ id: number; name: string; code: string }[]>([]);
  const [departments, setDepartments] = useState<{ id: number; name: string; code: string }[]>([]);
  const [responseHours, setResponseHours] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
  }, [navigate]);

  const loadReports = async () => {
    if (!isAuthenticated()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const ov = await apiGet("/api/reports/overview") as any;
      const bs = await apiGet("/api/reports/by-status") as Record<string, number>;
      const df = new URLSearchParams();
      if (dateFrom) df.set("date_from", dateFrom);
      if (dateTo) df.set("date_to", dateTo);
      if (branchFilter) df.set("branch_id", branchFilter);
      if (departmentFilter) df.set("department_id", departmentFilter);
      if (priorityFilter) df.set("priority", priorityFilter);
      const bd = await apiGet(`/api/reports/by-date?${df.toString()}`) as { date: string; count: number }[];
      const bb = await apiGet(`/api/reports/by-branch?${df.toString()}`) as { branch_name: string; count: number; branch_id?: number; branch_code?: string }[];
      const bp = await apiGet(`/api/reports/by-priority?${df.toString()}`) as Record<string, number>;
      const bdpt = await apiGet(`/api/reports/by-department?${df.toString()}`) as { department_name: string; count: number; department_id?: number; department_code?: string }[];
      const sla = await apiGet(`/api/reports/sla-compliance`) as any;
      const slaP = await apiGet(`/api/reports/sla-by-priority`) as any[];
      const rt = await apiGet(`/api/reports/response-time`) as { average_response_time_hours?: number };
      setOverview(ov);
      setByStatus(bs);
      setByDate(bd);
      setByBranch(bb.map((x) => ({ branch_name: x.branch_name, count: x.count })));
      setByPriority(bp);
      setByDepartment(bdpt.map((x) => ({ department_name: x.department_name, count: x.count })));
      setSlaCompliance(sla);
      setSlaByPriority(slaP);
      setResponseHours(rt?.average_response_time_hours ?? null);
    } catch (e: any) {
      console.error("Dashboard error:", e);
      setError(e?.message || t("dashboard.errors.fetch"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated()) {
      loadBranchesAndDepartments();
      loadReports();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadBranchesAndDepartments = async () => {
    try {
      const b = await apiGet(`/api/branches`) as any[];
      setBranches(b.map((x: any) => ({ id: x.id, name: x.name, code: x.code })));
      const d = await apiGet(`/api/departments?page_size=100`) as any[];
      setDepartments(d.map((x: any) => ({ id: x.id, name: x.name, code: x.code })));
    } catch {
      // ignore
    }
  };

  // Reload reports when filters change
  useEffect(() => {
    if (isAuthenticated() && (dateFrom || dateTo || branchFilter || departmentFilter || priorityFilter)) {
      loadReports();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dateFrom, dateTo, branchFilter, departmentFilter, priorityFilter]);

  const getPriorityLabel = (priority: string) =>
    t(`dashboard.priority.${priority}`, { defaultValue: priority });

  const byStatusData = useMemo(
    () => Object.entries(byStatus).map(([status, count]) => ({
      status: t(`dashboard.status.${status}`, { defaultValue: status }),
      count
    })),
    [byStatus, t]
  );

  const byPriorityData = useMemo(
    () => Object.entries(byPriority).map(([priority, count]) => ({
      priority: getPriorityLabel(priority),
      count
    })),
    [byPriority, t]
  );

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>{t("dashboard.title")}</h1>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
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
          <div className="grid grid-cols-4" style={{ marginBottom: 24 }}>
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

          {/* Response Time Card */}
          {responseHours !== null && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">{t("dashboard.cards.responseTime")}</h2>
              </div>
              <div style={{ fontSize: 48, fontWeight: 700, color: "var(--primary)", textAlign: "center", padding: "20px 0" }}>
                {responseHours.toFixed(2)} <span style={{ fontSize: 24, color: "var(--fg-secondary)" }}>{t("dashboard.cards.hours")}</span>
              </div>
            </div>
          )}

          {/* Status Charts - Bar and Pie */}
          <div className="grid grid-cols-1 lg:grid-cols-2" style={{ gap: 24, marginBottom: 24 }}>
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
              <ResponsiveContainer>
                <BarChart data={byStatusData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                    <XAxis dataKey="status" stroke="var(--fg-secondary)" fontSize={12} />
                    <YAxis allowDecimals={false} stroke="var(--fg-secondary)" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ 
                      background: "var(--bg-secondary)", 
                      border: "1px solid var(--border)",
                        borderRadius: "var(--radius)",
                        boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                      }}
                    />
                    <Bar 
                      dataKey="count" 
                      fill="url(#statusGradient)" 
                      radius={[8, 8, 0, 0]}
                      animationDuration={1000}
                    >
                      <defs>
                        <linearGradient id="statusGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#667eea" stopOpacity={1}/>
                          <stop offset="100%" stopColor="#764ba2" stopOpacity={1}/>
                        </linearGradient>
                      </defs>
                    </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

            {/* Pie Chart */}
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">{t("dashboard.charts.statusPie")}</h2>
              </div>
              <div style={{ width: "100%", height: 300 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={byStatusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ status, count, percent }) => `${status}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="count"
                      animationDuration={1000}
                    >
                      {byStatusData.map((entry, index) => {
                        const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b'];
                        return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                      })}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        background: "var(--bg-secondary)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius)",
                        boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
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
              <ResponsiveContainer>
                <AreaChart data={byDate}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                  <XAxis 
                    dataKey="date" 
                    stroke="var(--fg-secondary)" 
                    fontSize={11}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis allowDecimals={false} stroke="var(--fg-secondary)" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ 
                      background: "var(--bg-secondary)", 
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius)",
                      boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorCount)"
                    animationDuration={1500}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#059669" 
                    strokeWidth={2}
                    dot={{ fill: "#10b981", r: 5, strokeWidth: 2, stroke: "#fff" }}
                    activeDot={{ r: 8, strokeWidth: 2 }}
                    animationDuration={1500}
                  />
                </AreaChart>
              </ResponsiveContainer>
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
                  <ResponsiveContainer>
                    <BarChart data={byPriorityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                      <XAxis dataKey="priority" stroke="var(--fg-secondary)" fontSize={12} />
                      <YAxis allowDecimals={false} stroke="var(--fg-secondary)" fontSize={12} />
                      <Tooltip 
                        contentStyle={{ 
                          background: "var(--bg-secondary)", 
                          border: "1px solid var(--border)",
                          borderRadius: "var(--radius)",
                          boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                        }}
                      />
                      <Bar dataKey="count" radius={[8, 8, 0, 0]} animationDuration={1000}>
                        {byPriorityData.map((entry, index) => {
                          const colors = ['#dc2626', '#f59e0b', '#eab308', '#22c55e'];
                          return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Radar Chart */}
              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">{t("dashboard.charts.priorityComparison")}</h2>
                </div>
                <div style={{ width: "100%", height: 300 }}>
                  <ResponsiveContainer>
                    <RadarChart data={byPriorityData.map(d => ({ ...d, value: d.count }))}>
                      <PolarGrid stroke="var(--border)" opacity={0.3} />
                      <PolarAngleAxis 
                        dataKey="priority" 
                        stroke="var(--fg-secondary)"
                        fontSize={12}
                      />
                      <PolarRadiusAxis 
                        angle={90} 
                        domain={[0, 'dataMax']} 
                        stroke="var(--fg-secondary)"
                        fontSize={10}
                      />
                      <Radar
                        name={t("dashboard.labels.count")}
                        dataKey="count"
                        stroke="#667eea"
                        fill="#667eea"
                        fillOpacity={0.6}
                        animationDuration={1500}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          background: "var(--bg-secondary)", 
                          border: "1px solid var(--border)",
                          borderRadius: "var(--radius)",
                          boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                        }}
                      />
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
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
                <ResponsiveContainer>
                  <BarChart data={byDepartment} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                    <XAxis type="number" allowDecimals={false} stroke="var(--fg-secondary)" fontSize={12} />
                    <YAxis 
                      type="category"
                      dataKey="department_name" 
                      stroke="var(--fg-secondary)"
                      fontSize={12}
                      width={120}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        background: "var(--bg-secondary)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius)",
                        boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                      }}
                    />
                    <Bar 
                      dataKey="count" 
                      fill="url(#departmentGradient)" 
                      radius={[0, 8, 8, 0]}
                      animationDuration={1000}
                    >
                      <defs>
                        <linearGradient id="departmentGradient" x1="0" y1="0" x2="1" y2="0">
                          <stop offset="0%" stopColor="#3b82f6" stopOpacity={1}/>
                          <stop offset="100%" stopColor="#8b5cf6" stopOpacity={1}/>
                        </linearGradient>
                      </defs>
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
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
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={[
                          { name: t("dashboard.slaPie.onTime"), value: (slaCompliance.response_on_time || 0) + (slaCompliance.resolution_on_time || 0), fill: '#10b981' },
                          { name: t("dashboard.slaPie.warning"), value: (slaCompliance.response_warning || 0) + (slaCompliance.resolution_warning || 0), fill: '#f59e0b' },
                          { name: t("dashboard.slaPie.breached"), value: (slaCompliance.response_breached || 0) + (slaCompliance.resolution_breached || 0), fill: '#dc2626' },
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        animationDuration={1000}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          background: "var(--bg-secondary)", 
                          border: "1px solid var(--border)",
                          borderRadius: "var(--radius)",
                          boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
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
                  <ResponsiveContainer>
                    <BarChart data={slaByPriority.map(item => ({
                      priority: getPriorityLabel(item.priority),
                      response_rate: item.response_compliance_rate || 0,
                      resolution_rate: item.resolution_compliance_rate || 0
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                      <XAxis dataKey="priority" stroke="var(--fg-secondary)" fontSize={12} />
                      <YAxis domain={[0, 100]} stroke="var(--fg-secondary)" fontSize={12} />
                      <Tooltip 
                        contentStyle={{ 
                          background: "var(--bg-secondary)", 
                          border: "1px solid var(--border)",
                          borderRadius: "var(--radius)",
                          boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                        }}
                        formatter={(value: any) => `${value}%`}
                      />
                      <Legend />
                      <Bar dataKey="response_rate" fill="#667eea" name={t("dashboard.slaCards.responseRate")} radius={[8, 8, 0, 0]} />
                      <Bar dataKey="resolution_rate" fill="#10b981" name={t("dashboard.slaCards.resolutionRate")} radius={[8, 8, 0, 0]} />
                    </BarChart>
              </ResponsiveContainer>
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
                <ResponsiveContainer>
                  <BarChart data={byBranch}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                    <XAxis 
                      dataKey="branch_name" 
                      stroke="var(--fg-secondary)"
                      angle={-45}
                      textAnchor="end"
                      height={100}
                      fontSize={11}
                    />
                    <YAxis allowDecimals={false} stroke="var(--fg-secondary)" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        background: "var(--bg-secondary)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius)",
                        boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
                      }}
                    />
                    <Bar 
                      dataKey="count" 
                      fill="url(#branchGradient)" 
                      radius={[8, 8, 0, 0]}
                      animationDuration={1000}
                    >
                      <defs>
                        <linearGradient id="branchGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#f59e0b" stopOpacity={1}/>
                          <stop offset="100%" stopColor="#d97706" stopOpacity={1}/>
                        </linearGradient>
                      </defs>
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
