"""
Local Joint Classifier for Tool + Intent Classification.

Uses a trained DeBERTa-v3 model with:
- Tool classification head (3 classes: character_data, session_notes, rulebook)
- Per-tool intent heads (10, 20, 30 intents respectively)
- Temperature scaling for calibrated confidence scores
- Name normalization to align runtime queries with placeholder-based training data

The model was trained on templates with {CHARACTER}, {PARTY_MEMBER}, {NPC} placeholders.
At inference, we normalize actual names to these placeholders before classification.
"""

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import DebertaV2TokenizerFast, DebertaV2Model, DebertaV2PreTrainedModel, AutoConfig

from .base import ClassificationResult
from .gazetteer_ner import GazetteerEntityExtractor


@dataclass
class SingleClassificationResult:
    """Result from classifying a single query."""
    tool: str
    tool_confidence: float
    intent: str
    intent_confidence: float
    normalized_query: str
    combined_confidence: float


class JointClassifier(DebertaV2PreTrainedModel):
    """
    Joint Tool + Intent Classifier using DeBERTa-v3.
    
    Architecture matches the training notebook:
    - Shared DeBERTa encoder
    - Tool classification head (3 classes)
    - Per-tool intent heads (character: 10, session: 20, rulebook: 30)
    - Learnable temperature parameter for confidence calibration
    """
    
    def __init__(self, config, num_tools=3,
                 num_character_intents=10,
                 num_session_intents=20,
                 num_rulebook_intents=30):
        super().__init__(config)
        
        self.num_tools = num_tools
        self.num_character_intents = num_character_intents
        self.num_session_intents = num_session_intents
        self.num_rulebook_intents = num_rulebook_intents
        
        # Shared encoder
        self.deberta = DebertaV2Model(config)
        
        # Dropout
        classifier_dropout = getattr(config, 'classifier_dropout', 0.1)
        self.dropout = nn.Dropout(classifier_dropout)
        
        # Tool classification head
        self.tool_head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size, num_tools)
        )
        
        # Per-tool intent heads
        self.character_intent_head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size, num_character_intents)
        )
        self.session_intent_head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size, num_session_intents)
        )
        self.rulebook_intent_head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size, num_rulebook_intents)
        )
        
        # Temperature for calibration (scalar parameter, set from checkpoint)
        self.temperature = nn.Parameter(torch.tensor(1.0))
        
        self.post_init()
    
    def forward(self, input_ids=None, attention_mask=None):
        """
        Forward pass.
        
        Returns:
            tool_logits: (batch, num_tools)
            intent_logits: dict mapping tool name -> (batch, num_intents)
        """
        outputs = self.deberta(input_ids, attention_mask=attention_mask)
        
        # Get [CLS] token output
        cls_output = outputs.last_hidden_state[:, 0, :]
        cls_output = self.dropout(cls_output)
        
        # Tool logits
        tool_logits = self.tool_head(cls_output)
        
        # Intent logits for all tools
        intent_logits = {
            'character_data': self.character_intent_head(cls_output),
            'session_notes': self.session_intent_head(cls_output),
            'rulebook': self.rulebook_intent_head(cls_output),
        }
        
        return tool_logits, intent_logits


class LocalClassifier:
    """
    Local classifier using the trained Joint Tool+Intent model.
    
    Key features:
    - Name normalization: replaces character/party/NPC names with placeholders
    - Temperature-scaled confidence scores for calibration
    - Gazetteer NER for entity extraction (optional)
    
    Training vs Inference Flow:
        TRAINING: Templates with {CHARACTER} → Train model on placeholder patterns
        INFERENCE: "What level is Duskryn?" → normalize → "What level is {CHARACTER}?" → Classify
    """
    
    # Default model path relative to project root
    DEFAULT_MODEL_PATH = Path(__file__).parent.parent.parent / "574-Assignment" / "models" / "joint_classifier"
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        srd_cache_path: Optional[str] = None,
        device: str = 'auto',
        use_gazetteer: bool = True,
        gazetteer_min_similarity: float = 0.80,
    ):
        """
        Initialize the local classifier.
        
        Args:
            model_path: Path to the trained model directory. If None, uses default path.
            srd_cache_path: Path to SRD cache for gazetteer NER.
            device: Device to use ('auto', 'cuda', 'mps', 'cpu')
            use_gazetteer: Whether to use gazetteer NER for entity extraction.
            gazetteer_min_similarity: Minimum similarity for gazetteer matching.
        """
        self.model_path = Path(model_path) if model_path else self.DEFAULT_MODEL_PATH
        self.srd_cache_path = Path(srd_cache_path) if srd_cache_path else None
        self.use_gazetteer = use_gazetteer
        self.gazetteer_min_similarity = gazetteer_min_similarity
        
        # Determine device
        if device == 'auto':
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            elif torch.backends.mps.is_available():
                self.device = torch.device('mps')
            else:
                self.device = torch.device('cpu')
        else:
            self.device = torch.device(device)
        
        print(f"[LocalClassifier] Using device: {self.device}")
        print(f"[LocalClassifier] Model path: {self.model_path}")
        
        # Load components
        self._load_mappings()
        self._load_model()
        
        if use_gazetteer and srd_cache_path:
            self._load_gazetteer()
        else:
            self.gazetteer_ner = None
    
    def _load_mappings(self) -> None:
        """Load label mappings from training."""
        mappings_path = self.model_path / 'label_mappings.json'
        with open(mappings_path) as f:
            self.mappings = json.load(f)
        
        self.tool_to_idx = self.mappings['tool_to_idx']
        self.idx_to_tool = {int(k): v for k, v in self.mappings['idx_to_tool'].items()}
        self.tools = list(self.tool_to_idx.keys())
        
        self.intent_to_idx_per_tool = self.mappings['intent_to_idx_per_tool']
        self.idx_to_intent_per_tool = {
            tool: {int(k): v for k, v in intents.items()}
            for tool, intents in self.mappings['idx_to_intent_per_tool'].items()
        }
        self.num_intents_per_tool = self.mappings['num_intents_per_tool']
        
        # Preserved placeholders from training
        self.preserved_placeholders = self.mappings.get('preserved_placeholders', [
            '{CHARACTER}', '{PARTY_MEMBER}', '{NPC}'
        ])
        
        print(f"[LocalClassifier] Loaded mappings: {len(self.tools)} tools")
        for tool, num in self.num_intents_per_tool.items():
            print(f"  - {tool}: {num} intents")
    
    def _load_model(self) -> None:
        """Load the trained model, tokenizer, and checkpoint."""
        # Load tokenizer
        tokenizer_path = self.model_path / 'tokenizer'
        print(f"[LocalClassifier] Loading tokenizer from {tokenizer_path}")
        self.tokenizer = DebertaV2TokenizerFast.from_pretrained(str(tokenizer_path))
        
        # Load checkpoint (always load to CPU first, then move to device)
        # This avoids MPS float64 compatibility issues
        checkpoint_path = self.model_path / 'joint_classifier.pt'
        print(f"[LocalClassifier] Loading checkpoint from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        # Extract config from checkpoint
        self.training_config = checkpoint.get('config', {})
        self.max_length = self.training_config.get('max_length', 128)
        
        # Get calibrated temperature from checkpoint
        self.calibrated_temperature = checkpoint.get('temperature', 1.0)
        print(f"[LocalClassifier] Calibrated temperature: {self.calibrated_temperature:.4f}")
        
        # Initialize model architecture
        config = AutoConfig.from_pretrained(
            self.training_config.get('model_name', 'microsoft/deberta-v3-base')
        )
        config.classifier_dropout = self.training_config.get('classifier_dropout', 0.1)
        
        self.model = JointClassifier(
            config,
            num_tools=len(self.tools),
            num_character_intents=self.num_intents_per_tool['character_data'],
            num_session_intents=self.num_intents_per_tool['session_notes'],
            num_rulebook_intents=self.num_intents_per_tool['rulebook']
        )
        
        # Load state dict
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        # Set calibrated temperature
        self.model.temperature.data = torch.tensor([self.calibrated_temperature])
        
        self.model.to(self.device)
        self.model.eval()
        
        # Model stats
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"[LocalClassifier] Model loaded: {total_params:,} parameters")
    
    def _load_gazetteer(self) -> None:
        """Load gazetteer-based NER for entity extraction."""
        if self.srd_cache_path and self.srd_cache_path.exists():
            print(f"[LocalClassifier] Loading gazetteer NER from {self.srd_cache_path}")
            self.gazetteer_ner = GazetteerEntityExtractor(
                str(self.srd_cache_path),
                min_similarity=self.gazetteer_min_similarity
            )
        else:
            print("[LocalClassifier] Gazetteer NER not available (no SRD cache)")
            self.gazetteer_ner = None
    
    def _normalize_names(
        self,
        query: str,
        character_name: Optional[str] = None,
        character_aliases: Optional[List[str]] = None,
        party_members: Optional[List[str]] = None,
        known_npcs: Optional[List[str]] = None
    ) -> str:
        """
        Replace known names with placeholder tokens.
        
        This aligns runtime queries with the placeholder-based training data.
        The model was trained on patterns like "What level is {CHARACTER}?"
        so we need to normalize "What level is Duskryn?" to match.
        
        Args:
            query: The original query text
            character_name: The player's character name (can be full name like "Duskryn Nightwarden")
            character_aliases: Optional list of aliases/nicknames (e.g., ["Dusk", "DN"])
            party_members: List of party member names
            known_npcs: List of known NPC names
            
        Returns:
            Query with names replaced by placeholders
        """
        normalized = query
        
        # Helper for case-insensitive whole-word replacement
        def replace_name(text: str, name: str, placeholder: str) -> str:
            if not name or len(name) < 2:  # Skip empty or single-char names
                return text
            # Match whole word, case-insensitive
            pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)
            return pattern.sub(placeholder, text)
        
        # Build list of character name variants to match
        character_variants = []
        if character_name:
            # Add full name
            character_variants.append(character_name)
            # Add first name (split on space)
            name_parts = character_name.split()
            if len(name_parts) > 1:
                character_variants.append(name_parts[0])  # First name
                # Optionally add last name too
                if len(name_parts[-1]) > 2:  # Skip short suffixes like "Jr"
                    character_variants.append(name_parts[-1])
        
        # Add explicit aliases
        if character_aliases:
            character_variants.extend(character_aliases)
        
        # Replace character name variants (highest priority, longest first)
        # Sort by length descending to match longer names first (e.g., "Duskryn Nightwarden" before "Duskryn")
        character_variants = sorted(set(character_variants), key=len, reverse=True)
        for variant in character_variants:
            normalized = replace_name(normalized, variant, '{CHARACTER}')
        
        # Replace party member names
        if party_members:
            for member in party_members:
                if member:
                    # Also handle first names for party members
                    member_parts = member.split()
                    names_to_check = [member]
                    if len(member_parts) > 1:
                        names_to_check.append(member_parts[0])
                    for name in names_to_check:
                        # Don't replace if already a placeholder
                        if '{CHARACTER}' not in name:
                            normalized = replace_name(normalized, name, '{PARTY_MEMBER}')
        
        # Replace NPC names
        if known_npcs:
            for npc in known_npcs:
                if npc:
                    # Also handle first names for NPCs
                    npc_parts = npc.split()
                    names_to_check = [npc]
                    if len(npc_parts) > 1:
                        names_to_check.append(npc_parts[0])
                    for name in names_to_check:
                        normalized = replace_name(normalized, name, '{NPC}')
        
        return normalized
    
    def classify_single(
        self,
        query: str,
        character_name: Optional[str] = None,
        character_aliases: Optional[List[str]] = None,
        party_members: Optional[List[str]] = None,
        known_npcs: Optional[List[str]] = None
    ) -> SingleClassificationResult:
        """
        Classify a query and return the single best tool + intent.
        
        Args:
            query: The user's query text
            character_name: Optional character name for normalization (can be full name)
            character_aliases: Optional list of character aliases/nicknames
            party_members: Optional list of party member names
            known_npcs: Optional list of known NPC names
            
        Returns:
            SingleClassificationResult with tool, intent, and confidence scores
        """
        # Normalize names to placeholders
        normalized_query = self._normalize_names(
            query, character_name, character_aliases, party_members, known_npcs
        )
        
        # Tokenize
        encoding = self.tokenizer(
            normalized_query,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Run inference
        with torch.no_grad():
            tool_logits, intent_logits_dict = self.model(input_ids, attention_mask)
            
            # Apply temperature scaling for calibrated confidence
            temp = self.model.temperature.item()
            tool_probs = F.softmax(tool_logits / temp, dim=-1)
            
            # Get best tool
            tool_pred = torch.argmax(tool_probs, dim=-1).item()
            tool_conf = tool_probs[0, tool_pred].item()
            tool_name = self.idx_to_tool[tool_pred]
            
            # Get intent for predicted tool
            intent_logits = intent_logits_dict[tool_name]
            intent_probs = F.softmax(intent_logits / temp, dim=-1)
            intent_pred = torch.argmax(intent_probs, dim=-1).item()
            intent_conf = intent_probs[0, intent_pred].item()
            intent_name = self.idx_to_intent_per_tool[tool_name][intent_pred]
        
        return SingleClassificationResult(
            tool=tool_name,
            tool_confidence=tool_conf,
            intent=intent_name,
            intent_confidence=intent_conf,
            normalized_query=normalized_query,
            combined_confidence=tool_conf * intent_conf
        )
    
    def predict_sync(
        self,
        query: str,
        character_name: Optional[str] = None,
        character_aliases: Optional[List[str]] = None,
        party_members: Optional[List[str]] = None,
        known_npcs: Optional[List[str]] = None
    ) -> ClassificationResult:
        """
        Synchronous prediction returning ClassificationResult for integration.
        
        Args:
            query: The user's query text
            character_name: Optional character name for normalization
            character_aliases: Optional list of character aliases/nicknames
            party_members: Optional list of party member names
            known_npcs: Optional list of known NPC names
            
        Returns:
            ClassificationResult with tools_needed, tool_confidences, entities
        """
        start_time = time.time()
        
        # Get single classification result
        result = self.classify_single(query, character_name, character_aliases, party_members, known_npcs)
        
        # Normalize names to placeholders
        normalized_query = self._normalize_names(
            query, character_name, character_aliases, party_members, known_npcs
        )
        
        # Tokenize and get all tool confidences
        encoding = self.tokenizer(
            normalized_query,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            tool_logits, _ = self.model(input_ids, attention_mask)
            temp = self.model.temperature.item()
            tool_probs = F.softmax(tool_logits / temp, dim=-1)[0]
        
        tool_confidences = {
            self.idx_to_tool[i]: float(tool_probs[i].item())
            for i in range(len(self.tools))
        }
        
        # Build tools_needed list (single tool for now)
        tools_needed = [{
            'tool': result.tool,
            'intention': result.intent,
            'confidence': result.tool_confidence
        }]
        
        # Extract entities using gazetteer NER (if available)
        entities = []
        if self.gazetteer_ner:
            raw_entities = self.gazetteer_ner.extract_simple(query)
            entities = [
                {
                    'name': e['canonical'],
                    'text': e['text'],
                    'type': e['type'],
                    'confidence': e['confidence']
                }
                for e in raw_entities
            ]
        
        inference_time = (time.time() - start_time) * 1000
        
        return ClassificationResult(
            tools_needed=tools_needed,
            tool_confidences=tool_confidences,
            entities=entities,
            backend='local',
            inference_time_ms=inference_time
        )
    
    async def classify(
        self,
        query: str,
        character_name: Optional[str] = None,
        character_aliases: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        party_members: Optional[List[str]] = None,
        known_npcs: Optional[List[str]] = None
    ) -> ClassificationResult:
        """
        Async classification method (required by ClassifierBackend protocol).
        
        Args:
            query: The user's query text
            character_name: Optional character name for normalization
            character_aliases: Optional list of character aliases/nicknames
            conversation_history: Optional prior conversation (not used by local model)
            party_members: Optional list of party member names
            known_npcs: Optional list of known NPC names
            
        Returns:
            ClassificationResult with tools, intents, and entities
        """
        return self.predict_sync(query, character_name, character_aliases, party_members, known_npcs)
    
    def get_all_tool_confidences(
        self,
        query: str,
        character_name: Optional[str] = None,
        character_aliases: Optional[List[str]] = None,
        party_members: Optional[List[str]] = None,
        known_npcs: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Get confidence scores for all tools."""
        result = self.predict_sync(query, character_name, character_aliases, party_members, known_npcs)
        return result.tool_confidences
