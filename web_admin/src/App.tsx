import { Link, Outlet, useNavigate } from "react-router-dom";
import { useEffect, useState, ChangeEvent } from "react";
import { useTranslation } from "react-i18next";
import { getToken, logout, getStoredProfile, fetchProfile, setProfile, clearProfile } from "./services/api";
import logoUrl from "./assets/brand-logo.svg";

export default function App() {
  const navigate = useNavigate();
  const token = getToken();
  const [profile, setProfileState] = useState<any | null>(() => getStoredProfile());
  const [dark, setDark] = useState<boolean>(() => {
    return localStorage.getItem("imehr_dark") === "1";
  });
  const { t, i18n } = useTranslation();

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
    return t(`role.${role}`, { defaultValue: role });
  };
  
  const roleLabel = profile ? getRoleLabel(profile.role) : "";
  const handleLangChange = (e: ChangeEvent<HTMLSelectElement>) => {
    i18n.changeLanguage(e.target.value);
  };
  const versionLabel = t("layout.version", { version: "0.1.0" });

  return (
    <div className="container">
      <header>
        <div className="header-left">
          <Link to="/" className="brand">
            <img src={logoUrl} alt="لوگوی ایرانمهر" />
            <div className="brand-text">
              <span className="brand-title">{t("brandTitle")}</span>
              <span className="brand-subtitle">{t("brandSubtitle")}</span>
            </div>
          </Link>
          <nav>
            {profile?.role === "user" ? (
              // Navigation for regular users
              <>
                <Link to="/user-dashboard">{t("nav.dashboard")}</Link>
                <Link to="/user-portal">{t("nav.userPortal")}</Link>
              </>
            ) : (
              // Navigation for admins
              <>
                <Link to="/">{t("nav.dashboard")}</Link>
                {!isReportManager && <Link to="/tickets">{t("nav.tickets")}</Link>}
                {!isReportManager && <Link to="/branches">{t("nav.branches")}</Link>}
                {isAdmin && <Link to="/departments">{t("nav.departments")}</Link>}
                {isAdmin && <Link to="/users">{t("nav.users")}</Link>}
                {isAdmin && <Link to="/automation">{t("nav.automation")}</Link>}
                {isAdmin && <Link to="/sla">{t("nav.sla")}</Link>}
                {isAdmin && <Link to="/custom-fields">{t("nav.customFields")}</Link>}
                {isCentralAdmin && <Link to="/settings">{t("nav.settings")}</Link>}
                {isCentralAdmin && <Link to="/infrastructure">{t("nav.infrastructure")}</Link>}
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
            {dark ? t("actions.light") : t("actions.dark")}
          </button>
          <select
            value={i18n.language}
            onChange={handleLangChange}
            className="secondary"
            style={{ padding: "8px 12px", fontSize: 14, borderRadius: "var(--radius)" }}
          >
            <option value="fa">{t("actions.langFa")}</option>
            <option value="en">{t("actions.langEn")}</option>
          </select>
          {displayName && (
            <span style={{ fontSize: 14, color: "var(--fg-secondary)" }}>
              👤 {displayName} {roleLabel && `(${roleLabel})`}
            </span>
          )}
          {token ? (
            <button onClick={handleLogout} className="danger" style={{ padding: "8px 16px", fontSize: 14 }}>
              {t("actions.logout")}
            </button>
          ) : (
            <Link to="/login">
              <button className="secondary" style={{ padding: "8px 16px", fontSize: 14 }}>
                {t("actions.login")}
              </button>
            </Link>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer>
        <div>{t("layout.footer")}</div>
        <div style={{ marginTop: 4, fontSize: 11 }}>
          {versionLabel}
        </div>
      </footer>
    </div>
  );
}
