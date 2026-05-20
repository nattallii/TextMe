from fastapi import HTTPException
from src.models.contact import Contact

class ContactRepository():
    async def create(self, owner_id: int, contact_id: int, label: str | None = None):
        existing_contact = await Contact.find_one({
            "owner_id": owner_id,
            "contact_id": contact_id
        })

        if existing_contact:
            return existing_contact

        contact = Contact(
            owner_id=owner_id,
            contact_id=contact_id,
            label=label
        )

        await contact.insert()
        return contact



    async def get_users_contacts(self, user_id: int, ):
        contacts = await Contact.find({
            "owner_id": user_id,
        }).to_list()
        return contacts

    async def update_label(self, contact_id: str, label: str):
        contact = await Contact.find_one(Contact.id == contact_id)

        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

        contact.label = label
        await contact.save()

        return contact


    async def delete_contact(self, contact_id: str):
        contact = await Contact.get(contact_id)
        if contact:
            await contact.delete()
            return contact


    async def get_contact(
            self,
            owner_id: int,
            contact_id: int,
    ):
        return await Contact.find_one({
            "owner_id": owner_id,
            "contact_id": contact_id,
        })