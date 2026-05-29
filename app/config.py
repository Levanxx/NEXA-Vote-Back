import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    VOTE_SECRET_KEY = os.getenv("VOTE_SECRET_KEY", "nexa-vote-dev-key")
    SECRET_KEY = os.getenv("SECRET_KEY", "nexa-vote-dev-secret")