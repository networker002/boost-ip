from .client import supabase
from functools import lru_cache

@lru_cache(maxsize=1000)
def check_user_group(tg_id: int):
    response = supabase.table("user_groups") \
        .select("group_name") \
        .eq("tg_id", tg_id) \
        .execute()
    
    return response.data[0] if response.data else None


def set_user_group(tg_id: int, group_name: str) -> bool:
    result = supabase.table("user_groups") \
        .upsert({
            "tg_id": tg_id, 
            "group_name": group_name.upper()
        }, on_conflict="tg_id") \
        .execute()
    return bool(result.data)

# if __name__ == "__main__":
#     print(set_user_group(2, "test"))