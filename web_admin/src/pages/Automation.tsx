import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  isAuthenticated,
  getStoredProfile,
  fetchProfile,
} from "../services/api";
import type { AuthProfile } from "../services/api";

type RuleType = "auto_assign" | "auto_close" | "auto_notify";

type AutomationConditionValue = string | number | boolean | undefined;

type AutomationConditions = {
  priority?: string;
  category?: string;
  branch_id?: number;
  department_id?: number;
  ticket_status?: string;
  time_since_creation_minutes?: number;
  time_since_last_update_minutes?: number;
  [key: string]: AutomationConditionValue;
};

type AutomationActionValue = string | number | boolean | number[] | string[] | undefined;

type AutomationActions = {
  assign_to_user_id?: number;
  assign_to_department_id?: number;
  assign_to_role?: string;
  notify_user_id?: number;
  notify_users?: number[];
  notify_role?: string;
  notify_roles?: string[];
  auto_close_status?: string;
  message_template?: string;
  message?: string;
  close_after_hours?: number;
  round_robin?: boolean;
  only_if_resolved?: boolean;
  set_status?: string;
  send_notification_to_user_id?: number;
  send_notification_to_role?: string;
  notification_message?: string;
  [key: string]: AutomationActionValue;
};

type AutomationRule = {
  id: number;
  name: string;
  description?: string | null;
  rule_type: RuleType;
  conditions?: AutomationConditions | null;
  actions: AutomationActions;
  priority: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

type AutomationFormState = {
  name: string;
  description: string;
  rule_type: RuleType;
  conditions: AutomationConditions | null;
  actions: AutomationActions;
  priority: number;
  is_active: boolean;
};

const EMPTY_FORM: AutomationFormState = {
  name: "",
  description: "",
  rule_type: "auto_assign",
  conditions: null,
  actions: {},
  priority: 100,
  is_active: true,
};

const RULE_TYPES = [
  { value: "auto_assign", label: "تخصیص خودکار" },
  { value: "auto_close", label: "بستن خودکار" },
  { value: "auto_notify", label: "اعلان خودکار" },
];

export default function Automation() {
  const navigate = useNavigate();
  const [profile, setProfileState] = useState<AuthProfile | null>(() => getStoredProfile());
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<AutomationFormState>({ ...EMPTY_FORM });
  const [filterType, setFilterType] = useState<RuleType | "">("");
  const [filterActive, setFilterActive] = useState<"" | "true" | "false">("");

  const ensureProfile = useCallback(async () => {
    if (!isAuthenticated()) {
      navigate("/login");
      return null;
    }

    if (profile) {
      return profile;
    }

    const stored = getStoredProfile();
    if (stored) {
      setProfileState(stored);
      return stored;
    }

    try {
      const fetched = await fetchProfile();
      setProfileState(fetched);
      return fetched;
    } catch (err) {
      console.error("Failed to fetch profile:", err);
      navigate("/login");
      return null;
    }
  }, [navigate, profile]);

  const loadRules = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterType) params.set("rule_type", filterType);
      if (filterActive) params.set("is_active", filterActive);
      const query = params.toString() ? `?${params.toString()}` : "";
      const res = (await apiGet(`/api/automation${query}`)) as AutomationRule[];
      setRules(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در دریافت قوانین");
    } finally {
      setLoading(false);
    }
  }, [filterType, filterActive]);

  useEffect(() => {
    (async () => {
      const currentProfile = await ensureProfile();
      if (!currentProfile) {
        return;
      }
      if (!["admin", "central_admin"].includes(currentProfile.role)) {
        navigate("/");
        return;
      }
      loadRules();
    })();
  }, [ensureProfile, navigate, loadRules]);

  const startEdit = (rule: AutomationRule) => {
    setEditingId(rule.id);
    setForm({
      name: rule.name,
      description: rule.description || "",
      rule_type: rule.rule_type,
      conditions: rule.conditions || null,
      actions: rule.actions || {},
      priority: rule.priority,
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
    if (!form.name || !form.rule_type) {
      setError("نام و نوع قانون الزامی است.");
      return;
    }

    // Validate actions based on rule_type
    if (form.rule_type === "auto_assign") {
      if (!form.actions.assign_to_user_id && !form.actions.assign_to_department_id && !form.actions.assign_to_role) {
        setError("برای تخصیص خودکار، باید یکی از گزینه‌های assign_to_user_id، assign_to_department_id یا assign_to_role را مشخص کنید.");
        return;
      }
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      if (editingId) {
        await apiPut(`/api/automation/${editingId}`, form);
        setSuccess("قانون با موفقیت به‌روزرسانی شد.");
      } else {
        await apiPost("/api/automation", form);
        setSuccess("قانون جدید با موفقیت ایجاد شد.");
      }
      cancelEdit();
      await loadRules();
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در ذخیره قانون.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("آیا از حذف این قانون مطمئن هستید؟")) {
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await apiDelete(`/api/automation/${id}`);
      setSuccess("قانون با موفقیت حذف شد.");
      await loadRules();
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در حذف قانون.");
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (rule: AutomationRule) => {
    setLoading(true);
    setError(null);
    try {
      await apiPut(`/api/automation/${rule.id}`, { is_active: !rule.is_active });
      await loadRules();
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در تغییر وضعیت قانون.");
    } finally {
      setLoading(false);
    }
  };

  const updateActionsField = (key: string, value: AutomationActionValue) => {
    setForm((f) => ({
      ...f,
      actions: { ...f.actions, [key]: value },
    }));
  };

  const updateConditionsField = (key: string, value: AutomationConditionValue) => {
    setForm((f) => ({
      ...f,
      conditions: { ...(f.conditions || {}), [key]: value || undefined },
    }));
  };

  const removeActionsField = (key: string) => {
    setForm((f) => {
      const newActions = { ...f.actions };
      delete newActions[key];
      return { ...f, actions: newActions };
    });
  };

  const removeConditionsField = (key: string) => {
    setForm((f) => {
      const newConditions = { ...(f.conditions || {}) };
      delete newConditions[key];
      return { ...f, conditions: Object.keys(newConditions).length > 0 ? newConditions : null };
    });
  };

  const getRuleTypeLabel = (type: string) => {
    return RULE_TYPES.find((rt) => rt.value === type)?.label || type;
  };

  return (
    <div className="fade-in">
      <h1 className="page-title">🤖 مدیریت قوانین اتوماسیون</h1>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">{editingId ? "✏️ ویرایش قانون" : "➕ ایجاد قانون جدید"}</h2>
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
              placeholder="مثال: تخصیص خودکار تیکت‌های بحرانی به IT"
            />
          </label>
          <label>
            توضیحات:
            <textarea
              value={form.description || ""}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={2}
              placeholder="توضیحات اختیاری"
            ></textarea>
          </label>
          <label>
            نوع قانون:
            <select
              value={form.rule_type}
              onChange={(e) => {
                setForm((f) => ({ ...f, rule_type: e.target.value as RuleType, actions: {} }));
              }}
              required
            >
              {RULE_TYPES.map((rt) => (
                <option key={rt.value} value={rt.value}>
                  {rt.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            اولویت (کمتر = اولویت بالاتر):
            <input
              type="number"
              value={form.priority}
              onChange={(e) => setForm((f) => ({ ...f, priority: Number(e.target.value) }))}
              min={1}
              max={1000}
              required
            />
          </label>

          {/* Conditions Section */}
          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>شرایط (Conditions)</h3>
            <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <select
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    updateConditionsField(e.target.value, "");
                    e.target.value = "";
                  }
                }}
                style={{ flex: 1 }}
              >
                <option value="">➕ افزودن شرط</option>
                <option value="priority">اولویت</option>
                <option value="category">دسته‌بندی</option>
                <option value="department_id">دپارتمان</option>
                <option value="branch_id">شعبه</option>
                <option value="status">وضعیت</option>
              </select>
            </div>
            {form.conditions && Object.entries(form.conditions).map(([key, value]) => (
              <div key={key} style={{ display: "flex", gap: 8, marginBottom: 8, alignItems: "center" }}>
                <label style={{ flex: 1, display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ minWidth: 100 }}>{key}:</span>
                  {key === "priority" ? (
                    <select
                      value={String(value || "")}
                      onChange={(e) => updateConditionsField(key, e.target.value)}
                      style={{ flex: 1 }}
                    >
                      <option value="">همه</option>
                      <option value="critical">بحرانی</option>
                      <option value="high">بالا</option>
                      <option value="medium">متوسط</option>
                      <option value="low">پایین</option>
                    </select>
                  ) : key === "category" ? (
                    <select
                      value={String(value || "")}
                      onChange={(e) => updateConditionsField(key, e.target.value)}
                      style={{ flex: 1 }}
                    >
                      <option value="">همه</option>
                      <option value="internet">اینترنت</option>
                      <option value="equipment">تجهیزات</option>
                      <option value="software">نرم‌افزار</option>
                      <option value="other">سایر</option>
                    </select>
                  ) : key === "status" ? (
                    <select
                      value={String(value || "")}
                      onChange={(e) => updateConditionsField(key, e.target.value)}
                      style={{ flex: 1 }}
                    >
                      <option value="">همه</option>
                      <option value="pending">در انتظار</option>
                      <option value="in_progress">در حال انجام</option>
                      <option value="resolved">حل شده</option>
                      <option value="closed">بسته شده</option>
                    </select>
                  ) : (
                    <input
                      type={key.includes("_id") ? "number" : "text"}
                      value={String(value || "")}
                      onChange={(e) => updateConditionsField(key, key.includes("_id") ? Number(e.target.value) : e.target.value)}
                      style={{ flex: 1 }}
                      placeholder={key.includes("_id") ? "شناسه" : "مقدار"}
                    />
                  )}
                </label>
                <button
                  type="button"
                  onClick={() => removeConditionsField(key)}
                  className="danger small"
                  style={{ padding: "4px 8px" }}
                >
                  ✕
                </button>
              </div>
            ))}
            {(!form.conditions || Object.keys(form.conditions).length === 0) && (
              <div style={{ color: "var(--fg-secondary)", fontSize: 14, fontStyle: "italic" }}>
                هیچ شرطی تعریف نشده است (قانون برای همه تیکت‌ها اعمال می‌شود)
              </div>
            )}
          </div>

          {/* Actions Section */}
          <div style={{ marginTop: 20, padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
            <h3 style={{ marginBottom: 12, fontSize: 16, fontWeight: 600 }}>اقدامات (Actions)</h3>
            {form.rule_type === "auto_assign" && (
              <>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>تخصیص به کاربر:</span>
                  <input
                    type="number"
                    value={form.actions.assign_to_user_id || ""}
                    onChange={(e) => {
                      const value = e.target.value ? Number(e.target.value) : undefined;
                      if (value) {
                        updateActionsField("assign_to_user_id", value);
                        removeActionsField("assign_to_department_id");
                        removeActionsField("assign_to_role");
                      } else {
                        removeActionsField("assign_to_user_id");
                      }
                    }}
                    style={{ flex: 1 }}
                    placeholder="شناسه کاربر"
                  />
                </label>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>تخصیص به دپارتمان:</span>
                  <input
                    type="number"
                    value={form.actions.assign_to_department_id || ""}
                    onChange={(e) => {
                      const value = e.target.value ? Number(e.target.value) : undefined;
                      if (value) {
                        updateActionsField("assign_to_department_id", value);
                        removeActionsField("assign_to_user_id");
                        removeActionsField("assign_to_role");
                      } else {
                        removeActionsField("assign_to_department_id");
                      }
                    }}
                    style={{ flex: 1 }}
                    placeholder="شناسه دپارتمان"
                  />
                </label>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>Round-Robin:</span>
                  <input
                    type="checkbox"
                    checked={form.actions.round_robin || false}
                    onChange={(e) => updateActionsField("round_robin", e.target.checked)}
                  />
                  <span style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
                    توزیع یکنواخت بین کارشناسان
                  </span>
                </label>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>تخصیص به نقش:</span>
                  <select
                    value={form.actions.assign_to_role || ""}
                    onChange={(e) => {
                      const value = e.target.value || undefined;
                      if (value) {
                        updateActionsField("assign_to_role", value);
                        removeActionsField("assign_to_user_id");
                        removeActionsField("assign_to_department_id");
                      } else {
                        removeActionsField("assign_to_role");
                      }
                    }}
                    style={{ flex: 1 }}
                  >
                    <option value="">انتخاب کنید</option>
                    <option value="admin">مدیر سیستم</option>
                    <option value="central_admin">مدیر ارشد</option>
                    <option value="branch_admin">مسئول شعبه</option>
                    <option value="it_specialist">کارشناس IT</option>
                  </select>
                </label>
              </>
            )}
            {form.rule_type === "auto_close" && (
              <>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>بستن بعد از (ساعت):</span>
                  <input
                    type="number"
                    value={form.actions.close_after_hours ?? ""}
                    onChange={(e) => updateActionsField("close_after_hours", e.target.value ? Number(e.target.value) : undefined)}
                    style={{ flex: 1 }}
                    placeholder="مثال: 48"
                  />
                </label>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>فقط اگر حل شده:</span>
                  <input
                    type="checkbox"
                    checked={form.actions.only_if_resolved || false}
                    onChange={(e) => updateActionsField("only_if_resolved", e.target.checked)}
                  />
                </label>
              </>
            )}
            {form.rule_type === "auto_notify" && (
              <>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>شناسه کاربران:</span>
                  <input
                    type="text"
                    value={Array.isArray(form.actions.notify_users) ? form.actions.notify_users.join(", ") : ""}
                    onChange={(e) => {
                      const value = e.target.value
                        ? e.target.value.split(",").map((v) => Number(v.trim())).filter((v) => !isNaN(v))
                        : [];
                      updateActionsField("notify_users", value.length > 0 ? value : undefined);
                    }}
                    style={{ flex: 1 }}
                    placeholder="مثال: 1, 2, 3"
                  />
                </label>
                <label style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
                  <span style={{ minWidth: 200 }}>نقش‌ها:</span>
                  <input
                    type="text"
                    value={Array.isArray(form.actions.notify_roles) ? form.actions.notify_roles.join(", ") : ""}
                    onChange={(e) => {
                      const value = e.target.value
                        ? e.target.value.split(",").map((v) => v.trim()).filter((v) => v)
                        : [];
                      updateActionsField("notify_roles", value.length > 0 ? value : undefined);
                    }}
                    style={{ flex: 1 }}
                    placeholder="مثال: admin, it_specialist"
                  />
                </label>
                <label>
                  پیام:
                  <textarea
                    value={typeof form.actions.message === "string" ? form.actions.message : ""}
                    onChange={(e) => updateActionsField("message", e.target.value || undefined)}
                    rows={3}
                    placeholder="پیام اعلان"
                  ></textarea>
                </label>
              </>
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
          <h2 className="card-title">لیست قوانین</h2>
        </div>
        <div className="filters" style={{ marginBottom: 16 }}>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as RuleType | "")}
            style={{ flex: 1 }}
          >
            <option value="">همه انواع</option>
            {RULE_TYPES.map((rt) => (
              <option key={rt.value} value={rt.value}>
                {rt.label}
              </option>
            ))}
          </select>
          <select
            value={filterActive}
            onChange={(e) => setFilterActive(e.target.value as "" | "true" | "false")}
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
            هیچ قانونی یافت نشد.
          </div>
        )}
        {!loading && rules.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>نام</th>
                  <th>نوع</th>
                  <th>اولویت</th>
                  <th>شرایط</th>
                  <th>اقدامات</th>
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
                    <td>{getRuleTypeLabel(rule.rule_type)}</td>
                    <td>{rule.priority}</td>
                    <td>
                      {rule.conditions && Object.keys(rule.conditions).length > 0 ? (
                        <div style={{ fontSize: 12 }}>
                          {Object.entries(rule.conditions).map(([k, v]) => (
                            <div key={k}>
                              <strong>{k}:</strong> {String(v)}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <span style={{ color: "var(--fg-secondary)", fontSize: 12 }}>بدون شرط</span>
                      )}
                    </td>
                    <td>
                      <div style={{ fontSize: 12 }}>
                        {rule.rule_type === "auto_assign" && (
                          <>
                            {rule.actions.assign_to_user_id && (
                              <div>کاربر: {rule.actions.assign_to_user_id}</div>
                            )}
                            {rule.actions.assign_to_department_id && (
                              <div>دپارتمان: {rule.actions.assign_to_department_id}</div>
                            )}
                            {rule.actions.assign_to_role && (
                              <div>نقش: {rule.actions.assign_to_role}</div>
                            )}
                            {rule.actions.round_robin && <div>Round-Robin: ✓</div>}
                          </>
                        )}
                        {rule.rule_type === "auto_close" && (
                          <>
                            {rule.actions.close_after_hours && (
                              <div>بستن بعد از: {rule.actions.close_after_hours} ساعت</div>
                            )}
                            {rule.actions.only_if_resolved && <div>فقط اگر حل شده: ✓</div>}
                          </>
                        )}
                        {rule.rule_type === "auto_notify" && (
                          <>
                            {rule.actions.notify_users && (
                              <div>کاربران: {Array.isArray(rule.actions.notify_users) ? rule.actions.notify_users.join(", ") : rule.actions.notify_users}</div>
                            )}
                            {rule.actions.notify_roles && (
                              <div>نقش‌ها: {Array.isArray(rule.actions.notify_roles) ? rule.actions.notify_roles.join(", ") : rule.actions.notify_roles}</div>
                            )}
                            {rule.actions.message && (
                              <div>پیام: {rule.actions.message}</div>
                            )}
                          </>
                        )}
                      </div>
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

