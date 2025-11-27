import { useCallback, useEffect, useState, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiGet, isAuthenticated, getStoredProfile } from "../services/api";
import type { AuthProfile } from "../services/api";
import { stagger, fadeIn } from "../lib/gsap";
import { motion } from "framer-motion";

type Asset = {
  id: number;
  asset_code: string;
  name: string;
  asset_type: string;
  model?: string;
  serial_number?: string;
  manufacturer?: string;
  purchase_date?: string;
  purchase_price?: number;
  warranty_expiry?: string;
  status: string;
  location?: string;
  branch_id?: number;
  branch?: { id: number; name: string; code: string };
  assigned_to_user_id?: number;
  assigned_to?: { id: number; full_name: string; username: string };
  notes?: string;
  created_at: string;
  updated_at: string;
};

type AssetListResponse = {
  items: Asset[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type BranchSummary = { id: number; name: string; code: string };

const ASSET_TYPES = [
  { value: "pc", label: "💻 کامپیوتر", icon: "💻" },
  { value: "laptop", label: "📱 لپ‌تاپ", icon: "📱" },
  { value: "server", label: "🖥️ سرور", icon: "🖥️" },
  { value: "router", label: "📡 روتر", icon: "📡" },
  { value: "switch", label: "🔌 سوئیچ", icon: "🔌" },
  { value: "printer", label: "🖨️ پرینتر", icon: "🖨️" },
  { value: "monitor", label: "🖥️ مانیتور", icon: "🖥️" },
  { value: "tablet", label: "📱 تبلت", icon: "📱" },
  { value: "phone", label: "📞 تلفن", icon: "📞" },
  { value: "other", label: "📦 سایر", icon: "📦" },
];

const STATUS_OPTIONS = [
  { value: "available", label: "✅ در دسترس", color: "var(--success)" },
  { value: "assigned", label: "👤 تخصیص داده شده", color: "var(--info)" },
  { value: "maintenance", label: "🔧 در حال تعمیر", color: "var(--warning)" },
  { value: "retired", label: "🗑️ بازنشسته", color: "var(--muted)" },
  { value: "lost", label: "❌ گم شده", color: "var(--error)" },
];

const getAssetTypeLabel = (type: string) => {
  return ASSET_TYPES.find((t) => t.value === type)?.label || type;
};

const getAssetTypeIcon = (type: string) => {
  return ASSET_TYPES.find((t) => t.value === type)?.icon || "📦";
};

const getStatusBadge = (status: string) => {
  const statusOption = STATUS_OPTIONS.find((s) => s.value === status);
  if (!statusOption) return <span className="badge">{status}</span>;
  return (
    <span className="badge" style={{ background: statusOption.color, color: "white" }}>
      {statusOption.label}
    </span>
  );
};

// Helper functions for future use
// const formatCurrency = (amount?: number) => {
//   if (!amount) return "-";
//   return new Intl.NumberFormat("fa-IR", {
//     style: "currency",
//     currency: "IRR",
//     minimumFractionDigits: 0,
//   }).format(amount);
// };

// const formatDate = (date?: string) => {
//   if (!date) return "-";
//   return new Date(date).toLocaleDateString("fa-IR");
// };

const getWarrantyStatus = (warrantyExpiry?: string) => {
  if (!warrantyExpiry) return null;
  const expiry = new Date(warrantyExpiry);
  const now = new Date();
  const daysUntilExpiry = Math.floor((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  
  if (daysUntilExpiry < 0) {
    return { status: "expired", label: "منقضی شده", color: "var(--error)" };
  } else if (daysUntilExpiry <= 30) {
    return { status: "warning", label: `${daysUntilExpiry} روز باقی مانده`, color: "var(--warning)" };
  } else if (daysUntilExpiry <= 90) {
    return { status: "caution", label: `${daysUntilExpiry} روز باقی مانده`, color: "var(--info)" };
  }
  return { status: "valid", label: `${daysUntilExpiry} روز باقی مانده`, color: "var(--success)" };
};

export default function Assets() {
  const navigate = useNavigate();
  const [profile] = useState<AuthProfile | null>(() => getStoredProfile());
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterBranch, setFilterBranch] = useState<string>("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  
  const [branches, setBranches] = useState<BranchSummary[]>([]);
  
  const tableRef = useRef<HTMLTableSectionElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1); // Reset to first page on search
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const loadBranches = useCallback(async () => {
    try {
      const brs = (await apiGet("/api/branches?is_active=true")) as BranchSummary[];
      setBranches(brs);
    } catch (err) {
      console.error("Error loading branches:", err);
    }
  }, []);

  const loadAssets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", "20");
      if (debouncedSearch) params.set("search", debouncedSearch);
      if (filterType) params.set("asset_type", filterType);
      if (filterStatus) params.set("status", filterStatus);
      if (filterBranch) params.set("branch_id", filterBranch);

      const response = (await apiGet(`/api/assets?${params.toString()}`)) as AssetListResponse;
      setAssets(response.items || []);
      setTotalPages(response.total_pages || 1);
      setTotal(response.total || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطا در دریافت دارایی‌ها");
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, filterType, filterStatus, filterBranch]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    const allowedRoles = ["central_admin", "admin", "branch_admin", "it_specialist"];
    if (profile && !allowedRoles.includes(profile.role)) {
      navigate("/");
      return;
    }

    loadBranches();
  }, [navigate, profile, loadBranches]);

  useEffect(() => {
    if (isAuthenticated() && profile) {
      loadAssets();
    }
  }, [profile, loadAssets]);

  // Animate header on mount
  useEffect(() => {
    if (headerRef.current) {
      fadeIn(headerRef.current, { duration: 0.6, delay: 0.1 });
    }
  }, []);

  // Animate table rows when data changes
  useEffect(() => {
    if (assets.length > 0 && tableRef.current) {
      const rows = tableRef.current.querySelectorAll("tr");
      if (rows.length > 0) {
        stagger(
          rows,
          (el) => fadeIn(el, { duration: 0.4 }),
          { stagger: 0.03, delay: 0.1 }
        );
      }
    }
  }, [assets.length]);

  const clearFilters = () => {
    setSearchQuery("");
    setFilterType("");
    setFilterStatus("");
    setFilterBranch("");
    setPage(1);
  };

  const hasActiveFilters = searchQuery || filterType || filterStatus || filterBranch;

  return (
    <div className="fade-in">
      <div ref={headerRef} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 className="page-title">📦 مدیریت دارایی‌ها</h1>
          <p style={{ marginTop: 8, color: "var(--fg-secondary)", fontSize: 14 }}>
            مدیریت و ردیابی دارایی‌های IT سازمان
          </p>
        </div>
        <Link to="/assets/new">
          <button style={{ padding: "12px 24px", fontSize: 16 }}>
            ➕ ثبت دارایی جدید
          </button>
        </Link>
      </div>

      {error && <div className="alert error fade-in">{error}</div>}

      {/* Filters and Search */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2 className="card-title">🔍 جستجو و فیلتر</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              جستجو
            </label>
            <input
              type="text"
              placeholder="نام، کد، سریال، مدل..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: "100%" }}
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              نوع دارایی
            </label>
            <select
              value={filterType}
              onChange={(e) => {
                setFilterType(e.target.value);
                setPage(1);
              }}
              style={{ width: "100%" }}
            >
              <option value="">همه انواع</option>
              {ASSET_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              وضعیت
            </label>
            <select
              value={filterStatus}
              onChange={(e) => {
                setFilterStatus(e.target.value);
                setPage(1);
              }}
              style={{ width: "100%" }}
            >
              <option value="">همه وضعیت‌ها</option>
              {STATUS_OPTIONS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 500, fontSize: 14 }}>
              شعبه
            </label>
            <select
              value={filterBranch}
              onChange={(e) => {
                setFilterBranch(e.target.value);
                setPage(1);
              }}
              style={{ width: "100%" }}
            >
              <option value="">همه شعب</option>
              {branches.map((b) => (
                <option key={b.id} value={String(b.id)}>
                  {b.name} ({b.code})
                </option>
              ))}
            </select>
          </div>
        </div>
        {hasActiveFilters && (
          <div style={{ marginTop: 16, display: "flex", justifyContent: "flex-end" }}>
            <button type="button" className="secondary" onClick={clearFilters}>
              🗑️ پاک کردن فیلترها
            </button>
          </div>
        )}
      </div>

      {/* Stats Summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 24 }}>
        <div className="card" style={{ textAlign: "center", padding: 20 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: "var(--primary)" }}>{total}</div>
          <div style={{ marginTop: 8, color: "var(--fg-secondary)", fontSize: 14 }}>کل دارایی‌ها</div>
        </div>
        <div className="card" style={{ textAlign: "center", padding: 20 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: "var(--success)" }}>
            {assets.filter((a) => a.status === "available").length}
          </div>
          <div style={{ marginTop: 8, color: "var(--fg-secondary)", fontSize: 14 }}>در دسترس</div>
        </div>
        <div className="card" style={{ textAlign: "center", padding: 20 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: "var(--info)" }}>
            {assets.filter((a) => a.status === "assigned").length}
          </div>
          <div style={{ marginTop: 8, color: "var(--fg-secondary)", fontSize: 14 }}>تخصیص داده شده</div>
        </div>
        <div className="card" style={{ textAlign: "center", padding: 20 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: "var(--warning)" }}>
            {assets.filter((a) => a.status === "maintenance").length}
          </div>
          <div style={{ marginTop: 8, color: "var(--fg-secondary)", fontSize: 14 }}>در حال تعمیر</div>
        </div>
      </div>

      {/* Assets Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📋 لیست دارایی‌ها ({total})</h2>
        </div>

        {loading && !assets.length ? (
          <div style={{ textAlign: "center", padding: 40 }}>
            <div className="loading" style={{ margin: "0 auto" }}></div>
            <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
          </div>
        ) : assets.length === 0 ? (
          <div style={{ padding: 24, textAlign: "center", color: "var(--fg-secondary)" }}>
            {hasActiveFilters ? "هیچ دارایی با این فیلترها یافت نشد." : "هنوز دارایی ثبت نشده است."}
            <br />
            <Link to="/assets/new">
              <button style={{ marginTop: 16, padding: "12px 24px" }}>
                ➕ ثبت دارایی جدید
              </button>
            </Link>
          </div>
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>کد دارایی</th>
                    <th>نام</th>
                    <th>نوع</th>
                    <th>مدل / سریال</th>
                    <th>وضعیت</th>
                    <th>شعبه</th>
                    <th>تخصیص داده شده به</th>
                    <th>گارانتی</th>
                    <th>عملیات</th>
                  </tr>
                </thead>
                <tbody ref={tableRef}>
                  {assets.map((asset) => {
                    const warrantyStatus = getWarrantyStatus(asset.warranty_expiry);
                    return (
                      <motion.tr
                        key={asset.id}
                        whileHover={{ backgroundColor: "var(--bg-secondary)" }}
                        transition={{ duration: 0.2 }}
                      >
                        <td>
                          <strong style={{ fontFamily: "monospace", color: "var(--primary)" }}>
                            {asset.asset_code}
                          </strong>
                        </td>
                        <td style={{ fontWeight: 600 }}>{asset.name}</td>
                        <td>
                          <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                            {getAssetTypeIcon(asset.asset_type)} {getAssetTypeLabel(asset.asset_type)}
                          </span>
                        </td>
                        <td style={{ fontSize: 13, color: "var(--fg-secondary)" }}>
                          {asset.model && <div>مدل: {asset.model}</div>}
                          {asset.serial_number && <div>سریال: {asset.serial_number}</div>}
                        </td>
                        <td>{getStatusBadge(asset.status)}</td>
                        <td>
                          {asset.branch ? (
                            <span>{asset.branch.name} ({asset.branch.code})</span>
                          ) : (
                            <span style={{ color: "var(--fg-secondary)" }}>-</span>
                          )}
                        </td>
                        <td>
                          {asset.assigned_to ? (
                            <span>{asset.assigned_to.full_name}</span>
                          ) : (
                            <span style={{ color: "var(--fg-secondary)" }}>تخصیص داده نشده</span>
                          )}
                        </td>
                        <td>
                          {warrantyStatus ? (
                            <span
                              className="badge"
                              style={{
                                background: warrantyStatus.color,
                                color: "white",
                                fontSize: 12,
                              }}
                            >
                              {warrantyStatus.label}
                            </span>
                          ) : (
                            <span style={{ color: "var(--fg-secondary)" }}>-</span>
                          )}
                        </td>
                        <td>
                          <div style={{ display: "flex", gap: 8 }}>
                            <Link to={`/assets/${asset.id}`}>
                              <button className="secondary small">👁️ مشاهده</button>
                            </Link>
                            <Link to={`/assets/${asset.id}/edit`}>
                              <button className="secondary small">✏️ ویرایش</button>
                            </Link>
                          </div>
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24 }}>
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="secondary"
                >
                  ⬅️ قبلی
                </button>
                <span style={{ padding: "8px 16px", display: "flex", alignItems: "center" }}>
                  صفحه {page} از {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="secondary"
                >
                  بعدی ➡️
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

