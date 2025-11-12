"""
API client for Telegram Bot to communicate with FastAPI
"""
import httpx
from typing import Any, Dict, List, Optional
from app.telegram_bot.config import API_BASE_URL
from app.core.enums import TicketCategory


class APIClient:
    """Client for making API requests"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def login(self, username: str, password: str) -> Optional[str]:
        """
        Login and get access token
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Access token or None if failed
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/login",
                data={
                    "username": username,
                    "password": password
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
            return None
        except Exception:
            return None

    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user profile.
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    async def upload_ticket_attachment(
        self,
        token: str,
        ticket_id: int,
        file_name: str,
        file_bytes: bytes,
        content_type: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Upload an attachment for a ticket.

        Returns uploaded attachment metadata or None if failed.
        """
        files = {
            "file": (file_name, file_bytes, content_type),
        }
        try:
            response = await self.client.post(
                f"{self.base_url}/api/files/upload",
                headers={"Authorization": f"Bearer {token}"},
                params={"ticket_id": ticket_id},
                files=files,
            )
            if response.status_code in (200, 201):
                return response.json()
            return None
        except Exception:
            return None
    
    async def get_user_tickets(
        self,
        token: str,
        page: int = 1,
        page_size: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's tickets
        
        Args:
            token: Access token
            page: Page number
            page_size: Page size
            
        Returns:
            Tickets data or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/tickets",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "page": page,
                    "page_size": page_size
                }
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    async def get_ticket_by_number(
        self,
        token: str,
        ticket_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get ticket by ticket number
        
        Args:
            token: Access token
            ticket_number: Ticket number (e.g., T-20241111-0001)
            
        Returns:
            Ticket data or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/tickets/number/{ticket_number}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    async def get_ticket_by_id(
        self,
        token: str,
        ticket_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get ticket by ID
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            
        Returns:
            Ticket data or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/tickets/{ticket_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    async def get_branches(self, token: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of branches
        
        Args:
            token: Access token
            
        Returns:
            List of branches or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/branches",
                headers={"Authorization": f"Bearer {token}"},
                params={"is_active": True}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    async def create_ticket(
        self,
        token: str,
        title: str,
        description: str,
        category: TicketCategory,
        branch_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new ticket
        
        Args:
            token: Access token
            title: Ticket title
            description: Ticket description
            category: Ticket category
            branch_id: Branch ID (optional)
            
        Returns:
            Ticket data or None if failed
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            json_data = {
                "title": title,
                "description": description,
                "category": category.value
            }
            if branch_id:
                json_data["branch_id"] = branch_id
            
            response = await self.client.post(
                f"{self.base_url}/api/tickets",
                headers={"Authorization": f"Bearer {token}"},
                json=json_data
            )
            if response.status_code == 201:
                return response.json()
            
            # Log error details
            error_detail = None
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", str(error_data))
            except Exception:
                error_detail = response.text
            
            # Parse validation errors for better user feedback
            error_message = None
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "detail" in error_data:
                        details = error_data["detail"]
                        if isinstance(details, list) and len(details) > 0:
                            first_error = details[0]
                            field = first_error.get("loc", [])[-1] if first_error.get("loc") else "field"
                            msg = first_error.get("msg", "Validation error")
                            error_message = f"{field}: {msg}"
                except Exception:
                    pass
            
            logger.error(
                f"Failed to create ticket: status={response.status_code}, "
                f"detail={error_detail}, title={title[:50]}, category={category.value}"
            )
            return None
        except Exception as e:
            logger.exception(f"Exception while creating ticket: {e}")
            return None

    async def link_telegram_account(
        self,
        token: str,
        chat_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> bool:
        """Inform backend about Telegram chat id for current user."""
        try:
            payload: Dict[str, Any] = {"chat_id": chat_id}
            if username:
                payload["username"] = username
            if first_name:
                payload["first_name"] = first_name
            if last_name:
                payload["last_name"] = last_name

            response = await self.client.post(
                f"{self.base_url}/api/auth/link-telegram",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            return response.status_code in (200, 201)
        except Exception:
            return False

