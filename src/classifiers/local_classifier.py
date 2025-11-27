"""
Local Two-Stage Joint Model Classifier.

Wraps the trained DeBERTa-v3 model for tool/intent classification
and gazetteer-based NER for entity extraction.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

import torch
import torch.nn as nn
from transformers import DebertaV2TokenizerFast, DebertaV2Model, DebertaV2PreTrainedModel

from .base import ClassificationResult
from .gazetteer_ner import GazetteerEntityExtractor


class TwoStageJointModel(DebertaV2PreTrainedModel):
    """Two-Stage Joint DeBERTa-v3 Model for tool/intent classification."""
    
    def __init__(self, config, num_tools=3, num_ner_tags=25, 
                 num_character_intents=10, num_session_intents=20, num_rulebook_intents=30):
        super().__init__(config)
        
        self.num_tools = num_tools
        self.num_ner_tags = num_ner_tags
        self.num_character_intents = num_character_intents
        self.num_session_intents = num_session_intents
        self.num_rulebook_intents = num_rulebook_intents
        
        self.deberta = DebertaV2Model(config)
        
        classifier_dropout = (
            config.classifier_dropout 
            if hasattr(config, 'classifier_dropout') and config.classifier_dropout is not None
            else config.hidden_dropout_prob
        )
        self.dropout = nn.Dropout(classifier_dropout)
        
        # Stage 1: Tool classification
        self.tool_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size, num_tools)
        )
        
        # Stage 1: NER (kept for compatibility, but we prefer gazetteer)
        self.ner_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size // 2, num_ner_tags)
        )
        
        # Stage 2: Per-tool intent heads
        self.character_intent_head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size // 2, num_character_intents)
        )
        
        self.session_intent_head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size // 2, num_session_intents)
        )
        
        self.rulebook_intent_head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size // 2),
            nn.GELU(),
            nn.Dropout(classifier_dropout),
            nn.Linear(config.hidden_size // 2, num_rulebook_intents)
        )
        
        self.post_init()
        
    def forward(self, input_ids=None, attention_mask=None, **kwargs):
        outputs = self.deberta(input_ids=input_ids, attention_mask=attention_mask)
        
        sequence_output = outputs.last_hidden_state
        cls_output = self.dropout(sequence_output[:, 0, :])
        
        return {
            'tool_logits': self.tool_classifier(cls_output),
            'ner_logits': self.ner_classifier(sequence_output),
            'character_intent_logits': self.character_intent_head(cls_output),
            'session_intent_logits': self.session_intent_head(cls_output),
            'rulebook_intent_logits': self.rulebook_intent_head(cls_output),
        }


class LocalClassifier:
    """
    Local classifier using Two-Stage Joint Model + Gazetteer NER.
    
    Implements the ClassifierBackend protocol for integration with CentralEngine.
    """
    
    def __init__(
        self,
        model_path: str,
        srd_cache_path: str,
        device: str = 'auto',
        tool_threshold: float = 0.5,
        gazetteer_min_similarity: float = 0.80,
        temperature: float = 5.0  # Temperature scaling for calibrated confidence
    ):
        """
        Initialize the local classifier.
        
        Args:
            model_path: Path to the trained model directory
            srd_cache_path: Path to SRD cache for gazetteer NER
            device: Device to use ('auto', 'cuda', 'mps', 'cpu')
            tool_threshold: Confidence threshold for tool selection
            gazetteer_min_similarity: Minimum similarity for gazetteer matching
            temperature: Temperature for scaling logits (higher = softer probabilities)
                         Default 5.0 provides more calibrated confidence scores.
        """
        self.model_path = Path(model_path)
        self.srd_cache_path = Path(srd_cache_path)
        self.tool_threshold = tool_threshold
        self.temperature = temperature
        
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
        
        # Load model components
        self._load_mappings()
        self._load_model()
        self._load_gazetteer(gazetteer_min_similarity)
    
    def _load_mappings(self) -> None:
        """Load label mappings from training."""
        with open(self.model_path / 'label_mappings.json') as f:
            self.mappings = json.load(f)
        
        self.tools = list(self.mappings['tool_to_idx'].keys())
        self.idx_to_tag = {int(k): v for k, v in self.mappings['idx_to_tag'].items()}
        self.idx_to_intent_per_tool = self.mappings['idx_to_intent_per_tool']
        
        with open(self.model_path / 'training_config.json') as f:
            self.config = json.load(f)
        
        print(f"[LocalClassifier] Loaded mappings: {len(self.tools)} tools, "
              f"{len(self.mappings['tag_to_idx'])} NER tags")
    
    def _load_model(self) -> None:
        """Load the trained model and tokenizer."""
        print("[LocalClassifier] Loading tokenizer...")
        self.tokenizer = DebertaV2TokenizerFast.from_pretrained(self.model_path)
        
        print("[LocalClassifier] Loading model...")
        self.model = TwoStageJointModel.from_pretrained(
            self.model_path,
            num_tools=len(self.tools),
            num_ner_tags=len(self.mappings['tag_to_idx']),
            num_character_intents=self.mappings['num_intents_per_tool']['character_data'],
            num_session_intents=self.mappings['num_intents_per_tool']['session_notes'],
            num_rulebook_intents=self.mappings['num_intents_per_tool']['rulebook']
        )
        self.model.to(self.device)
        self.model.eval()
        print("[LocalClassifier] Model loaded successfully!")
    
    def _load_gazetteer(self, min_similarity: float) -> None:
        """Load gazetteer-based NER."""
        if self.srd_cache_path.exists():
            print("[LocalClassifier] Loading gazetteer NER...")
            self.gazetteer_ner = GazetteerEntityExtractor(
                self.srd_cache_path, 
                min_similarity=min_similarity
            )
        else:
            print(f"[LocalClassifier] Warning: SRD cache not found at {self.srd_cache_path}")
            self.gazetteer_ner = None
    
    def predict_sync(self, query: str) -> ClassificationResult:
        """
        Synchronous prediction for a query.
        
        Args:
            query: The user's query text
            
        Returns:
            ClassificationResult with tools, intents, and entities
        """
        start_time = time.time()
        
        # Tokenize
        encoding = self.tokenizer(
            query,
            max_length=self.config['max_length'],
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Run model inference
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        
        # Process tool predictions with temperature scaling for calibrated confidence
        # Raw sigmoid gives 0/1 due to large logits; temperature softens this
        tool_logits = outputs['tool_logits'][0]
        scaled_logits = tool_logits / self.temperature
        tool_probs = torch.sigmoid(scaled_logits).cpu().numpy()
        tool_confidences = {self.tools[i]: float(p) for i, p in enumerate(tool_probs)}
        
        # For actual selection, use raw sigmoid (model's true prediction)
        raw_probs = torch.sigmoid(tool_logits).cpu().numpy()
        selected_tools = [self.tools[i] for i, p in enumerate(raw_probs) if p > self.tool_threshold]
        
        # Get intents for selected tools
        tools_needed = []
        for tool in selected_tools:
            confidence = tool_confidences[tool]  # Use calibrated confidence for display
            
            # Get intention based on tool type
            if tool == 'character_data':
                idx = outputs['character_intent_logits'].argmax(dim=-1).item()
                intention = self.idx_to_intent_per_tool['character_data'][str(idx)]
            elif tool == 'session_notes':
                idx = outputs['session_intent_logits'].argmax(dim=-1).item()
                intention = self.idx_to_intent_per_tool['session_notes'][str(idx)]
            elif tool == 'rulebook':
                idx = outputs['rulebook_intent_logits'].argmax(dim=-1).item()
                intention = self.idx_to_intent_per_tool['rulebook'][str(idx)]
            else:
                intention = 'general'
            
            tools_needed.append({
                'tool': tool,
                'intention': intention,
                'confidence': confidence
            })
        
        # Extract entities using gazetteer NER
        entities = []
        if self.gazetteer_ner:
            raw_entities = self.gazetteer_ner.extract_simple(query)
            entities = [
                {
                    'name': e['canonical'],  # Use canonical name for matching
                    'text': e['text'],       # Original text from query
                    'type': e['type'],
                    'confidence': e['confidence']
                }
                for e in raw_entities
            ]
        
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        
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
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> ClassificationResult:
        """
        Async classification method (required by ClassifierBackend protocol).
        
        Note: The local model doesn't use character_name or conversation_history,
        but accepts them for interface compatibility.
        """
        # Run sync prediction (model inference is fast enough)
        return self.predict_sync(query)
    
    def get_all_tool_confidences(self, query: str) -> Dict[str, float]:
        """Get confidence scores for all tools (useful for comparison logging)."""
        result = self.predict_sync(query)
        return result.tool_confidences
