"""
D&D 5e Rulebook Storage System - Cache
"""

import hashlib
from typing import Dict, Optional, Any
from functools import lru_cache
from .types import RulebookQueryResult


class RulebookQueryCache:
    """Caching system for D&D 5e rulebook queries"""
    
    def __init__(self, max_size: int = 256):
        self.max_size = max_size
        self._cache: Dict[str, RulebookQueryResult] = {}
        self._access_order = []
    
    def get_cache_key(self, intent: str, entities: list) -> str:
        """Generate cache key from intent and entities"""
        content = f"{intent}:{','.join(sorted(entities))}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[RulebookQueryResult]:
        """Get cached result"""
        if cache_key in self._cache:
            # Update access order (LRU)
            self._access_order.remove(cache_key)
            self._access_order.append(cache_key)
            return self._cache[cache_key]
        return None
    
    def put(self, cache_key: str, result: RulebookQueryResult) -> None:
        """Store result in cache"""
        if cache_key in self._cache:
            # Update existing
            self._access_order.remove(cache_key)
        elif len(self._cache) >= self.max_size:
            # Evict least recently used
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[cache_key] = result
        self._access_order.append(cache_key)
    
    def clear(self) -> None:
        """Clear all cached results"""
        self._cache.clear()
        self._access_order.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'utilization': len(self._cache) / self.max_size if self.max_size > 0 else 0
        }
