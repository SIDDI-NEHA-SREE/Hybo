from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.config import settings
from app.utils.logger import logger

class SupabaseService:
    _client: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                raise ValueError("Supabase settings (SUPABASE_URL and SUPABASE_ANON_KEY) must be configured.")
            # Use service role key if available for backend operations to bypass RLS when performing admin actions, 
            # otherwise fall back to anon key.
            key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
            cls._client = create_client(settings.SUPABASE_URL, key)
            logger.info("Initialized Supabase Client")
        return cls._client

    @classmethod
    async def get_profile(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the profile of a user by their unique UUID.
        """
        try:
            client = cls.get_client()
            response = client.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
            return response.data if response else None
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {str(e)}")
            return None

    @classmethod
    async def create_or_update_profile(cls, user_id: str, email: str, name: Optional[str] = None, phone_number: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Creates or updates the user profile record matching the Supabase Auth UUID.
        """
        try:
            client = cls.get_client()
            profile_data = {
                "id": user_id,
                "email": email,
                "role": "citizen"
            }
            if name:
                profile_data["name"] = name
            if phone_number:
                profile_data["phone_number"] = phone_number

            # Upsert the profile record
            response = client.table("profiles").upsert(profile_data, on_conflict="id").execute()
            if response and response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating/updating profile for user {user_id}: {str(e)}")
            return None
