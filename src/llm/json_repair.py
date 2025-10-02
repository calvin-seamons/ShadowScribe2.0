"""
JSON Repair Utility

Fixes common JSON parsing issues and schema mismatches from LLM responses.
Ensures proper JSON structure and patches responses to match expected schemas.
"""

import json
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RepairResult:
    """Result of JSON repair operation."""
    data: Dict[str, Any]
    was_repaired: bool
    repair_details: List[str]
    original_error: Optional[str] = None


class JSONRepairError(Exception):
    """Raised when JSON cannot be repaired."""
    pass


class JSONRepair:
    """
    Utility class to repair malformed JSON responses from LLMs.
    
    Handles:
    1. Syntax errors (missing quotes, trailing commas, etc.)
    2. Schema mismatches (field name differences)
    3. Missing required fields
    4. Type corrections
    """
    
    @staticmethod
    def repair_json_string(json_str: str) -> RepairResult:
        """
        Attempt to repair a malformed JSON string.
        
        Args:
            json_str: The potentially malformed JSON string
            
        Returns:
            RepairResult with repaired data and details
        """
        repair_details = []
        original_error = None
        
        # First, try to parse as-is
        try:
            data = json.loads(json_str)
            return RepairResult(
                data=data,
                was_repaired=False,
                repair_details=[]
            )
        except json.JSONDecodeError as e:
            original_error = str(e)
            logger.debug(f"Initial JSON parse failed: {e}")
        
        # Apply common fixes
        repaired_str = json_str
        
        # Fix 1: Remove trailing commas
        if ",}" in repaired_str or ",]" in repaired_str:
            repaired_str = re.sub(r',\s*}', '}', repaired_str)
            repaired_str = re.sub(r',\s*]', ']', repaired_str)
            repair_details.append("Removed trailing commas")
        
        # Fix 2: Add missing quotes to keys
        repaired_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', repaired_str)
        
        # Fix 3: Fix single quotes to double quotes
        if "'" in repaired_str:
            repaired_str = repaired_str.replace("'", '"')
            repair_details.append("Converted single quotes to double quotes")
        
        # Fix 4: Handle boolean values
        repaired_str = re.sub(r'\bTrue\b', 'true', repaired_str)
        repaired_str = re.sub(r'\bFalse\b', 'false', repaired_str)
        repaired_str = re.sub(r'\bNone\b', 'null', repaired_str)
        
        # Fix 5: Remove Python-style comments
        repaired_str = re.sub(r'#.*$', '', repaired_str, flags=re.MULTILINE)
        
        # Fix 6: Handle XML-like garbage at the end (from truncated responses)
        if '</parameter>' in repaired_str or '</invoke>' in repaired_str:
            # Find the last valid JSON closing brace before the garbage
            last_brace = repaired_str.rfind('}')
            if last_brace > 0:
                repaired_str = repaired_str[:last_brace + 1]
                repair_details.append("Removed XML garbage from truncated response")
        
        # Fix 7: Handle malformed quoted keys like 'context_hints":
        repaired_str = re.sub(r'"([^"]+)"\s*":', r'"\1":', repaired_str)
        if r'":' in repaired_str:
            repair_details.append("Fixed malformed quoted keys")
        
        # Try parsing again
        try:
            data = json.loads(repaired_str)
            return RepairResult(
                data=data,
                was_repaired=True,
                repair_details=repair_details,
                original_error=original_error
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON repair failed: {e}")
            raise JSONRepairError(f"Unable to repair JSON: {e}") from e
    
    @staticmethod
    def repair_character_router_response(response: Any) -> RepairResult:
        """
        Repair and validate character router response.
        
        Expected schema:
        {
          "is_needed": boolean,
          "confidence": float,
          "user_intentions": array of strings,
          "entities": array
        }
        """
        repair_details = []
        
        # Handle string input (needs JSON parsing)
        if isinstance(response, str):
            repair_result = JSONRepair.repair_json_string(response)
            if repair_result.was_repaired:
                repair_details.extend(repair_result.repair_details)
            data = repair_result.data
        else:
            data = dict(response) if response else {}
        
        # Handle wrapped responses like {'json': {...}}
        if 'json' in data and isinstance(data['json'], dict):
            data = data['json']
            repair_details.append("Unwrapped response from 'json' key")
        
        # Ensure required fields exist
        if "is_needed" not in data:
            data["is_needed"] = False
            repair_details.append("Added missing 'is_needed' field (defaulted to false)")
        
        if "confidence" not in data:
            data["confidence"] = 0.5
            repair_details.append("Added missing 'confidence' field (defaulted to 0.5)")
        
        if "entities" not in data:
            data["entities"] = []
            repair_details.append("Added missing 'entities' field (defaulted to empty array)")
        
        # Handle user_intentions field
        if data.get("is_needed", False):
            # Handle both old and new field names for backwards compatibility
            user_intentions = None
            
            if "user_intentions" in data:
                user_intentions = data["user_intentions"]
            elif "user_intention" in data and data["user_intention"] is not None:
                # Convert single intention to array
                user_intentions = [data["user_intention"]]
                repair_details.append("Converted single 'user_intention' to 'user_intentions' array")
            elif "intention" in data and data["intention"] is not None:
                # Convert alternative field name
                user_intentions = [data["intention"]]
                repair_details.append("Mapped 'intention' to 'user_intentions' array")
            
            if user_intentions is None or len(user_intentions) == 0:
                user_intentions = ["character_basics"]  # Safe default
                repair_details.append("Added missing 'user_intentions' field (defaulted to ['character_basics'])")
            elif len(user_intentions) > 2:
                user_intentions = user_intentions[:2]
                repair_details.append("Truncated 'user_intentions' to maximum of 2 items")
            
            data["user_intentions"] = user_intentions
        else:
            data["user_intentions"] = []
        
        # Clean up old fields
        if "user_intention" in data:
            del data["user_intention"]
        if "intention" in data:
            del data["intention"]
        
        # Validate and fix entities format
        if not isinstance(data["entities"], list):
            data["entities"] = []
            repair_details.append("Fixed 'entities' field to be an array")
        
        # Ensure each entity has required fields
        fixed_entities = []
        for entity in data["entities"]:
            if not isinstance(entity, dict):
                continue
            
            fixed_entity = dict(entity)
            if "name" not in fixed_entity:
                fixed_entity["name"] = ""
            if "type" not in fixed_entity:
                fixed_entity["type"] = "unknown"
            if "confidence" not in fixed_entity:
                fixed_entity["confidence"] = 0.5
                
            fixed_entities.append(fixed_entity)
        
        if len(fixed_entities) != len(data["entities"]):
            repair_details.append("Fixed entity formats")
        
        data["entities"] = fixed_entities
        
        return RepairResult(
            data=data,
            was_repaired=len(repair_details) > 0,
            repair_details=repair_details
        )
    
    @staticmethod
    def repair_rulebook_router_response(response: Any) -> RepairResult:
        """
        Repair and validate rulebook router response.
        
        Expected schema:
        {
          "is_needed": boolean,
          "confidence": float,
          "intention": string or null,
          "entities": array,
          "context_hints": array
        }
        """
        repair_details = []
        
        # Handle string input (needs JSON parsing)
        if isinstance(response, str):
            repair_result = JSONRepair.repair_json_string(response)
            if repair_result.was_repaired:
                repair_details.extend(repair_result.repair_details)
            data = repair_result.data
        else:
            data = dict(response) if response else {}
        
        # Handle wrapped responses like {'json': {...}}
        if 'json' in data and isinstance(data['json'], dict):
            data = data['json']
            repair_details.append("Unwrapped response from 'json' key")
        
        # Ensure required fields exist
        if "is_needed" not in data:
            data["is_needed"] = False
            repair_details.append("Added missing 'is_needed' field (defaulted to false)")
        
        if "confidence" not in data:
            data["confidence"] = 0.5
            repair_details.append("Added missing 'confidence' field (defaulted to 0.5)")
        
        if "entities" not in data:
            data["entities"] = []
            repair_details.append("Added missing 'entities' field (defaulted to empty array)")
        
        if "context_hints" not in data:
            data["context_hints"] = []
            repair_details.append("Added missing 'context_hints' field (defaulted to empty array)")
        
        # Handle intention field (note: different from character router!)
        if data.get("is_needed", False):
            if "intention" not in data or data["intention"] is None:
                # Check for alternative field names
                if "user_intention" in data:
                    data["intention"] = data["user_intention"]
                    repair_details.append("Mapped 'user_intention' to 'intention'")
                else:
                    data["intention"] = "general"  # Safe default
                    repair_details.append("Added missing 'intention' field (defaulted to 'general')")
        else:
            data["intention"] = None
        
        # Validate and fix entities format
        if not isinstance(data["entities"], list):
            data["entities"] = []
            repair_details.append("Fixed 'entities' field to be an array")
        
        # Validate and fix context_hints format
        if not isinstance(data["context_hints"], list):
            data["context_hints"] = []
            repair_details.append("Fixed 'context_hints' field to be an array")
        
        # Ensure each entity has required fields
        fixed_entities = []
        for entity in data["entities"]:
            if not isinstance(entity, dict):
                continue
            
            fixed_entity = dict(entity)
            if "name" not in fixed_entity:
                fixed_entity["name"] = ""
            if "type" not in fixed_entity:
                fixed_entity["type"] = "unknown"
                
            fixed_entities.append(fixed_entity)
        
        if len(fixed_entities) != len(data["entities"]):
            repair_details.append("Fixed entity formats")
        
        data["entities"] = fixed_entities
        
        return RepairResult(
            data=data,
            was_repaired=len(repair_details) > 0,
            repair_details=repair_details
        )
    
    @staticmethod
    def repair_session_notes_router_response(response: Any) -> RepairResult:
        """
        Repair and validate session notes router response.
        
        Expected schema:
        {
          "is_needed": boolean,
          "confidence": float,
          "intention": string or null,  
          "entities": array,
          "context_hints": array
        }
        """
        repair_details = []
        
        # Handle string input (needs JSON parsing)
        if isinstance(response, str):
            repair_result = JSONRepair.repair_json_string(response)
            if repair_result.was_repaired:
                repair_details.extend(repair_result.repair_details)
            data = repair_result.data
        else:
            data = dict(response) if response else {}
        
        # Handle wrapped responses like {'json': {...}}
        if 'json' in data and isinstance(data['json'], dict):
            data = data['json']
            repair_details.append("Unwrapped response from 'json' key")
        
        # Ensure required fields exist
        if "is_needed" not in data:
            data["is_needed"] = False
            repair_details.append("Added missing 'is_needed' field (defaulted to false)")
        
        if "confidence" not in data:
            data["confidence"] = 0.5
            repair_details.append("Added missing 'confidence' field (defaulted to 0.5)")
        
        if "entities" not in data:
            data["entities"] = []
            repair_details.append("Added missing 'entities' field (defaulted to empty array)")
        
        if "context_hints" not in data:
            data["context_hints"] = []
            repair_details.append("Added missing 'context_hints' field (defaulted to empty array)")
        
        # Handle intention field
        if data.get("is_needed", False):
            if "intention" not in data or data["intention"] is None:
                # Check for alternative field names
                if "user_intention" in data:
                    data["intention"] = data["user_intention"]
                    repair_details.append("Mapped 'user_intention' to 'intention'")
                else:
                    data["intention"] = "general"  # Safe default
                    repair_details.append("Added missing 'intention' field (defaulted to 'general')")
        else:
            data["intention"] = None
        
        # Validate and fix entities format
        if not isinstance(data["entities"], list):
            data["entities"] = []
            repair_details.append("Fixed 'entities' field to be an array")
        
        # Validate and fix context_hints format
        if not isinstance(data["context_hints"], list):
            data["context_hints"] = []
            repair_details.append("Fixed 'context_hints' field to be an array")
        
        return RepairResult(
            data=data,
            was_repaired=len(repair_details) > 0,
            repair_details=repair_details
        )