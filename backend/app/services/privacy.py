"""Privacy mode service for masking sensitive text."""
import re
from dataclasses import dataclass
from typing import Optional
from functools import lru_cache

from app.core.config import get_settings


@dataclass
class MaskRange:
    """A range of characters to mask."""
    start: int
    end: int


class PrivacyService:
    """Service for detecting and masking sensitive text patterns."""
    
    def __init__(self):
        self.settings = get_settings()
        self._compiled_patterns: dict[str, re.Pattern] = {}
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile built-in and custom regex patterns."""
        # Built-in patterns
        builtin_patterns = {
            "secret": re.compile(
                r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|bearer[_-]?token|password|passwd|pwd)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_\-]{20,}',
                re.IGNORECASE
            ),
            "email": re.compile(
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
            ),
            "phone": re.compile(
                r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
            ),
            "card": re.compile(
                r'\b(?:\d[ -]*?){13,16}\b'
            ),
            "iban": re.compile(
                r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b'
            ),
            "ip": re.compile(
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ),
        }
        
        for rule in self.settings.privacy_rules:
            if rule in builtin_patterns:
                self._compiled_patterns[rule] = builtin_patterns[rule]
    
    def is_enabled(self) -> bool:
        """Check if privacy mode is enabled."""
        return self.settings.privacy_enabled
    
    def get_mask_char(self) -> str:
        """Get the mask character."""
        return self.settings.privacy_mask_char
    
    def find_matches(self, text: str) -> list[MaskRange]:
        """Find all matching ranges in text that should be masked."""
        if not self.is_enabled():
            return []
        
        matches: list[MaskRange] = []
        
        for name, pattern in self._compiled_patterns.items():
            for match in pattern.finditer(text):
                # Check if match is in an allow-listed host
                matched_text = match.group(0)
                if self._is_allowed(matched_text):
                    continue
                matches.append(MaskRange(match.start(), match.end()))
        
        # Merge overlapping ranges
        return self._merge_ranges(matches)
    
    def _is_allowed(self, text: str) -> bool:
        """Check if text contains an allow-listed host."""
        for host in self.settings.privacy_allow_hosts:
            if host in text:
                return True
        return False
    
    def _merge_ranges(self, ranges: list[MaskRange]) -> list[MaskRange]:
        """Merge overlapping or adjacent ranges."""
        if not ranges:
            return []
        
        sorted_ranges = sorted(ranges, key=lambda r: r.start)
        merged = [sorted_ranges[0]]
        
        for current in sorted_ranges[1:]:
            last = merged[-1]
            if current.start <= last.end:
                last.end = max(last.end, current.end)
            else:
                merged.append(current)
        
        return merged
    
    def mask_text(self, text: str) -> str:
        """Replace matched ranges with mask characters."""
        matches = self.find_matches(text)
        if not matches:
            return text
        
        result = []
        last_end = 0
        
        for match in matches:
            result.append(text[last_end:match.start])
            mask_len = match.end - match.start
            result.append(self.get_mask_char() * mask_len)
            last_end = match.end
        
        result.append(text[last_end:])
        return ''.join(result)
    
    @lru_cache(maxsize=1024)
    def _cached_mask_line(self, line: str) -> str:
        """Cache masked lines for performance."""
        return self.mask_text(line)


# Global instance
_privacy_service: Optional[PrivacyService] = None


def get_privacy_service() -> PrivacyService:
    """Get or create the global privacy service instance."""
    global _privacy_service
    if _privacy_service is None:
        _privacy_service = PrivacyService()
    return _privacy_service


def invalidate_privacy_cache() -> None:
    """Invalidate the privacy service cache (call when settings change)."""
    global _privacy_service
    if _privacy_service is not None:
        _privacy_service._cached_mask_line.cache_clear()
