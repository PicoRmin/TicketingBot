import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { apiGet, apiPost, isAuthenticated, getStoredProfile } from "../services/api";
import CustomFieldRenderer from "../components/CustomFieldRenderer";

type Ticket = {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  status: string;
  category: string;
  priority?: string;
  assigned_to?: { id: number; full_name: string; username: string } | null;
  created_at?: string;
  updated_at?: string;
};

type Comment = {
  id: number;
  comment: string;
  user: { id: number; full_name: string; username: string };
  created_at: string;
  is_internal: boolean;
};

type Attachment = {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  file_type: string;
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

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function UserTicketDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [profile] = useState<any | null>(() => getStoredProfile());
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newComment, setNewComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  
  // Custom Fields states (فقط برای نمایش)
  const [customFields, setCustomFields] = useState<any[]>([]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    
    // Check if user is regular user
    if (profile && !["user"].includes(profile.role)) {
      // Redirect admins to admin ticket detail
      navigate(`/tickets/${id}`);
      return;
    }
    
    loadData();
  }, [id, navigate, profile]);

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const t = await apiGet(`/api/tickets/${id}`) as Ticket;
      setTicket(t);
      
      // Load comments
      try {
        const commentsList = await apiGet(`/api/comments/ticket/${id}`) as Comment[];
        // Filter out internal comments for regular users (API already filters, but double check)
        setComments(commentsList.filter(c => !c.is_internal));
      } catch {
        setComments([]);
      }
      
      // Load attachments
      try {
        const atts = await apiGet(`/api/files/ticket/${id}/list`) as Attachment[];
        setAttachments(atts);
      } catch {
        setAttachments([]);
      }
      
      // Load custom fields (فقط برای نمایش)
      try {
        const fields = await apiGet(`/api/custom-fields/ticket/${id}`) as any[];
        // فیلتر فیلدهای قابل مشاهده برای کاربر
        const visibleFields = fields.filter((f) => f.is_visible_to_user);
        setCustomFields(visibleFields);
      } catch {
        setCustomFields([]);
      }
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت تیکت");
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !newComment.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      await apiPost(`/api/comments`, {
        ticket_id: Number(id),
        comment: newComment,
        is_internal: false, // Regular users can only add public comments
      });
      setNewComment("");
      await loadData();
    } catch (e: any) {
      setError(e?.message || "خطا در ارسال پیام");
    } finally {
      setSubmitting(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <div className="loading" style={{ margin: "0 auto" }}></div>
        <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
      </div>
    );
  }

  if (error && !ticket) {
    return (
      <div className="fade-in">
        <div className="alert error">{error}</div>
        <Link to="/user-portal">
          <button style={{ marginTop: 16 }}>🔙 بازگشت به لیست تیکت‌ها</button>
        </Link>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="fade-in">
        <div className="alert error">تیکت یافت نشد</div>
        <Link to="/user-portal">
          <button style={{ marginTop: 16 }}>🔙 بازگشت به لیست تیکت‌ها</button>
        </Link>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="page-title">جزئیات تیکت</h1>
        <Link to="/user-portal">
          <button className="secondary">🔙 بازگشت</button>
        </Link>
      </div>

      {error && <div className="alert error fade-in">{error}</div>}

      {/* Ticket Info */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">اطلاعات تیکت</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div>
            <strong>شماره تیکت:</strong>
            <div style={{ marginTop: 4 }}>{ticket.ticket_number}</div>
          </div>
          <div>
            <strong>وضعیت:</strong>
            <div style={{ marginTop: 4 }}>{getStatusBadge(ticket.status)}</div>
          </div>
          <div>
            <strong>دسته‌بندی:</strong>
            <div style={{ marginTop: 4 }}>{getCategoryText(ticket.category)}</div>
          </div>
          <div>
            <strong>اولویت:</strong>
            <div style={{ marginTop: 4 }}>{ticket.priority ? getPriorityBadge(ticket.priority) : "🟡 متوسط"}</div>
          </div>
          <div>
            <strong>کارشناس مسئول:</strong>
            <div style={{ marginTop: 4 }}>
              {ticket.assigned_to ? (
                <span>{ticket.assigned_to.full_name}</span>
              ) : (
                <span style={{ color: "var(--fg-secondary)" }}>تخصیص داده نشده</span>
              )}
            </div>
          </div>
          <div>
            <strong>تاریخ ایجاد:</strong>
            <div style={{ marginTop: 4 }}>
              {ticket.created_at
                ? new Date(ticket.created_at).toLocaleString("fa-IR")
                : "-"}
            </div>
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <strong>عنوان:</strong>
          <div style={{ marginTop: 4, fontSize: 18, fontWeight: 600 }}>{ticket.title}</div>
        </div>
        <div style={{ marginTop: 16 }}>
          <strong>توضیحات:</strong>
          <div style={{ marginTop: 4, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{ticket.description}</div>
          
          {/* فیلدهای سفارشی (فقط نمایش) */}
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
                      value={field.value || null}
                      onChange={() => {}} // فقط خواندنی
                      readOnly={true}
                    />
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Attachments */}
      {attachments.length > 0 && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h2 className="card-title">فایل‌های پیوست ({attachments.length})</h2>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
            {attachments.map((att) => (
              <a
                key={att.id}
                href={`${API_BASE_URL}/api/files/${att.id}`}
                target="_blank"
                rel="noreferrer"
                style={{
                  padding: 12,
                  background: "var(--bg-secondary)",
                  borderRadius: "var(--radius)",
                  textDecoration: "none",
                  color: "var(--fg)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                }}
              >
                <span style={{ fontWeight: 600, fontSize: 14 }}>📎 {att.original_filename}</span>
                <span style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                  {formatFileSize(att.file_size)}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Comments */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">پیام‌ها و پاسخ‌ها ({comments.length})</h2>
        </div>
        
        {comments.length === 0 ? (
          <div style={{ textAlign: "center", padding: 20, color: "var(--fg-secondary)" }}>
            هنوز پیامی ارسال نشده است.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {comments.map((comment) => (
              <div
                key={comment.id}
                style={{
                  padding: 16,
                  background: "var(--bg-secondary)",
                  borderRadius: "var(--radius)",
                  borderLeft: "3px solid var(--primary)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <strong>{comment.user.full_name}</strong>
                  <span style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                    {new Date(comment.created_at).toLocaleString("fa-IR")}
                  </span>
                </div>
                <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{comment.comment}</div>
              </div>
            ))}
          </div>
        )}

        {/* Add Comment Form */}
        <form onSubmit={handleAddComment} style={{ marginTop: 24, paddingTop: 24, borderTop: "1px solid var(--border)" }}>
          <label>
            ارسال پیام:
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="پیام خود را بنویسید..."
              rows={4}
              required
            />
          </label>
          <button type="submit" disabled={submitting || !newComment.trim()}>
            {submitting ? "⏳ در حال ارسال..." : "📤 ارسال پیام"}
          </button>
        </form>
      </div>
    </div>
  );
}

