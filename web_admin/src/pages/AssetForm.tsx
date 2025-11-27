import { useEffect, useState, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiGet, apiPost, apiPut } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import { fadeIn, scaleIn } from "../lib/gsap";

type BranchSummary = { id: number; name: string; code: string };
type UserSummary = { id: number; full_name: string; username: string };

type AssetFormData = {
  name: string;
  asset_type: string;
  model?: string;
  serial_number?: string;
  manufacturer?: string;
  purchase_date?: string;
  purchase_price?: string;
  warranty_expiry?: string;
  status: string;
  location?: string;
  branch_id?: string;
  assigned_to_user_id?: string;
  notes?: string;
};

const ASSET_TYPES = [
  { value: "pc", label: "💻 کامپیوتر", icon: "💻" },
  { value: "laptop", label: "📱 لپ‌تاپ", icon: "📱" },
  { value: "server", label: "🖥️ سرور", icon: "🖥️" },
  { value: "router", label: "📡 روتر", icon: "📡" },
  { value: "switch", label: "🔌 سوئیچ", icon: "🔌" },
  { value: "printer", label: "🖨️ پرینتر", icon: "🖨️" },
  { value: "monitor", label: "🖥️ مانیتور", icon: "🖥️" },
  { value: "tablet", label: "📱 تبلت", icon: "📱" },
  { value: "phone", label: "📞 تلفن", icon: "📞" },
  { value: "other", label: "📦 سایر", icon: "📦" },
];

const STATUS_OPTIONS = [
  { value: "available", label: "✅ در دسترس" },
  { value: "assigned", label: "👤 تخصیص داده شده" },
  { value: "maintenance", label: "🔧 در حال تعمیر" },
  { value: "retired", label: "🗑️ بازنشسته" },
  { value: "lost", label: "❌ گم شده" },
];

const getAssetTypeLabel = (type: string) => {
  return ASSET_TYPES.find((t) => t.value === type)?.label || type;
};

const getAssetTypeIcon = (type: string) => {
  return ASSET_TYPES.find((t) => t.value === type)?.icon || "📦";
};

const getStatusLabel = (status: string) => {
  return STATUS_OPTIONS.find((s) => s.value === status)?.label || status;
};

export default function AssetForm() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = !!id;
  
  // Multi-step form state
  const [currentStep, setCurrentStep] = useState(1);
  const [formDirection, setFormDirection] = useState<"forward" | "backward">("forward");
  const totalSteps = 4; // Step 1: Basic Info, Step 2: Details, Step 3: Assignment, Step 4: Review
  
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const [branches, setBranches] = useState<BranchSummary[]>([]);
  const [users, setUsers] = useState<UserSummary[]>([]);
  
  const [form, setForm] = useState<AssetFormData>({
    name: "",
    asset_type: "pc",
    model: "",
    serial_number: "",
    manufacturer: "",
    purchase_date: "",
    purchase_price: "",
    warranty_expiry: "",
    status: "available",
    location: "",
    branch_id: "",
    assigned_to_user_id: "",
    notes: "",
  });
  
  const formCardRef = useRef<HTMLDivElement>(null);
  const successRef = useRef<HTMLDivElement>(null);

  // Load branches and users
  useEffect(() => {
    const loadData = async () => {
      try {
        const [branchesData, usersData] = await Promise.all([
          apiGet("/api/branches?is_active=true") as Promise<BranchSummary[]>,
          apiGet("/api/users?is_active=true") as Promise<UserSummary[]>,
        ]);
        setBranches(branchesData);
        setUsers(usersData);
      } catch (err) {
        console.error("Error loading data:", err);
      }
    };
    loadData();
  }, []);

  // Load asset data if editing
  useEffect(() => {
    if (isEditMode && id) {
      setLoading(true);
      (apiGet(`/api/assets/${id}`) as Promise<Partial<AssetFormData> & { purchase_date?: string; warranty_expiry?: string; purchase_price?: number; branch_id?: number; assigned_to_user_id?: number }>)
        .then((asset) => {
          setForm({
            name: asset.name || "",
            asset_type: asset.asset_type || "pc",
            model: asset.model || "",
            serial_number: asset.serial_number || "",
            manufacturer: asset.manufacturer || "",
            purchase_date: asset.purchase_date ? asset.purchase_date.split("T")[0] : "",
            purchase_price: asset.purchase_price ? String(asset.purchase_price) : "",
            warranty_expiry: asset.warranty_expiry ? asset.warranty_expiry.split("T")[0] : "",
            status: asset.status || "available",
            location: asset.location || "",
            branch_id: asset.branch_id ? String(asset.branch_id) : "",
            assigned_to_user_id: asset.assigned_to_user_id ? String(asset.assigned_to_user_id) : "",
            notes: asset.notes || "",
          });
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : "خطا در دریافت اطلاعات دارایی");
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [isEditMode, id]);

  // Animate form on mount
  useEffect(() => {
    if (formCardRef.current) {
      scaleIn(formCardRef.current, { from: 0.9, to: 1, duration: 0.5 });
    }
  }, []);

  // Animate success message
  useEffect(() => {
    if (success && successRef.current) {
      fadeIn(successRef.current, { duration: 0.6, delay: 0.1 });
    }
  }, [success]);

  // Validation for each step
  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        if (!form.name || form.name.length < 3) {
          setError("نام دارایی باید حداقل 3 کاراکتر باشد");
          return false;
        }
        if (!form.asset_type) {
          setError("لطفاً نوع دارایی را انتخاب کنید");
          return false;
        }
        return true;
      case 2:
        // Step 2 is optional details, no validation needed
        return true;
      case 3:
        // Step 3 is optional assignment, no validation needed
        return true;
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setError(null);
      setFormDirection("forward");
      setCurrentStep((prev) => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setError(null);
    setFormDirection("backward");
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(1)) return;

    setSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      const payload: Record<string, unknown> = {
        name: form.name,
        asset_type: form.asset_type,
        status: form.status,
      };

      if (form.model) payload.model = form.model;
      if (form.serial_number) payload.serial_number = form.serial_number;
      if (form.manufacturer) payload.manufacturer = form.manufacturer;
      if (form.purchase_date) payload.purchase_date = form.purchase_date;
      if (form.purchase_price) payload.purchase_price = parseFloat(form.purchase_price) || 0;
      if (form.warranty_expiry) payload.warranty_expiry = form.warranty_expiry;
      if (form.location) payload.location = form.location;
      if (form.branch_id) payload.branch_id = parseInt(form.branch_id, 10);
      if (form.assigned_to_user_id) payload.assigned_to_user_id = parseInt(form.assigned_to_user_id, 10);
      if (form.notes) payload.notes = form.notes;

      if (isEditMode && id) {
        await apiPut(`/api/assets/${id}`, payload);
        setSuccess(true);
        setTimeout(() => {
          navigate("/assets");
        }, 2000);
      } else {
        const asset = await apiPost("/api/assets", payload) as { id: number };
        setSuccess(true);
        setTimeout(() => {
          navigate(`/assets/${asset.id}`);
        }, 2000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در ذخیره دارایی");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="fade-in" style={{ textAlign: "center", padding: 40 }}>
        <div className="loading" style={{ margin: "0 auto" }}></div>
        <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
      </div>
    );
  }

  if (success) {
    return (
      <div className="fade-in">
        <div ref={successRef} className="card" style={{ maxWidth: 600, margin: "40px auto", textAlign: "center", padding: 40 }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            style={{ fontSize: 64, marginBottom: 20 }}
          >
            ✅
          </motion.div>
          <h2 style={{ marginBottom: 16, fontSize: 24, fontWeight: 600 }}>
            {isEditMode ? "دارایی با موفقیت به‌روزرسانی شد" : "دارایی با موفقیت ثبت شد"}
          </h2>
          <p style={{ color: "var(--fg-secondary)", marginBottom: 24 }}>
            {isEditMode ? "در حال انتقال به لیست دارایی‌ها..." : "در حال انتقال به صفحه جزئیات..."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 className="page-title">{isEditMode ? "✏️ ویرایش دارایی" : "➕ ثبت دارایی جدید"}</h1>
          <p style={{ marginTop: 8, color: "var(--fg-secondary)", fontSize: 14 }}>
            {isEditMode ? "ویرایش اطلاعات دارایی" : "ثبت دارایی جدید در سیستم"}
          </p>
        </div>
        <button className="secondary" onClick={() => navigate("/assets")}>
          ❌ انصراف
        </button>
      </div>

      <div ref={formCardRef} className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">{isEditMode ? "ویرایش دارایی" : "ثبت دارایی جدید"}</h2>
        </div>

        {/* Progress Indicator */}
        <div className="multi-step-progress" style={{ marginBottom: 24, padding: "0 20px" }}>
          <div className="progress-steps">
            {[1, 2, 3, 4].map((step, idx) => {
              const isActive = step === currentStep;
              const isCompleted = step < currentStep;
              return (
                <div key={step} className="progress-step-container">
                  <div
                    className={`progress-step ${isActive ? "active" : ""} ${isCompleted ? "completed" : ""}`}
                    onClick={() => {
                      if (step < currentStep) {
                        setFormDirection("backward");
                        setCurrentStep(step);
                      }
                    }}
                    style={{ cursor: step < currentStep ? "pointer" : "default" }}
                  >
                    <div className="progress-step-number">{isCompleted ? "✓" : step}</div>
                    <div className="progress-step-label">
                      {step === 1 && "اطلاعات پایه"}
                      {step === 2 && "جزئیات"}
                      {step === 3 && "تخصیص"}
                      {step === 4 && "بازبینی"}
                    </div>
                  </div>
                  {idx < 3 && <div className={`progress-line ${isCompleted ? "completed" : ""}`} />}
                </div>
              );
            })}
          </div>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="alert error fade-in"
          >
            <strong>خطا:</strong> {error}
          </motion.div>
        )}

        <AnimatePresence mode="wait" custom={formDirection}>
          <motion.div
            key={currentStep}
            custom={formDirection}
            initial={{ opacity: 0, x: formDirection === "forward" ? 50 : -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: formDirection === "forward" ? -50 : 50 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            {/* Step 1: Basic Information */}
            {currentStep === 1 && (
              <div className="step-content">
                <h3 style={{ marginBottom: 20, fontSize: 18, fontWeight: 600 }}>📝 اطلاعات پایه</h3>
                <label>
                  نام دارایی: *
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => {
                      setForm({ ...form, name: e.target.value });
                      setError(null);
                    }}
                    placeholder="مثال: کامپیوتر اداری شماره 1"
                    required
                    minLength={3}
                  />
                </label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <label>
                    نوع دارایی: *
                    <select
                      value={form.asset_type}
                      onChange={(e) => {
                        setForm({ ...form, asset_type: e.target.value });
                        setError(null);
                      }}
                      required
                    >
                      {ASSET_TYPES.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    وضعیت: *
                    <select
                      value={form.status}
                      onChange={(e) => {
                        setForm({ ...form, status: e.target.value });
                        setError(null);
                      }}
                      required
                    >
                      {STATUS_OPTIONS.map((s) => (
                        <option key={s.value} value={s.value}>
                          {s.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <label>
                  مکان/موقعیت:
                  <input
                    type="text"
                    value={form.location}
                    onChange={(e) => setForm({ ...form, location: e.target.value })}
                    placeholder="مثال: اتاق 101، طبقه دوم"
                  />
                </label>
              </div>
            )}

            {/* Step 2: Details */}
            {currentStep === 2 && (
              <div className="step-content">
                <h3 style={{ marginBottom: 20, fontSize: 18, fontWeight: 600 }}>🔧 جزئیات فنی</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <label>
                    مدل:
                    <input
                      type="text"
                      value={form.model}
                      onChange={(e) => setForm({ ...form, model: e.target.value })}
                      placeholder="مثال: Dell OptiPlex 7090"
                    />
                  </label>
                  <label>
                    شماره سریال:
                    <input
                      type="text"
                      value={form.serial_number}
                      onChange={(e) => setForm({ ...form, serial_number: e.target.value })}
                      placeholder="مثال: SN123456789"
                    />
                  </label>
                </div>
                <label>
                  سازنده/برند:
                  <input
                    type="text"
                    value={form.manufacturer}
                    onChange={(e) => setForm({ ...form, manufacturer: e.target.value })}
                    placeholder="مثال: Dell, HP, Lenovo"
                  />
                </label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <label>
                    تاریخ خرید:
                    <input
                      type="date"
                      value={form.purchase_date}
                      onChange={(e) => setForm({ ...form, purchase_date: e.target.value })}
                    />
                  </label>
                  <label>
                    قیمت خرید (ریال):
                    <input
                      type="number"
                      value={form.purchase_price}
                      onChange={(e) => setForm({ ...form, purchase_price: e.target.value })}
                      placeholder="0"
                      min="0"
                    />
                  </label>
                </div>
                <label>
                  تاریخ پایان گارانتی:
                  <input
                    type="date"
                    value={form.warranty_expiry}
                    onChange={(e) => setForm({ ...form, warranty_expiry: e.target.value })}
                  />
                </label>
              </div>
            )}

            {/* Step 3: Assignment */}
            {currentStep === 3 && (
              <div className="step-content">
                <h3 style={{ marginBottom: 20, fontSize: 18, fontWeight: 600 }}>👤 تخصیص و موقعیت</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  <label>
                    شعبه:
                    <select
                      value={form.branch_id}
                      onChange={(e) => setForm({ ...form, branch_id: e.target.value })}
                    >
                      <option value="">انتخاب نشده</option>
                      {branches.map((b) => (
                        <option key={b.id} value={String(b.id)}>
                          {b.name} ({b.code})
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    تخصیص به کاربر:
                    <select
                      value={form.assigned_to_user_id}
                      onChange={(e) => setForm({ ...form, assigned_to_user_id: e.target.value })}
                    >
                      <option value="">تخصیص داده نشده</option>
                      {users.map((u) => (
                        <option key={u.id} value={String(u.id)}>
                          {u.full_name} ({u.username})
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <label>
                  یادداشت‌ها:
                  <textarea
                    value={form.notes}
                    onChange={(e) => setForm({ ...form, notes: e.target.value })}
                    placeholder="یادداشت‌های اضافی درباره دارایی..."
                    rows={4}
                  />
                </label>
              </div>
            )}

            {/* Step 4: Review */}
            {currentStep === 4 && (
              <div className="step-content">
                <h3 style={{ marginBottom: 20, fontSize: 18, fontWeight: 600 }}>👁️ بازبینی و تایید</h3>
                <div className="preview-card" style={{
                  background: "var(--bg-secondary)",
                  padding: 20,
                  borderRadius: "var(--radius)",
                  marginBottom: 20
                }}>
                  <div style={{ marginBottom: 16 }}>
                    <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>نام:</strong>
                    <p style={{ marginTop: 4, fontSize: 16 }}>{form.name}</p>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
                    <div>
                      <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>نوع:</strong>
                      <p style={{ marginTop: 4 }}>
                        {getAssetTypeIcon(form.asset_type)} {getAssetTypeLabel(form.asset_type)}
                      </p>
                    </div>
                    <div>
                      <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>وضعیت:</strong>
                      <p style={{ marginTop: 4 }}>{getStatusLabel(form.status)}</p>
                    </div>
                  </div>
                  {(form.model || form.serial_number || form.manufacturer) && (
                    <div style={{ marginBottom: 16 }}>
                      <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>جزئیات فنی:</strong>
                      <div style={{ marginTop: 8, display: "grid", gap: 4 }}>
                        {form.model && <div>مدل: {form.model}</div>}
                        {form.serial_number && <div>سریال: {form.serial_number}</div>}
                        {form.manufacturer && <div>سازنده: {form.manufacturer}</div>}
                      </div>
                    </div>
                  )}
                  {(form.purchase_date || form.purchase_price || form.warranty_expiry) && (
                    <div style={{ marginBottom: 16 }}>
                      <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>اطلاعات خرید:</strong>
                      <div style={{ marginTop: 8, display: "grid", gap: 4 }}>
                        {form.purchase_date && <div>تاریخ خرید: {new Date(form.purchase_date).toLocaleDateString("fa-IR")}</div>}
                        {form.purchase_price && <div>قیمت: {parseInt(form.purchase_price).toLocaleString("fa-IR")} ریال</div>}
                        {form.warranty_expiry && <div>پایان گارانتی: {new Date(form.warranty_expiry).toLocaleDateString("fa-IR")}</div>}
                      </div>
                    </div>
                  )}
                  {(form.branch_id || form.assigned_to_user_id) && (
                    <div style={{ marginBottom: 16 }}>
                      <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>تخصیص:</strong>
                      <div style={{ marginTop: 8, display: "grid", gap: 4 }}>
                        {form.branch_id && (
                          <div>شعبه: {branches.find((b) => String(b.id) === form.branch_id)?.name || "-"}</div>
                        )}
                        {form.assigned_to_user_id && (
                          <div>کاربر: {users.find((u) => String(u.id) === form.assigned_to_user_id)?.full_name || "-"}</div>
                        )}
                      </div>
                    </div>
                  )}
                  {form.location && (
                    <div style={{ marginBottom: 16 }}>
                      <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>مکان:</strong>
                      <p style={{ marginTop: 4 }}>{form.location}</p>
                    </div>
                  )}
                  {form.notes && (
                    <div>
                      <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>یادداشت‌ها:</strong>
                      <p style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>{form.notes}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        <div style={{ display: "flex", gap: 12, marginTop: 24, justifyContent: "space-between" }}>
          <div style={{ display: "flex", gap: 12 }}>
            {currentStep > 1 && (
              <button type="button" className="secondary" onClick={handlePrevious} disabled={submitting}>
                ⬅️ قبلی
              </button>
            )}
          </div>
          <div style={{ display: "flex", gap: 12 }}>
            {currentStep < totalSteps ? (
              <button type="button" onClick={handleNext} disabled={submitting}>
                بعدی ➡️
              </button>
            ) : (
              <button type="button" onClick={handleSubmit} disabled={submitting}>
                {submitting ? "⏳ در حال ذخیره..." : isEditMode ? "💾 به‌روزرسانی" : "💾 ثبت دارایی"}
              </button>
            )}
            <button
              type="button"
              className="secondary"
              onClick={() => navigate("/assets")}
              disabled={submitting}
            >
              انصراف
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

