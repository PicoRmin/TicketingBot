"""
API routes
"""
from app.api import auth, tickets, files, branches, comments, reports, users, settings, branch_infrastructure, departments, priorities, sla, automation, time_tracker, custom_fields, notifications, profile, knowledge_base

__all__ = [
    "auth",
    "tickets",
    "files",
    "branches",
    "comments",
    "reports",
    "users",
    "settings",
    "branch_infrastructure",
    "departments",
    "priorities",
    "sla",
    "automation",
    "time_tracker",
    "custom_fields",
    "notifications",
    "profile",
    "knowledge_base",
]
