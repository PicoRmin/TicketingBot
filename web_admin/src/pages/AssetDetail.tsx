import { useEffect, useState, useRef } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { apiGet, isAuthenticated, getStoredProfile } from "../services/api";
import type { AuthProfile } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import { fadeIn } from "../lib/gsap";
import ReactEChartsCore from "echarts-for-react/lib/core";
import * as echarts from "echarts/core";
import { LineChart, PieChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

// Register ECharts components
echarts.use([
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer,
]);

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

type AssetHistoryItem = {
  id: number;
  asset_id: number;
  action: string;
  old_value?: string | null;
  new_value?: string | null;
  changed_by?: { id: number; full_name: string; username: string } | null;
  created_at: string;
  notes?: string;
};

type AssetMaintenance = {
  id: number;
  asset_id: number;
  maintenance_type: string;
  description?: string;
  cost?: number;
  performed_by?: { id: number; full_name: string; username: string } | null;
  performed_at: string;
  next_maintenance_date?: string;
};

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

const formatCurrency = (amount?: number) => {
  if (!amount) return "-";
  return new Intl.NumberFormat("fa-IR", {
    style: "currency",
    currency: "IRR",
    minimumFractionDigits: 0,
  }).format(amount);
};

const formatDate = (date?: string) => {
  if (!date) return "-";
  return new Date(date).toLocaleDateString("fa-IR");
};

const getWarrantyStatus = (warrantyExpiry?: string) => {
  if (!warrantyExpiry) return null;
  const expiry = new Date(warrantyExpiry);
  const now = new Date();
  const daysUntilExpiry = Math.floor((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  
  if (daysUntilExpiry < 0) {
    return { status: "expired", label: "منقضی شده", color: "var(--error)", days: Math.abs(daysUntilExpiry) };
  } else if (daysUntilExpiry <= 30) {
    return { status: "warning", label: `${daysUntilExpiry} روز باقی مانده`, color: "var(--warning)", days: daysUntilExpiry };
  } else if (daysUntilExpiry <= 90) {
    return { status: "caution", label: `${daysUntilExpiry} روز باقی مانده`, color: "var(--info)", days: daysUntilExpiry };
  }
  return { status: "valid", label: `${daysUntilExpiry} روز باقی مانده`, color: "var(--success)", days: daysUntilExpiry };
};

const calculateLifeCycle = (purchaseDate?: string, warrantyExpiry?: string) => {
  if (!purchaseDate) return null;
  
  const purchase = new Date(purchaseDate);
  const now = new Date();
  const warranty = warrantyExpiry ? new Date(warrantyExpiry) : null;
  
  const totalDays = Math.floor((now.getTime() - purchase.getTime()) / (1000 * 60 * 60 * 24));
  const warrantyDays = warranty ? Math.floor((warranty.getTime() - purchase.getTime()) / (1000 * 60 * 60 * 24)) : null;
  
  return {
    totalDays,
    warrantyDays,
    ageInMonths: Math.floor(totalDays / 30),
    ageInYears: Math.floor(totalDays / 365),
  };
};

export default function AssetDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [profile] = useState<AuthProfile | null>(() => getStoredProfile());
  
  const [asset, setAsset] = useState<Asset | null>(null);
  const [history, setHistory] = useState<AssetHistoryItem[]>([]);
  const [maintenance, setMaintenance] = useState<AssetMaintenance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const timelineRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    const allowedRoles = ["central_admin", "admin", "branch_admin", "it_specialist"];
    if (profile && !allowedRoles.includes(profile.role)) {
      navigate("/assets");
      return;
    }
  }, [navigate, profile]);

  useEffect(() => {
    const loadData = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const [assetData, historyData, maintenanceData] = await Promise.all([
          apiGet(`/api/assets/${id}`) as Promise<Asset>,
          apiGet(`/api/assets/${id}/history`).catch(() => []) as Promise<AssetHistoryItem[]>,
          apiGet(`/api/assets/${id}/maintenance`).catch(() => []) as Promise<AssetMaintenance[]>,
        ]);
        setAsset(assetData);
        setHistory(historyData || []);
        setMaintenance(maintenanceData || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "خطا در دریافت اطلاعات دارایی");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id]);

  // Animate header on mount
  useEffect(() => {
    if (headerRef.current) {
      fadeIn(headerRef.current, { duration: 0.6, delay: 0.1 });
    }
  }, []);

  // Animate timeline on mount
  useEffect(() => {
    if (timelineRef.current && history.length > 0) {
      const items = timelineRef.current.querySelectorAll(".timeline-item");
      if (items.length > 0) {
        fadeIn(items, { duration: 0.4, delay: 0.1 });
      }
    }
  }, [history.length]);

  if (loading) {
    return (
      <div className="fade-in" style={{ textAlign: "center", padding: 40 }}>
        <div className="loading" style={{ margin: "0 auto" }}></div>
        <p style={{ marginTop: 16, color: "var(--fg-secondary)" }}>در حال بارگذاری...</p>
      </div>
    );
  }

  if (error || !asset) {
    return (
      <div className="fade-in">
        <div className="alert error">{error || "دارایی یافت نشد"}</div>
        <button onClick={() => navigate("/assets")} style={{ marginTop: 16 }}>
          بازگشت به لیست دارایی‌ها
        </button>
      </div>
    );
  }

  const warrantyStatus = getWarrantyStatus(asset.warranty_expiry);
  const lifeCycle = calculateLifeCycle(asset.purchase_date, asset.warranty_expiry);

  // Prepare Life Cycle Chart Data
  const lifeCycleChartOption = lifeCycle ? {
    title: {
      text: "چرخه عمر دارایی",
      left: "center",
      textStyle: { fontSize: 16, fontWeight: 600 },
    },
    tooltip: {
      trigger: "axis",
      formatter: (params: Array<{ seriesName: string; name: string; value: number }>) => {
        const param = params[0];
        return `${param.seriesName}<br/>${param.name}: ${param.value} روز`;
      },
    },
    legend: {
      data: ["عمر دارایی", "گارانتی"],
      bottom: 0,
    },
    xAxis: {
      type: "category",
      data: ["روز", "ماه", "سال"],
    },
    yAxis: {
      type: "value",
      name: "مدت زمان",
    },
    series: [
      {
        name: "عمر دارایی",
        type: "line",
        data: [
          lifeCycle.totalDays,
          lifeCycle.ageInMonths,
          lifeCycle.ageInYears,
        ],
        smooth: true,
        itemStyle: { color: "#3b82f6" },
        areaStyle: { opacity: 0.3 },
      },
      ...(lifeCycle.warrantyDays ? [{
        name: "گارانتی",
        type: "line",
        data: [
          lifeCycle.warrantyDays,
          Math.floor(lifeCycle.warrantyDays / 30),
          Math.floor(lifeCycle.warrantyDays / 365),
        ],
        smooth: true,
        itemStyle: { color: "#10b981" },
        areaStyle: { opacity: 0.3 },
      }] : []),
    ],
    animation: true,
    animationDuration: 1000,
    animationEasing: "cubicOut" as const,
  } : null;

  // Status Distribution Chart
  const statusHistory = history.filter((h) => h.action === "status_changed");
  const statusCounts: Record<string, number> = {};
  statusHistory.forEach((h) => {
    if (h.new_value) {
      statusCounts[h.new_value] = (statusCounts[h.new_value] || 0) + 1;
    }
  });

  const statusChartOption = Object.keys(statusCounts).length > 0 ? {
    title: {
      text: "توزیع وضعیت‌ها",
      left: "center",
      textStyle: { fontSize: 16, fontWeight: 600 },
    },
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b}: {c} ({d}%)",
    },
    legend: {
      orient: "vertical",
      left: "left",
      data: Object.keys(statusCounts).map((s) => STATUS_OPTIONS.find((opt) => opt.value === s)?.label || s),
    },
    series: [
      {
        name: "وضعیت",
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: "#fff",
          borderWidth: 2,
        },
        label: {
          show: true,
          formatter: "{b}: {c}",
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: "bold",
          },
        },
        data: Object.entries(statusCounts).map(([status, count]) => ({
          value: count,
          name: STATUS_OPTIONS.find((opt) => opt.value === status)?.label || status,
          itemStyle: {
            color: STATUS_OPTIONS.find((opt) => opt.value === status)?.color || "var(--primary)",
          },
        })),
      },
    ],
    animation: true,
    animationDuration: 1000,
    animationEasing: "cubicOut" as const,
  } : null;

  return (
    <div className="fade-in">
      <div ref={headerRef} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 className="page-title">
            {getAssetTypeIcon(asset.asset_type)} {asset.name}
          </h1>
          <p style={{ marginTop: 8, color: "var(--fg-secondary)", fontSize: 14 }}>
            کد دارایی: <strong style={{ fontFamily: "monospace" }}>{asset.asset_code}</strong>
          </p>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <Link to={`/assets/${asset.id}/edit`}>
            <button className="secondary">✏️ ویرایش</button>
          </Link>
          <button className="secondary" onClick={() => navigate("/assets")}>
            ← بازگشت
          </button>
        </div>
      </div>

      {error && <div className="alert error fade-in">{error}</div>}

      {/* Asset Info Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16, marginBottom: 24 }}>
        <div className="card">
          <div style={{ fontSize: 14, color: "var(--fg-secondary)", marginBottom: 8 }}>نوع دارایی</div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>
            {getAssetTypeIcon(asset.asset_type)} {getAssetTypeLabel(asset.asset_type)}
          </div>
        </div>
        <div className="card">
          <div style={{ fontSize: 14, color: "var(--fg-secondary)", marginBottom: 8 }}>وضعیت</div>
          <div>{getStatusBadge(asset.status)}</div>
        </div>
        {asset.purchase_date && (
          <div className="card">
            <div style={{ fontSize: 14, color: "var(--fg-secondary)", marginBottom: 8 }}>تاریخ خرید</div>
            <div style={{ fontSize: 18, fontWeight: 600 }}>{formatDate(asset.purchase_date)}</div>
          </div>
        )}
        {asset.purchase_price && (
          <div className="card">
            <div style={{ fontSize: 14, color: "var(--fg-secondary)", marginBottom: 8 }}>قیمت خرید</div>
            <div style={{ fontSize: 18, fontWeight: 600 }}>{formatCurrency(asset.purchase_price)}</div>
          </div>
        )}
      </div>

      {/* Warranty Alert */}
      {warrantyStatus && warrantyStatus.status !== "valid" && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
          style={{
            marginBottom: 24,
            borderLeft: `4px solid ${warrantyStatus.color}`,
            background: warrantyStatus.status === "expired" ? "var(--bg-secondary)" : "var(--bg)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ fontSize: 32 }}>
              {warrantyStatus.status === "expired" ? "⚠️" : "🔔"}
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ marginBottom: 4, fontSize: 18, fontWeight: 600 }}>
                {warrantyStatus.status === "expired" ? "گارانتی منقضی شده" : "هشدار گارانتی"}
              </h3>
              <p style={{ color: "var(--fg-secondary)", margin: 0 }}>
                {warrantyStatus.status === "expired"
                  ? `گارانتی این دارایی ${warrantyStatus.days} روز پیش منقضی شده است.`
                  : `گارانتی این دارایی ${warrantyStatus.days} روز دیگر منقضی می‌شود.`}
              </p>
            </div>
            {warrantyStatus.status === "warning" && (
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                style={{ fontSize: 24 }}
              >
                ⚠️
              </motion.div>
            )}
          </div>
        </motion.div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: 24, marginBottom: 24 }}>
        {/* Asset Details */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">📋 جزئیات دارایی</h2>
          </div>
          <div style={{ display: "grid", gap: 16 }}>
            {asset.model && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>مدل:</strong>
                <p style={{ marginTop: 4 }}>{asset.model}</p>
              </div>
            )}
            {asset.serial_number && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>شماره سریال:</strong>
                <p style={{ marginTop: 4, fontFamily: "monospace" }}>{asset.serial_number}</p>
              </div>
            )}
            {asset.manufacturer && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>سازنده:</strong>
                <p style={{ marginTop: 4 }}>{asset.manufacturer}</p>
              </div>
            )}
            {asset.location && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>مکان:</strong>
                <p style={{ marginTop: 4 }}>{asset.location}</p>
              </div>
            )}
            {asset.branch && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>شعبه:</strong>
                <p style={{ marginTop: 4 }}>{asset.branch.name} ({asset.branch.code})</p>
              </div>
            )}
            {asset.assigned_to && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>تخصیص داده شده به:</strong>
                <p style={{ marginTop: 4 }}>{asset.assigned_to.full_name}</p>
              </div>
            )}
            {asset.warranty_expiry && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>پایان گارانتی:</strong>
                <p style={{ marginTop: 4 }}>
                  {formatDate(asset.warranty_expiry)}
                  {warrantyStatus && (
                    <span
                      className="badge"
                      style={{
                        marginLeft: 8,
                        background: warrantyStatus.color,
                        color: "white",
                        fontSize: 12,
                      }}
                    >
                      {warrantyStatus.label}
                    </span>
                  )}
                </p>
              </div>
            )}
            {asset.notes && (
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>یادداشت‌ها:</strong>
                <p style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>{asset.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Life Cycle Info */}
        {lifeCycle && (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">📊 اطلاعات چرخه عمر</h2>
            </div>
            <div style={{ display: "grid", gap: 16 }}>
              <div>
                <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>عمر دارایی:</strong>
                <p style={{ marginTop: 4, fontSize: 18, fontWeight: 600 }}>
                  {lifeCycle.ageInYears > 0 && `${lifeCycle.ageInYears} سال و `}
                  {Math.floor((lifeCycle.totalDays % 365) / 30)} ماه
                </p>
                <p style={{ marginTop: 4, fontSize: 12, color: "var(--fg-secondary)" }}>
                  ({lifeCycle.totalDays} روز)
                </p>
              </div>
              {lifeCycle.warrantyDays && (
                <div>
                  <strong style={{ color: "var(--fg-secondary)", fontSize: 14 }}>مدت گارانتی:</strong>
                  <p style={{ marginTop: 4, fontSize: 18, fontWeight: 600 }}>
                    {Math.floor(lifeCycle.warrantyDays / 365)} سال و {Math.floor((lifeCycle.warrantyDays % 365) / 30)} ماه
                  </p>
                  <p style={{ marginTop: 4, fontSize: 12, color: "var(--fg-secondary)" }}>
                    ({lifeCycle.warrantyDays} روز)
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Charts */}
      {(lifeCycleChartOption || statusChartOption) && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: 24, marginBottom: 24 }}>
          {lifeCycleChartOption && (
            <div className="card">
              <ReactEChartsCore
                echarts={echarts}
                option={lifeCycleChartOption}
                style={{ height: "300px", width: "100%" }}
                notMerge={false}
                lazyUpdate={false}
              />
            </div>
          )}
          {statusChartOption && (
            <div className="card">
              <ReactEChartsCore
                echarts={echarts}
                option={statusChartOption}
                style={{ height: "300px", width: "100%" }}
                notMerge={false}
                lazyUpdate={false}
              />
            </div>
          )}
        </div>
      )}

      {/* Maintenance History */}
      {maintenance.length > 0 && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h2 className="card-title">🔧 تاریخچه تعمیرات ({maintenance.length})</h2>
          </div>
          <div style={{ display: "grid", gap: 12 }}>
            <AnimatePresence mode="popLayout">
              {maintenance.map((m, idx) => (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3, delay: idx * 0.05 }}
                  className="card"
                  style={{
                    padding: 16,
                    background: "var(--bg-secondary)",
                    borderLeft: "4px solid var(--warning)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
                    <div style={{ flex: 1, minWidth: 200 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                        <span className="badge" style={{ background: "var(--warning)", color: "white" }}>
                          {m.maintenance_type}
                        </span>
                        <span style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                          {formatDate(m.performed_at)}
                        </span>
                      </div>
                      {m.description && (
                        <p style={{ marginTop: 8, marginBottom: 0 }}>{m.description}</p>
                      )}
                      {m.cost && (
                        <p style={{ marginTop: 8, marginBottom: 0, fontWeight: 600 }}>
                          هزینه: {formatCurrency(m.cost)}
                        </p>
                      )}
                      {m.performed_by && (
                        <p style={{ marginTop: 4, fontSize: 12, color: "var(--fg-secondary)", marginBottom: 0 }}>
                          انجام شده توسط: {m.performed_by.full_name}
                        </p>
                      )}
                      {m.next_maintenance_date && (
                        <p style={{ marginTop: 8, fontSize: 12, color: "var(--info)", marginBottom: 0 }}>
                          تعمیر بعدی: {formatDate(m.next_maintenance_date)}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* History Timeline */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📜 تاریخچه تغییرات ({history.length})</h2>
        </div>
        {history.length === 0 ? (
          <div style={{ textAlign: "center", padding: 40, color: "var(--fg-secondary)" }}>
            📋 هیچ تغییراتی ثبت نشده است
          </div>
        ) : (
          <div ref={timelineRef} className="timeline-container" style={{ position: "relative", paddingLeft: 40 }}>
            <AnimatePresence mode="popLayout">
              {history.map((item, idx) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3, delay: idx * 0.05 }}
                  className="timeline-item"
                  style={{
                    position: "relative",
                    paddingBottom: 24,
                    paddingLeft: 24,
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      left: -8,
                      top: 4,
                      width: 16,
                      height: 16,
                      borderRadius: "50%",
                      background: "var(--primary)",
                      border: "3px solid var(--bg)",
                      zIndex: 2,
                    }}
                  />
                  {idx < history.length - 1 && (
                    <div
                      style={{
                        position: "absolute",
                        left: -1,
                        top: 20,
                        width: 2,
                        height: "calc(100% - 4px)",
                        background: "var(--border)",
                        zIndex: 1,
                      }}
                    />
                  )}
                  <div className="card" style={{ padding: 16, background: "var(--bg-secondary)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
                      <div style={{ flex: 1, minWidth: 200 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                          <span className="badge" style={{ background: "var(--primary)", color: "white" }}>
                            {item.action === "created" && "➕ ایجاد"}
                            {item.action === "status_changed" && "🔄 تغییر وضعیت"}
                            {item.action === "assigned" && "👤 تخصیص"}
                            {item.action === "updated" && "✏️ به‌روزرسانی"}
                            {item.action === "maintenance" && "🔧 تعمیر"}
                            {!["created", "status_changed", "assigned", "updated", "maintenance"].includes(item.action) && item.action}
                          </span>
                          <span style={{ fontSize: 12, color: "var(--fg-secondary)" }}>
                            {formatDate(item.created_at)}
                          </span>
                        </div>
                        {item.old_value && item.new_value && (
                          <div style={{ marginTop: 8, padding: 8, background: "var(--bg)", borderRadius: "4px" }}>
                            <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>
                              تغییر از:
                            </div>
                            <div style={{ fontSize: 13, marginBottom: 8 }}>{item.old_value}</div>
                            <div style={{ fontSize: 12, color: "var(--fg-secondary)", marginBottom: 4 }}>
                              به:
                            </div>
                            <div style={{ fontSize: 13 }}>{item.new_value}</div>
                          </div>
                        )}
                        {item.notes && (
                          <p style={{ marginTop: 8, marginBottom: 0, fontSize: 13, color: "var(--fg-secondary)" }}>
                            {item.notes}
                          </p>
                        )}
                        {item.changed_by && (
                          <p style={{ marginTop: 8, fontSize: 11, color: "var(--muted)", marginBottom: 0 }}>
                            تغییر توسط: {item.changed_by.full_name || item.changed_by.username}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}

