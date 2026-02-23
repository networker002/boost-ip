from aiogram.types import Update, Message, CallbackQuery
from aiogram.fsm.middleware import BaseMiddleware
import time

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, default_rate: float = 1.0):
        self.rate_limit = default_rate
        self.last_request = {}

    async def __call__(
        self,
        handler,
        event: Update,
        data: dict
    ):
        user_id = None

        if event.message and isinstance(event.message, Message):
            user_id = event.message.from_user.id

        elif event.callback_query and isinstance(event.callback_query, CallbackQuery):
            user_id = event.callback_query.from_user.id

        if user_id is None:
            return await handler(event, data)

        current_time = time.time()

        if user_id in self.last_request:
            time_since_last = current_time - self.last_request[user_id]
            if time_since_last < self.rate_limit:

                if event.message:
                    await event.message.answer(
                "Слишком частые запросы! Подождите немного."
            )
                return


        self.last_request[user_id] = current_time

        return await handler(event, data)
