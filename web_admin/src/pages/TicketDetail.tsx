import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiGet, apiPatch, apiUploadFile, isAuthenticated } from "../services/api";
import { apiPost } from "../services/api";

type Ticket = {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  status: string;
  category: string;
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

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, []);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const t = await apiGet(`/api/tickets/${id}`);
        setTicket(t);
        setNewStatus(t.status);
        const list = await apiGet(`/api/files/ticket/${id}/list`);
        setAttachments(list);
        const commentsList = await apiGet(`/api/comments/ticket/${id}`);
        setComments(commentsList);
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
      const updated = await apiPatch(`/api/tickets/${id}/status`, { status: newStatus });
      setTicket(updated);
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
      const res = await apiUploadFile(`/api/files/upload?ticket_id=${id}`, form);
      setAttachments((prev) => [...prev, {
        id: res.id,
        filename: res.filename,
        original_filename: res.original_filename,
        file_size: res.file_size,
        file_type: res.file_type,
        ticket_id: res.ticket_id
      }]);
      setFile(null);
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
      });
      setComments((prev) => [...prev, res]);
      setNewComment("");
      setIsInternal(false);
    } catch (e: any) {
      setError(e?.message || "خطا در ثبت نظر");
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div>
      <h1>جزئیات تیکت</h1>
      {loading && <div>در حال بارگذاری...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      {ticket && (
        <>
          <div style={{ display: "grid", gap: 8, marginBottom: 16 }}>
            <div>شماره: {ticket.ticket_number}</div>
            <div>عنوان: {ticket.title}</div>
            <div>توضیحات: {ticket.description}</div>
            <div>دسته: {ticket.category}</div>
            <div>وضعیت: {ticket.status}</div>
            <div>ایجاد: {ticket.created_at?.slice(0, 10) || ""}</div>
            <div>به‌روزرسانی: {ticket.updated_at?.slice(0, 10) || ""}</div>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <label>
              تغییر وضعیت:
              <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
                <option value="pending">در انتظار</option>
                <option value="in_progress">در حال انجام</option>
                <option value="resolved">حل شده</option>
                <option value="closed">بسته شده</option>
              </select>
            </label>
            <button onClick={changeStatus} disabled={updating}>
              ذخیره
            </button>
          </div>
          <hr style={{ margin: "16px 0" }} />
          <h2>پیوست‌ها</h2>
          <div className="table-wrap">
            <table border={1} cellPadding={6} style={{ width: "100%", marginTop: 8 }}>
              <thead>
                <tr>
                  <th>نام اصلی</th>
                  <th>نوع</th>
                  <th>اندازه</th>
                </tr>
              </thead>
              <tbody>
                {attachments.map(a => (
                  <tr key={a.id}>
                    <td>{a.original_filename}</td>
                    <td>{a.file_type}</td>
                    <td>{(a.file_size / 1024).toFixed(1)} KB</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <button onClick={upload} disabled={updating || !file}>آپلود</button>
          </div>
          <hr style={{ margin: "16px 0" }} />
          <h2>نظرات</h2>
          <div style={{ display: "grid", gap: 8, marginTop: 8 }}>
            {comments.map((c, idx) => (
              <div key={idx} style={{ border: "1px solid var(--border)", padding: 8 }}>
                <div style={{ fontSize: 12, color: "var(--muted)" }}>
                  {c.created_at?.slice(0, 16).replace("T", " ") || ""}
                  {c.is_internal ? " • داخلی" : ""}
                </div>
                <div>{c.comment}</div>
              </div>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <input
              placeholder="نظر جدید..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              style={{ flex: 1 }}
            />
            <label style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <input type="checkbox" checked={isInternal} onChange={(e) => setIsInternal(e.target.checked)} />
              داخلی
            </label>
            <button onClick={addComment} disabled={updating || !newComment.trim()}>ارسال</button>
          </div>
        </>
      )}
    </div>
  );
}

