from fastapi import APIRouter, Depends

from src.services.contact import ContactService
from src.schemas.contacts import (
    AddContactRequest,
    UpdateLabel,
    ContactOut,
)
from src.db.deps import get_current_user_id


router = APIRouter(prefix="/contacts")

service = ContactService()


@router.post("/", response_model=ContactOut)
async def add_contact(
    data: AddContactRequest,
    user_id: int = Depends(get_current_user_id),
):
    return await service.add_contact(
        user_id=user_id,
        phone=data.phone,
        label=data.label,
    )


@router.get("/", response_model=list[ContactOut])
async def get_contacts(
    user_id: int = Depends(get_current_user_id),
):
    return await service.get_contacts(user_id)


@router.patch("/{contact_id}", response_model=ContactOut)
async def update_label(
    contact_id: str,
    data: UpdateLabel,
):
    return await service.update_label(
        contact_id,
        data.label,
    )


@router.delete("/{contact_id}")
async def delete_contact(contact_id: str):
    return await service.delete_contact(contact_id)
