import { useState } from "react";
import { BellIcon } from "./icons";
import { useNotifications } from "../hooks/useNotifications";

export function NotificationBell() {
  const { notifications, unreadCount, loading, refresh, markAllAsRead } = useNotifications();
  const [open, setOpen] = useState(false);

  const toggle = () => setOpen((prev) => !prev);

  return (
    <div className="notification-bell">
      <button
        type="button"
        className="notification-bell__button secondary"
        onClick={toggle}
        aria-label="Notifications"
      >
        <BellIcon className="notification-bell__icon" />
        {unreadCount > 0 && <span className="notification-bell__badge">{unreadCount}</span>}
      </button>
      {open && (
        <div className="notification-bell__dropdown">
          <div className="notification-bell__header">
            <span>اعلان‌ها</span>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="secondary" style={{ padding: "4px 8px", fontSize: 12 }} onClick={refresh} disabled={loading}>
                {loading ? "..." : "بروزرسانی"}
              </button>
              {unreadCount > 0 && (
                <button className="secondary" style={{ padding: "4px 8px", fontSize: 12 }} onClick={markAllAsRead}>
                  خواندم
                </button>
              )}
            </div>
          </div>
          <div className="notification-bell__list">
            {notifications.length === 0 && !loading && <p className="notification-bell__empty">اعلان جدیدی وجود ندارد.</p>}
            {loading && (
              <div className="notification-bell__loading">
                <div className="loading" />
              </div>
            )}
            {notifications.map((notif) => (
              <div key={notif.id} className={`notification-item notification-item--${notif.severity || "info"}`}>
                <div className="notification-item__title">
                  {notif.title}
                  {!notif.read && <span className="notification-item__dot" />}
                </div>
                <div className="notification-item__body">{notif.body}</div>
                <div className="notification-item__time">{new Date(notif.created_at).toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" })}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

