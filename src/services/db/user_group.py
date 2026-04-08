import asyncio
from aiocache import cached, Cache
from .client import supabase

async def async_execute_supabase_call(callable, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: callable(*args, **kwargs))

@cached(ttl=10, cache=Cache.MEMORY)
async def check_user_group(tg_id: int) -> dict | None:
    response = await async_execute_supabase_call(
        lambda: supabase.table("user_groups").select("group_name", "tg_id").eq("tg_id", tg_id).execute()
    )
    return response.data[0] if response.data else None

@cached(ttl=10, cache=Cache.MEMORY)
async def auto_add(tg_id: int):
    resp = await async_execute_supabase_call(
        lambda: supabase.table("user_groups").select("tg_id").eq("tg_id", tg_id).execute()
    )

    if not resp.data:
        add = await async_execute_supabase_call(
            lambda: supabase.table("user_groups").insert({"tg_id": tg_id}).execute()
        )

async def set_user_group(tg_id: int, group_name: str) -> bool:
    try:
        result = await async_execute_supabase_call(
            lambda: supabase.table("user_groups").upsert(
                {
                    "tg_id": tg_id,
                    "group_name": group_name.upper()
                },
                on_conflict="tg_id"
            ).execute()
        )

        if result.data:
            cache = Cache(Cache.MEMORY)
            cache_key = f"check_user_group|{tg_id}"
            await cache.delete(cache_key)
            return True
        else:
            return False

    except Exception as e:
        print(f"Error setting user group for tg_id {tg_id}: {e}")
        return False
