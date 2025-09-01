"""
D&D 5e Rulebook Storage System

Core types and assignments for D&D 5e rulebook content organization.
"""

from .rulebook_types import (
    RulebookCategory, RulebookQueryIntent, RulebookSection,
    SearchResult, QueryRequest, QueryResponse,
    RULEBOOK_CATEGORY_ASSIGNMENTS,
    PATTERN_RULES,
    MULTI_CATEGORY_SECTIONS
)
from .rulebook_storage import RulebookStorage
from .categorizer import RulebookCategorizer
from .query_engine import RulebookQueryEngine

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
    'RulebookCategorizer',
    'RulebookQueryEngine'
]
