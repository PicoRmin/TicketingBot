import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiGet, isAuthenticated, getStoredProfile } from "../services/api";
import { OnboardingWizard } from "../components/OnboardingWizard";

type TicketStats = {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
  closed: number;
};

export default function UserDashboard() {
  const navigate = useNavigate();
  const [profile] = useState<any | null>(() => getStoredProfile());
  const [stats, setStats] = useState<TicketStats>({
    total: 0,
    pending: 0,
    in_progress: 0,
    resolved: 0,
    closed: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(() => {
    if (typeof window === "undefined") return false;
    try {
      const raw = localStorage.getItem("imehr_onboarding_state");
      if (raw) {
        const parsed = JSON.parse(raw);
        return !parsed.completed;
      }
    } catch {
      /* ignore */
    }
    return true;
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }
    
    // Check if user is regular user
    if (profile && !["user"].includes(profile.role)) {
      // Redirect admins to admin dashboard
      navigate("/");
      return;
    }
    
    loadStats();
  }, [navigate, profile]);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get tickets for each status (API automatically filters by user for regular users)
      const [all, pending, inProgress, resolved, closed] = await Promise.all([
        apiGet("/api/tickets?page_size=1") as Promise<{ total: number }>,
        apiGet("/api/tickets?status=pending&page_size=1") as Promise<{ total: number }>,
        apiGet("/api/tickets?status=in_progress&page_size=1") as Promise<{ total: number }>,
        apiGet("/api/tickets?status=resolved&page_size=1") as Promise<{ total: number }>,
        apiGet("/api/tickets?status=closed&page_size=1") as Promise<{ total: number }>,
      ]);

      setStats({
        total: all.total || 0,
        pending: pending.total || 0,
        in_progress: inProgress.total || 0,
        resolved: resolved.total || 0,
        closed: closed.total || 0,
      });
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت آمار");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <div className="loading" style={{ margin: "0 auto" }}></div>
        <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <h1 className="page-title">📊 داشبورد کاربری</h1>

      {error && <div className="alert error fade-in">{error}</div>}

      {showOnboarding && (
        <OnboardingWizard
          onComplete={() => {
            setShowOnboarding(false);
          }}
        />
      )}

      {!showOnboarding && (
        <div className="onboarding-card slim">
          <div>
            <strong>🎯 اطلاعات تکمیلی شما آماده است</strong>
            <p style={{ margin: 0, color: "var(--fg-secondary)" }}>برای به‌روزرسانی یا تغییر اهداف می‌توانید دوباره فرم را باز کنید.</p>
          </div>
          <button className="secondary" onClick={() => setShowOnboarding(true)}>ویرایش اطلاعات</button>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">عملیات سریع</h2>
        </div>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
          <Link to="/user-portal" style={{ textDecoration: "none" }}>
            <button style={{ padding: "16px 32px", fontSize: 16 }}>
              ➕ ایجاد تیکت جدید
            </button>
          </Link>
          <Link to="/user-portal" style={{ textDecoration: "none" }}>
            <button className="secondary" style={{ padding: "16px 32px", fontSize: 16 }}>
              🎫 مشاهده تیکت‌های من
            </button>
          </Link>
        </div>
      </div>

      {/* Statistics */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">آمار تیکت‌های من</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
          <div className="stat-card" style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}>
            <div className="stat-label">کل تیکت‌ها</div>
            <div className="stat-value">{stats.total}</div>
          </div>
          <div className="stat-card" style={{ background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)" }}>
            <div className="stat-label">در انتظار</div>
            <div className="stat-value">{stats.pending}</div>
          </div>
          <div className="stat-card" style={{ background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)" }}>
            <div className="stat-label">در حال انجام</div>
            <div className="stat-value">{stats.in_progress}</div>
          </div>
          <div className="stat-card" style={{ background: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)" }}>
            <div className="stat-label">حل شده</div>
            <div className="stat-value">{stats.resolved}</div>
          </div>
          <div className="stat-card" style={{ background: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)" }}>
            <div className="stat-label">بسته شده</div>
            <div className="stat-value">{stats.closed}</div>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="card" style={{ marginTop: 24 }}>
        <div className="card-header">
          <h2 className="card-title">لینک‌های سریع</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16 }}>
          <Link to="/user-portal?status=pending" style={{ textDecoration: "none" }}>
            <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", cursor: "pointer", transition: "transform 0.2s" }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>⏳</div>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>تیکت‌های در انتظار</div>
              <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
                {stats.pending} تیکت
              </div>
            </div>
          </Link>
          <Link to="/user-portal?status=in_progress" style={{ textDecoration: "none" }}>
            <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", cursor: "pointer", transition: "transform 0.2s" }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>🔄</div>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>تیکت‌های در حال انجام</div>
              <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
                {stats.in_progress} تیکت
              </div>
            </div>
          </Link>
          <Link to="/user-portal?status=resolved" style={{ textDecoration: "none" }}>
            <div style={{ padding: 20, background: "var(--bg-secondary)", borderRadius: "var(--radius)", cursor: "pointer", transition: "transform 0.2s" }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>✅</div>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>تیکت‌های حل شده</div>
              <div style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
                {stats.resolved} تیکت
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}

