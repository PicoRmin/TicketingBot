import { useEffect, useState, useRef } from "react";
import { apiGet, apiPost, apiPut, apiDelete, isAuthenticated } from "../services/api";
import { useNavigate } from "react-router-dom";
import { stagger, fadeIn, slideIn } from "../lib/gsap";

type Department = {
  id: number;
  name: string;
  name_en?: string | null;
  code: string;
  description?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export default function Departments() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Department[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({
    name: "",
    name_en: "",
    code: "",
    description: "",
    is_active: true
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, [navigate]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiGet("/api/departments?page_size=100") as Department[];
      setItems(res);
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "خطا در دریافت دپارتمان‌ها";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const startEdit = (dept: Department) => {
    setEditingId(dept.id);
    setForm({
      name: dept.name,
      name_en: dept.name_en || "",
      code: dept.code,
      description: dept.description || "",
      is_active: dept.is_active
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm({ name: "", name_en: "", code: "", description: "", is_active: true });
    setError(null);
  };

  const submit = async () => {
    if (!form.name || !form.code) {
      setError("نام و کد دپارتمان الزامی است");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      if (editingId) {
        await apiPut(`/api/departments/${editingId}`, form);
      } else {
        await apiPost("/api/departments", form);
      }
      await load();
      cancelEdit();
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "خطا در ذخیره دپارتمان";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("آیا از حذف این دپارتمان اطمینان دارید؟")) return;
    setLoading(true);
    setError(null);
    try {
      await apiDelete(`/api/departments/${id}`);
      await load();
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "خطا در حذف دپارتمان";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const titleRef = useRef<HTMLDivElement>(null);
  const formCardRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Animate on mount
  useEffect(() => {
    if (titleRef.current) {
      slideIn(titleRef.current, "right", { duration: 0.6, distance: 50 });
    }
    if (formCardRef.current) {
      fadeIn(formCardRef.current, { duration: 0.7, delay: 0.2 });
    }
  }, []);

  // Animate departments list when data changes
  useEffect(() => {
    if (items.length > 0 && listRef.current) {
      stagger(
        "tbody tr",
        (el) => slideIn(el, "left", { duration: 0.4, distance: 20 }),
        { stagger: 0.05, delay: 0.3 }
      );
    }
  }, [items.length]);

  return (
    <div className="fade-in">
      <div ref={titleRef} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>🏢 دپارتمان‌ها</h1>
        {items.length > 0 && (
          <div style={{ color: "var(--fg-secondary)", fontSize: 14 }}>
            مجموع: <strong>{items.length}</strong> دپارتمان
          </div>
        )}
      </div>

      {error && (
        <div className="alert error fade-in">
          <strong>خطا:</strong> {error}
        </div>
      )}

      <div ref={formCardRef} className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">{editingId ? "✏️ ویرایش دپارتمان" : "➕ افزودن دپارتمان جدید"}</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              نام دپارتمان <span style={{ color: "var(--error)" }}>*</span>
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="مثال: دپارتمان IT"
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              نام انگلیسی
            </label>
            <input
              type="text"
              value={form.name_en}
              onChange={(e) => setForm({ ...form, name_en: e.target.value })}
              placeholder="Example: IT Department"
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              کد دپارتمان <span style={{ color: "var(--error)" }}>*</span>
            </label>
            <input
              type="text"
              value={form.code}
              onChange={(e) => setForm({ ...form, code: e.target.value })}
              placeholder="مثال: it_department"
              disabled={!!editingId}
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              وضعیت
            </label>
            <select
              value={form.is_active ? "true" : "false"}
              onChange={(e) => setForm({ ...form, is_active: e.target.value === "true" })}
            >
              <option value="true">✅ فعال</option>
              <option value="false">❌ غیرفعال</option>
            </select>
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              توضیحات
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="توضیحات دپارتمان..."
              rows={3}
            />
          </div>
        </div>
        <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
          <button onClick={submit} disabled={loading}>
            {loading ? "⏳ در حال ذخیره..." : editingId ? "💾 به‌روزرسانی" : "➕ افزودن"}
          </button>
          {editingId && (
            <button className="secondary" onClick={cancelEdit} disabled={loading}>
              ❌ انصراف
            </button>
          )}
        </div>
      </div>

      {loading && !items.length ? (
        <div style={{ textAlign: "center", padding: 40 }}>
          <div className="loading" style={{ margin: "0 auto" }}></div>
          <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: 60 }}>
          <div style={{ fontSize: 64, marginBottom: 16 }}>🏢</div>
          <h2 style={{ margin: "0 0 8px 0" }}>دپارتمانی یافت نشد</h2>
          <p style={{ color: "var(--fg-secondary)", margin: 0 }}>
            هنوز دپارتمانی ایجاد نشده است. اولین دپارتمان را اضافه کنید.
          </p>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>نام</th>
                <th>کد</th>
                <th>توضیحات</th>
                <th>وضعیت</th>
                <th>تاریخ ایجاد</th>
                <th>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div style={{ fontWeight: 500 }}>{item.name}</div>
                    {item.name_en && (
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                        {item.name_en}
                      </div>
                    )}
                  </td>
                  <td>
                    <code style={{
                      background: "var(--bg-secondary)",
                      padding: "4px 8px",
                      borderRadius: "4px",
                      fontSize: 12
                    }}>
                      {item.code}
                    </code>
                  </td>
                  <td style={{ color: "var(--fg-secondary)", fontSize: 13 }}>
                    {item.description || "-"}
                  </td>
                  <td>
                    {item.is_active ? (
                      <span className="badge resolved">✅ فعال</span>
                    ) : (
                      <span className="badge closed">❌ غیرفعال</span>
                    )}
                  </td>
                  <td style={{ color: "var(--fg-secondary)", fontSize: 13 }}>
                    {new Date(item.created_at).toLocaleDateString("fa-IR")}
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        className="secondary"
                        onClick={() => startEdit(item)}
                        style={{ padding: "6px 12px", fontSize: 13 }}
                      >
                        ✏️ ویرایش
                      </button>
                      <button
                        className="danger"
                        onClick={() => handleDelete(item.id)}
                        style={{ padding: "6px 12px", fontSize: 13 }}
                        disabled={loading}
                      >
                        🗑️ حذف
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

