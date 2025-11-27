import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { motion, AnimatePresence } from "framer-motion";
import { fadeIn } from "../../lib/gsap";
import { useBranchStatus, type BranchStatus } from "../../hooks/useBranchStatus";

type BranchStatusBarProps = {
  enabled: boolean;
};

export function BranchStatusBar({ enabled }: BranchStatusBarProps) {
  const { t } = useTranslation();
  const { data: branches, isLoading } = useBranchStatus(enabled);
  const [hoveredBranch, setHoveredBranch] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && branches && branches.length > 0) {
      fadeIn(containerRef.current, { duration: 0.6, delay: 0.2 });
    }
  }, [branches]);

  if (isLoading || !branches || branches.length === 0) {
    return null;
  }

  const getStatusColor = (status: BranchStatus["status"]) => {
    switch (status) {
      case "critical":
        return "var(--error)";
      case "warning":
        return "var(--warning)";
      case "healthy":
        return "var(--success)";
      default:
        return "var(--muted)";
    }
  };

  const getStatusIcon = (status: BranchStatus["status"]) => {
    switch (status) {
      case "critical":
        return "🔴";
      case "warning":
        return "🟠";
      case "healthy":
        return "🟢";
      default:
        return "⚪";
    }
  };

  return (
    <div ref={containerRef} className="branch-status-bar">
      <div className="branch-status-bar__header">
        <h3 className="branch-status-bar__title">{t("dashboard.branchStatus.title")}</h3>
        <span className="branch-status-bar__count">{branches.length} {t("dashboard.branchStatus.branches")}</span>
      </div>
      <div className="branch-status-bar__container">
        <AnimatePresence mode="popLayout">
          {branches.map((branch, index) => (
            <motion.div
              key={branch.id}
              className={`branch-status-item branch-status-item--${branch.status}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              onMouseEnter={() => setHoveredBranch(branch.id)}
              onMouseLeave={() => setHoveredBranch(null)}
              whileHover={{ scale: 1.05, y: -2 }}
            >
              <div className="branch-status-item__icon" style={{ color: getStatusColor(branch.status) }}>
                {getStatusIcon(branch.status)}
              </div>
              <div className="branch-status-item__content">
                <div className="branch-status-item__name">{branch.name}</div>
                <div className="branch-status-item__code">{branch.code}</div>
              </div>
              <div className="branch-status-item__stats">
                <div className="branch-status-item__tickets">
                  <span className="branch-status-item__count">{branch.totalTickets}</span>
                  <span className="branch-status-item__label">{t("dashboard.branchStatus.tickets")}</span>
                </div>
              </div>
              {hoveredBranch === branch.id && (
                <motion.div
                  className="branch-status-tooltip"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="branch-status-tooltip__title">{branch.name}</div>
                  <div className="branch-status-tooltip__details">
                    <div>
                      <span>{t("dashboard.branchStatus.pending")}:</span>
                      <strong>{branch.pendingTickets}</strong>
                    </div>
                    <div>
                      <span>{t("dashboard.branchStatus.inProgress")}:</span>
                      <strong>{branch.inProgressTickets}</strong>
                    </div>
                    <div>
                      <span>{t("dashboard.branchStatus.critical")}:</span>
                      <strong style={{ color: "var(--error)" }}>{branch.criticalTickets}</strong>
                    </div>
                    <div>
                      <span>{t("dashboard.branchStatus.total")}:</span>
                      <strong>{branch.totalTickets}</strong>
                    </div>
                  </div>
                </motion.div>
              )}
              {branch.status === "critical" && (
                <motion.div
                  className="branch-status-item__pulse"
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                />
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

