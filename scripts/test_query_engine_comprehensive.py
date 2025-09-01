"""
Comprehensive Testing Script for RulebookQueryEngine
Tests various intentions, entities, and query patterns with detailed output logging
"""

import sys
from pathlib import Path
from datetime import datetime
import traceback

# Standard project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rulebook import RulebookStorage, RulebookQueryEngine
from src.rag.rulebook.rulebook_types import RulebookQueryIntent


class QueryEngineTestSuite:
    """Comprehensive test suite for RulebookQueryEngine"""
    
    def __init__(self, output_file: str = None):
        self.output_file = output_file or f"query_engine_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.output_lines = []
        
        # Initialize storage and engine
        self.storage = None
        self.engine = None
        
    def log(self, message: str, also_print: bool = True):
        """Log message to output file and optionally print to console"""
        self.output_lines.append(message)
        if also_print:
            print(message)
    
    def setup(self):
        """Initialize storage and query engine"""
        self.log("=" * 80)
        self.log("D&D 5E RULEBOOK QUERY ENGINE - COMPREHENSIVE TEST SUITE")
        self.log(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 80)
        
        try:
            # Load storage
            storage_path = "knowledge_base/processed_rulebook"
            self.storage = RulebookStorage(storage_path)
            self.storage.load_from_disk()
            
            self.log(f"✓ Loaded {len(self.storage.sections)} rulebook sections")
            
            # Initialize query engine
            self.engine = RulebookQueryEngine(self.storage)
            self.log("✓ Query engine initialized successfully")
            
            return True
            
        except FileNotFoundError:
            self.log("✗ CRITICAL ERROR: No rulebook storage found!")
            self.log("Please run: python -m scripts.build_rulebook_storage")
            return False
        except Exception as e:
            self.log(f"✗ CRITICAL ERROR during setup: {e}")
            self.log(traceback.format_exc())
            return False
    
    def run_test_query(self, test_name: str, intention: RulebookQueryIntent, 
                      user_query: str, entities: list, context_hints: list = None, 
                      k: int = 3, expected_keywords: list = None):
        """Run a single test query and log detailed results"""
        
        self.log(f"\n{'='*60}")
        self.log(f"TEST: {test_name}")
        self.log(f"{'='*60}")
        self.log(f"Intention: {intention.value}")
        self.log(f"Query: {user_query}")
        self.log(f"Entities: {entities}")
        self.log(f"Context Hints: {context_hints or 'None'}")
        self.log(f"Results Requested (k): {k}")
        if expected_keywords:
            self.log(f"Expected Keywords: {expected_keywords}")
        
        try:
            # Execute query
            results, performance = self.engine.query(
                intention=intention,
                user_query=user_query,
                entities=entities,
                context_hints=context_hints or [],
                k=k
            )
            
            self.log(f"\n📊 RESULTS: Found {len(results)} sections")
            self.log(f"⏱️  Query Time: {performance.total_time_ms:.1f}ms")
            
            if not results:
                self.log("⚠️  No results returned - this may indicate an issue")
                return
            
            # Analyze results
            for i, result in enumerate(results, 1):
                self.log(f"\n--- RESULT {i} ---")
                self.log(f"Score: {result.score:.4f}")
                self.log(f"Section Title: {result.section.title}")
                self.log(f"Section ID: {result.section.id}")
                self.log(f"Section Level: {result.section.level}")
                self.log(f"Categories: {[cat.name for cat in result.section.categories]}")
                self.log(f"Matched Entities: {result.matched_entities}")
                self.log(f"Matched Context: {result.matched_context}")
                self.log(f"Includes Children: {result.includes_children}")
                
                # Content analysis
                content_length = len(result.section.content)
                content_preview = result.section.content[:300].replace('\n', ' ').replace('  ', ' ')
                if content_length > 300:
                    content_preview += f"... [+{content_length-300} more chars]"
                
                self.log(f"Content Length: {content_length} characters")
                self.log(f"Content Preview: {content_preview}")
                
                # Check for expected keywords if provided
                if expected_keywords:
                    content_lower = result.section.content.lower()
                    title_lower = result.section.title.lower()
                    found_keywords = []
                    missing_keywords = []
                    
                    for keyword in expected_keywords:
                        if keyword.lower() in content_lower or keyword.lower() in title_lower:
                            found_keywords.append(keyword)
                        else:
                            missing_keywords.append(keyword)
                    
                    self.log(f"Expected Keywords Found: {found_keywords}")
                    if missing_keywords:
                        self.log(f"Expected Keywords Missing: {missing_keywords}")
            
            # Overall assessment
            self.log(f"\n📈 ASSESSMENT:")
            avg_score = sum(r.score for r in results) / len(results)
            self.log(f"Average Score: {avg_score:.4f}")
            
            entity_match_rate = sum(1 for r in results if r.matched_entities) / len(results)
            self.log(f"Entity Match Rate: {entity_match_rate:.2%}")
            
            if context_hints:
                context_match_rate = sum(1 for r in results if r.matched_context) / len(results)
                self.log(f"Context Hint Match Rate: {context_match_rate:.2%}")
            
            category_distribution = {}
            for result in results:
                for cat in result.section.categories:
                    category_distribution[cat.name] = category_distribution.get(cat.name, 0) + 1
            self.log(f"Category Distribution: {category_distribution}")
            
        except Exception as e:
            self.log(f"✗ ERROR executing query: {e}")
            self.log(traceback.format_exc())
    
    def run_all_tests(self):
        """Run comprehensive test suite covering all major use cases"""
        
        test_cases = [
            # SPELL QUERIES
            {
                "test_name": "Fireball Spell Details",
                "intention": RulebookQueryIntent.SPELL_DETAILS,
                "user_query": "How does the fireball spell work and what damage does it deal?",
                "entities": ["fireball", "damage", "spell"],
                "context_hints": ["area of effect", "3rd level", "dexterity saving throw", "evocation"],
                "k": 3,
                "expected_keywords": ["fireball", "8d6", "damage", "20-foot radius", "dexterity"]
            },
            {
                "test_name": "Healing Spells",
                "intention": RulebookQueryIntent.SPELL_DETAILS,
                "user_query": "What healing spells can a cleric cast?",
                "entities": ["healing", "cleric", "spells"],
                "context_hints": ["cure wounds", "healing word", "restore", "hit points"],
                "k": 4,
                "expected_keywords": ["healing", "hit points", "cleric"]
            },
            
            # CHARACTER CREATION
            {
                "test_name": "Elf Racial Traits",
                "intention": RulebookQueryIntent.CHARACTER_CREATION,
                "user_query": "What are the racial traits and abilities of elves?",
                "entities": ["elf", "racial traits", "abilities"],
                "context_hints": ["darkvision", "keen senses", "fey ancestry", "trance"],
                "k": 3,
                "expected_keywords": ["elf", "darkvision", "keen senses", "fey ancestry"]
            },
            {
                "test_name": "Multiclassing Rules",
                "intention": RulebookQueryIntent.MULTICLASS_RULES,
                "user_query": "How do multiclassing requirements and spell slots work?",
                "entities": ["multiclassing", "requirements", "spell slots"],
                "context_hints": ["ability score", "prerequisites", "spell slot table"],
                "k": 3,
                "expected_keywords": ["multiclassing", "prerequisites", "spell slots"]
            },
            
            # COMBAT MECHANICS
            {
                "test_name": "Opportunity Attacks",
                "intention": RulebookQueryIntent.TACTICAL_USAGE,
                "user_query": "When do opportunity attacks trigger and how do they work?",
                "entities": ["opportunity attack", "reaction", "movement"],
                "context_hints": ["leaving reach", "threatened area", "provoking"],
                "k": 2,
                "expected_keywords": ["opportunity attack", "reaction", "reach", "movement"]
            },
            {
                "test_name": "Grappling Rules",
                "intention": RulebookQueryIntent.TACTICAL_USAGE,
                "user_query": "How does grappling work in combat?",
                "entities": ["grappling", "grapple", "combat"],
                "context_hints": ["athletics", "acrobatics", "escape", "restrained"],
                "k": 3,
                "expected_keywords": ["grapple", "athletics", "restrained"]
            },
            
            # CLASS FEATURES
            {
                "test_name": "Barbarian Rage",
                "intention": RulebookQueryIntent.CLASS_SPELL_ACCESS,
                "user_query": "How does barbarian rage work and what bonuses does it provide?",
                "entities": ["barbarian", "rage", "bonuses"],
                "context_hints": ["damage bonus", "resistance", "advantage", "strength"],
                "k": 3,
                "expected_keywords": ["rage", "barbarian", "damage", "resistance"]
            },
            {
                "test_name": "Wizard Spell Preparation",
                "intention": RulebookQueryIntent.CLASS_SPELL_ACCESS,
                "user_query": "How do wizards prepare and learn new spells?",
                "entities": ["wizard", "spell preparation", "learning spells"],
                "context_hints": ["spellbook", "intelligence modifier", "spell scroll"],
                "k": 3,
                "expected_keywords": ["wizard", "spellbook", "prepare", "intelligence"]
            },
            
            # CONDITIONS AND EFFECTS
            {
                "test_name": "Condition Effects",
                "intention": RulebookQueryIntent.CONDITION_EFFECTS,
                "user_query": "What are the effects of being poisoned and paralyzed?",
                "entities": ["poisoned", "paralyzed", "conditions"],
                "context_hints": ["disadvantage", "incapacitated", "automatic critical"],
                "k": 4,
                "expected_keywords": ["poisoned", "paralyzed", "disadvantage", "incapacitated"]
            },
            
            # EQUIPMENT AND MAGIC ITEMS
            {
                "test_name": "Magic Weapon Properties",
                "intention": RulebookQueryIntent.EQUIPMENT_PROPERTIES,
                "user_query": "What are the properties of a +1 sword and how does magic weapon enhancement work?",
                "entities": ["magic weapon", "+1 sword", "enhancement"],
                "context_hints": ["attack bonus", "damage bonus", "magical"],
                "k": 3,
                "expected_keywords": ["magic", "weapon", "bonus", "attack"]
            },
            {
                "test_name": "Armor Class Calculation",
                "intention": RulebookQueryIntent.CALCULATE_VALUES,
                "user_query": "How is armor class calculated with different armor types?",
                "entities": ["armor class", "calculation", "armor types"],
                "context_hints": ["dexterity bonus", "base AC", "shield", "natural armor"],
                "k": 3,
                "expected_keywords": ["armor class", "dexterity", "AC", "calculation"]
            },
            
            # CREATURE STATS AND ABILITIES
            {
                "test_name": "Dragon Abilities",
                "intention": RulebookQueryIntent.CREATURE_ABILITIES,
                "user_query": "What special abilities do adult red dragons have?",
                "entities": ["adult red dragon", "dragon", "abilities"],
                "context_hints": ["breath weapon", "legendary actions", "frightful presence"],
                "k": 3,
                "expected_keywords": ["dragon", "breath", "legendary", "fire"]
            },
            
            # CORE MECHANICS
            {
                "test_name": "Advantage and Disadvantage",
                "intention": RulebookQueryIntent.RULE_MECHANICS,
                "user_query": "How do advantage and disadvantage work with dice rolls?",
                "entities": ["advantage", "disadvantage", "dice rolls"],
                "context_hints": ["roll twice", "highest", "lowest", "cancel out"],
                "k": 2,
                "expected_keywords": ["advantage", "disadvantage", "roll", "twice"]
            },
            
            # EXPLORATION AND TRAVEL
            {
                "test_name": "Travel and Rest Rules",
                "intention": RulebookQueryIntent.REST_MECHANICS,
                "user_query": "How do short rests and long rests work for recovery?",
                "entities": ["short rest", "long rest", "recovery"],
                "context_hints": ["hit dice", "spell slots", "8 hours", "1 hour"],
                "k": 3,
                "expected_keywords": ["rest", "recovery", "hit dice", "spell slots"]
            },
            
            # COMPLEX MULTI-SYSTEM QUERIES
            {
                "test_name": "Spellcasting in Combat",
                "intention": RulebookQueryIntent.ACTION_OPTIONS,
                "user_query": "What are the action economy rules for casting spells in combat?",
                "entities": ["spellcasting", "action economy", "combat"],
                "context_hints": ["bonus action", "reaction", "concentration", "casting time"],
                "k": 4,
                "expected_keywords": ["spell", "action", "bonus action", "concentration"]
            }
        ]
        
        # Run all test cases
        for test_case in test_cases:
            self.run_test_query(**test_case)
        
        # Summary statistics
        self.log(f"\n{'='*80}")
        self.log("TEST SUITE SUMMARY")
        self.log(f"{'='*80}")
        self.log(f"Total tests executed: {len(test_cases)}")
        self.log(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save all logged output to file"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for line in self.output_lines:
                    f.write(line + '\n')
            
            self.log(f"\n✓ Test results saved to: {self.output_file}")
            
        except Exception as e:
            self.log(f"✗ Error saving results: {e}")


def main():
    """Run the comprehensive test suite"""
    # Create test suite with timestamped output file
    test_suite = QueryEngineTestSuite()
    
    # Setup and run tests
    if test_suite.setup():
        test_suite.run_all_tests()
    else:
        test_suite.save_results()  # Save error logs even if setup failed


if __name__ == "__main__":
    main()
