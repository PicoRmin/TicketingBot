import { useCallback, useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, apiPost, isAuthenticated, getStoredProfile } from "../services/api";
import type { AuthProfile } from "../services/api";
import CustomFieldRenderer from "../components/CustomFieldRenderer";
import { Link } from "react-router-dom";
import { KnowledgeSuggestions } from "../components/KnowledgeSuggestions";
import { stagger, slideIn, scaleIn } from "../lib/gsap";

type TicketItem = {
  id: number;
  ticket_number: string;
  title: string;
  status: string;
  category: string;
  priority?: string;
  assigned_to?: { id: number; full_name: string; username: string } | null;
  created_at?: string;
  updated_at?: string;
};

type TicketListResponse = {
  items: TicketItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type BranchSummary = { id: number; name: string; code: string };

type CustomFieldDefinition = {
  id: number;
  name: string;
  label: string;
  label_en?: string | null;
  field_type: string;
  default_value?: string | null;
  is_visible_to_user: boolean;
  is_required: boolean;
  is_editable_by_user: boolean;
  display_order?: number | null;
  config?: Record<string, unknown> | null;
  placeholder?: string | null;
  description?: string | null;
};

type CustomFieldValuePayload = {
  custom_field_id: number;
  value: string | null;
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

export default function UserPortal() {
  const navigate = useNavigate();
  const [profile] = useState<AuthProfile | null>(() => getStoredProfile());
  const [tickets, setTickets] = useState<TicketItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [showNewTicketForm, setShowNewTicketForm] = useState(false);
  
  // New ticket form
  const [newTicket, setNewTicket] = useState({
    title: "",
    description: "",
    category: "other",
    priority: "medium",
    branch_id: "",
  });
  const [branches, setBranches] = useState<BranchSummary[]>([]);
  const [submitting, setSubmitting] = useState(false);
  
  // Custom Fields states
  const [customFields, setCustomFields] = useState<CustomFieldDefinition[]>([]);
  const [customFieldValues, setCustomFieldValues] = useState<Record<number, string | null>>({});

  const loadBranches = useCallback(async () => {
    try {
      const brs = (await apiGet("/api/branches")) as BranchSummary[];
      setBranches(brs);
    } catch (err) {
      console.error("Error loading branches:", err);
    }
  }, []);

  const loadTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "10");
      if (statusFilter) {
        params.set("status", statusFilter);
      }

      const response = (await apiGet(`/api/tickets?${params.toString()}`)) as TicketListResponse;
      setTickets(response.items || []);
      setTotalPages(response.total_pages || 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در دریافت تیکت‌ها");
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    if (profile && profile.role !== "user") {
      navigate("/");
      return;
    }

    loadBranches();
  }, [navigate, profile, loadBranches]);

  useEffect(() => {
    if (isAuthenticated() && profile?.role === "user") {
      loadTickets();
    }
  }, [profile, loadTickets]);

  /**
   * بارگذاری فیلدهای سفارشی بر اساس دسته‌بندی انتخاب شده
   * Load custom fields based on selected category
   */
  useEffect(() => {
    const loadCustomFields = async () => {
      if (!newTicket.category) {
        setCustomFields([]);
        setCustomFieldValues({});
        return;
      }
      
      try {
        // بارگذاری فیلدهای سفارشی برای دسته‌بندی انتخاب شده
        const fields = (await apiGet(
          `/api/custom-fields?category=${newTicket.category}&is_active=true`
        )) as CustomFieldDefinition[];
        
        // فیلتر فیلدهای قابل مشاهده برای کاربر و نرمال‌سازی
        const visibleFields = fields
          .filter((f) => f.is_visible_to_user)
          .map((field) => ({
            ...field,
            label: field.label ?? field.name,
            is_required: field.is_required ?? false,
            is_editable_by_user: field.is_editable_by_user ?? false,
          }));
        setCustomFields(visibleFields);
        
        // مقداردهی اولیه با مقادیر پیش‌فرض
        const values: Record<number, string | null> = {};
        visibleFields.forEach((field) => {
          if (field.default_value) {
            values[field.id] = field.default_value;
          } else {
            values[field.id] = null;
          }
        });
        setCustomFieldValues(values);
      } catch (err) {
        console.error("Error loading custom fields:", err);
        setCustomFields([]);
        setCustomFieldValues({});
      }
    };
    
    loadCustomFields();
  }, [newTicket.category]);

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicket.title || !newTicket.description) {
      setError("عنوان و توضیحات الزامی است");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const payload: {
        title: string;
        description: string;
        category: string;
        priority: string;
        branch_id?: number;
      } = {
        title: newTicket.title,
        description: newTicket.description,
        category: newTicket.category,
        priority: newTicket.priority,
      };

      if (newTicket.branch_id) {
        payload.branch_id = Number(newTicket.branch_id);
      }

      const ticket = (await apiPost("/api/tickets", payload)) as TicketItem;
      
      // ذخیره فیلدهای سفارشی (اگر وجود داشته باشند)
      if (Object.keys(customFieldValues).length > 0) {
        try {
          const valuesToSave: CustomFieldValuePayload[] = Object.entries(customFieldValues)
            .filter(([, value]) => value !== null && value !== "")
            .map(([fieldId, value]) => ({
              custom_field_id: parseInt(fieldId, 10),
              value: value ?? null,
            }));

          if (valuesToSave.length > 0) {
            await apiPost(`/api/custom-fields/ticket/${ticket.id}/values`, { values: valuesToSave });
          }
        } catch (err) {
          console.error("Error saving custom fields:", err);
          // خطا را نادیده می‌گیریم چون تیکت قبلاً ایجاد شده
        }
      }
      
      setShowNewTicketForm(false);
      setNewTicket({ title: "", description: "", category: "other", priority: "medium", branch_id: "" });
      setCustomFields([]);
      setCustomFieldValues({});
      await loadTickets();
      // Navigate to ticket detail
      navigate(`/user-tickets/${ticket.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در ایجاد تیکت");
    } finally {
      setSubmitting(false);
    }
  };

  const headerRef = useRef<HTMLDivElement>(null);
  const formCardRef = useRef<HTMLDivElement>(null);
  const ticketsListRef = useRef<HTMLDivElement>(null);

  // Animate header on mount
  useEffect(() => {
    if (headerRef.current) {
      slideIn(headerRef.current, "right", { duration: 0.6, distance: 50 });
    }
  }, []);

  // Animate form when it appears
  useEffect(() => {
    if (showNewTicketForm && formCardRef.current) {
      scaleIn(formCardRef.current, { from: 0.9, to: 1, duration: 0.5 });
    }
  }, [showNewTicketForm]);

  // Animate tickets list when data changes
  useEffect(() => {
    if (tickets.length > 0 && ticketsListRef.current) {
      stagger(
        "tbody tr",
        (el) => slideIn(el, "left", { duration: 0.4, distance: 30 }),
        { stagger: 0.05, delay: 0.2 }
      );
    }
  }, [tickets.length]);

  return (
    <div className="fade-in">
      <div ref={headerRef} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="page-title">🎫 پورتال کاربران</h1>
        <button
          onClick={() => setShowNewTicketForm(!showNewTicketForm)}
          style={{ padding: "12px 24px", fontSize: 16 }}
        >
          {showNewTicketForm ? "❌ انصراف" : "➕ تیکت جدید"}
        </button>
      </div>

      {/* New Ticket Form */}
      {showNewTicketForm && (
        <div ref={formCardRef} className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h2 className="card-title">ایجاد تیکت جدید</h2>
          </div>
          {error && <div className="alert error fade-in">{error}</div>}
          <form onSubmit={handleCreateTicket}>
            <label>
              عنوان تیکت:
              <input
                type="text"
                value={newTicket.title}
                onChange={(e) => setNewTicket({ ...newTicket, title: e.target.value })}
                placeholder="مثال: مشکل در اتصال به اینترنت"
                required
                minLength={5}
                maxLength={255}
              />
            </label>
            <label>
              توضیحات:
              <textarea
                value={newTicket.description}
                onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                placeholder="توضیحات کامل مشکل یا درخواست خود را بنویسید..."
                required
                minLength={10}
                rows={5}
              />
            </label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <label>
                دسته‌بندی:
                <select
                  value={newTicket.category}
                  onChange={(e) => setNewTicket({ ...newTicket, category: e.target.value })}
                  required
                >
                  <option value="internet">🌐 اینترنت</option>
                  <option value="equipment">💻 تجهیزات</option>
                  <option value="software">📱 نرم‌افزار</option>
                  <option value="other">📋 سایر</option>
                </select>
              </label>
              <label>
                اولویت:
                <select
                  value={newTicket.priority}
                  onChange={(e) => setNewTicket({ ...newTicket, priority: e.target.value })}
                  required
                >
                  <option value="low">🟢 پایین</option>
                  <option value="medium">🟡 متوسط</option>
                  <option value="high">🟠 بالا</option>
                  <option value="critical">🔴 بحرانی</option>
                </select>
              </label>
            </div>
            {branches.length > 0 && (
              <label>
                شعبه (اختیاری):
                <select
                  value={newTicket.branch_id}
                  onChange={(e) => setNewTicket({ ...newTicket, branch_id: e.target.value })}
                >
                  <option value="">انتخاب نشده</option>
                  {branches.map((b) => (
                    <option key={b.id} value={String(b.id)}>
                      {b.name} ({b.code})
                    </option>
                  ))}
                </select>
              </label>
            )}
            
            {/* فیلدهای سفارشی */}
            {customFields.length > 0 && (
              <div style={{ marginTop: "20px", paddingTop: "20px", borderTop: "1px solid var(--border)" }}>
                <h3 style={{ marginBottom: "15px", fontSize: "16px", fontWeight: "600" }}>
                  📋 فیلدهای سفارشی
                </h3>
                <div style={{ display: "grid", gap: "15px" }}>
                  {customFields
                    .sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
                    .map((field) => (
                      <CustomFieldRenderer
                        key={field.id}
                        field={field}
                        value={customFieldValues[field.id] || null}
                        onChange={(value) => {
                          setCustomFieldValues((prev) => ({
                            ...prev,
                            [field.id]: value,
                          }));
                        }}
                        disabled={submitting}
                      />
                    ))}
                </div>
              </div>
            )}
            <KnowledgeSuggestions category={newTicket.category} query={newTicket.title} />
            
            <div style={{ display: "flex", gap: "12", marginTop: "20px" }}>
              <button type="submit" disabled={submitting}>
                {submitting ? "⏳ در حال ایجاد..." : "💾 ایجاد تیکت"}
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setShowNewTicketForm(false);
                  setNewTicket({ title: "", description: "", category: "other", priority: "medium", branch_id: "" });
                  setError(null);
                }}
              >
                انصراف
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tickets List */}
      <div ref={ticketsListRef} className="card">
        <div className="card-header">
          <h2 className="card-title">تیکت‌های من</h2>
        </div>
        
        {/* Filters */}
        <div className="filters" style={{ marginBottom: 16 }}>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            style={{ flex: 1 }}
          >
            <option value="">همه وضعیت‌ها</option>
            <option value="pending">در انتظار</option>
            <option value="in_progress">در حال انجام</option>
            <option value="resolved">حل شده</option>
            <option value="closed">بسته شده</option>
          </select>
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <div className="loading" style={{ margin: "0 auto" }}></div>
            <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
          </div>
        )}

        {error && !loading && (
          <div className="alert error fade-in">{error}</div>
        )}

        {!loading && tickets.length === 0 && (
          <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
            {statusFilter ? "هیچ تیکتی با این فیلتر یافت نشد." : "هنوز تیکتی ایجاد نکرده‌اید."}
            <br />
            <button
              onClick={() => setShowNewTicketForm(true)}
              style={{ marginTop: 16, padding: "12px 24px" }}
            >
              ➕ ایجاد تیکت جدید
            </button>
          </div>
        )}

        {!loading && tickets.length > 0 && (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>شماره تیکت</th>
                    <th>عنوان</th>
                    <th>دسته‌بندی</th>
                    <th>اولویت</th>
                    <th>وضعیت</th>
                    <th>کارشناس مسئول</th>
                    <th>تاریخ ایجاد</th>
                    <th>عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((ticket) => (
                    <tr key={ticket.id}>
                      <td>
                        <strong>{ticket.ticket_number}</strong>
                      </td>
                      <td>{ticket.title}</td>
                      <td>{getCategoryText(ticket.category)}</td>
                      <td>{ticket.priority ? getPriorityBadge(ticket.priority) : "🟡 متوسط"}</td>
                      <td>{getStatusBadge(ticket.status)}</td>
                      <td>
                        {ticket.assigned_to ? (
                          <span>{ticket.assigned_to.full_name}</span>
                        ) : (
                          <span style={{ color: "var(--fg-secondary)", fontSize: 12 }}>تخصیص داده نشده</span>
                        )}
                      </td>
                      <td>
                        {ticket.created_at
                          ? new Date(ticket.created_at).toLocaleDateString("fa-IR")
                          : "-"}
                      </td>
                      <td>
                        <Link to={`/user-tickets/${ticket.id}`}>
                          <button className="secondary small">👁️ مشاهده</button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24 }}>
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="secondary"
                >
                  ⬅️ قبلی
                </button>
                <span style={{ padding: "8px 16px", display: "flex", alignItems: "center" }}>
                  صفحه {page} از {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="secondary"
                >
                  بعدی ➡️
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

