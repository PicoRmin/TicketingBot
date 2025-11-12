import { Link, Outlet, useNavigate } from "react-router-dom";
import { getToken, logout, getStoredProfile, fetchProfile, setProfile, clearProfile } from "./services/api";
import { useEffect, useState } from "react";
import logoUrl from "./assets/brand-logo.png";

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
      return;
    }

    const stored = getStoredProfile();
    if (stored) {
      setProfileState(stored);
      return;
    }

    fetchProfile()
      .then((p) => {
        setProfile(p);
        setProfileState(p);
      })
      .catch(() => {
        // ignore
      });
  }, [token]);

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
  const displayName = profile?.full_name || profile?.username;

  return (
    <div className="container">
      <header>
        <div className="header-left">
          <Link to="/" className="brand">
            <img src={logoUrl} alt="لوگوی ایرانمهر" />
            <div className="brand-text">
              <span className="brand-title">سیستم تیکتینگ ایرانمهر</span>
              <span className="brand-subtitle">پنل مدیریت</span>
            </div>
          </Link>
          <nav>
            <Link to="/">📊 داشبورد</Link>
            <Link to="/tickets">🎫 تیکت‌ها</Link>
            <Link to="/branches">🏢 شعب</Link>
            {isAdmin && <Link to="/users">👥 کاربران</Link>}
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
              👤 {displayName}
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
