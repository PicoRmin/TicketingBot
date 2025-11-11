"""
Script to test database models
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models import User, Ticket
from app.core.enums import UserRole, Language, TicketCategory, TicketStatus
from app.core.security import get_password_hash
from datetime import datetime


def test_models():
    """Test database models"""
    db = SessionLocal()
    try:
        print("🧪 Testing database models...\n")
        
        # Test 1: Create a user
        print("1. Creating a test user...")
        test_user = User(
            username="test_user",
            full_name="کاربر تست",
            password_hash=get_password_hash("test123"),
            role=UserRole.USER,
            language=Language.FA,
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"   ✅ User created: ID={test_user.id}, Username={test_user.username}")
        
        # Test 2: Create a ticket
        print("2. Creating a test ticket...")
        test_ticket = Ticket(
            ticket_number="T-20241111-0001",
            title="تست تیکت",
            description="این یک تیکت تستی است",
            category=TicketCategory.SOFTWARE,
            status=TicketStatus.PENDING,
            user_id=test_user.id
        )
        db.add(test_ticket)
        db.commit()
        db.refresh(test_ticket)
        print(f"   ✅ Ticket created: ID={test_ticket.id}, Number={test_ticket.ticket_number}")
        
        # Test 3: Test relationships
        print("3. Testing relationships...")
        user_tickets = db.query(Ticket).filter(Ticket.user_id == test_user.id).all()
        print(f"   ✅ User has {len(user_tickets)} ticket(s)")
        
        ticket_user = test_ticket.user
        print(f"   ✅ Ticket belongs to user: {ticket_user.username}")
        
        # Test 4: Query tests
        print("4. Testing queries...")
        all_users = db.query(User).all()
        all_tickets = db.query(Ticket).all()
        print(f"   ✅ Total users: {len(all_users)}")
        print(f"   ✅ Total tickets: {len(all_tickets)}")
        
        # Test 5: Update ticket status
        print("5. Testing update...")
        test_ticket.status = TicketStatus.IN_PROGRESS
        db.commit()
        db.refresh(test_ticket)
        print(f"   ✅ Ticket status updated to: {test_ticket.status}")
        
        # Cleanup (optional - comment out if you want to keep test data)
        print("\n6. Cleaning up test data...")
        db.delete(test_ticket)
        db.delete(test_user)
        db.commit()
        print("   ✅ Test data cleaned up")
        
        print("\n✅ All tests passed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error testing models: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_models()

