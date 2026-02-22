import asyncio
from aiocache import cached, Cache
from .client import supabase


async def async_execute_supabase_call(callable, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: callable(*args, **kwargs))


@cached(ttl=60, cache=Cache.MEMORY)
async def check_user_group(tg_id: int):
    response = await async_execute_supabase_call(
        lambda: supabase.table("user_groups").select("group_name").eq("tg_id", tg_id).execute()
    )
    return response.data[0] if response.data else None


async def set_user_group(tg_id: int, group_name: str) -> bool:
    result = await async_execute_supabase_call(
        lambda: supabase.table("user_groups").upsert(
            {
                "tg_id": tg_id,
                "group_name": group_name.upper()
            },
            on_conflict="tg_id"
        ).execute()
    )
    return bool(result.data)
