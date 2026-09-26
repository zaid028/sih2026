"""
FIREGUARD AI - Emergency Contacts API (Requirement 14)
"""
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import EmergencyContact
from backend.schemas.pydantic_models import (
    EmergencyContactCreateRequest, EmergencyContactResponse
)

router = APIRouter(prefix="/emergency-contacts", tags=["Emergency Contacts"])

@router.get("", response_model=List[EmergencyContactResponse], summary="List emergency contacts")
def list_contacts(db: Session = Depends(get_db)):
    contacts = db.query(EmergencyContact).all()
    return [c.to_dict() for c in contacts]

@router.post("", response_model=EmergencyContactResponse, status_code=201, summary="Create a new emergency contact")
def create_contact(
    req: EmergencyContactCreateRequest,
    db: Session = Depends(get_db)
):
    contact = EmergencyContact(
        id=str(uuid.uuid4()),
        category=req.category,
        name=req.name,
        agency=req.agency or "",
        designation=req.designation or "",
        phone=req.phone,
        email=req.email or "",
        state=req.state or "National",
        district=req.district or "",
        is_primary=req.is_primary if req.is_primary is not None else True
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact.to_dict()

@router.patch("/{id}", response_model=EmergencyContactResponse, summary="Update an emergency contact")
def update_contact(
    id: str = Path(..., example="contact-01"),
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    is_primary: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == id).first()
    if not contact:
        raise HTTPException(
            status_code=404,
            detail={"code": "CONTACT_NOT_FOUND", "message": f"Contact '{id}' not found"}
        )
    if name: contact.name = name
    if phone: contact.phone = phone
    if email: contact.email = email
    if is_primary is not None: contact.is_primary = is_primary
    db.commit()
    db.refresh(contact)
    return contact.to_dict()

@router.delete("/{id}", summary="Delete an emergency contact")
def delete_contact(
    id: str = Path(..., example="contact-01"),
    db: Session = Depends(get_db)
):
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == id).first()
    if not contact:
        raise HTTPException(
            status_code=404,
            detail={"code": "CONTACT_NOT_FOUND", "message": f"Contact '{id}' not found"}
        )
    db.delete(contact)
    db.commit()
    return {"success": True, "message": f"Contact '{id}' removed successfully"}
