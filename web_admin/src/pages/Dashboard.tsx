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
      const ov = await apiGet("/api/reports/overview");
      const bs = await apiGet("/api/reports/by-status");
      const df = new URLSearchParams();
      if (dateFrom) df.set("date_from", dateFrom);
      if (dateTo) df.set("date_to", dateTo);
      const bd = await apiGet(`/api/reports/by-date?${df.toString()}`);
      const bb = await apiGet(`/api/reports/by-branch`);
      const rt = await apiGet(`/api/reports/response-time`);
      setOverview(ov);
      setByStatus(bs);
      setByDate(bd);
      setByBranch(bb.map((x: any) => ({ branch_name: x.branch_name, count: x.count })));
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

  const byStatusData = useMemo(
    () => Object.entries(byStatus).map(([status, count]) => ({ status, count })),
    [byStatus]
  );

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div>
      <h1>داشبورد</h1>
      {loading && <div>در حال بارگذاری...</div>}
      {error && <div style={{ color: "red", padding: 12, marginBottom: 16 }}>{error}</div>}

      <section>
        <h2>نمای کلی</h2>
        {overview ? (
          <ul>
            <li>مجموع تیکت‌ها: {overview.total}</li>
            <li>در انتظار: {overview.pending || 0}</li>
            <li>در حال انجام: {overview.in_progress || 0}</li>
            <li>حل شده: {overview.resolved || 0}</li>
            <li>بسته شده: {overview.closed || 0}</li>
          </ul>
        ) : (
          <div>در حال بارگذاری...</div>
        )}
        <div style={{ marginTop: 8 }}>
          <strong>میانگین زمان پاسخ‌دهی (ساعت): </strong>
          {responseHours !== null ? responseHours.toFixed(2) : "-"}
        </div>
      </section>

      <section>
        <h2>بر اساس وضعیت</h2>
        <div style={{ width: "100%", height: 280 }}>
          <ResponsiveContainer>
            <BarChart data={byStatusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
          <a href={`${API_BASE_URL}/api/reports/export?kind=by-status`} target="_blank" rel="noreferrer">
            Export CSV (By Status)
          </a>
          <a href={`${API_BASE_URL}/api/reports/export?kind=overview`} target="_blank" rel="noreferrer">
            Export CSV (Overview)
          </a>
        </div>
      </section>

      <section>
        <h2>بر اساس تاریخ</h2>
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
          <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
          <button onClick={loadReports}>اعمال</button>
        </div>
        <div style={{ width: "100%", height: 280 }}>
          <ResponsiveContainer>
            <LineChart data={byDate}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div style={{ marginTop: 8 }}>
          <a
            href={`${API_BASE_URL}/api/reports/export?kind=by-date`}
            target="_blank"
            rel="noreferrer"
          >
            Export CSV (By Date)
          </a>
        </div>
      </section>

      <section>
        <h2>بر اساس شعبه</h2>
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={byBranch}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="branch_name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ marginTop: 8 }}>
          <a
            href={`${API_BASE_URL}/api/reports/export?kind=by-branch`}
            target="_blank"
            rel="noreferrer"
          >
            Export CSV (By Branch)
          </a>
        </div>
      </section>
    </div>
  );
}

