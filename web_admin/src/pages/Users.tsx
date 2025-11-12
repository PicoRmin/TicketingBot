import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  apiGet,
  createUserApi,
  deleteUserApi,
  fetchProfile,
  fetchUsers,
  getStoredProfile,
  isAuthenticated,
  setProfile,
  updateUserApi
} from "../services/api";

const ROLE_OPTIONS = [
  { value: "central_admin", label: "👑 مدیر ارشد" },
  { value: "admin", label: "🛡️ مدیر سیستم" },
  { value: "branch_admin", label: "🏢 مسئول شعبه" },
  { value: "report_manager", label: "📊 گزارش‌گیر" },
  { value: "user", label: "👤 کاربر" }
];

const LANGUAGE_OPTIONS = [
  { value: "fa", label: "🇮🇷 فارسی" },
  { value: "en", label: "🇬🇧 English" }
];

type UserItem = {
  id: number;
  username: string;
  full_name: string;
  role: string;
  language: string;
  branch_id?: number | null;
  branch?: { id: number; name: string; code: string } | null;
  is_active: boolean;
  created_at: string;
};

type BranchItem = {
  id: number;
  name: string;
  code: string;
  is_active: boolean;
};

const EMPTY_FORM = {
  username: "",
  full_name: "",
  password: "",
  role: "user",
  branch_id: "",
  language: "fa",
  is_active: true,
};

export default function Users() {
  const navigate = useNavigate();
  const [profile, setProfileState] = useState<any | null>(() => getStoredProfile());
  const [users, setUsers] = useState<UserItem[]>([]);
  const [branches, setBranches] = useState<BranchItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [filterRole, setFilterRole] = useState<string>("");
  const [filterBranch, setFilterBranch] = useState<string>("");

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    if (!profile) {
      fetchProfile()
        .then((data) => {
          setProfile(data);
          setProfileState(data);
        })
        .catch(() => {
          // ignore
        });
    }
  }, []);

  useEffect(() => {
    if (!profile) return;
    if (!["admin", "central_admin"].includes(profile.role)) {
      navigate("/");
      return;
    }
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile, filterRole, filterBranch]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: string[] = ["include_inactive=true"];
      if (filterRole) params.push(`role=${filterRole}`);
      if (filterBranch) params.push(`branch_id=${filterBranch}`);
      const query = params.length ? `?${params.join("&")}` : "";
      const [usersRes, branchesRes] = await Promise.all([
        fetchUsers(query),
        apiGet("/api/branches?is_active=true"),
      ]);
      setUsers(usersRes as UserItem[]);
      setBranches((branchesRes as BranchItem[]).filter((b) => b.is_active));
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت کاربران");
    } finally {
      setLoading(false);
    }
  };

  const roleLabel = (role: string) => {
    const opt = ROLE_OPTIONS.find((r) => r.value === role);
    return opt ? opt.label : role;
  };

  const branchLabel = (user: UserItem) => {
    if (user.branch) return `${user.branch.name}`;
    return user.branch_id ? `شعبه ${user.branch_id}` : "-";
  };

  const resetForm = () => {
    setForm({ ...EMPTY_FORM });
    setEditingId(null);
  };

  const onEdit = (user: UserItem) => {
    setEditingId(user.id);
    setForm({
      username: user.username,
      full_name: user.full_name,
      password: "",
      role: user.role,
      branch_id: user.branch_id ? String(user.branch_id) : "",
      language: user.language || "fa",
      is_active: user.is_active,
    });
    setSuccess(null);
    setError(null);
  };

  const onDelete = async (user: UserItem) => {
    if (!window.confirm(`آیا از حذف کاربر ${user.username} مطمئن هستید؟`)) {
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await deleteUserApi(user.id);
      setSuccess("کاربر با موفقیت حذف شد");
      await loadData();
      if (editingId === user.id) {
        resetForm();
      }
    } catch (e: any) {
      setError(e?.message || "خطا در حذف کاربر");
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    setError(null);
    setSuccess(null);

    if (!form.full_name.trim()) {
      setError("نام کامل الزامی است");
      return;
    }

    if (!editingId && !form.username.trim()) {
      setError("نام کاربری الزامی است");
      return;
    }

    if (!editingId && !form.password.trim()) {
      setError("رمز عبور الزامی است");
      return;
    }

    if (form.role === "branch_admin" && !form.branch_id) {
      setError("برای مسئول شعبه، انتخاب شعبه الزامی است");
      return;
    }

    setLoading(true);
    try {
      const branchIdValue = form.branch_id ? Number(form.branch_id) : undefined;

      if (editingId) {
        const payload: any = {
          full_name: form.full_name,
          language: form.language,
          role: form.role,
          branch_id: branchIdValue ?? null,
          is_active: form.is_active,
        };
        if (form.password.trim()) {
          payload.password = form.password;
        }
        await updateUserApi(editingId, payload);
        setSuccess("کاربر با موفقیت به‌روزرسانی شد");
      } else {
        await createUserApi({
          username: form.username,
          full_name: form.full_name,
          password: form.password,
          role: form.role,
          language: form.language,
          branch_id: branchIdValue ?? null,
        });
        setSuccess("کاربر جدید با موفقیت ایجاد شد");
      }
      resetForm();
      await loadData();
    } catch (e: any) {
      setError(e?.message || "خطا در ذخیره کاربر");
    } finally {
      setLoading(false);
    }
  };

  const branchOptions = useMemo(() => branches, [branches]);

  return (
    <div className="fade-in">
      <h1 className="page-title">👥 مدیریت کاربران</h1>

      {loading && (
        <div style={{ textAlign: "center", padding: 16 }}>
          <div className="loading" style={{ margin: "0 auto" }}></div>
          <p style={{ marginTop: 12, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
        </div>
      )}

      {error && (
        <div className="alert error fade-in">
          <strong>خطا:</strong> {error}
        </div>
      )}

      {success && (
        <div className="alert success fade-in">
          {success}
        </div>
      )}

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">{editingId ? "✏️ ویرایش کاربر" : "➕ افزودن کاربر جدید"}</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2" style={{ gap: 16 }}>
          {!editingId && (
            <label>
              نام کاربری:
              <input
                placeholder="username"
                value={form.username}
                onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
                required
              />
            </label>
          )}

          <label>
            نام کامل:
            <input
              placeholder="نام و نام خانوادگی"
              value={form.full_name}
              onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
              required
            />
          </label>

          <label>
            نقش:
            <select
              value={form.role}
              onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
            >
              {ROLE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            زبان:
            <select
              value={form.language}
              onChange={(e) => setForm((f) => ({ ...f, language: e.target.value }))}
            >
              {LANGUAGE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>

          {(form.role === "branch_admin" || form.role === "user") && (
            <label>
              شعبه:
              <select
                value={form.branch_id}
                onChange={(e) => setForm((f) => ({ ...f, branch_id: e.target.value }))}
              >
                <option value="">بدون شعبه</option>
                {branchOptions.map((branch) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.name}
                  </option>
                ))}
              </select>
            </label>
          )}

          <label>
            رمز عبور {editingId ? "(برای تغییر)" : ""}:
            <input
              type="password"
              placeholder={editingId ? "برای عدم تغییر خالی بگذارید" : "رمز عبور"}
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            />
          </label>

          {editingId && (
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
              />
              <span className="text-sm">کاربر فعال باشد</span>
            </label>
          )}
        </div>
        <div className="card-actions" style={{ marginTop: 16 }}>
          <button onClick={submit} disabled={loading} className="button primary">
            {editingId ? "💾 ذخیره تغییرات" : "➕ ایجاد کاربر"}
          </button>
          {editingId && (
            <button onClick={resetForm} disabled={loading} className="button secondary">
              ❌ انصراف
            </button>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header" style={{ flexWrap: "wrap", gap: 12 }}>
          <h2 className="card-title">فهرست کاربران</h2>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="small"
            >
              <option value="">همه نقش‌ها</option>
              {ROLE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <select
              value={filterBranch}
              onChange={(e) => setFilterBranch(e.target.value)}
              className="small"
            >
              <option value="">تمام شعب</option>
              {branchOptions.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        {users.length === 0 ? (
          <div style={{ padding: 24, textAlign: "center", color: "var(--fg-secondary)" }}>
            هیچ کاربری یافت نشد.
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>نام کامل</th>
                  <th>نام کاربری</th>
                  <th>نقش</th>
                  <th>شعبه</th>
                  <th>وضعیت</th>
                  <th>زبان</th>
                  <th>تاریخ ایجاد</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td style={{ fontWeight: 600 }}>{user.full_name}</td>
                    <td>{user.username}</td>
                    <td>{roleLabel(user.role)}</td>
                    <td>{branchLabel(user)}</td>
                    <td>
                      {user.is_active ? (
                        <span className="badge success">فعال</span>
                      ) : (
                        <span className="badge danger">غیرفعال</span>
                      )}
                    </td>
                    <td>{user.language === "en" ? "English" : "فارسی"}</td>
                    <td>{user.created_at ? new Date(user.created_at).toLocaleString("fa-IR") : "-"}</td>
                    <td style={{ display: "flex", gap: 8 }}>
                      <button
                        className="button secondary small"
                        onClick={() => onEdit(user)}
                        disabled={loading}
                      >
                        ✏️ ویرایش
                      </button>
                      {profile?.id !== user.id && profile?.role === "central_admin" && (
                        <button
                          className="button danger small"
                          onClick={() => onDelete(user)}
                          disabled={loading}
                        >
                          🗑️ حذف
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
