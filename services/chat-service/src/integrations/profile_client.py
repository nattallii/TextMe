import httpx


async def get_user_by_phone(phone: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "http://profile-service/api/v1/users/search",
            params={"phone": phone}
        )
        return res.json()