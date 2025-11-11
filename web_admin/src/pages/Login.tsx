import { FormEvent, useState } from "react";
import { login, isAuthenticated } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  if (isAuthenticated()) {
    navigate("/");
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    const ok = await login(username, password);
    if (ok) {
      navigate("/");
    } else {
      setError("نام کاربری یا رمز عبور نادرست است.");
    }
  };

  return (
    <div>
      <h1>ورود</h1>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12, maxWidth: 320 }}>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="نام کاربری" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="رمز عبور" type="password" />
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit">ورود</button>
      </form>
    </div>
  );
}

