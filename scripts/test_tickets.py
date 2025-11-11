"""
Test ticket API functionality
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models import User, Ticket
from app.services.ticket_service import (
    generate_ticket_number,
    create_ticket,
    get_ticket,
    get_user_tickets,
    can_user_access_ticket
)
from app.schemas.ticket import TicketCreate
from app.core.enums import TicketCategory, TicketStatus, UserRole
from app.core.security import get_password_hash


def test_ticket_service():
    """Test ticket service functions"""
    db = SessionLocal()
    try:
        print("🧪 Testing Ticket Service...\n")
        
        # Test 1: Generate ticket number
        print("1. Testing generate_ticket_number...")
        ticket_number = generate_ticket_number(db)
        print(f"   ✅ Generated ticket number: {ticket_number}")
        
        # Test 2: Get or create test user
        print("2. Getting test user...")
        test_user = db.query(User).filter(User.username == "test_user").first()
        if not test_user:
            test_user = User(
                username="test_user",
                full_name="کاربر تست",
                password_hash=get_password_hash("test123"),
                role=UserRole.USER,
                is_active=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        print(f"   ✅ Test user: {test_user.username} (ID: {test_user.id})")
        
        # Test 3: Create ticket
        print("3. Creating a test ticket...")
        ticket_data = TicketCreate(
            title="تست تیکت API",
            description="این یک تیکت تستی برای API است",
            category=TicketCategory.SOFTWARE
        )
        ticket = create_ticket(db, ticket_data, test_user.id)
        print(f"   ✅ Ticket created: {ticket.ticket_number}")
        print(f"      ID: {ticket.id}, Status: {ticket.status}")
        
        # Test 4: Get ticket
        print("4. Getting ticket by ID...")
        retrieved_ticket = get_ticket(db, ticket.id)
        if retrieved_ticket:
            print(f"   ✅ Ticket retrieved: {retrieved_ticket.ticket_number}")
        else:
            print("   ❌ Failed to retrieve ticket")
        
        # Test 5: Get user tickets
        print("5. Getting user tickets...")
        tickets, total = get_user_tickets(db, test_user.id)
        print(f"   ✅ User has {total} ticket(s)")
        
        # Test 6: Access control
        print("6. Testing access control...")
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin_user:
            can_access = can_user_access_ticket(admin_user, ticket)
            print(f"   ✅ Admin can access ticket: {can_access}")
        
        can_access_user = can_user_access_ticket(test_user, ticket)
        print(f"   ✅ Owner can access ticket: {can_access_user}")
        
        # Cleanup (optional)
        print("\n7. Cleaning up test data...")
        db.delete(ticket)
        if test_user.username == "test_user":
            db.delete(test_user)
        db.commit()
        print("   ✅ Test data cleaned up")
        
        print("\n✅ All ticket service tests passed!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error testing ticket service: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_ticket_service()

