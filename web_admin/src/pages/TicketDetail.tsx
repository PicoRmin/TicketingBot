import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { apiGet, apiPatch, apiUploadFile, isAuthenticated, API_BASE_URL } from "../services/api";
import { apiPost } from "../services/api";

type Ticket = {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  status: string;
  category: string;
  branch_id?: number | null;
  created_at?: string;
  updated_at?: string;
};

type Attachment = {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  ticket_id: number;
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

export default function TicketDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);
  const [newStatus, setNewStatus] = useState<string>("");
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState("");
  const [isInternal, setIsInternal] = useState(false);
  const [branches, setBranches] = useState<{ id: number; name: string; code: string }[]>([]);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, []);

  useEffect(() => {
    const loadBranches = async () => {
      try {
        const b = await apiGet(`/api/branches`) as any[];
        setBranches(b.map((x: any) => ({ id: x.id, name: x.name, code: x.code })));
      } catch {
        // ignore
      }
    };
    loadBranches();
  }, []);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const t = await apiGet(`/api/tickets/${id}`) as Ticket;
        setTicket(t);
        setNewStatus(t.status);
        const list = await apiGet(`/api/files/ticket/${id}/list`) as Attachment[];
        setAttachments(list);
        const commentsList = await apiGet(`/api/comments/ticket/${id}`) as any[];
        setComments(commentsList);
        const historyList = await apiGet(`/api/tickets/${id}/history`) as any[];
        setHistory(historyList);
      } catch (e: any) {
        setError(e?.message || "خطا در دریافت تیکت");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const changeStatus = async () => {
    if (!id) return;
    setUpdating(true);
    setError(null);
    try {
      const updated = await apiPatch(`/api/tickets/${id}/status`, { status: newStatus }) as Ticket;
      setTicket(updated);
      // Reload history after status change
      const historyList = await apiGet(`/api/tickets/${id}/history`) as any[];
      setHistory(historyList);
      setError(null);
    } catch (e: any) {
      setError(e?.message || "خطا در تغییر وضعیت");
    } finally {
      setUpdating(false);
    }
  };

  const upload = async () => {
    if (!id || !file) return;
    setUpdating(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await apiUploadFile(`/api/files/upload?ticket_id=${id}`, form) as Attachment;
      setAttachments((prev) => [...prev, {
        id: res.id,
        filename: res.filename,
        original_filename: res.original_filename,
        file_size: res.file_size,
        file_type: res.file_type,
        ticket_id: res.ticket_id
      }]);
      setFile(null);
      setError(null);
    } catch (e: any) {
      setError(e?.message || "خطا در آپلود فایل");
    } finally {
      setUpdating(false);
    }
  };

  const addComment = async () => {
    if (!id || !newComment.trim()) return;
    setUpdating(true);
    setError(null);
    try {
      const res = await apiPost(`/api/comments`, {
        ticket_id: Number(id),
        comment: newComment.trim(),
        is_internal: isInternal
      }) as any;
      setComments((prev) => [...prev, res]);
      setNewComment("");
      setIsInternal(false);
      setError(null);
    } catch (e: any) {
      setError(e?.message || "خطا در ثبت نظر");
    } finally {
      setUpdating(false);
    }
  };

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="fade-in">
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
        <Link to="/tickets">
          <button className="secondary">⬅️ بازگشت</button>
        </Link>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>🎫 جزئیات تیکت</h1>
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

      {ticket && (
        <>
          {/* Ticket Info Card */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <h2 className="card-title">📋 اطلاعات تیکت</h2>
              {getStatusBadge(ticket.status)}
            </div>
            <div className="grid grid-cols-2" style={{ gap: 16 }}>
              <div>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>شماره تیکت</div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>
                  <code style={{ 
                    background: "var(--bg-secondary)", 
                    padding: "4px 8px", 
                    borderRadius: "4px"
                  }}>
                    {ticket.ticket_number}
                  </code>
                </div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>دسته‌بندی</div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>{getCategoryText(ticket.category)}</div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>شعبه</div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>
                  {ticket.branch_id ? (
                    (() => {
                      const branch = branches.find(b => b.id === ticket.branch_id);
                      return branch ? `${branch.name} (${branch.code})` : `شعبه ${ticket.branch_id}`;
                    })()
                  ) : (
                    <span style={{ color: "var(--fg-secondary)" }}>بدون شعبه</span>
                  )}
                </div>
              </div>
              <div style={{ gridColumn: "1 / -1" }}>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>عنوان</div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>{ticket.title}</div>
              </div>
              <div style={{ gridColumn: "1 / -1" }}>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>توضیحات</div>
                <div style={{ 
                  background: "var(--bg-secondary)", 
                  padding: 12, 
                  borderRadius: "var(--radius)",
                  lineHeight: 1.6
                }}>
                  {ticket.description}
                </div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>تاریخ ایجاد</div>
                <div>{ticket.created_at ? new Date(ticket.created_at).toLocaleString("fa-IR") : "-"}</div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>آخرین به‌روزرسانی</div>
                <div>{ticket.updated_at ? new Date(ticket.updated_at).toLocaleString("fa-IR") : "-"}</div>
              </div>
            </div>
          </div>

          {/* Status Change Card */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <h2 className="card-title">🔄 تغییر وضعیت</h2>
            </div>
            <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 200 }}>
                <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                  وضعیت جدید
                </label>
                <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
                  <option value="pending">⏳ در انتظار</option>
                  <option value="in_progress">🔄 در حال انجام</option>
                  <option value="resolved">✅ حل شده</option>
                  <option value="closed">🔒 بسته شده</option>
                </select>
              </div>
              <button 
                onClick={changeStatus} 
                disabled={updating || newStatus === ticket.status}
                style={{ minWidth: 120 }}
              >
                {updating ? "⏳ در حال ذخیره..." : "💾 ذخیره تغییرات"}
              </button>
            </div>
          </div>

          {/* Attachments Card */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <h2 className="card-title">📎 پیوست‌ها ({attachments.length})</h2>
            </div>
            {attachments.length === 0 ? (
              <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
                📭 هیچ فایلی پیوست نشده است
              </div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>نام فایل</th>
                      <th>نوع</th>
                      <th>اندازه</th>
                      <th>عملیات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attachments.map(a => (
                      <tr key={a.id}>
                        <td style={{ fontWeight: 500 }}>{a.original_filename}</td>
                        <td>
                          <span className="badge" style={{ background: "var(--bg-secondary)", color: "var(--fg)" }}>
                            {a.file_type}
                          </span>
                        </td>
                        <td style={{ color: "var(--fg-secondary)" }}>
                          {(a.file_size / 1024).toFixed(1)} KB
                        </td>
                        <td>
                          <a 
                            href={`${API_BASE_URL}/api/files/${a.id}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            <button className="secondary" style={{ padding: "6px 12px", fontSize: 13 }}>
                              ⬇️ دانلود
                            </button>
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div style={{ marginTop: 16, display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 200 }}>
                <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                  افزودن فایل جدید
                </label>
                <input 
                  type="file" 
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  style={{ padding: "8px" }}
                />
              </div>
              <button 
                onClick={upload} 
                disabled={updating || !file}
                style={{ minWidth: 120 }}
              >
                {updating ? "⏳ در حال آپلود..." : "📤 آپلود"}
              </button>
            </div>
          </div>

          {/* Comments Card */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">💬 نظرات ({comments.length})</h2>
            </div>
            {comments.length === 0 ? (
              <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
                💭 هیچ نظری ثبت نشده است
              </div>
            ) : (
              <div style={{ display: "grid", gap: 12, marginBottom: 20 }}>
                {comments.map((c, idx) => (
                  <div 
                    key={idx} 
                    className="card"
                    style={{ 
                      padding: 16,
                      background: c.is_internal ? "var(--bg)" : "var(--bg-secondary)",
                      borderLeft: c.is_internal ? "4px solid var(--warning)" : "4px solid var(--info)"
                    }}
                  >
                    <div style={{ 
                      display: "flex", 
                      justifyContent: "space-between", 
                      alignItems: "center",
                      marginBottom: 8
                    }}>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                        {c.created_at ? new Date(c.created_at).toLocaleString("fa-IR") : "-"}
                      </div>
                      {c.is_internal && (
                        <span className="badge" style={{ background: "var(--warning)", color: "white" }}>
                          🔒 داخلی
                        </span>
                      )}
                    </div>
                    <div style={{ lineHeight: 1.6 }}>{c.comment}</div>
                  </div>
                ))}
              </div>
            )}
            <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 200 }}>
                <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                  نظر جدید
                </label>
                <textarea
                  placeholder="نظر خود را وارد کنید..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  rows={3}
                  style={{ resize: "vertical" }}
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
                  <input 
                    type="checkbox" 
                    checked={isInternal} 
                    onChange={(e) => setIsInternal(e.target.checked)}
                  />
                  <span style={{ fontSize: 14 }}>🔒 نظر داخلی</span>
                </label>
                <button 
                  onClick={addComment} 
                  disabled={updating || !newComment.trim()}
                  style={{ minWidth: 120 }}
                >
                  {updating ? "⏳ در حال ارسال..." : "📤 ارسال نظر"}
                </button>
              </div>
            </div>
          </div>

          {/* History Card */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">📜 تاریخچه تغییرات ({history.length})</h2>
            </div>
            {history.length === 0 ? (
              <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
                📋 هیچ تغییر وضعیتی ثبت نشده است
              </div>
            ) : (
              <div style={{ display: "grid", gap: 12 }}>
                {history.map((h, idx) => (
                  <div 
                    key={idx} 
                    className="card"
                    style={{ 
                      padding: 16,
                      background: "var(--bg)",
                      borderLeft: "4px solid var(--primary)",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      flexWrap: "wrap",
                      gap: 12
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 200 }}>
                      <div style={{ 
                        display: "flex", 
                        alignItems: "center", 
                        gap: 8,
                        marginBottom: 4
                      }}>
                        <span className={`badge ${h.status?.toLowerCase()}`}>
                          {getStatusBadge(h.status)}
                        </span>
                        <span style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                          {h.created_at ? new Date(h.created_at).toLocaleString("fa-IR") : "-"}
                        </span>
                      </div>
                      {h.comment && (
                        <div style={{ 
                          marginTop: 8, 
                          padding: 8, 
                          background: "var(--bg-secondary)", 
                          borderRadius: "4px",
                          fontSize: 13,
                          color: "var(--fg-secondary)"
                        }}>
                          {h.comment}
                        </div>
                      )}
                      {h.changed_by && (
                        <div style={{ 
                          marginTop: 4, 
                          fontSize: 11, 
                          color: "var(--muted)" 
                        }}>
                          تغییر توسط: {h.changed_by.full_name || h.changed_by.username}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
