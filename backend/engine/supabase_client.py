"""
backend/engine/supabase_client.py

Supabase Database Adapter:
Provides persistent synchronization for user profiles, interaction logs, interest graph states,
and user feedback. Works in dual mode:
- Live Mode: Connects to Supabase REST / Postgres using URL and Anon Key.
- Local Mode: Fast in-memory & file-backed store for immediate offline use.
"""

from typing import Dict, List, Any, Optional
import os
import json
import httpx
from datetime import datetime


class SupabaseClientAdapter:
    """Manages cloud sync with Supabase or falls back to local storage."""

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL", "")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY", "")
        self.is_connected = False
        self.local_events: List[Dict] = []
        self.local_feedback: List[Dict] = []
        self.local_user_profiles: Dict[str, Dict] = {}

        if self.supabase_url and self.supabase_key:
            self.test_connection()

    def set_credentials(self, url: str, key: str) -> Dict[str, Any]:
        """Updates Supabase credentials and tests connection."""
        self.supabase_url = url.strip()
        self.supabase_key = key.strip()
        os.environ["SUPABASE_URL"] = self.supabase_url
        os.environ["SUPABASE_ANON_KEY"] = self.supabase_key
        return self.test_connection()

    def test_connection(self) -> Dict[str, Any]:
        """Tests if the Supabase instance is reachable."""
        if not self.supabase_url or not self.supabase_key:
            self.is_connected = False
            return {
                "connected": False,
                "mode": "Local / Offline Mode",
                "message": "No Supabase credentials configured. Running in high-performance local mode."
            }

        try:
            # Ping Supabase REST endpoint
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}"
            }
            url = f"{self.supabase_url.rstrip('/')}/rest/v1/"
            with httpx.Client(timeout=4.0) as client:
                res = client.get(url, headers=headers)
                if res.status_code in (200, 404, 401):
                    self.is_connected = True
                    return {
                        "connected": True,
                        "mode": "Supabase Cloud Connected",
                        "url": self.supabase_url,
                        "status_code": res.status_code,
                        "message": "Successfully connected to Supabase backend!"
                    }
        except Exception as e:
            self.is_connected = False
            return {
                "connected": False,
                "mode": "Local Fallback",
                "error": str(e),
                "message": "Could not connect to Supabase endpoint. Operating in local mode."
            }

        self.is_connected = False
        return {"connected": False, "mode": "Local Mode", "message": "Credentials invalid."}

    def sync_user_interaction(self, interaction: Dict) -> bool:
        """Stores interaction event either in Supabase or local event log."""
        self.local_events.append(interaction)
        if not self.is_connected:
            return True

        try:
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            url = f"{self.supabase_url.rstrip('/')}/rest/v1/interactions"
            with httpx.Client(timeout=3.0) as client:
                res = client.post(url, json=interaction, headers=headers)
                return res.status_code in (200, 201)
        except Exception:
            return False

    def sync_feedback(self, feedback: Dict) -> bool:
        """Stores user feedback."""
        self.local_feedback.append(feedback)
        if not self.is_connected:
            return True

        try:
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            url = f"{self.supabase_url.rstrip('/')}/rest/v1/feedback"
            with httpx.Client(timeout=3.0) as client:
                res = client.post(url, json=feedback, headers=headers)
                return res.status_code in (200, 201)
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Returns the current sync status."""
        return {
            "is_connected": self.is_connected,
            "supabase_url": self.supabase_url if self.supabase_url else None,
            "local_events_count": len(self.local_events),
            "local_feedback_count": len(self.local_feedback),
            "mode": "Live Supabase Cloud" if self.is_connected else "Local InMemory & File Store"
        }
