from supabase import create_client, Client
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

supabase: Client = create_client(
    os.environ.get("DATABASE_URL"),
    os.environ.get("DATABASE_SERVICE_KEY")
)
