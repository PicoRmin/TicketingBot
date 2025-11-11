import { Link, Outlet, useNavigate } from "react-router-dom";
import { getToken, logout } from "./services/api";
import { useEffect, useState } from "react";

export default function App() {
  const navigate = useNavigate();
  const token = getToken();
  const [dark, setDark] = useState<boolean>(() => {
    return localStorage.getItem("imehr_dark") === "1";
  });

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
    navigate("/login");
  };

  return (
    <div className="container">
      <header>
        <nav>
          <Link to="/">📊 داشبورد</Link>
          <Link to="/tickets">🎫 تیکت‌ها</Link>
          <Link to="/branches">🏢 شعب</Link>
        </nav>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <button 
            onClick={() => setDark((d) => !d)} 
            className="secondary"
            style={{ padding: "8px 16px", fontSize: 14 }}
          >
            {dark ? "☀️ روشن" : "🌙 تاریک"}
          </button>
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
