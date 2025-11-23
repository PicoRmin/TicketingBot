import { Link, Outlet, useNavigate } from "react-router-dom";
import { getToken, logout, getStoredProfile, fetchProfile, setProfile, clearProfile } from "./services/api";
import { useEffect, useState } from "react";
import logoUrl from "./assets/brand-logo.svg";

export default function App() {
  const navigate = useNavigate();
  const token = getToken();
  const [profile, setProfileState] = useState<any | null>(() => getStoredProfile());
  const [dark, setDark] = useState<boolean>(() => {
    return localStorage.getItem("imehr_dark") === "1";
  });

  useEffect(() => {
    if (!token) {
      setProfileState(null);
      clearProfile();
      navigate("/login");
      return;
    }

    const stored = getStoredProfile();
    if (stored) {
      setProfileState(stored);
        // Redirect regular users to user dashboard
        if (stored.role === "user" && window.location.pathname.startsWith("/") && 
            !window.location.pathname.startsWith("/user-portal") && 
            !window.location.pathname.startsWith("/user-tickets") &&
            !window.location.pathname.startsWith("/user-dashboard") &&
            window.location.pathname !== "/login") {
          navigate("/user-dashboard");
        }
      return;
    }

    fetchProfile()
      .then((p: any) => {
        setProfile(p);
        setProfileState(p);
        // Redirect regular users to user dashboard
        if (p?.role === "user" && window.location.pathname.startsWith("/") && 
            !window.location.pathname.startsWith("/user-portal") && 
            !window.location.pathname.startsWith("/user-tickets") &&
            !window.location.pathname.startsWith("/user-dashboard") &&
            window.location.pathname !== "/login") {
          navigate("/user-dashboard");
        }
      })
      .catch(() => {
        // ignore
      });
  }, [token, navigate]);

  useEffect(() => {
    const cls = document.documentElement.classList;
    if (dark) {
      cls.add("dark");
      localStorage.setItem("imehr_dark", "1");
    } else {
      cls.remove("dark");
      localStorage.removeItem("imehr_dark");
    }
  }, [dark]);

  const handleLogout = () => {
    logout();
    setProfileState(null);
    navigate("/login");
  };

  const isAdmin = profile && ["admin", "central_admin"].includes(profile.role);
  const isCentralAdmin = profile && profile.role === "central_admin";
  const isReportManager = profile && profile.role === "report_manager";
  const displayName = profile?.full_name || profile?.username;
  
  // Role labels
  const getRoleLabel = (role: string) => {
    const roleMap: Record<string, string> = {
      "central_admin": "👑 مدیر ارشد",
      "admin": "🛡️ مدیر سیستم",
      "branch_admin": "🏢 مسئول شعبه",
      "it_specialist": "💻 کارشناس IT",
      "report_manager": "📊 گزارش‌گیر",
      "user": "👤 کاربر"
    };
    return roleMap[role] || role;
  };
  
  const roleLabel = profile ? getRoleLabel(profile.role) : "";

  return (
    <div className="container">
      <header>
        <div className="header-left">
          <Link to="/" className="brand">
            <img src={logoUrl} alt="لوگوی ایرانمهر" />
            <div className="brand-text">
              <span className="brand-title">IranMehr</span>
              <span className="brand-subtitle">Help Desk Ticketing System</span>
            </div>
          </Link>
          <nav>
            {profile?.role === "user" ? (
              // Navigation for regular users
              <>
                <Link to="/user-dashboard">📊 داشبورد</Link>
                <Link to="/user-portal">🎫 تیکت‌های من</Link>
              </>
            ) : (
              // Navigation for admins
              <>
                <Link to="/">📊 داشبورد</Link>
                {!isReportManager && <Link to="/tickets">🎫 تیکت‌ها</Link>}
                {!isReportManager && <Link to="/branches">🏢 شعب</Link>}
                {isAdmin && <Link to="/departments">🏢 دپارتمان‌ها</Link>}
                {isAdmin && <Link to="/users">👥 کاربران</Link>}
                {isAdmin && <Link to="/automation">🤖 اتوماسیون</Link>}
                {isAdmin && <Link to="/sla">⏱️ SLA</Link>}
                {isCentralAdmin && <Link to="/settings">⚙️ تنظیمات</Link>}
                {isCentralAdmin && <Link to="/infrastructure">🏗️ زیرساخت</Link>}
              </>
            )}
          </nav>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", justifyContent: "flex-end" }}>
          <button
            onClick={() => setDark((d) => !d)}
            className="secondary"
            style={{ padding: "8px 16px", fontSize: 14 }}
          >
            {dark ? "☀️ روشن" : "🌙 تاریک"}
          </button>
          {displayName && (
            <span style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
              👤 {displayName} {roleLabel && `(${roleLabel})`}
            </span>
          )}
          {token ? (
            <button onClick={handleLogout} className="danger" style={{ padding: "8px 16px", fontSize: 14 }}>
              🚪 خروج
            </button>
          ) : (
            <Link to="/login">
              <button className="secondary" style={{ padding: "8px 16px", fontSize: 14 }}>
                🔐 ورود
              </button>
            </Link>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer>
        <div>سیستم تیکتینگ ایرانمهر © 2025</div>
        <div style={{ marginTop: 4, fontSize: 11 }}>
          نسخه 0.1.0 | توسعه یافته با ❤️
        </div>
      </footer>
    </div>
  );
}
