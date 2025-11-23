import { useEffect, useState } from "react";
import { apiGet, apiPost, apiPatch, isAuthenticated } from "../services/api";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

type TicketItem = {
  id: number;
  ticket_number: string;
  title: string;
  status: string;
  category: string;
  priority?: string;
  department_id?: number | null;
  assigned_to_id?: number | null;
  assigned_to?: { id: number; full_name: string; username: string } | null;
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

const getPriorityBadge = (priority: string) => {
  const priorityMap: Record<string, { text: string; class: string; emoji: string }> = {
    critical: { text: "بحرانی", class: "priority-critical", emoji: "🔴" },
    high: { text: "بالا", class: "priority-high", emoji: "🟠" },
    medium: { text: "متوسط", class: "priority-medium", emoji: "🟡" },
    low: { text: "پایین", class: "priority-low", emoji: "🟢" },
  };
  const p = priorityMap[priority] || { text: priority, class: "priority-medium", emoji: "🟡" };
  return <span className={`badge ${p.class}`} title={p.text}>{p.emoji} {p.text}</span>;
};

export default function Tickets() {
  const navigate = useNavigate();
  const [data, setData] = useState<TicketListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");
  
  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    // Redirect report_manager to dashboard (they can only see reports)
    const profile = JSON.parse(localStorage.getItem("imehr_profile") || "{}");
    if (profile.role === "report_manager") {
      navigate("/");
      return;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);
  const [category, setCategory] = useState<string>("");
  const [priority, setPriority] = useState<string>("");
  const [departmentId, setDepartmentId] = useState<string>("");
  const [query, setQuery] = useState<string>("");
  const [branches, setBranches] = useState<{ id: number; name: string; code: string }[]>([]);
  const [departments, setDepartments] = useState<{ id: number; name: string; code: string }[]>([]);
  const [users, setUsers] = useState<{ id: number; full_name: string; username: string }[]>([]);
  const [branchId, setBranchId] = useState<string>("");
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [selectedTickets, setSelectedTickets] = useState<Set<number>>(new Set());
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [bulkAction, setBulkAction] = useState<string>("");
  const [bulkStatus, setBulkStatus] = useState<string>("");
  const [bulkAssignee, setBulkAssignee] = useState<string>("");
  const [bulkProcessing, setBulkProcessing] = useState(false);

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
        if (priority) params.set("priority", priority);
        if (departmentId) params.set("department_id", departmentId);
        if (branchId) params.set("branch_id", branchId);
        const res = await apiGet(`/api/tickets?${params.toString()}`) as TicketListResponse;
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
  }, [page, status, category, priority, departmentId, branchId, query]);

  useEffect(() => {
    const loadBranches = async () => {
      try {
        const me = await apiGet(`/api/auth/me`) as { role?: string };
        setIsAdmin(me?.role === "admin" || me?.role === "central_admin");
        const b = await apiGet(`/api/branches`) as any[];
        setBranches(b.map((x: any) => ({ id: x.id, name: x.name, code: x.code })));
        const d = await apiGet(`/api/departments?page_size=100`) as any[];
        setDepartments(d.map((x: any) => ({ id: x.id, name: x.name, code: x.code })));
        const u = await apiGet(`/api/users?page_size=100`) as any;
        setUsers(u.items?.map((x: any) => ({ id: x.id, full_name: x.full_name, username: x.username })) || []);
      } catch {
        // ignore
      }
    };
    loadBranches();
  }, []);

  const toggleSelectTicket = (ticketId: number) => {
    setSelectedTickets((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(ticketId)) {
        newSet.delete(ticketId);
      } else {
        newSet.add(ticketId);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedTickets.size === data?.items.length) {
      setSelectedTickets(new Set());
    } else {
      setSelectedTickets(new Set(data?.items.map(t => t.id) || []));
    }
  };

  const handleBulkAction = async () => {
    if (selectedTickets.size === 0 || !bulkAction) return;
    
    setBulkProcessing(true);
    setError(null);
    
    try {
      const payload: any = {
        ticket_ids: Array.from(selectedTickets),
        action: bulkAction
      };
      
      if (bulkAction === "status" && bulkStatus) {
        payload.status = bulkStatus;
      } else if (bulkAction === "assign" && bulkAssignee) {
        payload.assigned_to_id = Number(bulkAssignee);
      }
      
      const result = await apiPost("/api/tickets/bulk-action", payload) as any;
      
      if (result.failed_count > 0) {
        setError(`عملیات روی ${result.success_count} تیکت موفق بود، اما ${result.failed_count} تیکت ناموفق بود.`);
      } else {
        setError(null);
      }
      
      // Clear selections and reload
      setSelectedTickets(new Set());
      setShowBulkActions(false);
      setBulkAction("");
      setBulkStatus("");
      setBulkAssignee("");
      
      // Reload tickets
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "10");
      if (status) params.set("status", status);
      if (category) params.set("category", category);
      if (priority) params.set("priority", priority);
      if (departmentId) params.set("department_id", departmentId);
      if (branchId) params.set("branch_id", branchId);
      const res = await apiGet(`/api/tickets?${params.toString()}`) as TicketListResponse;
      if (query) {
        res.items = res.items.filter((it: any) =>
          it.title?.toLowerCase().includes(query.toLowerCase())
        );
      }
      setData(res);
      
    } catch (e: any) {
      setError(e?.message || "خطا در انجام عملیات گروهی");
    } finally {
      setBulkProcessing(false);
    }
  };

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>🎫 تیکت‌ها</h1>
        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          {data && (
            <div style={{ color: "var(--fg-secondary)", fontSize: 14 }}>
              مجموع: <strong>{data.total}</strong> تیکت
            </div>
          )}
          {selectedTickets.size > 0 && (
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <span style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
                {selectedTickets.size} تیکت انتخاب شده
              </span>
              <button
                onClick={() => setShowBulkActions(true)}
                className="secondary"
                style={{ padding: "8px 16px", fontSize: 14 }}
              >
                ⚡ عملیات گروهی
              </button>
              <button
                onClick={() => setSelectedTickets(new Set())}
                className="secondary"
                style={{ padding: "8px 16px", fontSize: 14 }}
              >
                ✖️ لغو انتخاب
              </button>
            </div>
          )}
        </div>
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
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="">⚡ همه اولویت‌ها</option>
          <option value="critical">🔴 بحرانی</option>
          <option value="high">🟠 بالا</option>
          <option value="medium">🟡 متوسط</option>
          <option value="low">🟢 پایین</option>
        </select>
        {departments.length > 0 && (
          <select value={departmentId} onChange={(e) => setDepartmentId(e.target.value)}>
            <option value="">🏢 همه دپارتمان‌ها</option>
            {departments.map((d) => (
              <option key={d.id} value={String(d.id)}>
                {d.name}
              </option>
            ))}
          </select>
        )}
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
                    {isAdmin && (
                      <th style={{ width: 40 }}>
                        <input
                          type="checkbox"
                          checked={selectedTickets.size === data.items.length && data.items.length > 0}
                          onChange={toggleSelectAll}
                          style={{ cursor: "pointer" }}
                        />
                      </th>
                    )}
                    <th>شماره تیکت</th>
                    <th>عنوان</th>
                    <th>اولویت</th>
                    <th>وضعیت</th>
                    <th>دسته</th>
                    <th>دپارتمان</th>
                    <th>مسئول</th>
                    <th>تاریخ ایجاد</th>
                    <th>عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((t) => (
                    <tr key={t.id}>
                      {isAdmin && (
                        <td>
                          <input
                            type="checkbox"
                            checked={selectedTickets.has(t.id)}
                            onChange={() => toggleSelectTicket(t.id)}
                            style={{ cursor: "pointer" }}
                          />
                        </td>
                      )}
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
                      <td>{getPriorityBadge(t.priority || "medium")}</td>
                      <td>{getStatusBadge(t.status)}</td>
                      <td>{getCategoryText(t.category)}</td>
                      <td style={{ color: "var(--fg-secondary)", fontSize: 13 }}>
                        {t.department_id ? (
                          departments.find(d => d.id === t.department_id)?.name || "-"
                        ) : "-"}
                      </td>
                      <td style={{ color: "var(--fg-secondary)", fontSize: 13 }}>
                        {t.assigned_to ? t.assigned_to.full_name : "-"}
                      </td>
                      <td style={{ color: "var(--fg-secondary)", fontSize: 13 }}>
                        {t.created_at ? new Date(t.created_at).toLocaleDateString("fa-IR") : "-"}
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                          <Link to={`/tickets/${t.id}`}>
                            <button className="secondary" style={{ padding: "6px 12px", fontSize: 13 }}>
                              👁️ مشاهده
                            </button>
                          </Link>
                          {isAdmin && (
                            <>
                              {t.status !== "in_progress" && (
                                <button
                                  className="secondary"
                                  style={{ padding: "6px 12px", fontSize: 13 }}
                                  onClick={async () => {
                                    try {
                                      await apiPatch(`/api/tickets/${t.id}/status`, { status: "in_progress" });
                                      // Reload
                                      const params = new URLSearchParams();
                                      params.set("page", String(page));
                                      params.set("page_size", "10");
                                      if (status) params.set("status", status);
                                      if (category) params.set("category", category);
                                      if (priority) params.set("priority", priority);
                                      if (departmentId) params.set("department_id", departmentId);
                                      if (branchId) params.set("branch_id", branchId);
                                      const res = await apiGet(`/api/tickets?${params.toString()}`) as TicketListResponse;
                                      if (query) {
                                        res.items = res.items.filter((it: any) =>
                                          it.title?.toLowerCase().includes(query.toLowerCase())
                                        );
                                      }
                                      setData(res);
                                    } catch (e: any) {
                                      setError(e?.message || "خطا در تغییر وضعیت");
                                    }
                                  }}
                                  title="شروع کار"
                                >
                                  ▶️
                                </button>
                              )}
                              {t.status !== "resolved" && t.status !== "closed" && (
                                <button
                                  className="secondary"
                                  style={{ padding: "6px 12px", fontSize: 13 }}
                                  onClick={async () => {
                                    try {
                                      await apiPatch(`/api/tickets/${t.id}/status`, { status: "resolved" });
                                      // Reload
                                      const params = new URLSearchParams();
                                      params.set("page", String(page));
                                      params.set("page_size", "10");
                                      if (status) params.set("status", status);
                                      if (category) params.set("category", category);
                                      if (priority) params.set("priority", priority);
                                      if (departmentId) params.set("department_id", departmentId);
                                      if (branchId) params.set("branch_id", branchId);
                                      const res = await apiGet(`/api/tickets?${params.toString()}`) as TicketListResponse;
                                      if (query) {
                                        res.items = res.items.filter((it: any) =>
                                          it.title?.toLowerCase().includes(query.toLowerCase())
                                        );
                                      }
                                      setData(res);
                                    } catch (e: any) {
                                      setError(e?.message || "خطا در تغییر وضعیت");
                                    }
                                  }}
                                  title="حل شده"
                                >
                                  ✅
                                </button>
                              )}
                              {t.status !== "closed" && (
                                <button
                                  className="secondary"
                                  style={{ padding: "6px 12px", fontSize: 13 }}
                                  onClick={async () => {
                                    try {
                                      await apiPatch(`/api/tickets/${t.id}/status`, { status: "closed" });
                                      // Reload
                                      const params = new URLSearchParams();
                                      params.set("page", String(page));
                                      params.set("page_size", "10");
                                      if (status) params.set("status", status);
                                      if (category) params.set("category", category);
                                      if (priority) params.set("priority", priority);
                                      if (departmentId) params.set("department_id", departmentId);
                                      if (branchId) params.set("branch_id", branchId);
                                      const res = await apiGet(`/api/tickets?${params.toString()}`) as TicketListResponse;
                                      if (query) {
                                        res.items = res.items.filter((it: any) =>
                                          it.title?.toLowerCase().includes(query.toLowerCase())
                                        );
                                      }
                                      setData(res);
                                    } catch (e: any) {
                                      setError(e?.message || "خطا در تغییر وضعیت");
                                    }
                                  }}
                                  title="بستن"
                                >
                                  🔒
                                </button>
                              )}
                            </>
                          )}
                        </div>
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

      {/* Bulk Actions Modal */}
      {showBulkActions && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000
        }}>
          <div className="card" style={{ maxWidth: 500, width: "90%", maxHeight: "90vh", overflow: "auto" }}>
            <div className="card-header">
              <h2 className="card-title">⚡ عملیات گروهی</h2>
              <button
                onClick={() => {
                  setShowBulkActions(false);
                  setBulkAction("");
                  setBulkStatus("");
                  setBulkAssignee("");
                }}
                className="secondary"
                style={{ padding: "4px 8px" }}
              >
                ✖️
              </button>
            </div>
            
            <div style={{ marginBottom: 16 }}>
              <strong>{selectedTickets.size} تیکت</strong> انتخاب شده است.
            </div>
            
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              نوع عملیات
            </label>
            <select
              value={bulkAction}
              onChange={(e) => {
                setBulkAction(e.target.value);
                setBulkStatus("");
                setBulkAssignee("");
              }}
              style={{ width: "100%", marginBottom: 16 }}
            >
              <option value="">انتخاب کنید...</option>
              <option value="status">تغییر وضعیت</option>
              <option value="assign">تخصیص به کارشناس</option>
              <option value="unassign">حذف تخصیص</option>
              {isAdmin && <option value="delete">حذف تیکت‌ها</option>}
            </select>
            
            {bulkAction === "status" && (
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                  وضعیت جدید
                </label>
                <select
                  value={bulkStatus}
                  onChange={(e) => setBulkStatus(e.target.value)}
                  style={{ width: "100%" }}
                >
                  <option value="">انتخاب کنید...</option>
                  <option value="pending">⏳ در انتظار</option>
                  <option value="in_progress">🔄 در حال انجام</option>
                  <option value="resolved">✅ حل شده</option>
                  <option value="closed">🔒 بسته شده</option>
                </select>
              </div>
            )}
            
            {bulkAction === "assign" && (
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                  کارشناس مسئول
                </label>
                <select
                  value={bulkAssignee}
                  onChange={(e) => setBulkAssignee(e.target.value)}
                  style={{ width: "100%" }}
                >
                  <option value="">انتخاب کنید...</option>
                  {users.map((u: { id: number; full_name: string; username: string }) => (
                    <option key={u.id} value={String(u.id)}>
                      {u.full_name} ({u.username})
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            {bulkAction === "delete" && (
              <div className="alert error" style={{ marginBottom: 16 }}>
                ⚠️ هشدار: این عملیات غیرقابل بازگشت است. آیا مطمئن هستید؟
              </div>
            )}
            
            <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
              <button
                onClick={() => {
                  setShowBulkActions(false);
                  setBulkAction("");
                  setBulkStatus("");
                  setBulkAssignee("");
                }}
                className="secondary"
                disabled={bulkProcessing}
              >
                انصراف
              </button>
              <button
                onClick={handleBulkAction}
                disabled={bulkProcessing || !bulkAction || (bulkAction === "status" && !bulkStatus) || (bulkAction === "assign" && !bulkAssignee)}
                className="danger"
              >
                {bulkProcessing ? "⏳ در حال پردازش..." : bulkAction === "delete" ? "🗑️ حذف" : "💾 اعمال"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
