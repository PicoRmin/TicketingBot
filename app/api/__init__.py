"""
API routes
"""
from app.api import auth, tickets, files, branches, comments, reports, users, settings, branch_infrastructure, departments, priorities, sla, automation, time_tracker

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
]
