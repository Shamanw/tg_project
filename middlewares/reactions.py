from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Any, Dict

class ReactionTypeFixMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: Dict[str, Any]):
        update_data = event.to_python()
        if "message_reaction_count" in update_data:
            mrc = update_data["message_reaction_count"]
            if "reactions" in mrc and isinstance(mrc["reactions"], list):
                for reaction in mrc["reactions"]:
                    if isinstance(reaction.get("type"), dict) and reaction["type"].get("type") == "paid":
                        return None
        fixed_update = Update(**update_data)
        return await handler(event, data)
