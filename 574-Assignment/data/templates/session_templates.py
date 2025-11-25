"""
Session Notes Query Templates

Templates for generating synthetic training data for the session_notes tool.
Each intent has 10-15 templates that can be filled with entity slots.

20 Intents:
- character_status
- event_sequence
- npc_info
- location_details
- item_tracking
- combat_recap
- spell_ability_usage
- character_decisions
- party_dynamics
- quest_tracking
- puzzle_solutions
- loot_rewards
- death_revival
- divine_religious
- memory_vision
- rules_mechanics
- humor_moments
- unresolved_mysteries
- future_implications
- cross_session
"""

# =============================================================================
# CHARACTER_STATUS - Current state of characters
# =============================================================================

CHARACTER_STATUS_TEMPLATES = [
    {"template": "What is my current HP?", "slots": {}},
    {"template": "What conditions am I suffering from?", "slots": {}},
    {"template": "Am I alive or dead right now?", "slots": {}},
    {"template": "Where is my character located?", "slots": {}},
    {"template": "What's my character's current state?", "slots": {}},
    {"template": "How did my physical state change in the last session?", "slots": {}},
    {"template": "What happened to me in the last session?", "slots": {}},
    {"template": "Am I injured?", "slots": {}},
    {"template": "What debuffs do I have?", "slots": {}},
    {"template": "Is my character conscious?", "slots": {}},
]

# =============================================================================
# EVENT_SEQUENCE - Chronological events
# =============================================================================

EVENT_SEQUENCE_TEMPLATES = [
    {"template": "What happened in the last session?", "slots": {}},
    {"template": "Walk me through the events of the last session", "slots": {}},
    {"template": "What were the key events that occurred?", "slots": {}},
    {"template": "Give me a chronological summary", "slots": {}},
    {"template": "What happened first, second, and third?", "slots": {}},
    {"template": "Describe the last session in order", "slots": {}},
    {"template": "What's the timeline of recent events?", "slots": {}},
    {"template": "Recap what happened", "slots": {}},
    {"template": "What did we do last time?", "slots": {}},
    {"template": "Summarize the session events", "slots": {}},
]

# =============================================================================
# NPC_INFO - NPC interactions and relationships
# =============================================================================

NPC_INFO_TEMPLATES = [
    {"template": "Who did we meet in the last session?", "slots": {}},
    {"template": "Tell me about the NPCs we encountered", "slots": {}},
    {"template": "What NPCs did we interact with?", "slots": {}},
    {"template": "Who was the {creature} we met?", "slots": {"creature": "creature"}},
    {"template": "What did the {creature} want?", "slots": {"creature": "creature"}},
    {"template": "How did our conversation with the {creature} go?", "slots": {"creature": "creature"}},
    {"template": "What do we know about the NPCs?", "slots": {}},
    {"template": "Who helped us?", "slots": {}},
    {"template": "Who was hostile to us?", "slots": {}},
    {"template": "What's the relationship with the NPCs we met?", "slots": {}},
    {"template": "Did we make any new allies?", "slots": {}},
    {"template": "Who betrayed us?", "slots": {}},
]

# =============================================================================
# LOCATION_DETAILS - Places visited and explored
# =============================================================================

LOCATION_DETAILS_TEMPLATES = [
    {"template": "Where did we go in the last session?", "slots": {}},
    {"template": "What locations did we visit?", "slots": {}},
    {"template": "Describe the {location} we explored", "slots": {"location": "location"}},
    {"template": "What's notable about the places we visited?", "slots": {}},
    {"template": "What did we find at the {location}?", "slots": {"location": "location"}},
    {"template": "Where are we now?", "slots": {}},
    {"template": "What places have we explored?", "slots": {}},
    {"template": "Tell me about the dungeon we went through", "slots": {}},
    {"template": "What was the environment like?", "slots": {}},
    {"template": "What dangers were in the {location}?", "slots": {"location": "location"}},
]

# =============================================================================
# ITEM_TRACKING - Items found, lost, used
# =============================================================================

ITEM_TRACKING_TEMPLATES = [
    {"template": "What items did we find in the last session?", "slots": {}},
    {"template": "What did we pick up?", "slots": {}},
    {"template": "Did we lose any items?", "slots": {}},
    {"template": "What happened to the {item}?", "slots": {"item": "item"}},
    {"template": "What items were used during the session?", "slots": {}},
    {"template": "Who has the {item}?", "slots": {"item": "item"}},
    {"template": "What did we trade?", "slots": {}},
    {"template": "Did we buy or sell anything?", "slots": {}},
    {"template": "What equipment changed hands?", "slots": {}},
    {"template": "Track the {item} - where is it now?", "slots": {"item": "item"}},
]

# =============================================================================
# COMBAT_RECAP - Past combat encounters
# =============================================================================

COMBAT_RECAP_TEMPLATES = [
    {"template": "What fights did we have?", "slots": {}},
    {"template": "Describe the combat encounters", "slots": {}},
    {"template": "How did the battle go?", "slots": {}},
    {"template": "Who did we fight?", "slots": {}},
    {"template": "What was the outcome of the combat?", "slots": {}},
    {"template": "How much damage did we take?", "slots": {}},
    {"template": "What tactics did we use?", "slots": {}},
    {"template": "How did we defeat the {creature}?", "slots": {"creature": "creature"}},
    {"template": "What was the hardest fight?", "slots": {}},
    {"template": "Did anyone go down in combat?", "slots": {}},
    {"template": "What enemies did we face?", "slots": {}},
]

# =============================================================================
# SPELL_ABILITY_USAGE - Spells and abilities used
# =============================================================================

SPELL_ABILITY_USAGE_TEMPLATES = [
    {"template": "What spells were cast in the session?", "slots": {}},
    {"template": "Did I use {spell}?", "slots": {"spell": "spell"}},
    {"template": "What abilities did we use?", "slots": {}},
    {"template": "How effective was {spell}?", "slots": {"spell": "spell"}},
    {"template": "What magical effects happened?", "slots": {}},
    {"template": "Did anyone cast {spell}?", "slots": {"spell": "spell"}},
    {"template": "What special abilities were activated?", "slots": {}},
    {"template": "How did {feature} work in that situation?", "slots": {"feature": "feature"}},
    {"template": "What resources did we expend?", "slots": {}},
    {"template": "Track spell slot usage", "slots": {}},
]

# =============================================================================
# CHARACTER_DECISIONS - Important choices made
# =============================================================================

CHARACTER_DECISIONS_TEMPLATES = [
    {"template": "What important decisions did we make?", "slots": {}},
    {"template": "Why did we choose that path?", "slots": {}},
    {"template": "What was our reasoning?", "slots": {}},
    {"template": "What moral choices did we face?", "slots": {}},
    {"template": "What did we decide about the {creature}?", "slots": {"creature": "creature"}},
    {"template": "What commitments did we make?", "slots": {}},
    {"template": "What promises did we give?", "slots": {}},
    {"template": "Why did my character do that?", "slots": {}},
    {"template": "What influenced our decisions?", "slots": {}},
    {"template": "What consequences came from our choices?", "slots": {}},
]

# =============================================================================
# PARTY_DYNAMICS - Group interactions
# =============================================================================

PARTY_DYNAMICS_TEMPLATES = [
    {"template": "How is the party getting along?", "slots": {}},
    {"template": "What happened between party members?", "slots": {}},
    {"template": "Did anyone argue?", "slots": {}},
    {"template": "What party interactions were significant?", "slots": {}},
    {"template": "How did the group work together?", "slots": {}},
    {"template": "Were there any conflicts?", "slots": {}},
    {"template": "Who took the lead?", "slots": {}},
    {"template": "What bonding moments happened?", "slots": {}},
    {"template": "How did party roles develop?", "slots": {}},
    {"template": "What's the group dynamic like?", "slots": {}},
]

# =============================================================================
# QUEST_TRACKING - Quest progress and completion
# =============================================================================

QUEST_TRACKING_TEMPLATES = [
    {"template": "What quest progress did we make?", "slots": {}},
    {"template": "What quests did we complete?", "slots": {}},
    {"template": "What new quests did we accept?", "slots": {}},
    {"template": "What's the status of our main quest?", "slots": {}},
    {"template": "What objectives did we accomplish?", "slots": {}},
    {"template": "What side quests are active?", "slots": {}},
    {"template": "What did we learn about our quest?", "slots": {}},
    {"template": "How close are we to finishing the quest?", "slots": {}},
    {"template": "What quest rewards did we get?", "slots": {}},
    {"template": "What quest-related NPCs did we meet?", "slots": {}},
]

# =============================================================================
# PUZZLE_SOLUTIONS - Puzzles encountered and solved
# =============================================================================

PUZZLE_SOLUTIONS_TEMPLATES = [
    {"template": "What puzzles did we encounter?", "slots": {}},
    {"template": "How did we solve the puzzle?", "slots": {}},
    {"template": "What riddles did we face?", "slots": {}},
    {"template": "What traps did we disarm?", "slots": {}},
    {"template": "How did we get past the obstacle?", "slots": {}},
    {"template": "What was the solution to the puzzle?", "slots": {}},
    {"template": "Did we miss any puzzles?", "slots": {}},
    {"template": "What challenges required thinking?", "slots": {}},
    {"template": "What clues did we find?", "slots": {}},
    {"template": "How did we figure it out?", "slots": {}},
]

# =============================================================================
# LOOT_REWARDS - Treasure and items obtained
# =============================================================================

LOOT_REWARDS_TEMPLATES = [
    {"template": "What loot did we get?", "slots": {}},
    {"template": "What treasure did we find?", "slots": {}},
    {"template": "How much gold did we earn?", "slots": {}},
    {"template": "What rewards were we given?", "slots": {}},
    {"template": "What magic items did we discover?", "slots": {}},
    {"template": "How did we divide the loot?", "slots": {}},
    {"template": "What valuable items did we obtain?", "slots": {}},
    {"template": "What did the {creature} drop?", "slots": {"creature": "creature"}},
    {"template": "What quest rewards did we receive?", "slots": {}},
    {"template": "What's the total value of our haul?", "slots": {}},
]

# =============================================================================
# DEATH_REVIVAL - Character deaths and revivals
# =============================================================================

DEATH_REVIVAL_TEMPLATES = [
    {"template": "Did anyone die in the session?", "slots": {}},
    {"template": "Who went down?", "slots": {}},
    {"template": "How did the death happen?", "slots": {}},
    {"template": "Was anyone revived?", "slots": {}},
    {"template": "What resurrection was used?", "slots": {}},
    {"template": "Who made death saving throws?", "slots": {}},
    {"template": "How close to death did we get?", "slots": {}},
    {"template": "What brought someone back?", "slots": {}},
    {"template": "Any near-death experiences?", "slots": {}},
    {"template": "What were the consequences of dying?", "slots": {}},
]

# =============================================================================
# DIVINE_RELIGIOUS - Deity interactions
# =============================================================================

DIVINE_RELIGIOUS_TEMPLATES = [
    {"template": "Did any gods intervene?", "slots": {}},
    {"template": "What divine events occurred?", "slots": {}},
    {"template": "What religious significance was there?", "slots": {}},
    {"template": "Did we visit any temples?", "slots": {}},
    {"template": "What prayers were answered?", "slots": {}},
    {"template": "What holy symbols or artifacts did we find?", "slots": {}},
    {"template": "What divine guidance did we receive?", "slots": {}},
    {"template": "Did we interact with any clerics or priests?", "slots": {}},
    {"template": "What religious factions were involved?", "slots": {}},
    {"template": "Were there any omens or signs?", "slots": {}},
]

# =============================================================================
# MEMORY_VISION - Memories, visions, dreams
# =============================================================================

MEMORY_VISION_TEMPLATES = [
    {"template": "What visions did we see?", "slots": {}},
    {"template": "What memories were revealed?", "slots": {}},
    {"template": "Did anyone have dreams?", "slots": {}},
    {"template": "What flashbacks occurred?", "slots": {}},
    {"template": "What prophetic visions happened?", "slots": {}},
    {"template": "What did the vision show?", "slots": {}},
    {"template": "What past events were revealed?", "slots": {}},
    {"template": "What did we learn from the vision?", "slots": {}},
    {"template": "Who had the vision?", "slots": {}},
    {"template": "What supernatural experiences occurred?", "slots": {}},
]

# =============================================================================
# RULES_MECHANICS - Rule interpretations during play
# =============================================================================

RULES_MECHANICS_TEMPLATES = [
    {"template": "What rules questions came up?", "slots": {}},
    {"template": "How did we handle that mechanic?", "slots": {}},
    {"template": "What house rules did we use?", "slots": {}},
    {"template": "How did the DM rule on that?", "slots": {}},
    {"template": "What edge cases did we encounter?", "slots": {}},
    {"template": "How did {spell} work in that situation?", "slots": {"spell": "spell"}},
    {"template": "What mechanics were unclear?", "slots": {}},
    {"template": "How did we resolve the rules dispute?", "slots": {}},
    {"template": "What ruling did we go with?", "slots": {}},
    {"template": "Were there any contested rolls?", "slots": {}},
]

# =============================================================================
# HUMOR_MOMENTS - Funny moments
# =============================================================================

HUMOR_MOMENTS_TEMPLATES = [
    {"template": "What funny moments happened?", "slots": {}},
    {"template": "What made everyone laugh?", "slots": {}},
    {"template": "What were the best jokes?", "slots": {}},
    {"template": "Any memorable quotes?", "slots": {}},
    {"template": "What silly things happened?", "slots": {}},
    {"template": "What was the funniest part?", "slots": {}},
    {"template": "What critical fails were entertaining?", "slots": {}},
    {"template": "What unexpected humor occurred?", "slots": {}},
    {"template": "What running jokes continued?", "slots": {}},
    {"template": "What was the most ridiculous thing that happened?", "slots": {}},
]

# =============================================================================
# UNRESOLVED_MYSTERIES - Ongoing mysteries
# =============================================================================

UNRESOLVED_MYSTERIES_TEMPLATES = [
    {"template": "What mysteries remain unsolved?", "slots": {}},
    {"template": "What questions do we still have?", "slots": {}},
    {"template": "What's still unknown?", "slots": {}},
    {"template": "What plot threads are hanging?", "slots": {}},
    {"template": "What didn't make sense?", "slots": {}},
    {"template": "What are we still trying to figure out?", "slots": {}},
    {"template": "What secrets weren't revealed?", "slots": {}},
    {"template": "What was left unexplained?", "slots": {}},
    {"template": "What suspicious things happened?", "slots": {}},
    {"template": "What unanswered questions came up?", "slots": {}},
]

# =============================================================================
# FUTURE_IMPLICATIONS - Setup for future sessions
# =============================================================================

FUTURE_IMPLICATIONS_TEMPLATES = [
    {"template": "What's the cliffhanger?", "slots": {}},
    {"template": "What happens next?", "slots": {}},
    {"template": "What should we prepare for?", "slots": {}},
    {"template": "What threats are looming?", "slots": {}},
    {"template": "What did we set up for next time?", "slots": {}},
    {"template": "What consequences will we face?", "slots": {}},
    {"template": "What's coming in future sessions?", "slots": {}},
    {"template": "What foreshadowing happened?", "slots": {}},
    {"template": "What plans did we make?", "slots": {}},
    {"template": "Where are we heading next?", "slots": {}},
]

# =============================================================================
# CROSS_SESSION - Multi-session patterns
# =============================================================================

CROSS_SESSION_TEMPLATES = [
    {"template": "How does this connect to previous sessions?", "slots": {}},
    {"template": "What recurring themes are there?", "slots": {}},
    {"template": "What callbacks happened?", "slots": {}},
    {"template": "How has the story evolved?", "slots": {}},
    {"template": "What long-term plots are developing?", "slots": {}},
    {"template": "What patterns have emerged?", "slots": {}},
    {"template": "How did past events influence this session?", "slots": {}},
    {"template": "What character arcs are progressing?", "slots": {}},
    {"template": "What story threads connected?", "slots": {}},
    {"template": "How does this fit the bigger picture?", "slots": {}},
]

# =============================================================================
# CONSOLIDATED TEMPLATES
# =============================================================================

SESSION_TEMPLATES = {
    "character_status": CHARACTER_STATUS_TEMPLATES,
    "event_sequence": EVENT_SEQUENCE_TEMPLATES,
    "npc_info": NPC_INFO_TEMPLATES,
    "location_details": LOCATION_DETAILS_TEMPLATES,
    "item_tracking": ITEM_TRACKING_TEMPLATES,
    "combat_recap": COMBAT_RECAP_TEMPLATES,
    "spell_ability_usage": SPELL_ABILITY_USAGE_TEMPLATES,
    "character_decisions": CHARACTER_DECISIONS_TEMPLATES,
    "party_dynamics": PARTY_DYNAMICS_TEMPLATES,
    "quest_tracking": QUEST_TRACKING_TEMPLATES,
    "puzzle_solutions": PUZZLE_SOLUTIONS_TEMPLATES,
    "loot_rewards": LOOT_REWARDS_TEMPLATES,
    "death_revival": DEATH_REVIVAL_TEMPLATES,
    "divine_religious": DIVINE_RELIGIOUS_TEMPLATES,
    "memory_vision": MEMORY_VISION_TEMPLATES,
    "rules_mechanics": RULES_MECHANICS_TEMPLATES,
    "humor_moments": HUMOR_MOMENTS_TEMPLATES,
    "unresolved_mysteries": UNRESOLVED_MYSTERIES_TEMPLATES,
    "future_implications": FUTURE_IMPLICATIONS_TEMPLATES,
    "cross_session": CROSS_SESSION_TEMPLATES,
}

# Intent descriptions
SESSION_INTENT_DESCRIPTIONS = {
    "character_status": "Current state of characters: HP, conditions, location, alive/dead status",
    "event_sequence": "Chronological events: what happened when, timeline of the session",
    "npc_info": "NPC interactions: who we met, relationships, conversations",
    "location_details": "Places visited: descriptions, notable features, dangers",
    "item_tracking": "Items: found, lost, used, traded, who has what",
    "combat_recap": "Combat encounters: fights, tactics, outcomes, damage",
    "spell_ability_usage": "Spells and abilities: what was cast, effects, resource usage",
    "character_decisions": "Important choices: decisions made, reasoning, consequences",
    "party_dynamics": "Group interactions: conflicts, bonding, teamwork",
    "quest_tracking": "Quest progress: completed objectives, new quests, status",
    "puzzle_solutions": "Puzzles: encountered challenges, solutions, clues",
    "loot_rewards": "Treasure: items found, gold earned, quest rewards",
    "death_revival": "Deaths and revivals: who died, how, resurrection",
    "divine_religious": "Divine events: deity interactions, temples, religious significance",
    "memory_vision": "Visions and dreams: prophetic visions, flashbacks, memories",
    "rules_mechanics": "Rules: interpretations, house rules, contested mechanics",
    "humor_moments": "Funny moments: jokes, memorable quotes, silly events",
    "unresolved_mysteries": "Mysteries: unanswered questions, plot threads, secrets",
    "future_implications": "Future setup: cliffhangers, foreshadowing, upcoming threats",
    "cross_session": "Multi-session: recurring themes, callbacks, story evolution",
}

# Slot mappings
SLOT_MAPPINGS = {
    "creature": "creature",
    "location": "location",
    "item": "item",
    "spell": "spell",
    "feature": "feature",
}


def get_all_session_templates():
    """Return all session templates as a flat list with intent labels."""
    all_templates = []
    for intent, templates in SESSION_TEMPLATES.items():
        for template in templates:
            all_templates.append({
                "template": template["template"],
                "slots": template["slots"],
                "tool": "session_notes",
                "intent": intent,
            })
    return all_templates


def get_intent_templates(intent: str):
    """Get all templates for a specific intent."""
    return SESSION_TEMPLATES.get(intent, [])
