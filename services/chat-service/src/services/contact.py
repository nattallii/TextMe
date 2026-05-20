import httpx
from fastapi import HTTPException
from src.repository.contact import ContactRepository
from src.services.chat import ChatService



class ContactService:
    def __init__(self):
        self.repo = ContactRepository()
        self.chat_service = ChatService()

    async def add_contact(
            self,
            user_id: int,
            phone: str,
            label: str | None,
    ):

        user = await self.get_user_by_phone(phone)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User with this phone not found"
            )

        contact_id = user["user_id"]

        if contact_id == user_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot add yourself"
            )

        existing_contact = await self.repo.get_contact(
            owner_id=user_id,
            contact_id=contact_id,
        )

        if existing_contact:
            raise HTTPException(
                status_code=409,
                detail="User already in contacts"
            )

        # await self.chat_service.create_private_chat(
        #     user_id,
        #     [contact_id]
        # )

        contact = await self.repo.create(
            owner_id=user_id,
            contact_id=contact_id,
            label=label,
        )

        return {
            "id": contact.id,
            "label": contact.label,
            "user": user,
        }

    async def get_user_from_profile(self, user_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://profile:8000/api/v1/users/{user_id}"
            )

            if response.status_code != 200:
                print("PROFILE ERROR:", response.status_code, response.text)
                return None

            return response.json()

    async def get_contacts(self, user_id: int):
        contacts = await self.repo.get_users_contacts(user_id)

        result = []

        for contact in contacts:
            user = await self.get_user_from_profile(contact.contact_id)

            result.append({
                "id": contact.id,
                "label": contact.label,
                "user": user
            })

        return result

    async def update_label(self, contact_id: str, label: str):
        return await self.repo.update_label(contact_id, label)

    async def delete_contact(self, contact_id: str):
        return await self.repo.delete_contact(contact_id)


    async def get_user_by_phone(self, phone: str):

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://profile:8000/api/v1/users/search",
                params={"phone": phone}
            )

            if response.status_code != 200:
                return None

            return response.json()

