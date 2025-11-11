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
      <header style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link to="/">داشبورد</Link>
          <Link to="/tickets">تیکت‌ها</Link>
          <Link to="/branches">شعب</Link>
        </nav>
        <div>
          <button onClick={() => setDark((d) => !d)} style={{ marginInlineEnd: 12 }}>
            {dark ? "Light" : "Dark"}
          </button>
          {token ? (
            <button onClick={handleLogout}>خروج</button>
          ) : (
            <Link to="/login">ورود</Link>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer style={{ marginTop: 24, fontSize: 12, color: "var(--muted)" }}>
        Iranmehr Ticketing Admin
      </footer>
    </div>
  );
}

