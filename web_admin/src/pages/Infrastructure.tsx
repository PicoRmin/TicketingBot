import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiGet, apiPost, apiPut, apiDelete, isAuthenticated, fetchProfile, getStoredProfile } from "../services/api";

type InfrastructureItem = {
  id: number;
  branch_id: number;
  branch?: { id: number; name: string };
  infrastructure_type: string;
  name: string;
  description?: string;
  ip_address?: string;
  hostname?: string;
  model?: string;
  serial_number?: string;
  service_type?: string;
  service_url?: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
};

type BranchItem = {
  id: number;
  name: string;
  code: string;
};

const INFRASTRUCTURE_TYPES = [
  { value: "ip", label: "🌐 آدرس IP" },
  { value: "server", label: "🖥️ سرور" },
  { value: "equipment", label: "💻 تجهیزات" },
  { value: "service", label: "🔧 سرویس" },
];

const STATUS_OPTIONS = [
  { value: "active", label: "✅ فعال" },
  { value: "inactive", label: "❌ غیرفعال" },
  { value: "maintenance", label: "🔧 در حال تعمیر" },
];

export default function Infrastructure() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [infrastructure, setInfrastructure] = useState<InfrastructureItem[]>([]);
  const [branches, setBranches] = useState<BranchItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({
    branch_id: "",
    infrastructure_type: "ip",
    name: "",
    description: "",
    ip_address: "",
    hostname: "",
    model: "",
    serial_number: "",
    service_type: "",
    service_url: "",
    status: "active",
    notes: "",
  });
  const [filterBranch, setFilterBranch] = useState<string>("");
  const [filterType, setFilterType] = useState<string>("");

  useEffect(() => {
    const checkAuthAndLoad = async () => {
      if (!isAuthenticated()) {
        navigate("/login");
        return;
      }
      const profile = getStoredProfile() || await fetchProfile();
      if (!profile || profile.role !== "central_admin") {
        navigate("/");
        return;
      }
      loadData();
    };
    checkAuthAndLoad();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterBranch) params.set("branch_id", filterBranch);
      if (filterType) params.set("infrastructure_type", filterType);
      
      const [infraData, branchesData] = await Promise.all([
        apiGet(`/api/branch-infrastructure?${params.toString()}`),
        apiGet("/api/branches?is_active=true"),
      ]);
      setInfrastructure(infraData);
      setBranches(branchesData);
    } catch (e: any) {
      setError(e?.message || "خطا در دریافت اطلاعات");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated()) {
      loadData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterBranch, filterType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const payload: any = {
        branch_id: parseInt(form.branch_id),
        infrastructure_type: form.infrastructure_type,
        name: form.name,
        status: form.status,
      };
      if (form.description) payload.description = form.description;
      if (form.ip_address) payload.ip_address = form.ip_address;
      if (form.hostname) payload.hostname = form.hostname;
      if (form.model) payload.model = form.model;
      if (form.serial_number) payload.serial_number = form.serial_number;
      if (form.service_type) payload.service_type = form.service_type;
      if (form.service_url) payload.service_url = form.service_url;
      if (form.notes) payload.notes = form.notes;

      if (editingId) {
        await apiPut(`/api/branch-infrastructure/${editingId}`, payload);
        setSuccess("زیرساخت با موفقیت به‌روزرسانی شد");
      } else {
        await apiPost("/api/branch-infrastructure", payload);
        setSuccess("زیرساخت جدید با موفقیت ایجاد شد");
      }
      resetForm();
      await loadData();
    } catch (e: any) {
      setError(e?.message || "خطا در ذخیره زیرساخت");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("آیا از حذف این زیرساخت اطمینان دارید؟")) return;
    setLoading(true);
    try {
      await apiDelete(`/api/branch-infrastructure/${id}`);
      setSuccess("زیرساخت با موفقیت حذف شد");
      await loadData();
    } catch (e: any) {
      setError(e?.message || "خطا در حذف زیرساخت");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setForm({
      branch_id: "",
      infrastructure_type: "ip",
      name: "",
      description: "",
      ip_address: "",
      hostname: "",
      model: "",
      serial_number: "",
      service_type: "",
      service_url: "",
      status: "active",
      notes: "",
    });
    setEditingId(null);
  };

  const onEdit = (item: InfrastructureItem) => {
    setEditingId(item.id);
    setForm({
      branch_id: String(item.branch_id),
      infrastructure_type: item.infrastructure_type,
      name: item.name,
      description: item.description || "",
      ip_address: item.ip_address || "",
      hostname: item.hostname || "",
      model: item.model || "",
      serial_number: item.serial_number || "",
      service_type: item.service_type || "",
      service_url: item.service_url || "",
      status: item.status,
      notes: item.notes || "",
    });
  };

  const getTypeLabel = (type: string) => {
    return INFRASTRUCTURE_TYPES.find((t) => t.value === type)?.label || type;
  };

  const getStatusLabel = (status: string) => {
    return STATUS_OPTIONS.find((s) => s.value === status)?.label || status;
  };

  return (
    <div className="fade-in">
      <h1 style={{ marginBottom: 24, fontSize: 32, fontWeight: 700 }}>🏗️ مدیریت زیرساخت شعب</h1>

      {error && (
        <div className="alert error fade-in">
          <strong>خطا:</strong> {error}
        </div>
      )}

      {success && (
        <div className="alert success fade-in">
          <strong>موفق:</strong> {success}
        </div>
      )}

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">{editingId ? "✏️ ویرایش زیرساخت" : "➕ افزودن زیرساخت جدید"}</h2>
        </div>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16 }}>
            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                شعبه: *
              </label>
              <select
                value={form.branch_id}
                onChange={(e) => setForm({ ...form, branch_id: e.target.value })}
                required
              >
                <option value="">انتخاب شعبه</option>
                {branches.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                نوع زیرساخت: *
              </label>
              <select
                value={form.infrastructure_type}
                onChange={(e) => setForm({ ...form, infrastructure_type: e.target.value })}
                required
              >
                {INFRASTRUCTURE_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                نام: *
              </label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
            </div>

            {form.infrastructure_type === "ip" && (
              <div>
                <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                  آدرس IP:
                </label>
                <input
                  value={form.ip_address}
                  onChange={(e) => setForm({ ...form, ip_address: e.target.value })}
                />
              </div>
            )}

            {form.infrastructure_type === "server" && (
              <>
                <div>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    آدرس IP:
                  </label>
                  <input
                    value={form.ip_address}
                    onChange={(e) => setForm({ ...form, ip_address: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    نام میزبان:
                  </label>
                  <input
                    value={form.hostname}
                    onChange={(e) => setForm({ ...form, hostname: e.target.value })}
                  />
                </div>
              </>
            )}

            {form.infrastructure_type === "equipment" && (
              <>
                <div>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    مدل:
                  </label>
                  <input
                    value={form.model}
                    onChange={(e) => setForm({ ...form, model: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    شماره سریال:
                  </label>
                  <input
                    value={form.serial_number}
                    onChange={(e) => setForm({ ...form, serial_number: e.target.value })}
                  />
                </div>
              </>
            )}

            {form.infrastructure_type === "service" && (
              <>
                <div>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    نوع سرویس:
                  </label>
                  <input
                    value={form.service_type}
                    onChange={(e) => setForm({ ...form, service_type: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                    آدرس سرویس:
                  </label>
                  <input
                    value={form.service_url}
                    onChange={(e) => setForm({ ...form, service_url: e.target.value })}
                  />
                </div>
              </>
            )}

            <div>
              <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
                وضعیت: *
              </label>
              <select
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                required
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              توضیحات:
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
            />
          </div>

          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              یادداشت‌ها:
            </label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              rows={2}
            />
          </div>

          <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
            {editingId && (
              <button type="button" onClick={resetForm} className="secondary">
                ❌ لغو
              </button>
            )}
            <button type="submit" disabled={loading} className="success">
              {loading ? "⏳ در حال ذخیره..." : editingId ? "💾 به‌روزرسانی" : "➕ ایجاد"}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📋 لیست زیرساخت‌ها</h2>
        </div>

        <div className="filters" style={{ marginBottom: 16 }}>
          <select value={filterBranch} onChange={(e) => setFilterBranch(e.target.value)}>
            <option value="">همه شعب</option>
            {branches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="">همه انواع</option>
            {INFRASTRUCTURE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        {loading && !infrastructure.length ? (
          <div style={{ textAlign: "center", padding: 40 }}>
            <div className="loading" style={{ margin: "0 auto" }}></div>
          </div>
        ) : infrastructure.length === 0 ? (
          <div style={{ padding: 24, textAlign: "center", color: "var(--fg-secondary)" }}>
            هیچ زیرساختی یافت نشد.
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>شعبه</th>
                  <th>نوع</th>
                  <th>نام</th>
                  <th>جزئیات</th>
                  <th>وضعیت</th>
                  <th>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {infrastructure.map((item) => (
                  <tr key={item.id}>
                    <td>{item.branch?.name || `شعبه ${item.branch_id}`}</td>
                    <td>{getTypeLabel(item.infrastructure_type)}</td>
                    <td style={{ fontWeight: 600 }}>{item.name}</td>
                    <td>
                      {item.infrastructure_type === "ip" && item.ip_address && `IP: ${item.ip_address}`}
                      {item.infrastructure_type === "server" && (
                        <>
                          {item.hostname && `Host: ${item.hostname}`}
                          {item.ip_address && ` | IP: ${item.ip_address}`}
                        </>
                      )}
                      {item.infrastructure_type === "equipment" && (
                        <>
                          {item.model && `Model: ${item.model}`}
                          {item.serial_number && ` | SN: ${item.serial_number}`}
                        </>
                      )}
                      {item.infrastructure_type === "service" && (
                        <>
                          {item.service_type && `Type: ${item.service_type}`}
                          {item.service_url && ` | URL: ${item.service_url}`}
                        </>
                      )}
                    </td>
                    <td>{getStatusLabel(item.status)}</td>
                    <td style={{ display: "flex", gap: 8 }}>
                      <button
                        className="button secondary small"
                        onClick={() => onEdit(item)}
                        disabled={loading}
                      >
                        ✏️ ویرایش
                      </button>
                      <button
                        className="button danger small"
                        onClick={() => handleDelete(item.id)}
                        disabled={loading}
                      >
                        🗑️ حذف
                      </button>
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

