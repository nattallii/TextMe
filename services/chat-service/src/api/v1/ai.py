from fastapi import APIRouter
from pydantic import BaseModel

from src.services.ai import AIService

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)

service = AIService()


class SmartReplySchema(BaseModel):
    message: str


@router.post("/smart-reply")
async def smart_reply(
    data: SmartReplySchema,
):
    replies = await (
        service.generate_smart_replies(
            data.message
        )
    )

    return {
        "replies": replies
    }