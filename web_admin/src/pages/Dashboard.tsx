import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, API_BASE_URL, isAuthenticated } from "../services/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line
} from "recharts";

export default function Dashboard() {
  const navigate = useNavigate();
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
  const [responseHours, setResponseHours] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

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
      const bd = await apiGet(`/api/reports/by-date?${df.toString()}`) as { date: string; count: number }[];
      const bb = await apiGet(`/api/reports/by-branch`) as { branch_name: string; count: number; branch_id?: number; branch_code?: string }[];
      const bp = await apiGet(`/api/reports/by-priority`) as Record<string, number>;
      const bdpt = await apiGet(`/api/reports/by-department`) as { department_name: string; count: number; department_id?: number; department_code?: string }[];
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
      setError(e?.message || "خطا در دریافت گزارش‌ها");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated()) {
      loadReports();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reload reports when date filters change
  useEffect(() => {
    if (isAuthenticated() && (dateFrom || dateTo)) {
      loadReports();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dateFrom, dateTo]);

  const byStatusData = useMemo(
    () => Object.entries(byStatus).map(([status, count]) => ({ 
      status: status === "pending" ? "در انتظار" : 
              status === "in_progress" ? "در حال انجام" :
              status === "resolved" ? "حل شده" : "بسته شده",
      count 
    })),
    [byStatus]
  );

  const byPriorityData = useMemo(
    () => Object.entries(byPriority).map(([priority, count]) => ({
      priority: priority === "critical" ? "🔴 بحرانی" :
                priority === "high" ? "🟠 بالا" :
                priority === "medium" ? "🟡 متوسط" : "🟢 پایین",
      count
    })),
    [byPriority]
  );

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>📊 داشبورد</h1>
        <button onClick={loadReports} disabled={loading} className="secondary">
          {loading ? "🔄 در حال بارگذاری..." : "🔄 به‌روزرسانی"}
        </button>
      </div>

      {loading && !overview && (
        <div style={{ textAlign: "center", padding: 40 }}>
          <div className="loading" style={{ margin: "0 auto" }}></div>
          <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
        </div>
      )}

      {error && (
        <div className="alert error fade-in">
          <strong>خطا:</strong> {error}
        </div>
      )}

      {overview && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-4" style={{ marginBottom: 24 }}>
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}>
              <div className="stat-label">مجموع تیکت‌ها</div>
              <div className="stat-value">{overview.total || 0}</div>
            </div>
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)" }}>
              <div className="stat-label">در انتظار</div>
              <div className="stat-value">{overview.pending || 0}</div>
            </div>
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)" }}>
              <div className="stat-label">در حال انجام</div>
              <div className="stat-value">{overview.in_progress || 0}</div>
            </div>
            <div className="stat-card" style={{ background: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)" }}>
              <div className="stat-label">حل شده</div>
              <div className="stat-value">{overview.resolved || 0}</div>
            </div>
          </div>

          {/* Response Time Card */}
          {responseHours !== null && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">⏱️ میانگین زمان پاسخ‌دهی</h2>
              </div>
              <div style={{ fontSize: 48, fontWeight: 700, color: "var(--primary)", textAlign: "center", padding: "20px 0" }}>
                {responseHours.toFixed(2)} <span style={{ fontSize: 24, color: "var(--fg-secondary)" }}>ساعت</span>
              </div>
            </div>
          )}

          {/* Status Chart */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <h2 className="card-title">📊 تیکت‌ها بر اساس وضعیت</h2>
              <a 
                href={`${API_BASE_URL}/api/reports/export?kind=by-status`} 
                target="_blank" 
                rel="noreferrer"
                style={{ fontSize: 14 }}
              >
                📥 CSV
              </a>
            </div>
            <div style={{ width: "100%", height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={byStatusData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="status" stroke="var(--fg-secondary)" />
                  <YAxis allowDecimals={false} stroke="var(--fg-secondary)" />
                  <Tooltip 
                    contentStyle={{ 
                      background: "var(--bg-secondary)", 
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius)"
                    }}
                  />
                  <Bar dataKey="count" fill="#667eea" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Date Chart */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <h2 className="card-title">📅 تیکت‌ها بر اساس تاریخ</h2>
              <a 
                href={`${API_BASE_URL}/api/reports/export?kind=by-date`} 
                target="_blank" 
                rel="noreferrer"
                style={{ fontSize: 14 }}
              >
                📥 CSV
              </a>
            </div>
            <div className="filters" style={{ marginBottom: 16 }}>
              <input 
                type="date" 
                value={dateFrom} 
                onChange={(e) => setDateFrom(e.target.value)}
                placeholder="از تاریخ"
              />
              <input 
                type="date" 
                value={dateTo} 
                onChange={(e) => setDateTo(e.target.value)}
                placeholder="تا تاریخ"
              />
              <button onClick={() => loadReports()} disabled={loading}>
                🔍 اعمال فیلتر
              </button>
              {(dateFrom || dateTo) && (
                <button 
                  onClick={() => {
                    setDateFrom("");
                    setDateTo("");
                  }} 
                  className="secondary"
                  disabled={loading}
                >
                  🗑️ پاک کردن فیلتر
                </button>
              )}
            </div>
            <div style={{ width: "100%", height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={byDate}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="date" stroke="var(--fg-secondary)" />
                  <YAxis allowDecimals={false} stroke="var(--fg-secondary)" />
                  <Tooltip 
                    contentStyle={{ 
                      background: "var(--bg-secondary)", 
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius)"
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    dot={{ fill: "#10b981", r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Priority Chart */}
          {byPriorityData.length > 0 && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">⚡ تیکت‌ها بر اساس اولویت</h2>
                <a 
                  href={`${API_BASE_URL}/api/reports/export?kind=by-priority`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ fontSize: 14 }}
                >
                  📥 CSV
                </a>
              </div>
              <div style={{ width: "100%", height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={byPriorityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="priority" stroke="var(--fg-secondary)" />
                    <YAxis allowDecimals={false} stroke="var(--fg-secondary)" />
                    <Tooltip 
                      contentStyle={{ 
                        background: "var(--bg-secondary)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius)"
                      }}
                    />
                    <Bar dataKey="count" fill="#dc2626" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Department Chart */}
          {byDepartment.length > 0 && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">🏢 تیکت‌ها بر اساس دپارتمان</h2>
                <a 
                  href={`${API_BASE_URL}/api/reports/export?kind=by-department`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ fontSize: 14 }}
                >
                  📥 CSV
                </a>
              </div>
              <div style={{ width: "100%", height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={byDepartment}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis 
                      dataKey="department_name" 
                      stroke="var(--fg-secondary)"
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis allowDecimals={false} stroke="var(--fg-secondary)" />
                    <Tooltip 
                      contentStyle={{ 
                        background: "var(--bg-secondary)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius)"
                      }}
                    />
                    <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* SLA Compliance Card */}
          {slaCompliance && slaCompliance.total_tickets_with_sla > 0 && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">⏱️ گزارش رعایت SLA</h2>
                <a 
                  href={`${API_BASE_URL}/api/reports/export?kind=sla-compliance`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ fontSize: 14 }}
                >
                  📥 CSV
                </a>
              </div>
              <div className="grid grid-cols-2" style={{ gap: 16, marginBottom: 16 }}>
                <div>
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>مجموع تیکت‌های دارای SLA</div>
                  <div style={{ fontSize: 24, fontWeight: 700 }}>{slaCompliance.total_tickets_with_sla}</div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>تیکت‌های Escalated</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: slaCompliance.escalated_count > 0 ? "var(--warning)" : "var(--success)" }}>
                    {slaCompliance.escalated_count}
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2" style={{ gap: 16, marginBottom: 16 }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>وضعیت پاسخ</div>
                  <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                    <div style={{ flex: 1, minWidth: 100 }}>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>✅ در مهلت</div>
                      <div style={{ fontSize: 18, fontWeight: 600, color: "var(--success)" }}>
                        {slaCompliance.response_on_time || 0}
                      </div>
                    </div>
                    <div style={{ flex: 1, minWidth: 100 }}>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>⚠️ هشدار</div>
                      <div style={{ fontSize: 18, fontWeight: 600, color: "var(--warning)" }}>
                        {slaCompliance.response_warning || 0}
                      </div>
                    </div>
                    <div style={{ flex: 1, minWidth: 100 }}>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>❌ نقض شده</div>
                      <div style={{ fontSize: 18, fontWeight: 600, color: "var(--error)" }}>
                        {slaCompliance.response_breached || 0}
                      </div>
                    </div>
                  </div>
                  <div style={{ marginTop: 8, padding: 8, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
                    <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>نرخ رعایت</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: slaCompliance.response_compliance_rate >= 80 ? "var(--success)" : "var(--warning)" }}>
                      {slaCompliance.response_compliance_rate}%
                    </div>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>وضعیت حل</div>
                  <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                    <div style={{ flex: 1, minWidth: 100 }}>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>✅ در مهلت</div>
                      <div style={{ fontSize: 18, fontWeight: 600, color: "var(--success)" }}>
                        {slaCompliance.resolution_on_time || 0}
                      </div>
                    </div>
                    <div style={{ flex: 1, minWidth: 100 }}>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>⚠️ هشدار</div>
                      <div style={{ fontSize: 18, fontWeight: 600, color: "var(--warning)" }}>
                        {slaCompliance.resolution_warning || 0}
                      </div>
                    </div>
                    <div style={{ flex: 1, minWidth: 100 }}>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>❌ نقض شده</div>
                      <div style={{ fontSize: 18, fontWeight: 600, color: "var(--error)" }}>
                        {slaCompliance.resolution_breached || 0}
                      </div>
                    </div>
                  </div>
                  <div style={{ marginTop: 8, padding: 8, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
                    <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>نرخ رعایت</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: slaCompliance.resolution_compliance_rate >= 80 ? "var(--success)" : "var(--warning)" }}>
                      {slaCompliance.resolution_compliance_rate}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SLA by Priority */}
          {slaByPriority.length > 0 && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">⏱️ رعایت SLA بر اساس اولویت</h2>
              </div>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%" }}>
                  <thead>
                    <tr>
                      <th>اولویت</th>
                      <th>تعداد تیکت</th>
                      <th>پاسخ در مهلت</th>
                      <th>پاسخ نقض شده</th>
                      <th>حل در مهلت</th>
                      <th>حل نقض شده</th>
                      <th>نرخ رعایت پاسخ</th>
                      <th>نرخ رعایت حل</th>
                    </tr>
                  </thead>
                  <tbody>
                    {slaByPriority.map((item, idx) => (
                      <tr key={idx}>
                        <td>
                          {item.priority === "critical" ? "🔴 بحرانی" :
                           item.priority === "high" ? "🟠 بالا" :
                           item.priority === "medium" ? "🟡 متوسط" : "🟢 پایین"}
                        </td>
                        <td>{item.total_tickets}</td>
                        <td style={{ color: "var(--success)" }}>{item.response_on_time}</td>
                        <td style={{ color: "var(--error)" }}>{item.response_breached}</td>
                        <td style={{ color: "var(--success)" }}>{item.resolution_on_time}</td>
                        <td style={{ color: "var(--error)" }}>{item.resolution_breached}</td>
                        <td>
                          <span style={{ 
                            color: item.response_compliance_rate >= 80 ? "var(--success)" : "var(--warning)",
                            fontWeight: 600
                          }}>
                            {item.response_compliance_rate}%
                          </span>
                        </td>
                        <td>
                          <span style={{ 
                            color: item.resolution_compliance_rate >= 80 ? "var(--success)" : "var(--warning)",
                            fontWeight: 600
                          }}>
                            {item.resolution_compliance_rate}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Branch Chart */}
          {byBranch.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">🏢 تیکت‌ها بر اساس شعبه</h2>
                <a 
                  href={`${API_BASE_URL}/api/reports/export?kind=by-branch`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ fontSize: 14 }}
                >
                  📥 CSV
                </a>
              </div>
              <div style={{ width: "100%", height: 300 }}>
                <ResponsiveContainer>
                  <BarChart data={byBranch}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis 
                      dataKey="branch_name" 
                      stroke="var(--fg-secondary)"
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis allowDecimals={false} stroke="var(--fg-secondary)" />
                    <Tooltip 
                      contentStyle={{ 
                        background: "var(--bg-secondary)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius)"
                      }}
                    />
                    <Bar dataKey="count" fill="#f59e0b" radius={[8, 8, 0, 0]} />
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
