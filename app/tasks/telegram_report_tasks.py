"""Background task that sends summaries to the Telegram admin group."""
import asyncio
import logging
from datetime import datetime, timedelta

from app.config import settings
from app.database import SessionLocal
from app.services.notification_service import notify_admin_group
from app.services.report_service import (
    tickets_overview,
    tickets_by_status,
    tickets_by_priority,
    sla_compliance_report,
    average_response_time_hours,
)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


async def send_daily_admin_report() -> None:
    """Gather KPIs and send a daily summary to the admin Telegram group."""

    if not settings.TELEGRAM_ADMIN_GROUP_ID:
        logger.debug("Admin group ID is not configured; skipping daily report")
        return

    db: Session = SessionLocal()
    try:
        overview = tickets_overview(db)
        status_counts = tickets_by_status(db)
        priority_counts = tickets_by_priority(db)
        sla_summary = sla_compliance_report(db)
        avg_response = average_response_time_hours(db)

        today_label = datetime.now().strftime("%Y-%m-%d")
        lines = [
            "📊 گزارش روزانه مدیران سیستم",
            f"🗓 تاریخ: {today_label}",
            "",
            f"✅ مجموع تیکت‌ها: {overview.get('total', 0)}",
        ]

        if status_counts:
            status_line = " | ".join(
                f"{status_label(status)}: {count}" for status, count in status_counts.items()
            )
            lines.append(status_line)

        if priority_counts:
            top_priorities = sorted(
                priority_counts.items(), key=lambda item: -item[1]
            )[:3]
            priority_line = " | ".join(f"{priority}: {count}" for priority, count in top_priorities)
            lines.append(f"🎯 اولویت‌های پرتکرار: {priority_line}")

        if sla_summary:
            lines.append(
                """🕒 SLA:
• پاسخ به‌موقع: {response_on_time}/{total}
• حل به‌موقع: {resolution_on_time}/{total}""".strip().format(
                    response_on_time=sla_summary.get("response_on_time", 0),
                    resolution_on_time=sla_summary.get("resolution_on_time", 0),
                    total=sla_summary.get("total_tickets_with_sla", 0),
                )
            )

        if avg_response is not None:
            lines.append(f"⏱ میانگین زمان پاسخ: {avg_response:.2f} ساعت")

        message = "\n".join(lines)
        await notify_admin_group(message)
        logger.info("Daily admin report dispatched")
    except Exception as exc:
        logger.error("Failed to send daily admin report: %s", exc, exc_info=True)
    finally:
        db.close()


def status_label(status_key: str) -> str:
    mapping = {
        "pending": "در انتظار",
        "in_progress": "در حال انجام",
        "resolved": "حل شده",
        "closed": "بسته شده",
    }
    return mapping.get(status_key.lower(), status_key)


async def _scheduler_loop() -> None:
    hour = max(0, min(23, settings.TELEGRAM_ADMIN_DAILY_REPORT_HOUR))
    while True:
        now = datetime.utcnow()
        target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        logger.debug("Next admin report scheduled in %.1f seconds", wait_seconds)
        await asyncio.sleep(wait_seconds)
        await send_daily_admin_report()


def start_daily_report_scheduler() -> None:
    if not settings.TELEGRAM_ADMIN_DAILY_REPORT_ENABLED or not settings.TELEGRAM_ADMIN_GROUP_ID:
        logger.info("Daily Telegram report disabled (missing config)")
        return

    try:
        asyncio.create_task(_scheduler_loop())
        logger.info(
            "Telegram daily report scheduler started (hour=%s)",
            settings.TELEGRAM_ADMIN_DAILY_REPORT_HOUR,
        )
    except Exception as exc:
        logger.error("Failed to start daily Telegram report scheduler: %s", exc, exc_info=True)
"\"\"\"\n+Background task that sends summaries to the Telegram admin group.\n+"\"\"\"\n+import asyncio\n+import logging\n+from datetime import datetime, timedelta\n+from typing import Optional\n+\n+from app.config import settings\n+from app.database import SessionLocal\n+from app.services.notification_service import notify_admin_group\n+from app.services.report_service import (\n+    tickets_overview,\n+    tickets_by_status,\n+    tickets_by_priority,\n+    sla_compliance_report,\n+    average_response_time_hours,\n+)\n+from sqlalchemy.orm import Session\n+\n+logger = logging.getLogger(__name__)\n+\n+\n+async def send_daily_admin_report() -> None:\n+    \"\"\"Gather KPIs and send a daily summary to the admin Telegram group.\"\"\"\n+\n+    if not settings.TELEGRAM_ADMIN_GROUP_ID:\n+        logger.debug(\"Admin group ID is not configured; skipping daily report\")\n+        return\n+\n+    db: Session = SessionLocal()\n+    try:\n+        overview = tickets_overview(db)\n+        status_counts = tickets_by_status(db)\n+        priority_counts = tickets_by_priority(db)\n+        sla_summary = sla_compliance_report(db)\n+        avg_response = average_response_time_hours(db)\n+\n+        today_label = datetime.now().strftime(\"%Y-%m-%d\")\n+        lines = [\n+            \"📊 گزارش روزانه مدیران سیستم\", \n+            f\"🗓 تاریخ: {today_label}\",\n+            \"\",\n+            f\"✅ مجموع تیکت‌ها: {overview.get('total', 0)}\",\n+        ]\n+\n+        if status_counts:\n+            status_line = \" | \".join(\n+                f\"{status_label(status)}: {count}\" for status, count in status_counts.items()\n+            )\n+            lines.append(status_line)\n+\n+        if priority_counts:\n+            top_priorities = sorted(\n+                priority_counts.items(), key=lambda item: -item[1]\n+            )[:3]\n+            priority_line = \" | \".join(f\"{priority}: {count}\" for priority, count in top_priorities)\n+            lines.append(f\"🎯 اولویت‌های پرتکرار: {priority_line}\")\n+\n+        if sla_summary:\n+            lines.append(\n+                \"\"\"\n+🕒 SLA:\n+• پاسخ به‌موقع: {response_on_time}/{total}\n+• حل به‌موقع: {resolution_on_time}/{total}\n+\"\"\".strip().format(\n+                    response_on_time=sla_summary.get(\"response_on_time\", 0),\n+                    resolution_on_time=sla_summary.get(\"resolution_on_time\", 0),\n+                    total=sla_summary.get(\"total_tickets_with_sla\", 0),\n+                )\n+            )\n+\n+        if avg_response is not None:\n+            lines.append(f\"⏱ میانگین زمان پاسخ: {avg_response:.2f} ساعت\")\n+\n+        message = \"\\n\".join(lines)\n+        await notify_admin_group(message)\n+        logger.info(\"Daily admin report dispatched\")\n+    except Exception as exc:\n+        logger.error(\"Failed to send daily admin report: %s\", exc, exc_info=True)\n+    finally:\n+        db.close()\n+\n+\n+def status_label(status_key: str) -> str:\n+    mapping = {\n+        \"pending\": \"در انتظار\",\n+        \"in_progress\": \"در حال انجام\",\n+        \"resolved\": \"حل شده\",\n+        \"closed\": \"بسته شده\",\n+    }\n+    return mapping.get(status_key.lower(), status_key)\n+\n+\n+async def _scheduler_loop() -> None:\n+    hour = max(0, min(23, settings.TELEGRAM_ADMIN_DAILY_REPORT_HOUR))\n+    while True:\n+        now = datetime.utcnow()\n+        target = now.replace(hour=hour, minute=0, second=0, microsecond=0)\n+        if target <= now:\n+            target += timedelta(days=1)\n+        wait_seconds = (target - now).total_seconds()\n+        logger.debug(\"Next admin report scheduled in %.1f seconds\", wait_seconds)\n+        await asyncio.sleep(wait_seconds)\n+        await send_daily_admin_report()\n+\n+\n+def start_daily_report_scheduler() -> None:\n+    if not settings.TELEGRAM_ADMIN_DAILY_REPORT_ENABLED or not settings.TELEGRAM_ADMIN_GROUP_ID:\n+        logger.info(\"Daily Telegram report disabled (missing config)\")\n+        return\n+\n+    try:\n+        asyncio.create_task(_scheduler_loop())\n+        logger.info(\"Telegram daily report scheduler started (hour=%s)\", settings.TELEGRAM_ADMIN_DAILY_REPORT_HOUR)\n+    except Exception as exc:\n+        logger.error(\"Failed to start daily Telegram report scheduler: %s\", exc, exc_info=True)\n*** End Patch*** End Patch

