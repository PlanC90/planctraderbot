from typing import Any, Dict, List, Optional
import time


class AccountService:
    def __init__(self, client):
        self.client = client
        self._cache_account = {'ts': 0.0, 'data': None}
        self._cache_positions = {'ts': 0.0, 'data': None}

    def get_account(self, ttl_seconds: int = 30) -> Dict[str, Any]:
        now = time.time()
        if now - self._cache_account['ts'] > ttl_seconds or not self._cache_account['data']:
            data = self.client.futures_account()
            self._cache_account = {'ts': now, 'data': data}
        return self._cache_account['data']

    def get_positions(self, ttl_seconds: int = 5) -> List[Dict[str, Any]]:
        now = time.time()
        if now - self._cache_positions['ts'] > ttl_seconds or not self._cache_positions['data']:
            data = self.client.futures_position_information()
            self._cache_positions = {'ts': now, 'data': data}
        return self._cache_positions['data']



