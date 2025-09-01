"""
D&D 5e Rulebook Storage System

Core types and assignments for D&D 5e rulebook content organization.
"""

from .types import (
    RulebookCategory, RulebookQueryIntent, RulebookSection,
    SearchResult, QueryRequest, QueryResponse
)
from .rulebook_assignments import (
    RULEBOOK_CATEGORY_ASSIGNMENTS,
    PATTERN_RULES,
    MULTI_CATEGORY_SECTIONS
)
from .storage import RulebookStorage
from .categorizer import RulebookCategorizer

__all__ = [
    'RulebookCategory',
    'RulebookQueryIntent', 
    'RulebookSection',
    'SearchResult',
    'QueryRequest', 
    'QueryResponse',
    'RULEBOOK_CATEGORY_ASSIGNMENTS',
    'PATTERN_RULES',
    'MULTI_CATEGORY_SECTIONS',
    'RulebookStorage',
    'RulebookCategorizer'
]
