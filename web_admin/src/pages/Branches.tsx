import { useEffect, useState } from "react";
import { apiGet, apiPost, isAuthenticated } from "../services/api";
import { useNavigate } from "react-router-dom";

type Branch = {
  id: number;
  name: string;
  name_en?: string | null;
  code: string;
  address?: string | null;
  phone?: string | null;
  is_active: boolean;
  created_at: string;
};

export default function Branches() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Branch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    name_en: "",
    code: "",
    address: "",
    phone: "",
    is_active: true
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
    }
  }, []);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiGet("/api/branches");
      setItems(res);
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت شعب");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async () => {
    if (!form.name || !form.code) {
      setError("نام و کد شعبه الزامی است");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await apiPost("/api/branches", {
        name: form.name,
        name_en: form.name_en || undefined,
        code: form.code,
        address: form.address || undefined,
        phone: form.phone || undefined,
        is_active: form.is_active
      });
      setForm({ name: "", name_en: "", code: "", address: "", phone: "", is_active: true });
      await load();
    } catch (e: any) {
      setError(e?.message || "خطا در ثبت شعبه");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>شعب</h1>
      {loading && <div>در حال بارگذاری...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      <div style={{ display: "grid", gap: 8, maxWidth: 480, marginBottom: 16 }}>
        <input placeholder="نام" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input placeholder="نام انگلیسی" value={form.name_en} onChange={(e) => setForm({ ...form, name_en: e.target.value })} />
        <input placeholder="کد" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
        <input placeholder="آدرس" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        <input placeholder="تلفن" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <label style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
          فعال
        </label>
        <button onClick={submit} disabled={loading}>افزودن شعبه</button>
      </div>
      <div className="table-wrap">
        <table border={1} cellPadding={6} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>نام</th>
              <th>کد</th>
              <th>فعال</th>
              <th>تلفن</th>
              <th>آدرس</th>
              <th>تاریخ ایجاد</th>
            </tr>
          </thead>
          <tbody>
            {items.map((b) => (
              <tr key={b.id}>
                <td>{b.name}</td>
                <td>{b.code}</td>
                <td>{b.is_active ? "بله" : "خیر"}</td>
                <td>{b.phone || ""}</td>
                <td>{b.address || ""}</td>
                <td>{b.created_at?.slice(0, 10) || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

