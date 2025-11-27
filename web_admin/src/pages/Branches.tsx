import { useEffect, useState, useRef } from "react";
import { apiGet, apiPost, apiPut, isAuthenticated } from "../services/api";
import { useNavigate } from "react-router-dom";
import { stagger, fadeIn, slideIn } from "../lib/gsap";

type Branch = {
  id: number;
  name: string;
  name_en?: string | null;
  code: string;
  address?: string | null;
  phone?: string | null;
  is_active: boolean;
  created_at: string;
};

export default function Branches() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({
    name: "",
    name_en: "",
    code: "",
    address: "",
    phone: "",
    is_active: true
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, []);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiGet("/api/branches");
      setItems(res);
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت شعب");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const startEdit = (branch: Branch) => {
    setEditingId(branch.id);
    setForm({
      name: branch.name,
      name_en: branch.name_en || "",
      code: branch.code,
      address: branch.address || "",
      phone: branch.phone || "",
      is_active: branch.is_active
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm({ name: "", name_en: "", code: "", address: "", phone: "", is_active: true });
    setError(null);
  };

  const submit = async () => {
    if (!form.name || !form.code) {
      setError("نام و کد شعبه الزامی است");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      if (editingId) {
        await apiPut(`/api/branches/${editingId}`, {
          name: form.name,
          name_en: form.name_en || undefined,
          code: form.code,
          address: form.address || undefined,
          phone: form.phone || undefined,
          is_active: form.is_active
        });
        setEditingId(null);
      } else {
        await apiPost("/api/branches", {
          name: form.name,
          name_en: form.name_en || undefined,
          code: form.code,
          address: form.address || undefined,
          phone: form.phone || undefined,
          is_active: form.is_active
        });
      }
      setForm({ name: "", name_en: "", code: "", address: "", phone: "", is_active: true });
      await load();
      setError(null);
    } catch (e: any) {
      setError(e?.message || (editingId ? "خطا در ویرایش شعبه" : "خطا در ثبت شعبه"));
    } finally {
      setLoading(false);
    }
  };

  const titleRef = useRef<HTMLHeadingElement>(null);
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

  // Animate branches list when data changes
  useEffect(() => {
    if (items.length > 0 && listRef.current) {
      stagger(
        ".branch-item",
        (el) => slideIn(el, "left", { duration: 0.4, distance: 20 }),
        { stagger: 0.05, delay: 0.3 }
      );
    }
  }, [items.length]);

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="fade-in">
      <h1 ref={titleRef} style={{ margin: "0 0 24px 0", fontSize: 32, fontWeight: 700 }}>🏢 مدیریت شعب</h1>

      {loading && !items.length && (
        <div style={{ textAlign: "center", padding: 40 }}>
          <div className="loading" style={{ margin: "0 auto" }}></div>
          <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
        </div>
      )}

      {error && (
        <div className={`alert ${error.includes("خطا") ? "error" : "info"} fade-in`}>
          {error}
        </div>
      )}

      {/* Form Card */}
      <div ref={formCardRef} className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">
            {editingId ? "✏️ ویرایش شعبه" : "➕ افزودن شعبه جدید"}
          </h2>
          {editingId && (
            <button onClick={cancelEdit} className="secondary" style={{ padding: "6px 12px" }}>
              ❌ لغو
            </button>
          )}
        </div>
        <div className="grid grid-cols-2" style={{ gap: 16 }}>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              نام شعبه <span style={{ color: "var(--error)" }}>*</span>
            </label>
            <input
              placeholder="مثال: دفتر مرکزی"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              نام انگلیسی (اختیاری)
            </label>
            <input
              placeholder="Example: Main Office"
              value={form.name_en}
              onChange={(e) => setForm({ ...form, name_en: e.target.value })}
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              کد شعبه <span style={{ color: "var(--error)" }}>*</span>
            </label>
            <input
              placeholder="مثال: MAIN-001"
              value={form.code}
              onChange={(e) => setForm({ ...form, code: e.target.value })}
              required
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              شماره تلفن (اختیاری)
            </label>
            <input
              placeholder="021-12345678"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              آدرس (اختیاری)
            </label>
            <textarea
              placeholder="آدرس کامل شعبه..."
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
              rows={2}
              style={{ resize: "vertical" }}
            />
          </div>
          <div>
            <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
              />
              <span style={{ fontSize: 14 }}>✅ شعبه فعال است</span>
            </label>
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "flex-end" }}>
            <button onClick={submit} disabled={loading} style={{ minWidth: 150 }}>
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
                  <span className="loading"></span>
                  {editingId ? "در حال ذخیره..." : "در حال ثبت..."}
                </span>
              ) : (
                editingId ? "💾 ذخیره تغییرات" : "➕ افزودن شعبه"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Branches List */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📋 لیست شعب ({items.length})</h2>
        </div>
        {items.length === 0 ? (
          <div style={{ textAlign: "center", padding: 60, color: "var(--fg-secondary)" }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>🏢</div>
            <h3 style={{ margin: "0 0 8px 0" }}>هیچ شعبه‌ای ثبت نشده است</h3>
            <p style={{ margin: 0 }}>برای شروع، شعبه اول را اضافه کنید.</p>
          </div>
        ) : (
          <div ref={listRef} className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>نام</th>
                  <th>کد</th>
                  <th>وضعیت</th>
                  <th>تلفن</th>
                  <th>آدرس</th>
                  <th>تاریخ ایجاد</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {items.map((b) => (
                  <tr key={b.id} className="branch-item">
                    <td style={{ fontWeight: 500 }}>
                      {b.name}
                      {b.name_en && (
                        <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                          {b.name_en}
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
                        {b.code}
                      </code>
                    </td>
                    <td>
                      {b.is_active ? (
                        <span className="badge resolved">✅ فعال</span>
                      ) : (
                        <span className="badge closed">❌ غیرفعال</span>
                      )}
                    </td>
                    <td style={{ color: "var(--fg-secondary)" }}>{b.phone || "-"}</td>
                    <td style={{ color: "var(--fg-secondary)", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis" }}>
                      {b.address || "-"}
                    </td>
                    <td style={{ color: "var(--fg-secondary)", fontSize: 13 }}>
                      {b.created_at ? new Date(b.created_at).toLocaleDateString("fa-IR") : "-"}
                    </td>
                    <td>
                      <button
                        onClick={() => startEdit(b)}
                        disabled={loading}
                        className="secondary"
                        style={{ padding: "6px 12px", fontSize: 13 }}
                      >
                        ✏️ ویرایش
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
