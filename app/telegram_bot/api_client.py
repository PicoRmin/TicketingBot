"""
API client for Telegram Bot to communicate with FastAPI
"""
import httpx
import logging
from typing import Any, Dict, List, Optional
from app.telegram_bot.config import API_BASE_URL
from app.core.enums import TicketCategory

logger = logging.getLogger(__name__)


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
    
    async def get_file_settings(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get file upload settings from API
        
        Args:
            token: Access token
            
        Returns:
            File settings dictionary or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/settings/file",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get file settings: {e}")
            return None
    
    async def get_ticket_attachments_count(
        self,
        token: str,
        ticket_id: int
    ) -> Optional[Dict[str, int]]:
        """
        Get count of images and documents for a ticket
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            
        Returns:
            Dictionary with image_count and document_count, or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/files/ticket/{ticket_id}/list",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                attachments = response.json()
                from app.services.file_service import ALLOWED_IMAGE_TYPES, ALLOWED_DOCUMENT_TYPES
                image_count = sum(1 for att in attachments if att.get("file_type") in ALLOWED_IMAGE_TYPES)
                document_count = sum(1 for att in attachments if att.get("file_type") in ALLOWED_DOCUMENT_TYPES)
                return {"image_count": image_count, "document_count": document_count}
            return None
        except Exception as e:
            logger.error(f"Failed to get ticket attachments count: {e}")
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
        try:
            # Prepare multipart form data
            files = {
                "file": (file_name, file_bytes, content_type),
            }
            headers = {
                "Authorization": f"Bearer {token}",
            }
            
            logger.debug(
                f"Uploading file: ticket_id={ticket_id}, file_name={file_name}, "
                f"size={len(file_bytes)}, content_type={content_type}"
            )
            
            response = await self.client.post(
                f"{self.base_url}/api/files/upload",
                headers=headers,
                params={"ticket_id": ticket_id},
                files=files,
                timeout=60.0,  # Increase timeout for large files
            )
            
            logger.debug(f"Upload response: status={response.status_code}")
            
            if response.status_code in (200, 201):
                result = response.json()
                logger.info(f"File uploaded successfully: ticket_id={ticket_id}, file_name={file_name}")
                return result
            
            # Log error details for debugging
            error_detail = None
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", str(error_data))
                logger.error(
                    f"File upload failed: status={response.status_code}, "
                    f"ticket_id={ticket_id}, file_name={file_name}, detail={error_detail}"
                )
            except Exception:
                error_text = response.text[:500] if response.text else "No response body"
                logger.error(
                    f"File upload failed: status={response.status_code}, "
                    f"ticket_id={ticket_id}, file_name={file_name}, response={error_text}"
                )
            return None
        except httpx.TimeoutException as e:
            logger.error(f"File upload timeout: ticket_id={ticket_id}, file_name={file_name}, error={e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"File upload request error: ticket_id={ticket_id}, file_name={file_name}, error={e}")
            return None
        except Exception as e:
            logger.exception(f"Exception during file upload: ticket_id={ticket_id}, file_name={file_name}, error={e}")
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
        branch_id: Optional[int] = None,
        department_id: Optional[int] = None,
        priority: Optional[str] = None
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
            if department_id:
                json_data["department_id"] = department_id
            if priority:
                json_data["priority"] = priority
            
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

    async def get_infrastructure(self, token: str, infrastructure_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single infrastructure record."""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/branch-infrastructure/{infrastructure_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                return response.json()
            logger.warning("Failed to fetch infrastructure %s: status=%s", infrastructure_id, response.status_code)
            return None
        except Exception as exc:
            logger.error("Error fetching infrastructure %s: %s", infrastructure_id, exc)
            return None

    async def list_infrastructure(self, token: str, branch_id: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """List infrastructure entries, optionally filtered by branch."""
        try:
            params = {}
            if branch_id:
                params["branch_id"] = branch_id
            response = await self.client.get(
                f"{self.base_url}/api/branch-infrastructure",
                headers={"Authorization": f"Bearer {token}"},
                params=params or None,
            )
            if response.status_code == 200:
                return response.json()
            logger.warning("Failed to list infrastructure: status=%s", response.status_code)
            return None
        except Exception as exc:
            logger.error("Error listing infrastructure: %s", exc)
            return None

    async def create_infrastructure(self, token: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create new infrastructure record."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/branch-infrastructure",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            if response.status_code in (200, 201):
                return response.json()
            logger.warning("Failed to create infrastructure: status=%s detail=%s", response.status_code, response.text)
            return None
        except Exception as exc:
            logger.error("Error creating infrastructure: %s", exc)
            return None

    async def update_infrastructure(self, token: str, infrastructure_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing infrastructure record."""
        try:
            response = await self.client.put(
                f"{self.base_url}/api/branch-infrastructure/{infrastructure_id}",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            if response.status_code == 200:
                return response.json()
            logger.warning("Failed to update infrastructure %s: status=%s detail=%s", infrastructure_id, response.status_code, response.text)
            return None
        except Exception as exc:
            logger.error("Error updating infrastructure %s: %s", infrastructure_id, exc)
            return None
    
    async def update_ticket_status(
        self,
        token: str,
        ticket_id: int,
        status: str,
        comment: Optional[str] = None,
        is_internal: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Update ticket status
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            status: New status (pending, in_progress, resolved, closed)
            
        Returns:
            Updated ticket data or None if failed
        """
        try:
            payload: Dict[str, Any] = {"status": status}
            if comment:
                payload["comment"] = comment
                payload["is_internal"] = is_internal

            response = await self.client.patch(
                f"{self.base_url}/api/tickets/{ticket_id}/status",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to update ticket status: {e}")
            return None

    async def get_ticket_comments(
        self,
        token: str,
        ticket_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get comments for a ticket
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            
        Returns:
            List of comments or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/comments/ticket/{ticket_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get ticket comments: {e}")
            return None

    async def add_comment(
        self,
        token: str,
        ticket_id: int,
        comment: str,
        is_internal: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Add a comment to a ticket
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            comment: Comment text
            is_internal: Whether comment is internal (admin only)
            
        Returns:
            Created comment data or None if failed
        """
        try:
            payload = {
                "ticket_id": ticket_id,
                "comment": comment,
                "is_internal": is_internal
            }
            response = await self.client.post(
                f"{self.base_url}/api/comments",
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            if response.status_code in (200, 201):
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            return None

    async def get_ticket_history(
        self,
        token: str,
        ticket_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get ticket history
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            
        Returns:
            List of history entries or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/tickets/{ticket_id}/history",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get ticket history: {e}")
            return None

    async def get_ticket_attachments(
        self,
        token: str,
        ticket_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get attachments for a ticket
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            
        Returns:
            List of attachments or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/files/ticket/{ticket_id}/list",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get ticket attachments: {e}")
            return None

    async def update_ticket_priority(
        self,
        token: str,
        ticket_id: int,
        priority: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update ticket priority
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            priority: New priority (critical, high, medium, low)
            
        Returns:
            Updated ticket data or None if failed
        """
        try:
            payload = {"priority": priority}
            response = await self.client.put(
                f"{self.base_url}/api/tickets/{ticket_id}",
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to update ticket priority: {e}")
            return None

    async def assign_ticket(
        self,
        token: str,
        ticket_id: int,
        assigned_to_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Assign ticket to a specialist
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            assigned_to_id: User ID to assign to
            
        Returns:
            Updated ticket data or None if failed
        """
        try:
            payload = {"assigned_to_id": assigned_to_id}
            response = await self.client.patch(
                f"{self.base_url}/api/tickets/{ticket_id}/assign",
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to assign ticket: {e}")
            return None

    async def get_users(
        self,
        token: str,
        role: Optional[str] = None,
        branch_id: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of users (for assignment)
        
        Args:
            token: Access token
            role: Filter by role (optional)
            branch_id: Filter by branch (optional)
            
        Returns:
            List of users or None if failed
        """
        try:
            params = {}
            if role:
                params["role"] = role
            if branch_id:
                params["branch_id"] = branch_id
            response = await self.client.get(
                f"{self.base_url}/api/users",
                headers={"Authorization": f"Bearer {token}"},
                params=params or None
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return None

    async def search_tickets(
        self,
        token: str,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        ticket_number: Optional[str] = None,
        search_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search tickets with filters
        
        Args:
            token: Access token
            page: Page number
            page_size: Page size
            status: Filter by status
            priority: Filter by priority
            category: Filter by category
            date_from: Filter from date (YYYY-MM-DD)
            date_to: Filter to date (YYYY-MM-DD)
            ticket_number: Filter by ticket number
            search_text: Search in title and description
            
        Returns:
            Tickets data or None if failed
        """
        try:
            params = {
                "page": page,
                "page_size": page_size
            }
            if status:
                params["status"] = status
            if priority:
                params["priority"] = priority
            if category:
                params["category"] = category
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to
            if ticket_number:
                params["ticket_number"] = ticket_number
            
            response = await self.client.get(
                f"{self.base_url}/api/tickets",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )
            if response.status_code == 200:
                data = response.json()
                # Filter by search_text if provided (client-side filtering for now)
                if search_text and data.get("items"):
                    search_lower = search_text.lower()
                    filtered_items = [
                        item for item in data["items"]
                        if search_lower in item.get("title", "").lower() or
                        search_lower in item.get("description", "").lower()
                    ]
                    data["items"] = filtered_items
                    data["total"] = len(filtered_items)
                return data
            return None
        except Exception as e:
            logger.error(f"Failed to search tickets: {e}")
            return None

    async def bulk_action_tickets(
        self,
        token: str,
        ticket_ids: List[int],
        action: str,
        status: Optional[str] = None,
        assigned_to_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Perform bulk action on tickets
        
        Args:
            token: Access token
            ticket_ids: List of ticket IDs
            action: Action type (status, assign, unassign, delete)
            status: New status (for action=status)
            assigned_to_id: User ID (for action=assign)
            
        Returns:
            Bulk action result or None if failed
        """
        try:
            payload = {
                "ticket_ids": ticket_ids,
                "action": action
            }
            if status:
                payload["status"] = status
            if assigned_to_id:
                payload["assigned_to_id"] = assigned_to_id
            
            response = await self.client.post(
                f"{self.base_url}/api/tickets/bulk-action",
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to perform bulk action: {e}")
            return None

    async def get_ticket_sla(
        self,
        token: str,
        ticket_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get SLA log for a ticket
        
        Args:
            token: Access token
            ticket_id: Ticket ID
            
        Returns:
            SLA log data or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/sla/ticket/{ticket_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get ticket SLA: {e}")
            return None

    async def get_sla_logs(
        self,
        token: str,
        page: int = 1,
        page_size: int = 50,
        ticket_id: Optional[int] = None,
        sla_rule_id: Optional[int] = None,
        response_status: Optional[str] = None,
        resolution_status: Optional[str] = None,
        escalated: Optional[bool] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get SLA logs with filters
        
        Args:
            token: Access token
            page: Page number
            page_size: Page size
            ticket_id: Filter by ticket ID
            sla_rule_id: Filter by SLA rule ID
            response_status: Filter by response status (on_time, warning, breached)
            resolution_status: Filter by resolution status (on_time, warning, breached)
            escalated: Filter by escalated status
            
        Returns:
            List of SLA logs or None if failed
        """
        try:
            params = {
                "page": page,
                "page_size": page_size
            }
            if ticket_id:
                params["ticket_id"] = ticket_id
            if sla_rule_id:
                params["sla_rule_id"] = sla_rule_id
            if response_status:
                params["response_status"] = response_status
            if resolution_status:
                params["resolution_status"] = resolution_status
            if escalated is not None:
                params["escalated"] = escalated
            
            response = await self.client.get(
                f"{self.base_url}/api/sla/logs",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get SLA logs: {e}")
            return None

    async def get_sla_compliance_report(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get SLA compliance report
        
        Args:
            token: Access token
            
        Returns:
            SLA compliance report data or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/reports/sla-compliance",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get SLA compliance report: {e}")
            return None

    async def get_sla_by_priority_report(
        self,
        token: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get SLA report by priority
        
        Args:
            token: Access token
            
        Returns:
            List of SLA reports by priority or None if failed
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/reports/sla-by-priority",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get SLA by priority report: {e}")
            return None

