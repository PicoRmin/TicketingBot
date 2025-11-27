import { useEffect, useState, useRef, useCallback } from "react";
import { apiGet, apiPut, isAuthenticated, fetchProfile, getStoredProfile } from "../services/api";
import type { AuthProfile } from "../services/api";
import { useNavigate } from "react-router-dom";
import { fadeIn, slideIn } from "../lib/gsap";

type FileSettings = {
  max_images_per_ticket: number;
  max_documents_per_ticket: number;
  max_file_size_mb: number;
  allowed_image_types: string[];
  allowed_document_types: string[];
};

const DEFAULT_IMAGE_TYPES = [
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp"
];

const DEFAULT_DOCUMENT_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain"
];

export default function Settings() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [settings, setSettings] = useState<FileSettings>({
    max_images_per_ticket: 10,
    max_documents_per_ticket: 5,
    max_file_size_mb: 10,
    allowed_image_types: DEFAULT_IMAGE_TYPES,
    allowed_document_types: DEFAULT_DOCUMENT_TYPES,
  });
  const titleRef = useRef<HTMLHeadingElement>(null);
  const formCardRef = useRef<HTMLDivElement>(null);
  const userCardRef = useRef<HTMLDivElement>(null);

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiGet("/api/settings/file") as FileSettings;
      setSettings(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در دریافت تنظیمات");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const checkAuthAndLoad = async () => {
      if (!isAuthenticated()) {
        navigate("/login");
        return;
      }
      let profile: AuthProfile | null = getStoredProfile();
      if (!profile) {
        try {
          profile = await fetchProfile();
        } catch (e) {
          console.error("Failed to fetch profile:", e);
          navigate("/login");
          return;
        }
      }
      if (!profile || profile.role !== "central_admin") {
        navigate("/");
        return;
      }
      loadSettings();
    };
    checkAuthAndLoad();
  }, [navigate, loadSettings]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await apiPut("/api/settings/file", settings);
      setSuccess("تنظیمات با موفقیت ذخیره شد");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در ذخیره تنظیمات");
    } finally {
      setSaving(false);
    }
  };

  const handleImageTypeToggle = (type: string) => {
    setSettings((prev) => ({
      ...prev,
      allowed_image_types: prev.allowed_image_types.includes(type)
        ? prev.allowed_image_types.filter((t) => t !== type)
        : [...prev.allowed_image_types, type],
    }));
  };

  const handleDocumentTypeToggle = (type: string) => {
    setSettings((prev) => ({
      ...prev,
      allowed_document_types: prev.allowed_document_types.includes(type)
        ? prev.allowed_document_types.filter((t) => t !== type)
        : [...prev.allowed_document_types, type],
    }));
  };

  // Animate on mount
  useEffect(() => {
    if (titleRef.current) {
      slideIn(titleRef.current, "right", { duration: 0.6, distance: 50 });
    }
    if (formCardRef.current) {
      fadeIn(formCardRef.current, { duration: 0.7, delay: 0.2 });
    }
    if (userCardRef.current) {
      fadeIn(userCardRef.current, { duration: 0.7, delay: 0.4 });
    }
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <div className="loading" style={{ margin: "0 auto" }}></div>
        <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری تنظیمات...</p>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <h1 ref={titleRef} style={{ marginBottom: 24, fontSize: 32, fontWeight: 700 }}>⚙️ تنظیمات سیستم</h1>

      {error && (
        <div className="alert error fade-in">
          <strong>خطا:</strong> {error}
        </div>
      )}

      {success && (
        <div className="alert success fade-in">
          <strong>موفق:</strong> {success}
        </div>
      )}

      <form onSubmit={handleSave}>
        <div ref={formCardRef} className="card">
          <div className="card-header">
            <h2 className="card-title">📎 تنظیمات فایل</h2>
          </div>

          <div style={{ display: "grid", gap: 20 }}>
            {/* Max Images */}
            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                حداکثر تعداد عکس در هر تیکت:
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={settings.max_images_per_ticket}
                onChange={(e) =>
                  setSettings({ ...settings, max_images_per_ticket: parseInt(e.target.value) || 1 })
                }
                required
              />
              <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                کاربران می‌توانند حداکثر {settings.max_images_per_ticket} عکس در هر تیکت آپلود کنند
              </div>
            </div>

            {/* Max Documents */}
            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                حداکثر تعداد فایل متنی در هر تیکت:
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={settings.max_documents_per_ticket}
                onChange={(e) =>
                  setSettings({ ...settings, max_documents_per_ticket: parseInt(e.target.value) || 1 })
                }
                required
              />
              <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                کاربران می‌توانند حداکثر {settings.max_documents_per_ticket} فایل متنی در هر تیکت آپلود کنند
              </div>
            </div>

            {/* Max File Size */}
            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                حداکثر اندازه فایل (مگابایت):
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={settings.max_file_size_mb}
                onChange={(e) =>
                  setSettings({ ...settings, max_file_size_mb: parseInt(e.target.value) || 1 })
                }
                required
              />
              <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginTop: 4 }}>
                حداکثر اندازه هر فایل: {settings.max_file_size_mb} مگابایت
              </div>
            </div>

            {/* Allowed Image Types */}
            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                انواع فایل تصویری مجاز:
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 8 }}>
                {DEFAULT_IMAGE_TYPES.map((type) => (
                  <label
                    key={type}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: 8,
                      background: settings.allowed_image_types.includes(type)
                        ? "var(--bg-secondary)"
                        : "var(--bg)",
                      border: "1px solid var(--border)",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={settings.allowed_image_types.includes(type)}
                      onChange={() => handleImageTypeToggle(type)}
                    />
                    <span style={{ fontSize: 13 }}>{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Allowed Document Types */}
            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                انواع فایل متنی مجاز:
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 8 }}>
                {DEFAULT_DOCUMENT_TYPES.map((type) => (
                  <label
                    key={type}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: 8,
                      background: settings.allowed_document_types.includes(type)
                        ? "var(--bg-secondary)"
                        : "var(--bg)",
                      border: "1px solid var(--border)",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={settings.allowed_document_types.includes(type)}
                      onChange={() => handleDocumentTypeToggle(type)}
                    />
                    <span style={{ fontSize: 13 }}>{type}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div style={{ marginTop: 24, display: "flex", gap: 12, justifyContent: "flex-end" }}>
            <button type="submit" disabled={saving} className="success">
              {saving ? "⏳ در حال ذخیره..." : "💾 ذخیره تنظیمات"}
            </button>
          </div>
        </div>
      </form>

      <div ref={userCardRef} className="card" style={{ marginTop: 24 }}>
        <div className="card-header">
          <h2 className="card-title">👥 دسترسی‌های کاربران</h2>
        </div>
        <div style={{ padding: 20 }}>
          <p style={{ marginBottom: 16, color: "var(--fg-secondary)" }}>
            دسترسی‌های کاربران بر اساس نقش آن‌ها تعیین می‌شود. برای تغییر نقش کاربران، از صفحه{" "}
            <a href="/users" style={{ color: "var(--primary)", textDecoration: "underline" }}>
              مدیریت کاربران
            </a>{" "}
            استفاده کنید.
          </p>
          
          <div style={{ display: "grid", gap: 16, marginTop: 20 }}>
            <div style={{ padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 16, fontWeight: 600 }}>👑 مدیر ارشد (Central Admin)</h3>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--fg-secondary)", fontSize: 14 }}>
                <li>دسترسی کامل به تمام بخش‌ها</li>
                <li>مدیریت کاربران و شعب</li>
                <li>تنظیمات سیستم</li>
                <li>مدیریت زیرساخت شعب</li>
                <li>مشاهده و تغییر وضعیت تیکت‌ها</li>
              </ul>
            </div>

            <div style={{ padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 16, fontWeight: 600 }}>🛡️ مدیر سیستم (Admin)</h3>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--fg-secondary)", fontSize: 14 }}>
                <li>مدیریت کاربران و تیکت‌ها</li>
                <li>مشاهده گزارش‌ها</li>
                <li>تغییر وضعیت تیکت‌ها</li>
              </ul>
            </div>

            <div style={{ padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 16, fontWeight: 600 }}>🏢 مسئول شعبه (Branch Admin)</h3>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--fg-secondary)", fontSize: 14 }}>
                <li>مدیریت تیکت‌های شعبه خود</li>
                <li>تغییر وضعیت تیکت‌های شعبه خود</li>
              </ul>
            </div>

            <div style={{ padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 16, fontWeight: 600 }}>💻 کارشناس IT (IT Specialist)</h3>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--fg-secondary)", fontSize: 14 }}>
                <li>مشاهده تیکت‌ها</li>
                <li>تغییر وضعیت تیکت‌ها</li>
              </ul>
            </div>

            <div style={{ padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 16, fontWeight: 600 }}>📊 گزارش‌گیر (Report Manager)</h3>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--fg-secondary)", fontSize: 14 }}>
                <li>فقط مشاهده گزارش‌ها و داشبورد</li>
                <li>بدون دسترسی به مدیریت تیکت‌ها یا کاربران</li>
              </ul>
            </div>

            <div style={{ padding: 16, background: "var(--bg-secondary)", borderRadius: "var(--radius)" }}>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 16, fontWeight: 600 }}>👤 کاربر (User)</h3>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--fg-secondary)", fontSize: 14 }}>
                <li>ایجاد و مشاهده تیکت‌های خود</li>
                <li>پیگیری وضعیت تیکت‌های خود</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

