from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactRequest, ContactResponse
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=ContactResponse)
async def send_contact_message(
    contact_data: ContactRequest,
    db: Session = Depends(get_db)
):
    """Send contact/support form"""
    try:
        import uuid
        
        contact_message = ContactMessage(
            id=uuid.uuid4(),
            full_name=contact_data.full_name,
            email=contact_data.email,
            subject=contact_data.subject,
            message=contact_data.message,
            is_resolved=False,
            created_at=datetime.utcnow()
        )
        
        db.add(contact_message)
        db.commit()
        db.refresh(contact_message)
        
        return ContactResponse(
            id=str(contact_message.id),
            status="received"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send contact message: {str(e)}"
        )
