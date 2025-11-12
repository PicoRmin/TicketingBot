"""
API routes
"""
from app.api import auth, tickets, files, branches, comments, reports, users

__all__ = [
    "auth",
    "tickets",
    "files",
    "branches",
    "comments",
    "reports",
    "users",
]
