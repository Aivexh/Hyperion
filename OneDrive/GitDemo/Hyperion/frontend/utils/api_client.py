import os
import json
import requests
from typing import Generator, Dict, Any, List

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class HyperAgentAPIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip('/')

    def check_health(self) -> bool:
        """Checks backend server health."""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Fetches all generation entries from backend archive."""
        try:
            r = requests.get(f"{self.base_url}/evolution/history", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"API Error fetching history: {e}")
        return []

    def get_generation_diff(self, gen_a: str, gen_b: str) -> Dict[str, Any]:
        """Fetches prompt diff between two generation versions."""
        try:
            r = requests.get(f"{self.base_url}/evolution/diff", params={"gen_a": gen_a, "gen_b": gen_b}, timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"API Error fetching diff: {e}")
        return {}

    def stream_chat(self, query: str, generation_id: str = None) -> Generator[Dict[str, Any], None, None]:
        """Consumes SSE stream from /chat/stream."""
        url = f"{self.base_url}/chat/stream"
        payload = {"query": query, "generation_id": generation_id}
        
        try:
            with requests.post(url, json=payload, stream=True, timeout=60) as response:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data: "):
                            json_str = decoded[6:]
                            try:
                                yield json.loads(json_str)
                            except Exception:
                                pass
        except Exception as e:
            yield {"type": "error", "message": f"Connection error to backend streaming chat: {str(e)}"}

    def stream_evolution_trigger(self) -> Generator[Dict[str, Any], None, None]:
        """Consumes SSE stream from /evolve/trigger."""
        url = f"{self.base_url}/evolve/trigger"
        try:
            with requests.post(url, stream=True, timeout=120) as response:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data: "):
                            json_str = decoded[6:]
                            try:
                                yield json.loads(json_str)
                            except Exception:
                                pass
        except Exception as e:
            yield {"type": "log", "message": f"Evolution trigger error: {str(e)}"}

api_client = HyperAgentAPIClient()
