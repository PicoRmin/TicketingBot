import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { BellIcon } from "./icons";
import { useNotificationsQuery } from "../hooks/useNotificationsQuery";
import { dropdownVariants, listItemVariants, microButtonVariants } from "../lib/motion";

export function NotificationBell() {
  const { notifications, unreadCount, loading, refresh, markAllAsRead } = useNotificationsQuery();
  const [open, setOpen] = useState(false);
  const { t } = useTranslation();

  const toggle = () => setOpen((prev) => !prev);
  const ariaLabel = t("notifications.ariaLabel", { defaultValue: "Notifications" });

  return (
    <div className="notification-bell">
      <motion.button
        type="button"
        className="notification-bell__button secondary"
        onClick={toggle}
        aria-label={ariaLabel}
        variants={microButtonVariants}
        initial="rest"
        whileHover="hover"
        whileTap="tap"
      >
        <BellIcon className="notification-bell__icon" />
        {unreadCount > 0 && <span className="notification-bell__badge">{unreadCount}</span>}
      </motion.button>
      <AnimatePresence>
      {open && (
          <motion.div
            className="notification-bell__dropdown"
            variants={dropdownVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            role="menu"
            aria-label={ariaLabel}
          >
          <div className="notification-bell__header">
              <span>{t("notifications.title")}</span>
            <div style={{ display: "flex", gap: 8 }}>
                <motion.button
                  className="secondary"
                  style={{ padding: "4px 8px", fontSize: 12 }}
                  onClick={refresh}
                  disabled={loading}
                  variants={microButtonVariants}
                  whileHover="hover"
                  whileTap="tap"
                  initial="rest"
                >
                  {loading ? t("notifications.loading") : t("notifications.refresh")}
                </motion.button>
              {unreadCount > 0 && (
                  <motion.button
                    className="secondary"
                    style={{ padding: "4px 8px", fontSize: 12 }}
                    onClick={markAllAsRead}
                    variants={microButtonVariants}
                    whileHover="hover"
                    whileTap="tap"
                    initial="rest"
                  >
                    {t("notifications.markAll")}
                  </motion.button>
              )}
            </div>
          </div>
          <div className="notification-bell__list">
              {notifications.length === 0 && !loading && <p className="notification-bell__empty">{t("notifications.empty")}</p>}
            {loading && (
              <div className="notification-bell__loading">
                <div className="loading" />
              </div>
            )}
              {notifications.map((notif, index) => (
                <motion.div
                  key={notif.id}
                  className={`notification-item notification-item--${notif.severity || "info"}`}
                  variants={listItemVariants(index)}
                  initial="hidden"
                  animate="visible"
                >
                <div className="notification-item__title">
                  {notif.title}
                  {!notif.read && <span className="notification-item__dot" />}
                </div>
                <div className="notification-item__body">{notif.body}</div>
                  <div className="notification-item__time">
                    {new Date(notif.created_at).toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" })}
              </div>
                </motion.div>
            ))}
          </div>
          </motion.div>
      )}
      </AnimatePresence>
    </div>
  );
}

