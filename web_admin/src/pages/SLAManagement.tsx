import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, apiPost, apiPut, apiDelete, isAuthenticated, getStoredProfile } from "../services/api";

type SLARule = {
  id: number;
  name: string;
  description?: string | null;
  priority?: string | null;
  category?: string | null;
  department_id?: number | null;
  response_time_minutes: number;
  resolution_time_minutes: number;
  response_warning_minutes: number;
  resolution_warning_minutes: number;
  escalation_enabled: boolean;
  escalation_after_minutes?: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

const EMPTY_FORM = {
  name: "",
  description: "",
  priority: "",
  category: "",
  department_id: "",
  response_time_minutes: 60,
  resolution_time_minutes: 240,
  response_warning_minutes: 30,
  resolution_warning_minutes: 60,
  escalation_enabled: false,
  escalation_after_minutes: "",
  is_active: true,
};

const PRIORITIES = [
  { value: "", label: "همه اولویت‌ها" },
  { value: "critical", label: "🔴 بحرانی" },
  { value: "high", label: "🟠 بالا" },
  { value: "medium", label: "🟡 متوسط" },
  { value: "low", label: "🟢 پایین" },
];

const CATEGORIES = [
  { value: "", label: "همه دسته‌بندی‌ها" },
  { value: "internet", label: "اینترنت" },
  { value: "equipment", label: "تجهیزات" },
  { value: "software", label: "نرم‌افزار" },
  { value: "other", label: "سایر" },
];

export default function SLAManagement() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any | null>(() => getStoredProfile());
  const [rules, setRules] = useState<SLARule[]>([]);
  const [departments, setDepartments] = useState<{ id: number; name: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [filterActive, setFilterActive] = useState<string>("");

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    if (!profile || !["admin", "central_admin"].includes(profile.role)) {
      navigate("/");
      return;
    }
    loadDepartments();
    loadRules();
  }, [navigate, profile, filterActive]);

  const loadDepartments = async () => {
    try {
      const depts = await apiGet("/api/departments?page_size=100") as { id: number; name: string }[];
      setDepartments(depts);
    } catch (e: any) {
      console.error("Error loading departments:", e);
    }
  };

  const loadRules = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterActive) params.set("is_active", filterActive);
      const query = params.toString() ? `?${params.toString()}` : "";
      const res = await apiGet(`/api/sla${query}`) as SLARule[];
      setRules(res);
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت قوانین SLA");
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (rule: SLARule) => {
    setEditingId(rule.id);
    setForm({
      name: rule.name,
      description: rule.description || "",
      priority: rule.priority || "",
      category: rule.category || "",
      department_id: rule.department_id ? String(rule.department_id) : "",
      response_time_minutes: rule.response_time_minutes,
      resolution_time_minutes: rule.resolution_time_minutes,
      response_warning_minutes: rule.response_warning_minutes,
      resolution_warning_minutes: rule.resolution_warning_minutes,
      escalation_enabled: rule.escalation_enabled,
      escalation_after_minutes: rule.escalation_after_minutes ? String(rule.escalation_after_minutes) : "",
      is_active: rule.is_active,
    });
    setSuccess(null);
    setError(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setError(null);
    setSuccess(null);
  };

  const submit = async () => {
    if (!form.name || !form.response_time_minutes || !form.resolution_time_minutes) {
      setError("نام، زمان پاسخ و زمان حل الزامی است.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const payload: any = {
        name: form.name,
        description: form.description || null,
        priority: form.priority || null,
        category: form.category || null,
        department_id: form.department_id ? Number(form.department_id) : null,
        response_time_minutes: form.response_time_minutes,
        resolution_time_minutes: form.resolution_time_minutes,
        response_warning_minutes: form.response_warning_minutes,
        resolution_warning_minutes: form.resolution_warning_minutes,
        escalation_enabled: form.escalation_enabled,
        escalation_after_minutes: form.escalation_after_minutes ? Number(form.escalation_after_minutes) : null,
        is_active: form.is_active,
      };

      if (editingId) {
        await apiPut(`/api/sla/${editingId}`, payload);
        setSuccess("قانون SLA با موفقیت به‌روزرسانی شد.");
      } else {
        await apiPost("/api/sla", payload);
        setSuccess("قانون SLA جدید با موفقیت ایجاد شد.");
      }
      cancelEdit();
      await loadRules();
    } catch (e: any) {
      setError(e?.message || "خطا در ذخیره قانون SLA.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("آیا از حذف این قانون SLA مطمئن هستید؟")) {
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await apiDelete(`/api/sla/${id}`);
      setSuccess("قانون SLA با موفقیت حذف شد.");
      await loadRules();
    } catch (e: any) {
      setError(e?.message || "خطا در حذف قانون SLA.");
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (rule: SLARule) => {
    setLoading(true);
    setError(null);
    try {
      await apiPut(`/api/sla/${rule.id}`, { is_active: !rule.is_active });
      await loadRules();
    } catch (e: any) {
      setError(e?.message || "خطا در تغییر وضعیت قانون.");
    } finally {
      setLoading(false);
    }
  };

  const getPriorityLabel = (priority: string | null) => {
    if (!priority) return "همه اولویت‌ها";
    return PRIORITIES.find((p) => p.value === priority)?.label || priority;
  };

  const getCategoryLabel = (category: string | null) => {
    if (!category) return "همه دسته‌بندی‌ها";
    return CATEGORIES.find((c) => c.value === category)?.label || category;
  };

  const formatMinutes = (minutes: number) => {
    if (minutes < 60) return `${minutes} دقیقه`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (mins === 0) return `${hours} ساعت`;
    return `${hours} ساعت و ${mins} دقیقه`;
  };

  return (
    <div className="fade-in">
      <h1 className="page-title">⏱️ مدیریت قوانین SLA</h1>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">{editingId ? "✏️ ویرایش قانون SLA" : "➕ ایجاد قانون SLA جدید"}</h2>
        </div>
        {error && <div className="alert error fade-in">{error}</div>}
        {success && <div className="alert success fade-in">{success}</div>}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submit();
          }}
        >
          <label>
            نام قانون:
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              placeholder="مثال: SLA تیکت‌های بحرانی IT"
            />
          </label>
          <label>
            توضیحات:
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={2}
              placeholder="توضیحات اختیاری"
            ></textarea>
          </label>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginTop: 16 }}>
            <label>
              اولویت:
              <select
                value={form.priority}
                onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
              >
                {PRIORITIES.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              دسته‌بندی:
              <select
                value={form.category}
                onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              دپارتمان:
              <select
                value={form.department_id}
                onChange={(e) => setForm((f) => ({ ...f, department_id: e.target.value }))}
              >
                <option value="">همه دپارتمان‌ها</option>
                {departments.map((d) => (
                  <option key={d.id} value={String(d.id)}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>زمان‌های هدف</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <label>
                زمان پاسخ هدف (دقیقه):
                <input
                  type="number"
                  value={form.response_time_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, response_time_minutes: Number(e.target.value) }))}
                  min={1}
                  required
                  placeholder="مثال: 60"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.response_time_minutes)})
                </div>
              </label>
              <label>
                زمان حل هدف (دقیقه):
                <input
                  type="number"
                  value={form.resolution_time_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, resolution_time_minutes: Number(e.target.value) }))}
                  min={1}
                  required
                  placeholder="مثال: 240"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.resolution_time_minutes)})
                </div>
              </label>
            </div>
          </div>

          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>هشدارها</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <label>
                هشدار قبل از مهلت پاسخ (دقیقه):
                <input
                  type="number"
                  value={form.response_warning_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, response_warning_minutes: Number(e.target.value) }))}
                  min={0}
                  required
                  placeholder="مثال: 30"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.response_warning_minutes)})
                </div>
              </label>
              <label>
                هشدار قبل از مهلت حل (دقیقه):
                <input
                  type="number"
                  value={form.resolution_warning_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, resolution_warning_minutes: Number(e.target.value) }))}
                  min={0}
                  required
                  placeholder="مثال: 60"
                />
                <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                  ({formatMinutes(form.resolution_warning_minutes)})
                </div>
              </label>
            </div>
          </div>

          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>Escalation</h3>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.escalation_enabled}
                onChange={(e) => setForm((f) => ({ ...f, escalation_enabled: e.target.checked }))}
              />
              فعال کردن Escalation
            </label>
            {form.escalation_enabled && (
              <label style={{ marginTop: 12 }}>
                Escalation بعد از (دقیقه):
                <input
                  type="number"
                  value={form.escalation_after_minutes}
                  onChange={(e) => setForm((f) => ({ ...f, escalation_after_minutes: e.target.value }))}
                  min={1}
                  placeholder="مثال: 120"
                />
                {form.escalation_after_minutes && (
                  <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                    ({formatMinutes(Number(form.escalation_after_minutes))})
                  </div>
                )}
              </label>
            )}
          </div>

          <label className="checkbox-label" style={{ marginTop: 16 }}>
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
            />
            فعال
          </label>
          <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
            <button type="submit" disabled={loading}>
              {loading ? "⏳ در حال ذخیره..." : "💾 ذخیره"}
            </button>
            {editingId && (
              <button type="button" className="secondary" onClick={cancelEdit} disabled={loading}>
                انصراف
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">لیست قوانین SLA</h2>
        </div>
        <div className="filters" style={{ marginBottom: 16 }}>
          <select
            value={filterActive}
            onChange={(e) => setFilterActive(e.target.value)}
            style={{ flex: 1 }}
          >
            <option value="">همه وضعیت‌ها</option>
            <option value="true">فعال</option>
            <option value="false">غیرفعال</option>
          </select>
        </div>
        {loading && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <div className="loading" style={{ margin: "0 auto" }}></div>
            <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
          </div>
        )}
        {!loading && rules.length === 0 && (
          <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
            هیچ قانون SLA یافت نشد.
          </div>
        )}
        {!loading && rules.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>نام</th>
                  <th>اولویت</th>
                  <th>دسته‌بندی</th>
                  <th>دپارتمان</th>
                  <th>زمان پاسخ</th>
                  <th>زمان حل</th>
                  <th>Escalation</th>
                  <th>وضعیت</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {rules.map((rule) => (
                  <tr key={rule.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{rule.name}</div>
                      {rule.description && (
                        <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                          {rule.description}
                        </div>
                      )}
                    </td>
                    <td>{getPriorityLabel(rule.priority)}</td>
                    <td>{getCategoryLabel(rule.category)}</td>
                    <td>
                      {rule.department_id
                        ? departments.find((d) => d.id === rule.department_id)?.name || `ID: ${rule.department_id}`
                        : "همه"}
                    </td>
                    <td>
                      <div style={{ fontSize: 14 }}>{formatMinutes(rule.response_time_minutes)}</div>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                        هشدار: {formatMinutes(rule.response_warning_minutes)} قبل
                      </div>
                    </td>
                    <td>
                      <div style={{ fontSize: 14 }}>{formatMinutes(rule.resolution_time_minutes)}</div>
                      <div style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                        هشدار: {formatMinutes(rule.resolution_warning_minutes)} قبل
                      </div>
                    </td>
                    <td>
                      {rule.escalation_enabled ? (
                        <div>
                          <span className="badge success">فعال</span>
                          {rule.escalation_after_minutes && (
                            <div style={{ fontSize: 12, marginTop: 4 }}>
                              بعد از {formatMinutes(rule.escalation_after_minutes)}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="badge secondary">غیرفعال</span>
                      )}
                    </td>
                    <td>
                      {rule.is_active ? (
                        <span className="badge success">فعال</span>
                      ) : (
                        <span className="badge danger">غیرفعال</span>
                      )}
                    </td>
                    <td>
                      <button
                        className="secondary small"
                        onClick={() => toggleActive(rule)}
                        disabled={loading}
                        title={rule.is_active ? "غیرفعال کردن" : "فعال کردن"}
                      >
                        {rule.is_active ? "⏸️" : "▶️"}
                      </button>
                      <button
                        className="secondary small"
                        onClick={() => startEdit(rule)}
                        style={{ marginLeft: 8 }}
                      >
                        ✏️ ویرایش
                      </button>
                      <button
                        className="danger small"
                        onClick={() => handleDelete(rule.id)}
                        style={{ marginLeft: 8 }}
                      >
                        🗑️ حذف
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

