import { useEffect, useState, useRef } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { apiGet, apiPatch, apiUploadFile, isAuthenticated, API_BASE_URL } from "../services/api";
import { apiPost } from "../services/api";
import CustomFieldRenderer from "../components/CustomFieldRenderer";
import { PriorityBadge } from "@/components/tickets/PriorityBadge";
import { motion, AnimatePresence } from "framer-motion";
import { fadeIn } from "../lib/gsap";

type Ticket = {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  status: string;
  category: string;
  priority?: string;
  branch_id?: number | null;
  department_id?: number | null;
  assigned_to_id?: number | null;
  assigned_to?: { id: number; full_name: string; username: string } | null;
  user_id?: number;
  created_at?: string;
  updated_at?: string;
};

type SLALog = {
  id: number;
  ticket_id: number;
  sla_rule_id: number;
  target_response_time: string;
  target_resolution_time: string;
  actual_response_time?: string | null;
  actual_resolution_time?: string | null;
  response_status?: string | null;
  resolution_status?: string | null;
  escalated: boolean;
  escalated_at?: string | null;
};

type Attachment = {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  ticket_id: number;
};

type Comment = {
  id: number;
  ticket_id: number;
  user_id: number;
  comment: string;
  is_internal: boolean;
  created_at: string;
  user?: { id: number; full_name: string; username: string } | null;
};

type HistoryItem = {
  id: number;
  ticket_id: number;
  user_id: number;
  action: string;
  old_value?: string | null;
  new_value?: string | null;
  status?: string | null;
  comment?: string;
  changed_by?: { id: number; full_name: string; username: string } | null;
  created_at: string;
  user?: { id: number; full_name: string; username: string } | null;
};

type TimeLog = {
  id: number;
  ticket_id: number;
  user_id: number;
  description?: string | null;
  start_time: string;
  end_time?: string | null;
  duration_minutes?: number | null;
  is_active: boolean;
  created_at: string;
  user?: { id: number; full_name: string; username: string } | null;
};

type CustomField = {
  id: number;
  name: string;
  label: string;
  field_type: string;
  config?: Record<string, unknown> | null;
  is_required: boolean;
  is_visible_to_user: boolean;
  is_editable_by_user: boolean;
  default_value?: string | null;
  value?: string | null;
  display_order?: number;
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

// getPriorityBadge removed - using PriorityBadge component instead

const getSLAStatusBadge = (status: string | null | undefined) => {
  if (!status) return null;
  const statusMap: Record<string, { text: string; class: string; emoji: string }> = {
    on_time: { text: "در مهلت", class: "badge resolved", emoji: "✅" },
    warning: { text: "هشدار", class: "badge in_progress", emoji: "⚠️" },
    breached: { text: "نقض شده", class: "badge pending", emoji: "❌" },
  };
  const s = statusMap[status] || { text: status, class: "badge", emoji: "" };
  return <span className={s.class} title={s.text}>{s.emoji} {s.text}</span>;
};

const formatTimeRemaining = (targetTime: string) => {
  const target = new Date(targetTime);
  const now = new Date();
  const diff = target.getTime() - now.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (diff < 0) {
    const absMinutes = Math.abs(minutes);
    const absHours = Math.abs(hours);
    const absDays = Math.abs(days);
    if (absDays > 0) return `${absDays} روز گذشته`;
    if (absHours > 0) return `${absHours} ساعت گذشته`;
    return `${absMinutes} دقیقه گذشته`;
  }
  
  if (days > 0) return `${days} روز باقی مانده`;
  if (hours > 0) return `${hours} ساعت باقی مانده`;
  return `${minutes} دقیقه باقی مانده`;
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
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState("");
  const [isInternal, setIsInternal] = useState(false);
  const [branches, setBranches] = useState<{ id: number; name: string; code: string }[]>([]);
  const [departments, setDepartments] = useState<{ id: number; name: string; code: string }[]>([]);
  const [users, setUsers] = useState<{ id: number; full_name: string; username: string }[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [slaLog, setSlaLog] = useState<SLALog | null>(null);
  const [assigning, setAssigning] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [canAssign, setCanAssign] = useState(false);
  
  // Time Tracker states
  const [activeTimer, setActiveTimer] = useState<TimeLog | null>(null);
  const [timeLogs, setTimeLogs] = useState<TimeLog[]>([]);
  const [timeSummary, setTimeSummary] = useState<{ total_minutes: number; total_hours: number; logs_count: number } | null>(null);
  const [timerDescription, setTimerDescription] = useState("");
  const [timerLoading, setTimerLoading] = useState(false);
  
  // Custom Fields states
  const [customFields, setCustomFields] = useState<CustomField[]>([]);
  const [customFieldValues, setCustomFieldValues] = useState<Record<number, string | null>>({});
  const [savingCustomFields, setSavingCustomFields] = useState(false);
  
  // Refs for animations and auto-scroll
  const commentsContainerRef = useRef<HTMLDivElement>(null);
  const historyContainerRef = useRef<HTMLDivElement>(null);
  const attachmentsContainerRef = useRef<HTMLDivElement>(null);
  const [prevCommentsLength, setPrevCommentsLength] = useState(0);
  const [prevAttachmentsLength, setPrevAttachmentsLength] = useState(0);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, [navigate]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const b = await apiGet(`/api/branches`) as { id: number; name: string; code: string }[];
        setBranches(b.map((x) => ({ id: x.id, name: x.name, code: x.code })));
        const d = await apiGet(`/api/departments?page_size=100`) as { id: number; name: string; code: string }[];
        setDepartments(d.map((x) => ({ id: x.id, name: x.name, code: x.code })));
        const u = await apiGet(`/api/users?page_size=100`) as { items?: { id: number; full_name: string; username: string }[] };
        setUsers(u.items?.map((x) => ({ id: x.id, full_name: x.full_name, username: x.username })) || []);
        
        // Check if user can assign tickets
        const profile = await apiGet(`/api/auth/me`) as { role?: string };
        const allowedRoles = ["admin", "central_admin", "branch_admin", "it_specialist"];
        setCanAssign(allowedRoles.includes(profile?.role || ""));
      } catch {
        // ignore
      }
    };
    loadData();
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
        setPrevAttachmentsLength(list.length);
        const commentsList = await apiGet(`/api/comments/ticket/${id}`) as Comment[];
        setComments(commentsList);
        const historyList = await apiGet(`/api/tickets/${id}/history`) as HistoryItem[];
        setHistory(historyList);
        try {
          const sla = await apiGet(`/api/sla/ticket/${id}`) as SLALog;
          setSlaLog(sla);
        } catch {
          // SLA log might not exist for old tickets
          setSlaLog(null);
        }
        
        // Set selected user for assignment
        if (t.assigned_to_id) {
          setSelectedUserId(String(t.assigned_to_id));
        }
        
        // Load Time Tracker data
        loadTimeTrackerData();
        
        // Load Custom Fields
        loadCustomFields();
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : "خطا در دریافت تیکت";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const changeStatus = async () => {
    if (!id) return;
    setUpdating(true);
    setError(null);
    try {
      const updated = await apiPatch(`/api/tickets/${id}/status`, { status: newStatus }) as Ticket;
      setTicket(updated);
      // Reload history after status change
      const historyList = await apiGet(`/api/tickets/${id}/history`) as HistoryItem[];
      setHistory(historyList);
      setError(null);
    } catch (e) {
      const errorMessage = (e instanceof Error ? e.message : "خطا در تغییر وضعیت");
      setError(errorMessage);
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
      setAttachments((prev) => {
        const newList = [...prev, {
          id: res.id,
          filename: res.filename,
          original_filename: res.original_filename,
          file_size: res.file_size,
          file_type: res.file_type,
          ticket_id: res.ticket_id
        }];
        setPrevAttachmentsLength(newList.length);
        return newList;
      });
      setFile(null);
      setError(null);
    } catch (e) {
      const errorMessage = (e instanceof Error ? e.message : "خطا در آپلود فایل");
      setError(errorMessage);
    } finally {
      setUpdating(false);
    }
  };

  const assignTicket = async () => {
    if (!id) return;
    setAssigning(true);
    setError(null);
    try {
      if (selectedUserId) {
        await apiPatch(`/api/tickets/${id}/assign`, { assigned_to_id: Number(selectedUserId) });
      } else {
        await apiPatch(`/api/tickets/${id}/unassign`, {});
      }
      // Reload ticket
      const t = await apiGet(`/api/tickets/${id}`) as Ticket;
      setTicket(t);
      if (t.assigned_to_id) {
        setSelectedUserId(String(t.assigned_to_id));
      } else {
        setSelectedUserId("");
      }
      // Reload history
      const historyList = await apiGet(`/api/tickets/${id}/history`) as HistoryItem[];
      setHistory(historyList);
      setError(null);
    } catch (e) {
      const errorMessage = (e instanceof Error ? e.message : "خطا در تخصیص تیکت");
      setError(errorMessage);
    } finally {
      setAssigning(false);
    }
  };

  /**
   * بارگذاری فیلدهای سفارشی برای تیکت
   * Load custom fields for the ticket
   */
  const loadCustomFields = async () => {
    if (!id) return;
    try {
      const fields = await apiGet(`/api/custom-fields/ticket/${id}`) as CustomField[];
      setCustomFields(fields || []);
      
      // بارگذاری مقادیر فیلدها
      const values: Record<number, string | null> = {};
      fields.forEach((field) => {
        if (field.value !== null && field.value !== undefined) {
          values[field.id] = field.value;
        } else if (field.default_value) {
          values[field.id] = field.default_value;
        } else {
          values[field.id] = null;
        }
      });
      setCustomFieldValues(values);
    } catch (e) {
      console.error("Error loading custom fields:", e);
      // خطا را نمایش ندهیم چون فیلدهای سفارشی اختیاری هستند
    }
  };

  /**
   * ذخیره مقادیر فیلدهای سفارشی
   * Save custom field values
   */
  const saveCustomFields = async () => {
    if (!id) return;
    setSavingCustomFields(true);
    setError(null);
    try {
      // ساخت آرایه مقادیر برای ارسال
      const valuesToSave = Object.entries(customFieldValues)
        .filter(([_, value]) => value !== null && value !== "")
        .map(([fieldId, value]) => ({
          custom_field_id: parseInt(fieldId),
          value: value,
        }));

      if (valuesToSave.length > 0) {
        await apiPost(`/api/custom-fields/ticket/${id}/values`, { values: valuesToSave });
        // بارگذاری مجدد فیلدها
        await loadCustomFields();
        setError(null);
      }
    } catch (e) {
      const errorMessage = (e instanceof Error ? e.message : "خطا در ذخیره فیلدهای سفارشی");
      setError(errorMessage);
    } finally {
      setSavingCustomFields(false);
    }
  };

  const loadTimeTrackerData = async () => {
    if (!id) return;
    try {
      // Load active timer
      const active = await apiGet(`/api/time-tracker/active`) as TimeLog | null;
      if (active && active.ticket_id === Number(id)) {
        setActiveTimer(active);
      } else {
        setActiveTimer(null);
      }
      
      // Load time logs for this ticket
      const logs = await apiGet(`/api/time-tracker/ticket/${id}`) as TimeLog[];
      setTimeLogs(logs || []);
      
      // Load time summary
      const summary = await apiGet(`/api/time-tracker/ticket/${id}/summary`) as { total_minutes: number; total_hours: number; logs_count: number } | null;
      setTimeSummary(summary);
    } catch (e) {
      // Time tracker might not be available for all users
      console.warn("Time tracker error:", e);
    }
  };

  const startTimer = async () => {
    if (!id) return;
    setTimerLoading(true);
    setError(null);
    try {
      const timer = await apiPost(`/api/time-tracker/start`, {
        ticket_id: Number(id),
        description: timerDescription
      }) as TimeLog;
      setActiveTimer(timer);
      setTimerDescription("");
      await loadTimeTrackerData();
    } catch (e) {
      const errorMessage = (e instanceof Error ? e.message : "خطا در شروع تایمر");
      setError(errorMessage);
    } finally {
      setTimerLoading(false);
    }
  };

  const stopTimer = async (timeLogId?: number) => {
    setTimerLoading(true);
    setError(null);
    try {
      if (timeLogId) {
        await apiPost(`/api/time-tracker/stop/${timeLogId}`, {
          description: timerDescription
        });
      } else {
        await apiPost(`/api/time-tracker/stop-active`, {
          description: timerDescription
        });
      }
      setActiveTimer(null);
      setTimerDescription("");
      await loadTimeTrackerData();
    } catch (e) {
      const errorMessage = (e instanceof Error ? e.message : "خطا در توقف تایمر");
      setError(errorMessage);
    } finally {
      setTimerLoading(false);
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours} ساعت و ${mins} دقیقه`;
    }
    return `${mins} دقیقه`;
  };

  const formatElapsedTime = (startTime: string) => {
    const start = new Date(startTime);
    const now = new Date();
    const diff = Math.floor((now.getTime() - start.getTime()) / 1000 / 60); // minutes
    return formatDuration(diff);
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
      }) as Comment;
      setComments((prev) => {
        const newList = [...prev, res];
        setPrevCommentsLength(newList.length);
        return newList;
      });
      setNewComment("");
      setIsInternal(false);
      setError(null);
      
      // Auto-scroll to new comment after a short delay
      setTimeout(() => {
        if (commentsContainerRef.current) {
          commentsContainerRef.current.scrollTo({
            top: commentsContainerRef.current.scrollHeight,
            behavior: "smooth",
          });
        }
      }, 100);
    } catch (e) {
      const errorMessage = (e instanceof Error ? e.message : "خطا در ثبت نظر");
      setError(errorMessage);
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
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>اولویت</div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>
                  <PriorityBadge priority={ticket.priority || "medium"} />
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
              <div>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>دپارتمان</div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>
                  {ticket.department_id ? (
                    departments.find(d => d.id === ticket.department_id)?.name || "-"
                  ) : (
                    <span style={{ color: "var(--fg-secondary)" }}>بدون دپارتمان</span>
                  )}
                </div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>کارشناس مسئول</div>
                <div style={{ fontSize: 18, fontWeight: 600 }}>
                  {ticket.assigned_to ? (
                    ticket.assigned_to.full_name
                  ) : (
                    <span style={{ color: "var(--fg-secondary)" }}>تخصیص داده نشده</span>
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
              
              {/* فیلدهای سفارشی */}
              {customFields.length > 0 && (
                <div style={{ gridColumn: "1 / -1", marginTop: "20px", paddingTop: "20px", borderTop: "1px solid var(--border)" }}>
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
                          disabled={savingCustomFields}
                        />
                      ))}
                  </div>
                  <button
                    onClick={saveCustomFields}
                    disabled={savingCustomFields}
                    style={{
                      marginTop: "15px",
                      padding: "10px 20px",
                      background: "var(--accent)",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: savingCustomFields ? "not-allowed" : "pointer",
                      fontSize: "14px",
                      fontWeight: "bold",
                      opacity: savingCustomFields ? 0.6 : 1,
                    }}
                  >
                    {savingCustomFields ? "💾 در حال ذخیره..." : "💾 ذخیره فیلدهای سفارشی"}
                  </button>
                </div>
              )}
              
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

          {/* SLA Status Card */}
          {slaLog && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">⏱️ وضعیت SLA</h2>
              </div>
              <div className="grid grid-cols-2" style={{ gap: 16 }}>
                <div>
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>وضعیت پاسخ</div>
                  <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                    {getSLAStatusBadge(slaLog.response_status)}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                    {slaLog.actual_response_time ? (
                      <>پاسخ داده شده: {new Date(slaLog.actual_response_time).toLocaleString("fa-IR")}</>
                    ) : (
                      <>مهلت: {new Date(slaLog.target_response_time).toLocaleString("fa-IR")} ({formatTimeRemaining(slaLog.target_response_time)})</>
                    )}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>وضعیت حل</div>
                  <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                    {getSLAStatusBadge(slaLog.resolution_status)}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                    {slaLog.actual_resolution_time ? (
                      <>حل شده: {new Date(slaLog.actual_resolution_time).toLocaleString("fa-IR")}</>
                    ) : (
                      <>مهلت: {new Date(slaLog.target_resolution_time).toLocaleString("fa-IR")} ({formatTimeRemaining(slaLog.target_resolution_time)})</>
                    )}
                  </div>
                </div>
                {slaLog.escalated && (
                  <div style={{ gridColumn: "1 / -1" }}>
                    <div className="alert" style={{ 
                      background: "var(--warning)", 
                      color: "white",
                      padding: "12px",
                      borderRadius: "var(--radius)"
                    }}>
                      <strong>⚠️ Escalated:</strong> این تیکت به سطح بالاتر ارجاع داده شده است.
                      {slaLog.escalated_at && (
                        <span style={{ display: "block", marginTop: 4, fontSize: 12 }}>
                          زمان: {new Date(slaLog.escalated_at).toLocaleString("fa-IR")}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

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

          {/* Assignment Card */}
          {canAssign && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">👤 تخصیص تیکت</h2>
              </div>
              <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: 250 }}>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    کارشناس مسئول
                  </label>
                  <select 
                    value={selectedUserId} 
                    onChange={(e) => setSelectedUserId(e.target.value)}
                    disabled={assigning}
                  >
                    <option value="">بدون تخصیص</option>
                    {users
                      .filter(u => u.id !== ticket.user_id) // Don't show ticket creator
                      .map((user) => (
                        <option key={user.id} value={String(user.id)}>
                          {user.full_name} ({user.username})
                        </option>
                      ))}
                  </select>
                </div>
                <button 
                  onClick={assignTicket} 
                  disabled={assigning || selectedUserId === String(ticket.assigned_to_id || "")}
                  style={{ minWidth: 140 }}
                >
                  {assigning ? "⏳ در حال ذخیره..." : selectedUserId ? "💾 تخصیص" : "🗑️ حذف تخصیص"}
                </button>
              </div>
              {ticket.assigned_to && (
                <div style={{ marginTop: 12, padding: 12, background: "var(--bg-secondary)", borderRadius: "var(--radius)", fontSize: 14 }}>
                  <strong>کارشناس فعلی:</strong> {ticket.assigned_to.full_name} ({ticket.assigned_to.username})
                </div>
              )}
            </div>
          )}

          {/* Time Tracker Card */}
          {canAssign && (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="card-header">
                <h2 className="card-title">⏱️ زمان‌سنج کار</h2>
                {timeSummary && (
                  <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
                    کل زمان: <strong>{formatDuration(timeSummary.total_minutes)}</strong> ({timeSummary.logs_count} رکورد)
                  </div>
                )}
              </div>
              
              {/* Active Timer */}
              {activeTimer && (
                <div style={{ 
                  padding: 16, 
                  background: "var(--success)", 
                  color: "white", 
                  borderRadius: "var(--radius)",
                  marginBottom: 16
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <div>
                      <strong>⏱️ تایمر فعال</strong>
                      <div style={{ fontSize: 12, marginTop: 4, opacity: 0.9 }}>
                        زمان سپری شده: {formatElapsedTime(activeTimer.start_time)}
                      </div>
                    </div>
                    <button
                      onClick={() => stopTimer()}
                      disabled={timerLoading}
                      className="danger"
                      style={{ padding: "8px 16px" }}
                    >
                      {timerLoading ? "⏳ در حال توقف..." : "⏹️ توقف"}
                    </button>
                  </div>
                  {activeTimer.description && (
                    <div style={{ fontSize: 12, opacity: 0.9, marginTop: 8 }}>
                      توضیحات: {activeTimer.description}
                    </div>
                  )}
                </div>
              )}
              
              {/* Start Timer */}
              {!activeTimer && (
                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    توضیحات کار (اختیاری)
                  </label>
                  <textarea
                    value={timerDescription}
                    onChange={(e) => setTimerDescription(e.target.value)}
                    placeholder="مثال: بررسی مشکل شبکه..."
                    rows={2}
                    style={{ width: "100%", marginBottom: 12 }}
                  />
                  <button
                    onClick={startTimer}
                    disabled={timerLoading}
                    style={{ padding: "10px 20px" }}
                  >
                    {timerLoading ? "⏳ در حال شروع..." : "▶️ شروع تایمر"}
                  </button>
                </div>
              )}
              
              {/* Time Logs List */}
              {timeLogs.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <h3 style={{ fontSize: 16, marginBottom: 12 }}>تاریخچه زمان کار</h3>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>کاربر</th>
                          <th>شروع</th>
                          <th>پایان</th>
                          <th>مدت زمان</th>
                          <th>توضیحات</th>
                        </tr>
                      </thead>
                      <tbody>
                        {timeLogs.map((log) => (
                          <tr key={log.id}>
                            <td>{log.user?.full_name || "ناشناس"}</td>
                            <td>{new Date(log.start_time).toLocaleString("fa-IR")}</td>
                            <td>{log.end_time ? new Date(log.end_time).toLocaleString("fa-IR") : "-"}</td>
                            <td>
                              {log.duration_minutes 
                                ? formatDuration(log.duration_minutes)
                                : log.is_active === true 
                                  ? <span style={{ color: "var(--success)" }}>در حال کار...</span>
                                  : "-"}
                            </td>
                            <td style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                              {log.description || "-"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

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
                    <AnimatePresence mode="popLayout">
                      {attachments.map((a, idx) => {
                        const isNew = idx >= prevAttachmentsLength;
                        return (
                          <motion.tr
                            key={a.id}
                            initial={isNew ? { opacity: 0, scale: 0.95 } : { opacity: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ 
                              duration: 0.3,
                              delay: isNew ? 0 : idx * 0.05,
                              ease: "easeOut"
                            }}
                          >
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
                          </motion.tr>
                        );
                      })}
                    </AnimatePresence>
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
              <div 
                ref={commentsContainerRef}
                style={{ 
                  display: "grid", 
                  gap: 12, 
                  marginBottom: 20,
                  maxHeight: "600px",
                  overflowY: "auto",
                  paddingRight: 8
                }}
              >
                <AnimatePresence mode="popLayout">
                  {comments.map((c, idx) => {
                    const isNew = idx >= prevCommentsLength;
                    return (
                      <motion.div
                        key={c.id || idx}
                        initial={isNew ? { opacity: 0, x: -20, scale: 0.95 } : { opacity: 0 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, x: 20, scale: 0.95 }}
                        transition={{ 
                          duration: 0.3,
                          delay: isNew ? 0 : idx * 0.05
                        }}
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
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
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
              <div 
                ref={historyContainerRef}
                style={{ 
                  display: "grid", 
                  gap: 12,
                  maxHeight: "600px",
                  overflowY: "auto",
                  paddingRight: 8
                }}
              >
                <AnimatePresence mode="popLayout">
                  {history.map((h, idx) => (
                    <motion.div
                      key={h.id || idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3, delay: idx * 0.05 }}
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
                        <span className={`badge ${(h.status ?? "pending").toLowerCase()}`}>
                          {getStatusBadge(h.status ?? "pending")}
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
                          تغییر توسط: {h.changed_by?.full_name || h.changed_by?.username}
                        </div>
                      )}
                    </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
