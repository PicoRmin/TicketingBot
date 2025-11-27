/**
 * صفحه مدیریت فیلدهای سفارشی
 * Custom Fields Management Page
 * 
 * این صفحه امکان ایجاد، ویرایش، حذف و مدیریت فیلدهای سفارشی را فراهم می‌کند.
 * This page provides the ability to create, edit, delete and manage custom fields.
 */

import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, apiPost, apiPatch, apiDelete, isAuthenticated, getStoredProfile } from "../services/api";
import { stagger, fadeIn, slideIn, scaleIn } from "../lib/gsap";

// نوع داده‌های فیلد سفارشی
type CustomField = {
  id: number;
  name: string;
  label: string;
  label_en?: string | null;
  field_type: string;
  description?: string | null;
  config?: any;
  category?: string | null;
  department_id?: number | null;
  branch_id?: number | null;
  is_required: boolean;
  is_visible_to_user: boolean;
  is_editable_by_user: boolean;
  default_value?: string | null;
  display_order: number;
  help_text?: string | null;
  placeholder?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

// نوع داده‌های دپارتمان و شعبه
type Department = {
  id: number;
  name: string;
  code: string;
};

type Branch = {
  id: number;
  name: string;
  code: string;
};

// فرم خالی برای ایجاد فیلد جدید
const EMPTY_FORM = {
  name: "",
  label: "",
  label_en: "",
  field_type: "text",
  description: "",
  config: null,
  category: "",
  department_id: "",
  branch_id: "",
  is_required: false,
  is_visible_to_user: true,
  is_editable_by_user: true,
  default_value: "",
  display_order: 0,
  help_text: "",
  placeholder: "",
  is_active: true,
};

// انواع فیلدهای سفارشی
const FIELD_TYPES = [
  { value: "text", label: "📝 متن (Text)" },
  { value: "textarea", label: "📄 متن چندخطی (Textarea)" },
  { value: "number", label: "🔢 عدد (Number)" },
  { value: "date", label: "📅 تاریخ (Date)" },
  { value: "datetime", label: "📅 زمان (DateTime)" },
  { value: "boolean", label: "☑️ بله/خیر (Boolean)" },
  { value: "select", label: "📋 انتخاب تکی (Select)" },
  { value: "multiselect", label: "📋 انتخاب چندتایی (MultiSelect)" },
  { value: "url", label: "🔗 لینک (URL)" },
  { value: "email", label: "📧 ایمیل (Email)" },
  { value: "phone", label: "📞 تلفن (Phone)" },
];

// دسته‌بندی‌های تیکت
const CATEGORIES = [
  { value: "", label: "همه دسته‌بندی‌ها" },
  { value: "internet", label: "🌐 اینترنت" },
  { value: "equipment", label: "💻 تجهیزات" },
  { value: "software", label: "📱 نرم‌افزار" },
  { value: "other", label: "📋 سایر" },
];

export default function CustomFields() {
  const navigate = useNavigate();
  const [profile] = useState<any | null>(() => getStoredProfile());
  const [fields, setFields] = useState<CustomField[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [showForm, setShowForm] = useState(false);
  const [configOptions, setConfigOptions] = useState<Array<{ value: string; label: string }>>([]);
  const [configMin, setConfigMin] = useState("");
  const [configMax, setConfigMax] = useState("");
  const [configStep, setConfigStep] = useState("");

  // فیلترها
  const [filterCategory, setFilterCategory] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterActive, setFilterActive] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    if (!profile || !["admin", "central_admin"].includes(profile.role)) {
      navigate("/");
      return;
    }
    loadData();
  }, [navigate, profile, filterCategory, filterType, filterActive]);

  // بارگذاری داده‌ها
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // بارگذاری فیلدهای سفارشی
      const params = new URLSearchParams();
      if (filterCategory) params.set("category", filterCategory);
      if (filterType) params.set("field_type", filterType);
      if (filterActive) params.set("is_active", filterActive);
      const query = params.toString() ? `?${params.toString()}` : "";
      const fieldsData = await apiGet(`/api/custom-fields${query}`) as CustomField[];
      setFields(fieldsData);

      // بارگذاری دپارتمان‌ها
      const depts = await apiGet("/api/departments") as Department[];
      setDepartments(depts);

      // بارگذاری شعب
      const brs = await apiGet("/api/branches") as Branch[];
      setBranches(brs);
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت داده‌ها");
    } finally {
      setLoading(false);
    }
  };

  // شروع ویرایش
  const startEdit = (field: CustomField) => {
    setEditingId(field.id);
    setForm({
      name: field.name,
      label: field.label,
      label_en: field.label_en || "",
      field_type: field.field_type,
      description: field.description || "",
      config: field.config || null,
      category: field.category || "",
      department_id: field.department_id?.toString() || "",
      branch_id: field.branch_id?.toString() || "",
      is_required: field.is_required,
      is_visible_to_user: field.is_visible_to_user,
      is_editable_by_user: field.is_editable_by_user,
      default_value: field.default_value || "",
      display_order: field.display_order,
      help_text: field.help_text || "",
      placeholder: field.placeholder || "",
      is_active: field.is_active,
    });

    // بارگذاری تنظیمات config
    if (field.config) {
      if (field.field_type === "select" || field.field_type === "multiselect") {
        setConfigOptions(field.config.options || []);
      } else if (field.field_type === "number") {
        setConfigMin(field.config.min?.toString() || "");
        setConfigMax(field.config.max?.toString() || "");
        setConfigStep(field.config.step?.toString() || "");
      }
    } else {
      setConfigOptions([]);
      setConfigMin("");
      setConfigMax("");
      setConfigStep("");
    }

    setShowForm(true);
  };

  // شروع ایجاد جدید
  const startNew = () => {
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setConfigOptions([]);
    setConfigMin("");
    setConfigMax("");
    setConfigStep("");
    setShowForm(true);
  };

  // لغو ویرایش
  const cancelEdit = () => {
    setShowForm(false);
    setEditingId(null);
    setForm({ ...EMPTY_FORM });
    setConfigOptions([]);
    setConfigMin("");
    setConfigMax("");
    setConfigStep("");
  };

  // ذخیره فیلد
  const saveField = async () => {
    setError(null);
    setSuccess(null);

    // اعتبارسنجی
    if (!form.name || !form.label) {
      setError("نام و برچسب فیلد الزامی است");
      return;
    }

    try {
      // ساخت config بر اساس نوع فیلد
      let config: any = null;
      if (form.field_type === "select" || form.field_type === "multiselect") {
        if (configOptions.length === 0) {
          setError("برای فیلدهای Select/MultiSelect باید حداقل یک گزینه تعریف کنید");
          return;
        }
        config = { options: configOptions };
      } else if (form.field_type === "number") {
        config = {};
        if (configMin) config.min = parseFloat(configMin);
        if (configMax) config.max = parseFloat(configMax);
        if (configStep) config.step = parseFloat(configStep);
        if (Object.keys(config).length === 0) config = null;
      }

      const fieldData = {
        ...form,
        config: config,
        category: form.category || null,
        department_id: form.department_id ? parseInt(form.department_id) : null,
        branch_id: form.branch_id ? parseInt(form.branch_id) : null,
        display_order: parseInt(form.display_order.toString()) || 0,
      };

      if (editingId) {
        // ویرایش
        await apiPatch(`/api/custom-fields/${editingId}`, fieldData);
        setSuccess("فیلد با موفقیت به‌روزرسانی شد");
      } else {
        // ایجاد
        await apiPost("/api/custom-fields", fieldData);
        setSuccess("فیلد با موفقیت ایجاد شد");
      }

      cancelEdit();
      loadData();
    } catch (e: any) {
      setError(e?.message || "خطا در ذخیره فیلد");
    }
  };

  // حذف فیلد
  const deleteField = async (id: number) => {
    if (!confirm("آیا از حذف این فیلد اطمینان دارید؟")) {
      return;
    }

    try {
      await apiDelete(`/api/custom-fields/${id}`);
      setSuccess("فیلد با موفقیت حذف شد");
      loadData();
    } catch (e: any) {
      setError(e?.message || "خطا در حذف فیلد");
    }
  };

  // افزودن گزینه به config
  const addConfigOption = () => {
    setConfigOptions([...configOptions, { value: "", label: "" }]);
  };

  // حذف گزینه از config
  const removeConfigOption = (index: number) => {
    setConfigOptions(configOptions.filter((_, i) => i !== index));
  };

  // به‌روزرسانی گزینه در config
  const updateConfigOption = (index: number, key: "value" | "label", value: string) => {
    const updated = [...configOptions];
    updated[index] = { ...updated[index], [key]: value };
    setConfigOptions(updated);
  };

  const titleRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLDivElement>(null);
  const fieldsListRef = useRef<HTMLDivElement>(null);

  // Animate on mount
  useEffect(() => {
    if (titleRef.current) {
      slideIn(titleRef.current, "right", { duration: 0.6, distance: 50 });
    }
  }, []);

  // Animate form when it appears
  useEffect(() => {
    if (showForm && formRef.current) {
      scaleIn(formRef.current, { from: 0.9, to: 1, duration: 0.5 });
    }
  }, [showForm]);

  // Animate fields list when data changes
  useEffect(() => {
    if (fields.length > 0 && fieldsListRef.current) {
      stagger(
        ".field-card",
        (el) => slideIn(el, "left", { duration: 0.4, distance: 30 }),
        { stagger: 0.08, delay: 0.2 }
      );
    }
  }, [fields.length]);

  return (
    <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
      <div ref={titleRef} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1>📋 مدیریت فیلدهای سفارشی</h1>
        <button
          onClick={startNew}
          style={{
            padding: "10px 20px",
            background: "var(--accent)",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "14px",
            fontWeight: "bold",
          }}
        >
          ➕ افزودن فیلد جدید
        </button>
      </div>

      {error && (
        <div style={{ padding: "12px", background: "#fee", color: "#c33", borderRadius: "6px", marginBottom: "20px" }}>
          ⚠️ {error}
        </div>
      )}

      {success && (
        <div style={{ padding: "12px", background: "#efe", color: "#3c3", borderRadius: "6px", marginBottom: "20px" }}>
          ✅ {success}
        </div>
      )}

      {/* فیلترها */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", flexWrap: "wrap" }}>
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          style={{ padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
        >
          <option value="">همه دسته‌بندی‌ها</option>
          {CATEGORIES.slice(1).map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{ padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
        >
          <option value="">همه انواع</option>
          {FIELD_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>

        <select
          value={filterActive}
          onChange={(e) => setFilterActive(e.target.value)}
          style={{ padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
        >
          <option value="">همه وضعیت‌ها</option>
          <option value="true">فعال</option>
          <option value="false">غیرفعال</option>
        </select>
      </div>

      {/* فرم ایجاد/ویرایش */}
      {showForm && (
        <div
          ref={formRef}
          style={{
            background: "var(--bg-secondary)",
            padding: "20px",
            borderRadius: "8px",
            marginBottom: "20px",
            border: "1px solid var(--border)",
          }}
        >
          <h2>{editingId ? "✏️ ویرایش فیلد" : "➕ افزودن فیلد جدید"}</h2>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "15px" }}>
            {/* نام فیلد (internal) */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                نام فیلد (Internal) <span style={{ color: "red" }}>*</span>
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="مثال: project_name"
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
                disabled={!!editingId}
              />
              <small style={{ color: "var(--fg-secondary)" }}>
                فقط حروف، اعداد، خط تیره و زیرخط (بدون فاصله)
              </small>
            </div>

            {/* برچسب فارسی */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                برچسب (فارسی) <span style={{ color: "red" }}>*</span>
              </label>
              <input
                type="text"
                value={form.label}
                onChange={(e) => setForm({ ...form, label: e.target.value })}
                placeholder="مثال: نام پروژه"
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              />
            </div>

            {/* برچسب انگلیسی */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                برچسب (انگلیسی)
              </label>
              <input
                type="text"
                value={form.label_en}
                onChange={(e) => setForm({ ...form, label_en: e.target.value })}
                placeholder="Example: Project Name"
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              />
            </div>

            {/* نوع فیلد */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                نوع فیلد <span style={{ color: "red" }}>*</span>
              </label>
              <select
                value={form.field_type}
                onChange={(e) => {
                  setForm({ ...form, field_type: e.target.value });
                  // پاک کردن config هنگام تغییر نوع
                  setConfigOptions([]);
                  setConfigMin("");
                  setConfigMax("");
                  setConfigStep("");
                }}
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              >
                {FIELD_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* دسته‌بندی */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                دسته‌بندی تیکت
              </label>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
              <small style={{ color: "var(--fg-secondary)" }}>خالی = همه دسته‌بندی‌ها</small>
            </div>

            {/* دپارتمان */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                دپارتمان
              </label>
              <select
                value={form.department_id}
                onChange={(e) => setForm({ ...form, department_id: e.target.value })}
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              >
                <option value="">همه دپارتمان‌ها</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>

            {/* شعبه */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                شعبه
              </label>
              <select
                value={form.branch_id}
                onChange={(e) => setForm({ ...form, branch_id: e.target.value })}
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              >
                <option value="">همه شعب</option>
                {branches.map((branch) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.name}
                  </option>
                ))}
              </select>
            </div>

            {/* ترتیب نمایش */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                ترتیب نمایش
              </label>
              <input
                type="number"
                value={form.display_order}
                onChange={(e) => setForm({ ...form, display_order: parseInt(e.target.value) || 0 })}
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              />
              <small style={{ color: "var(--fg-secondary)" }}>عدد کمتر = نمایش زودتر</small>
            </div>

            {/* توضیحات */}
            <div style={{ gridColumn: "1 / -1" }}>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                توضیحات
              </label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={3}
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              />
            </div>

            {/* Placeholder */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                Placeholder
              </label>
              <input
                type="text"
                value={form.placeholder}
                onChange={(e) => setForm({ ...form, placeholder: e.target.value })}
                placeholder="مثال: نام پروژه را وارد کنید"
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              />
            </div>

            {/* Help Text */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                متن راهنما
              </label>
              <input
                type="text"
                value={form.help_text}
                onChange={(e) => setForm({ ...form, help_text: e.target.value })}
                placeholder="مثال: نام کامل پروژه را وارد کنید"
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              />
            </div>

            {/* مقدار پیش‌فرض */}
            <div>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                مقدار پیش‌فرض
              </label>
              <input
                type="text"
                value={form.default_value}
                onChange={(e) => setForm({ ...form, default_value: e.target.value })}
                style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
              />
            </div>
          </div>

          {/* تنظیمات پیشرفته */}
          <div style={{ marginTop: "20px", padding: "15px", background: "var(--bg-primary)", borderRadius: "6px" }}>
            <h3 style={{ marginTop: 0 }}>⚙️ تنظیمات پیشرفته</h3>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={form.is_required}
                  onChange={(e) => setForm({ ...form, is_required: e.target.checked })}
                />
                <span>الزامی</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={form.is_visible_to_user}
                  onChange={(e) => setForm({ ...form, is_visible_to_user: e.target.checked })}
                />
                <span>قابل مشاهده برای کاربر</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={form.is_editable_by_user}
                  onChange={(e) => setForm({ ...form, is_editable_by_user: e.target.checked })}
                />
                <span>قابل ویرایش توسط کاربر</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                />
                <span>فعال</span>
              </label>
            </div>
          </div>

          {/* تنظیمات Config برای SELECT/MULTISELECT */}
          {(form.field_type === "select" || form.field_type === "multiselect") && (
            <div style={{ marginTop: "20px", padding: "15px", background: "var(--bg-primary)", borderRadius: "6px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                <h3 style={{ margin: 0 }}>📋 گزینه‌های انتخاب</h3>
                <button
                  type="button"
                  onClick={addConfigOption}
                  style={{
                    padding: "6px 12px",
                    background: "var(--accent)",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  ➕ افزودن گزینه
                </button>
              </div>

              {configOptions.map((option, index) => (
                <div
                  key={index}
                  style={{
                    display: "flex",
                    gap: "10px",
                    marginBottom: "10px",
                    alignItems: "center",
                  }}
                >
                  <input
                    type="text"
                    value={option.value}
                    onChange={(e) => updateConfigOption(index, "value", e.target.value)}
                    placeholder="مقدار (value)"
                    style={{ flex: 1, padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
                  />
                  <input
                    type="text"
                    value={option.label}
                    onChange={(e) => updateConfigOption(index, "label", e.target.value)}
                    placeholder="برچسب (label)"
                    style={{ flex: 1, padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
                  />
                  <button
                    type="button"
                    onClick={() => removeConfigOption(index)}
                    style={{
                      padding: "8px 12px",
                      background: "#dc3545",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                    }}
                  >
                    🗑️
                  </button>
                </div>
              ))}

              {configOptions.length === 0 && (
                <p style={{ color: "var(--fg-secondary)", fontStyle: "italic" }}>
                  هیچ گزینه‌ای تعریف نشده است. لطفاً حداقل یک گزینه اضافه کنید.
                </p>
              )}
            </div>
          )}

          {/* تنظیمات Config برای NUMBER */}
          {form.field_type === "number" && (
            <div style={{ marginTop: "20px", padding: "15px", background: "var(--bg-primary)", borderRadius: "6px" }}>
              <h3 style={{ marginTop: 0 }}>🔢 محدودیت‌های عددی</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
                <div>
                  <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                    حداقل
                  </label>
                  <input
                    type="number"
                    value={configMin}
                    onChange={(e) => setConfigMin(e.target.value)}
                    placeholder="حداقل"
                    style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                    حداکثر
                  </label>
                  <input
                    type="number"
                    value={configMax}
                    onChange={(e) => setConfigMax(e.target.value)}
                    placeholder="حداکثر"
                    style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                    Step
                  </label>
                  <input
                    type="number"
                    value={configStep}
                    onChange={(e) => setConfigStep(e.target.value)}
                    placeholder="Step"
                    style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border)" }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* دکمه‌های عملیات */}
          <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
            <button
              onClick={saveField}
              style={{
                padding: "10px 20px",
                background: "var(--accent)",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "bold",
              }}
            >
              💾 ذخیره
            </button>
            <button
              onClick={cancelEdit}
              style={{
                padding: "10px 20px",
                background: "var(--bg-secondary)",
                color: "var(--fg-primary)",
                border: "1px solid var(--border)",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
              }}
            >
              ❌ لغو
            </button>
          </div>
        </div>
      )}

      {/* لیست فیلدها */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "40px" }}>در حال بارگذاری...</div>
      ) : fields.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px", color: "var(--fg-secondary)" }}>
          هیچ فیلد سفارشی تعریف نشده است.
        </div>
      ) : (
        <div ref={fieldsListRef} style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", background: "var(--bg-primary)" }}>
            <thead>
              <tr style={{ background: "var(--bg-secondary)", borderBottom: "2px solid var(--border)" }}>
                <th style={{ padding: "12px", textAlign: "right" }}>نام</th>
                <th style={{ padding: "12px", textAlign: "right" }}>برچسب</th>
                <th style={{ padding: "12px", textAlign: "right" }}>نوع</th>
                <th style={{ padding: "12px", textAlign: "right" }}>دسته‌بندی</th>
                <th style={{ padding: "12px", textAlign: "right" }}>وضعیت</th>
                <th style={{ padding: "12px", textAlign: "right" }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {fields.map((field) => (
                <tr key={field.id} className="field-card" style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "12px" }}>
                    <code style={{ background: "var(--bg-secondary)", padding: "4px 8px", borderRadius: "4px" }}>
                      {field.name}
                    </code>
                  </td>
                  <td style={{ padding: "12px", fontWeight: "500" }}>{field.label}</td>
                  <td style={{ padding: "12px" }}>
                    {FIELD_TYPES.find((t) => t.value === field.field_type)?.label || field.field_type}
                  </td>
                  <td style={{ padding: "12px", color: "var(--fg-secondary)" }}>
                    {field.category
                      ? CATEGORIES.find((c) => c.value === field.category)?.label || field.category
                      : "همه"}
                  </td>
                  <td style={{ padding: "12px" }}>
                    <span
                      style={{
                        padding: "4px 8px",
                        borderRadius: "4px",
                        fontSize: "12px",
                        background: field.is_active ? "#d4edda" : "#f8d7da",
                        color: field.is_active ? "#155724" : "#721c24",
                      }}
                    >
                      {field.is_active ? "✅ فعال" : "❌ غیرفعال"}
                    </span>
                  </td>
                  <td style={{ padding: "12px" }}>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <button
                        onClick={() => startEdit(field)}
                        style={{
                          padding: "6px 12px",
                          background: "var(--accent)",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "12px",
                        }}
                      >
                        ✏️ ویرایش
                      </button>
                      <button
                        onClick={() => deleteField(field.id)}
                        style={{
                          padding: "6px 12px",
                          background: "#dc3545",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "12px",
                        }}
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

