from .client import supabase
from typing import Optional


def check_user_group(tg_id: int):
    response = supabase.table("user_groups") \
        .select("group_name") \
        .eq("tg_id", tg_id) \
        .execute()
    
    if response.data:
        return response.data[0]


def set_user_group(tg_id: int, group_name: str) -> str:
    existing = supabase.table("user_groups") \
        .select("id") \
        .eq("tg_id", tg_id) \
        .execute()
    
    if existing.data:
        supabase.table("user_groups") \
            .update({"group_name": group_name.upper()}) \
            .eq("id", existing.data[0]["id"]) \
            .execute()
    else:
        supabase.table("user_groups") \
            .insert({"tg_id": tg_id, "group_name": group_name.upper()}) \
            .execute()

    return "OK"


# if __name__ == "__main__":
#     print(set_user_group(2, "test"))