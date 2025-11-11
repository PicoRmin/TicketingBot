import { useEffect, useState } from "react";
import { apiGet, isAuthenticated } from "../services/api";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

type TicketItem = {
  id: number;
  ticket_number: string;
  title: string;
  status: string;
  category: string;
  created_at?: string;
};

type TicketListResponse = {
  items: TicketItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

const getStatusBadge = (status: string) => {
  const statusMap: Record<string, { text: string; class: string }> = {
    pending: { text: "در انتظار", class: "pending" },
    in_progress: { text: "در حال انجام", class: "in_progress" },
    resolved: { text: "حل شده", class: "resolved" },
    closed: { text: "بسته شده", class: "closed" },
  };
  const s = statusMap[status] || { text: status, class: "pending" };
  return <span className={`badge ${s.class}`}>{s.text}</span>;
};

const getCategoryText = (category: string) => {
  const catMap: Record<string, string> = {
    internet: "🌐 اینترنت",
    equipment: "💻 تجهیزات",
    software: "📱 نرم‌افزار",
    other: "📋 سایر",
  };
  return catMap[category] || category;
};

export default function Tickets() {
  const navigate = useNavigate();
  const [data, setData] = useState<TicketListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");
  const [category, setCategory] = useState<string>("");
  const [query, setQuery] = useState<string>("");
  const [branches, setBranches] = useState<{ id: number; name: string; code: string }[]>([]);
  const [branchId, setBranchId] = useState<string>("");
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, []);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        params.set("page", String(page));
        params.set("page_size", "10");
        if (status) params.set("status", status);
        if (category) params.set("category", category);
        if (branchId) params.set("branch_id", branchId);
        const res = await apiGet(`/api/tickets?${params.toString()}`);
        if (query) {
          res.items = res.items.filter((it: any) =>
            it.title?.toLowerCase().includes(query.toLowerCase())
          );
        }
        setData(res);
      } catch (e: any) {
        setError(e?.message || "خطا در دریافت لیست تیکت‌ها");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [page, status, category, branchId, query]);

  useEffect(() => {
    const loadBranches = async () => {
      try {
        const me = await apiGet(`/api/auth/me`);
        setIsAdmin(me?.role === "admin");
        const b = await apiGet(`/api/branches`);
        setBranches(b.map((x: any) => ({ id: x.id, name: x.name, code: x.code })));
      } catch {
        // ignore
      }
    };
    loadBranches();
  }, []);

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>🎫 تیکت‌ها</h1>
        {data && (
          <div style={{ color: "var(--fg-secondary)", fontSize: 14 }}>
            مجموع: <strong>{data.total}</strong> تیکت
          </div>
        )}
      </div>

      <div className="filters">
        <input
          placeholder="🔍 جستجو در عنوان..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ flex: 2 }}
        />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">📊 همه وضعیت‌ها</option>
          <option value="pending">⏳ در انتظار</option>
          <option value="in_progress">🔄 در حال انجام</option>
          <option value="resolved">✅ حل شده</option>
          <option value="closed">🔒 بسته شده</option>
        </select>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">📂 همه دسته‌ها</option>
          <option value="internet">🌐 اینترنت</option>
          <option value="equipment">💻 تجهیزات</option>
          <option value="software">📱 نرم‌افزار</option>
          <option value="other">📋 سایر</option>
        </select>
        {isAdmin && branches.length > 0 && (
          <select value={branchId} onChange={(e) => setBranchId(e.target.value)}>
            <option value="">🏢 همه شعب</option>
            {branches.map((b) => (
              <option key={b.id} value={String(b.id)}>
                {b.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {loading && (
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

      {data && !loading && (
        <>
          {data.items.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: 60 }}>
              <div style={{ fontSize: 64, marginBottom: 16 }}>📭</div>
              <h2 style={{ margin: "0 0 8px 0" }}>تیکتی یافت نشد</h2>
              <p style={{ color: "var(--fg-secondary)", margin: 0 }}>
                هیچ تیکتی با فیلترهای انتخابی شما یافت نشد.
              </p>
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>شماره تیکت</th>
                    <th>عنوان</th>
                    <th>وضعیت</th>
                    <th>دسته</th>
                    <th>تاریخ ایجاد</th>
                    <th>عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((t) => (
                    <tr key={t.id}>
                      <td>
                        <code style={{ 
                          background: "var(--bg-secondary)", 
                          padding: "4px 8px", 
                          borderRadius: "4px",
                          fontSize: 12
                        }}>
                          {t.ticket_number}
                        </code>
                      </td>
                      <td style={{ fontWeight: 500 }}>{t.title}</td>
                      <td>{getStatusBadge(t.status)}</td>
                      <td>{getCategoryText(t.category)}</td>
                      <td style={{ color: "var(--fg-secondary)", fontSize: 13 }}>
                        {t.created_at ? new Date(t.created_at).toLocaleDateString("fa-IR") : "-"}
                      </td>
                      <td>
                        <Link to={`/tickets/${t.id}`}>
                          <button className="secondary" style={{ padding: "6px 12px", fontSize: 13 }}>
                            👁️ مشاهده
                          </button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {data.total_pages > 1 && (
            <div className="pagination">
              <button 
                disabled={page <= 1} 
                onClick={() => setPage((p) => p - 1)}
                className="secondary"
              >
                ⬅️ قبلی
              </button>
              <span style={{ padding: "0 16px", color: "var(--fg-secondary)" }}>
                صفحه <strong>{data.page}</strong> از <strong>{data.total_pages}</strong>
              </span>
              <button 
                disabled={page >= data.total_pages} 
                onClick={() => setPage((p) => p + 1)}
                className="secondary"
              >
                بعدی ➡️
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
