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

export default function Tickets() {
  const navigate = useNavigate();
  const [data, setData] = useState<TicketListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");
  const [category, setCategory] = useState<string>("");
  const [query, setQuery] = useState<string>("");

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
        const res = await apiGet(`/api/tickets?${params.toString()}`);
        // جستجوی ساده سمت کلاینت بر اساس عنوان در صورت تعیین query
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
  }, [page, status, category, query]);

  return (
    <div>
      <h1>تیکت‌ها</h1>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <input
          placeholder="جستجو عنوان..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <label>
          وضعیت:
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">همه</option>
            <option value="pending">در انتظار</option>
            <option value="in_progress">در حال انجام</option>
            <option value="resolved">حل شده</option>
            <option value="closed">بسته شده</option>
          </select>
        </label>
        <label>
          دسته:
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">همه</option>
            <option value="internet">اینترنت</option>
            <option value="equipment">تجهیزات</option>
            <option value="software">نرم‌افزار</option>
            <option value="other">سایر</option>
          </select>
        </label>
      </div>
      {loading && <div>در حال بارگذاری...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      {data && (
        <>
          <table border={1} cellPadding={6} style={{ width: "100%", marginTop: 12 }}>
            <thead>
              <tr>
                <th>شماره</th>
                <th>عنوان</th>
                <th>وضعیت</th>
                <th>دسته</th>
                <th>تاریخ</th>
                <th>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((t) => (
                <tr key={t.id}>
                  <td>{t.ticket_number}</td>
                  <td>{t.title}</td>
                  <td>{t.status}</td>
                  <td>{t.category}</td>
                  <td>{t.created_at?.slice(0, 10) || ""}</td>
                  <td>
                    <Link to={`/tickets/${t.id}`}>جزئیات</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              قبلی
            </button>
            <span>
              صفحه {data.page} از {data.total_pages}
            </span>
            <button disabled={page >= data.total_pages} onClick={() => setPage((p) => p + 1)}>
              بعدی
            </button>
          </div>
        </>
      )}
    </div>
  );
}

