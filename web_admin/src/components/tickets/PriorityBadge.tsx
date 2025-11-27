import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";

type PriorityBadgeProps = {
  priority: string;
  slaDeadline?: Date | null;
  slaStatus?: "on_time" | "warning" | "breached" | null;
  className?: string;
};

export function PriorityBadge({ priority, slaDeadline, slaStatus, className = "" }: PriorityBadgeProps) {
  const { t } = useTranslation();
  const badgeRef = useRef<HTMLSpanElement>(null);
  const [timeRemaining, setTimeRemaining] = useState<string | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const priorityMap: Record<string, { text: string; class: string; emoji: string }> = {
    critical: { text: t("tickets.priority.critical"), class: "priority-critical", emoji: "🔴" },
    high: { text: t("tickets.priority.high"), class: "priority-high", emoji: "🟠" },
    medium: { text: t("tickets.priority.medium"), class: "priority-medium", emoji: "🟡" },
    low: { text: t("tickets.priority.low"), class: "priority-low", emoji: "🟢" },
  };

  const p = priorityMap[priority] || { text: priority, class: "priority-medium", emoji: "🟡" };

  // Calculate time remaining for SLA
  useEffect(() => {
    if (!slaDeadline) {
      setTimeRemaining(null);
      return;
    }

    const updateTimeRemaining = () => {
      const now = new Date();
      const diff = slaDeadline.getTime() - now.getTime();

      if (diff < 0) {
        setTimeRemaining(t("tickets.sla.breached"));
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

      if (hours > 0) {
        setTimeRemaining(`${hours} ${t("tickets.sla.hours")} ${minutes} ${t("tickets.sla.minutes")}`);
      } else if (minutes > 0) {
        setTimeRemaining(`${minutes} ${t("tickets.sla.minutes")}`);
      } else {
        setTimeRemaining(t("tickets.sla.lessThanMinute"));
      }
    };

    updateTimeRemaining();
    const interval = setInterval(updateTimeRemaining, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [slaDeadline, t]);

  // Shake animation for critical priority
  const shakeVariants = {
    shake: {
      x: [0, -4, 4, -4, 4, -2, 2, 0],
      transition: {
        duration: 0.5,
        repeat: Infinity,
        repeatDelay: 3,
      },
    },
  };

  // Pulse animation for high priority
  const pulseVariants = {
    pulse: {
      scale: [1, 1.05, 1],
      opacity: [1, 0.9, 1],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  const badgeContent = (
    <span
      ref={badgeRef}
      className={`badge ${p.class} ${className} ${slaStatus === "breached" || slaStatus === "warning" ? "priority-sla-alert" : ""}`}
      title={p.text}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {p.emoji} {p.text}
    </span>
  );

  // Apply animations based on priority
  if (priority === "critical") {
    return (
      <motion.span variants={shakeVariants} animate="shake" style={{ display: "inline-block" }}>
        {badgeContent}
        {showTooltip && timeRemaining && (
          <motion.div
            className="priority-tooltip"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <div className="priority-tooltip__title">{t("tickets.sla.timeRemaining")}</div>
            <div className="priority-tooltip__time">{timeRemaining}</div>
          </motion.div>
        )}
      </motion.span>
    );
  }

  if (priority === "high") {
    return (
      <motion.span variants={pulseVariants} animate="pulse" style={{ display: "inline-block" }}>
        {badgeContent}
        {showTooltip && timeRemaining && (
          <motion.div
            className="priority-tooltip"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <div className="priority-tooltip__title">{t("tickets.sla.timeRemaining")}</div>
            <div className="priority-tooltip__time">{timeRemaining}</div>
          </motion.div>
        )}
      </motion.span>
    );
  }

  return (
    <>
      {badgeContent}
      {showTooltip && timeRemaining && (
        <motion.div
          className="priority-tooltip"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <div className="priority-tooltip__title">{t("tickets.sla.timeRemaining")}</div>
          <div className="priority-tooltip__time">{timeRemaining}</div>
        </motion.div>
      )}
    </>
  );
}

