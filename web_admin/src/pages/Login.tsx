import { FormEvent, useState, useEffect, useRef } from "react";
import { login, isAuthenticated } from "../services/api";
import { Link, useNavigate } from "react-router-dom";
import { scaleIn, slideIn } from "../lib/gsap";

export default function Login() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const cardRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/");
    }
  }, [navigate]);

  useEffect(() => {
    if (cardRef.current && titleRef.current && formRef.current) {
      // Animate card with scale and fade
      scaleIn(cardRef.current, { from: 0.8, to: 1, duration: 0.8, delay: 0.1 });
      
      // Animate title with slide from top
      slideIn(titleRef.current, "top", { duration: 0.6, distance: 30, delay: 0.3 });
      
      // Animate form with fade and slide from bottom
      slideIn(formRef.current, "bottom", { duration: 0.7, distance: 40, delay: 0.5 });
    }
  }, []);

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
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "خطا در ورود به سیستم";
      setError(errorMessage);
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
      <div ref={cardRef} className="card" style={{ maxWidth: 400, width: "100%", margin: "0 20px" }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <h1 ref={titleRef} style={{ margin: "0 0 8px 0", fontSize: 28, fontWeight: 700 }}>
            سیستم تیکتینگ ایرانمهر
          </h1>
          <p style={{ color: "var(--fg-secondary)", margin: 0 }}>
            لطفاً وارد حساب کاربری خود شوید
          </p>
        </div>
        
        <form ref={formRef} onSubmit={onSubmit} style={{ display: "grid", gap: 16 }}>
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

        <div style={{ marginTop: 16, textAlign: "center" }}>
          <span style={{ color: "var(--fg-secondary)", marginInlineEnd: 8 }}>حساب کاربری ندارید؟</span>
          <Link to="/register" className="link">
            شروع ثبت‌نام چندمرحله‌ای
          </Link>
        </div>
      </div>
    </div>
  );
}
