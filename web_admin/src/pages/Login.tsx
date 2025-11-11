import { FormEvent, useState } from "react";
import { login, isAuthenticated } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  if (isAuthenticated()) {
    navigate("/");
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const ok = await login(username, password);
      if (ok) {
        navigate("/");
      } else {
        setError("نام کاربری یا رمز عبور نادرست است.");
      }
    } catch (err: any) {
      setError(err?.message || "خطا در ورود به سیستم");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    }}>
      <div className="card" style={{ maxWidth: 400, width: "100%", margin: "0 20px" }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <h1 style={{ margin: "0 0 8px 0", fontSize: 28, fontWeight: 700 }}>
            سیستم تیکتینگ ایرانمهر
          </h1>
          <p style={{ color: "var(--fg-secondary)", margin: 0 }}>
            لطفاً وارد حساب کاربری خود شوید
          </p>
        </div>
        
        <form onSubmit={onSubmit} style={{ display: "grid", gap: 16 }}>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              نام کاربری
            </label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="نام کاربری"
              required
              autoFocus
            />
          </div>
          
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              رمز عبور
            </label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="رمز عبور"
              type="password"
              required
            />
          </div>
          
          {error && (
            <div className="alert error fade-in">
              {error}
            </div>
          )}
          
          <button type="submit" disabled={loading} style={{ width: "100%", padding: 14 }}>
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
                <span className="loading"></span>
                در حال ورود...
              </span>
            ) : (
              "ورود"
            )}
          </button>
        </form>
        
        <div style={{ marginTop: 24, padding: 16, background: "var(--bg)", borderRadius: "var(--radius)", fontSize: 12, color: "var(--muted)" }}>
          <strong>اطلاعات پیش‌فرض:</strong><br />
          نام کاربری: <code>admin</code><br />
          رمز عبور: <code>admin123</code>
        </div>
      </div>
    </div>
  );
}
