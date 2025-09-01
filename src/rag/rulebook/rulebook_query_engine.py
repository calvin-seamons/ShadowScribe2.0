"""
D&D 5e Rulebook Query Engine
Intelligent semantic search with intention-based filtering and multi-stage scoring
"""

import re
import time
import numpy as np
from typing import List, Dict, Tuple, Optional
import openai
import hashlib

from .rulebook_types import (
    RulebookQueryIntent, RulebookSection, SearchResult, 
    RulebookCategory, INTENTION_CATEGORY_MAP, QueryPerformanceMetrics
)
from ..config import get_config

# Note: dotenv is loaded in config.py


class EmbeddingCache:
    """LRU cache for embeddings to avoid repeated API calls"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.access_order = []
        self.max_size = max_size
    
    def _hash_text(self, text: str) -> str:
        """Create hash key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        key = self._hash_text(text)
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, text: str, embedding: List[float]) -> None:
        """Store embedding in cache"""
        key = self._hash_text(text)
        
        # Remove if already exists
        if key in self.cache:
            self.access_order.remove(key)
        
        # Evict oldest if at capacity
        while len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        # Add new embedding
        self.cache[key] = embedding
        self.access_order.append(key)


class RulebookQueryEngine:
    """
    Intelligent query engine for D&D 5e rulebook sections.
    Combines semantic search with entity matching and context hints.
    """
    
    def __init__(self, storage):
        """Initialize with RulebookStorage instance"""
        from .rulebook_storage import RulebookStorage  # Import here to avoid circular import
        
        if not isinstance(storage, RulebookStorage):
            raise TypeError("storage must be a RulebookStorage instance")
            
        self.storage = storage
        self.config = get_config()
        self.embedding_model = self.config.embedding_model
        self.embedding_cache = EmbeddingCache(max_size=self.config.embedding_cache_size)
        
        # Initialize OpenAI with API key from config
        openai.api_key = self.config.openai_api_key
        if not self.config.validate_openai_key():
            raise ValueError("Invalid or missing OpenAI API key in configuration")
    
    def query(
        self,
        intention: RulebookQueryIntent,
        user_query: str,
        entities: List[str],
        context_hints: List[str] = None,
        k: int = 5
    ) -> Tuple[List[SearchResult], QueryPerformanceMetrics]:
        """
        Perform intelligent query against rulebook sections.
        
        Args:
            intention: Query intent to determine search categories
            user_query: Original user query string
            entities: Normalized entities extracted from query
            context_hints: Additional phrases to enhance search
            k: Number of results to return
            
        Returns:
            Tuple of (SearchResult list, QueryPerformanceMetrics)
        """
        start_time = time.perf_counter()
        
        # Initialize performance tracking
        performance = QueryPerformanceMetrics()
        performance.total_sections_available = len(self.storage.sections)
        
        if context_hints is None:
            context_hints = []
            
        # 1. Filter sections by intention
        filter_start = time.perf_counter()
        candidate_sections = self._filter_sections_by_intention(intention)
        filter_end = time.perf_counter()
        
        performance.intention_filtering_ms = (filter_end - filter_start) * 1000
        performance.sections_after_filtering = len(candidate_sections)
        
        if not candidate_sections:
            performance.total_time_ms = (time.perf_counter() - start_time) * 1000
            return [], performance
        
        # 2. Perform semantic search
        semantic_start = time.perf_counter()
        semantic_results = self._semantic_search(user_query, candidate_sections, performance)
        semantic_end = time.perf_counter()
        
        performance.semantic_search_ms = (semantic_end - semantic_start) * 1000
        
        # 3. Apply entity boosting
        entity_start = time.perf_counter()
        entity_boosted_results = self._boost_entity_matches(semantic_results, entities)
        entity_end = time.perf_counter()
        
        performance.entity_boosting_ms = (entity_end - entity_start) * 1000
        
        # 4. Enhance with context hints
        context_start = time.perf_counter()
        final_results = self._enhance_with_context_hints(entity_boosted_results, context_hints, performance)
        context_end = time.perf_counter()
        
        performance.context_enhancement_ms = (context_end - context_start) * 1000
        
        # 5. Take top-k and create SearchResult objects
        assembly_start = time.perf_counter()
        top_results = final_results[:k]
        search_results = []
        
        for section, score in top_results:
            # Find matched entities and context for this section
            matched_entities = self._find_matched_entities(section, entities)
            matched_context = self._find_matched_context(section, context_hints)
            
            search_result = SearchResult(
                section=section,
                score=score,
                matched_entities=matched_entities,
                matched_context=matched_context,
                includes_children=True  # We'll include children content
            )
            search_results.append(search_result)
        
        assembly_end = time.perf_counter()
        performance.result_assembly_ms = (assembly_end - assembly_start) * 1000
        performance.results_returned = len(search_results)
        
        # 6. Include children content for complete context
        children_start = time.perf_counter()
        self._include_children_content(search_results)
        children_end = time.perf_counter()
        
        performance.children_inclusion_ms = (children_end - children_start) * 1000
        
        # Finalize performance metrics
        end_time = time.perf_counter()
        performance.total_time_ms = (end_time - start_time) * 1000
        
        return search_results, performance
    
    def _filter_sections_by_intention(self, intention: RulebookQueryIntent) -> List[RulebookSection]:
        """Filter sections to only those relevant to the query intention"""
        target_categories = INTENTION_CATEGORY_MAP.get(intention, [])
        
        if not target_categories:
            # If no specific mapping, return all sections
            return list(self.storage.sections.values())
        
        candidate_sections = []
        for section in self.storage.sections.values():
            # Check if section has any of the target categories
            section_category_values = [cat.value if hasattr(cat, 'value') else cat for cat in section.categories]
            target_category_values = [cat.value if hasattr(cat, 'value') else cat for cat in target_categories]
            
            if any(cat in target_category_values for cat in section_category_values):
                candidate_sections.append(section)
        
        return candidate_sections
    
    def _semantic_search(self, query: str, candidate_sections: List[RulebookSection], performance: QueryPerformanceMetrics) -> List[Tuple[RulebookSection, float]]:
        """Perform semantic search using embeddings"""
        if not candidate_sections:
            return []
        
        # Track sections with embeddings
        performance.sections_with_embeddings = sum(1 for s in candidate_sections if s.vector is not None)
        
        # Embed the query
        embed_start = time.perf_counter()
        query_embedding = self._get_embedding(query, performance)
        embed_end = time.perf_counter()
        
        performance.embedding_total_ms += (embed_end - embed_start) * 1000
        
        results = []
        for section in candidate_sections:
            if section.vector is None:
                # Skip sections without embeddings
                continue
                
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, section.vector)
            results.append((section, similarity))
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _boost_entity_matches(self, results: List[Tuple[RulebookSection, float]], entities: List[str]) -> List[Tuple[RulebookSection, float]]:
        """Boost scores based on entity matches in section content"""
        if not entities:
            return results
        
        boosted_results = []
        for section, base_score in results:
            entity_boost = 0.0
            
            for entity in entities:
                entity_lower = entity.lower()
                
                # Check title (high weight)
                if entity_lower in section.title.lower():
                    entity_boost += 0.3
                
                # Check ID (medium weight)
                if entity_lower in section.id.lower():
                    entity_boost += 0.2
                
                # Check content (medium weight, scaled by frequency)
                content_lower = section.content.lower()
                entity_count = content_lower.count(entity_lower)
                if entity_count > 0:
                    # Diminishing returns for multiple mentions
                    entity_boost += min(0.25 * entity_count, 0.5)
            
            # Apply entity boost (25% of total score)
            boosted_score = base_score * 0.75 + entity_boost * 0.25
            boosted_results.append((section, boosted_score))
        
        # Re-sort by boosted scores
        boosted_results.sort(key=lambda x: x[1], reverse=True)
        return boosted_results
    
    def _enhance_with_context_hints(self, results: List[Tuple[RulebookSection, float]], hints: List[str], performance: QueryPerformanceMetrics) -> List[Tuple[RulebookSection, float]]:
        """Enhance scores using context hints"""
        if not hints:
            return results
        
        # Get embeddings for all context hints using batch processing
        embed_start = time.perf_counter()
        hint_embeddings = self._get_embeddings_batch(hints, performance)
        embed_end = time.perf_counter()
        
        performance.embedding_total_ms += (embed_end - embed_start) * 1000
        
        enhanced_results = []
        for section, base_score in results:
            if section.vector is None:
                enhanced_results.append((section, base_score))
                continue
            
            context_boost = 0.0
            
            # Check similarity with each context hint
            for hint_embedding in hint_embeddings:
                similarity = self._cosine_similarity(hint_embedding, section.vector)
                context_boost += similarity
            
            # Average the context hint similarities
            if hint_embeddings:
                context_boost /= len(hint_embeddings)
            
            # Apply context boost (15% of total score)
            enhanced_score = base_score * 0.85 + context_boost * 0.15
            enhanced_results.append((section, enhanced_score))
        
        # Re-sort by enhanced scores
        enhanced_results.sort(key=lambda x: x[1], reverse=True)
        return enhanced_results
    
    def _include_children_content(self, search_results: List[SearchResult]) -> None:
        """Include children content for hierarchical completeness"""
        for result in search_results:
            # Get full content including children
            full_content = result.section.get_full_content(
                include_children=True, 
                storage=self.storage
            )
            
            # Update the section content with hierarchical content
            # Note: We modify the content but keep the original section structure
            if full_content != result.section.content:
                # Create a copy of the section with full content
                result.section.content = full_content
                result.includes_children = True
    
    def _find_matched_entities(self, section: RulebookSection, entities: List[str]) -> List[str]:
        """Find which entities match in this section"""
        matched = []
        section_text = f"{section.title} {section.id} {section.content}".lower()
        
        for entity in entities:
            if entity.lower() in section_text:
                matched.append(entity)
        
        return matched
    
    def _find_matched_context(self, section: RulebookSection, context_hints: List[str]) -> List[str]:
        """Find which context hints are relevant to this section"""
        if not context_hints:
            return []
        
        matched = []
        section_text = f"{section.title} {section.content}".lower()
        
        for hint in context_hints:
            # Simple word overlap check for context relevance
            hint_words = set(hint.lower().split())
            section_words = set(section_text.split())
            
            # If hint has significant word overlap with section, consider it matched
            overlap = len(hint_words & section_words)
            if overlap >= min(2, len(hint_words) // 2):  # At least 2 words or half the hint words
                matched.append(hint)
        
        return matched
    
    def _get_embedding(self, text: str, performance: QueryPerformanceMetrics) -> List[float]:
        """Get embedding for text using OpenAI API with caching"""
        # Check cache first
        cached_embedding = self.embedding_cache.get(text)
        if cached_embedding is not None:
            performance.embedding_cache_hits += 1
            return cached_embedding
        
        performance.embedding_cache_misses += 1
        performance.embedding_api_calls += 1
        
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            
            # Store in cache
            self.embedding_cache.put(text, embedding)
            return embedding
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            fallback = [0.0] * 3072  # text-embedding-3-large dimension
            self.embedding_cache.put(text, fallback)
            return fallback
    
    def _get_embeddings_batch(self, texts: List[str], performance: QueryPerformanceMetrics) -> List[List[float]]:
        """Get embeddings for multiple texts, using cache where possible"""
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cached_embedding = self.embedding_cache.get(text)
            if cached_embedding is not None:
                embeddings.append(cached_embedding)
                performance.embedding_cache_hits += 1
            else:
                embeddings.append(None)  # Placeholder
                texts_to_embed.append(text)
                indices_to_embed.append(i)
                performance.embedding_cache_misses += 1
        
        # Batch embed uncached texts
        if texts_to_embed:
            performance.embedding_api_calls += 1  # One batch API call
                
            try:
                response = openai.embeddings.create(
                    model=self.embedding_model,
                    input=texts_to_embed
                )
                
                # Fill in the embeddings and cache them
                for j, embedding_data in enumerate(response.data):
                    text = texts_to_embed[j]
                    embedding = embedding_data.embedding
                    index = indices_to_embed[j]
                    
                    embeddings[index] = embedding
                    self.embedding_cache.put(text, embedding)
                    
            except Exception as e:
                print(f"Error getting batch embeddings: {e}")
                # Fill with zero vectors as fallback
                fallback = [0.0] * 3072  # text-embedding-3-large dimension
                for i in indices_to_embed:
                    embeddings[i] = fallback
                    self.embedding_cache.put(texts[i], fallback)
        
        return embeddings
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
