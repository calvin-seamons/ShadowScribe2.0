"""
Result Enhancer - Post-processing for entity boosting and context hints
Applies identical scoring to results from both RAG systems
"""
import re
from typing import List, Dict, Any


class ResultEnhancer:
    """Post-processing: entity boosting + context hints enhancement"""
    
    def __init__(self, semantic_weight: float = 0.75, entity_weight: float = 0.25, context_weight: float = 0.15):
        """
        Initialize enhancer with scoring weights
        
        Args:
            semantic_weight: Weight for semantic similarity score
            entity_weight: Weight for entity matching score
            context_weight: Weight for context hint matching score
        """
        self.semantic_weight = semantic_weight
        self.entity_weight = entity_weight
        self.context_weight = context_weight
    
    def enhance_results(
        self, 
        search_results: List[Dict[str, Any]], 
        entities: List[str], 
        context_hints: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply identical scoring to both systems
        
        Args:
            search_results: List of search results with 'section' and 'similarity_score' keys
            entities: List of entity strings to boost
            context_hints: Optional list of context phrases
            
        Returns:
            Sorted list of results by final score
        """
        if context_hints is None:
            context_hints = []
        
        for result in search_results:
            semantic_score = result.get('similarity_score', 0.0)
            entity_score = self._calculate_entity_boost(result, entities)
            context_score = self._calculate_context_boost(result, context_hints)
            
            # Combined scoring (same weights as current system)
            result['final_score'] = (
                semantic_score * self.semantic_weight +
                entity_score * self.entity_weight +
                context_score * self.context_weight
            )
            
            # Store component scores for analysis
            result['score_components'] = {
                'semantic': semantic_score,
                'entity': entity_score,
                'context': context_score
            }
        
        # Sort by final score
        return sorted(search_results, key=lambda x: x['final_score'], reverse=True)
    
    def _calculate_entity_boost(self, result: Dict[str, Any], entities: List[str]) -> float:
        """
        Entity matching in title/content
        
        Args:
            result: Search result with section data
            entities: List of entity strings
            
        Returns:
            Entity boost score (0.0 to 1.0)
        """
        if not entities:
            return 0.0
        
        section = result.get('section', {})
        title = section.get('title', '').lower()
        content = section.get('content', '').lower()
        
        # Combine title and content for matching
        combined_text = f"{title} {content}"
        
        # Count entity matches
        matches = 0
        for entity in entities:
            entity_lower = entity.lower()
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(entity_lower) + r'\b'
            if re.search(pattern, combined_text):
                matches += 1
        
        # Normalize by number of entities
        entity_score = matches / len(entities) if entities else 0.0
        
        return min(entity_score, 1.0)  # Cap at 1.0
    
    def _calculate_context_boost(self, result: Dict[str, Any], context_hints: List[str]) -> float:
        """
        Context hint similarity
        
        Args:
            result: Search result with section data
            context_hints: List of context phrase strings
            
        Returns:
            Context boost score (0.0 to 1.0)
        """
        if not context_hints:
            return 0.0
        
        section = result.get('section', {})
        title = section.get('title', '').lower()
        content = section.get('content', '').lower()
        
        combined_text = f"{title} {content}"
        
        # Count context hint matches
        matches = 0
        for hint in context_hints:
            hint_lower = hint.lower()
            # Use substring matching for context hints (more flexible)
            if hint_lower in combined_text:
                matches += 1
        
        # Normalize by number of hints
        context_score = matches / len(context_hints) if context_hints else 0.0
        
        return min(context_score, 1.0)  # Cap at 1.0
