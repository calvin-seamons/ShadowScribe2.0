# Task List for Local Router Decision System Implementation

**Understanding**: The current system has a `CentralEngine` that makes 3 parallel LLM calls to decide which routers to run (character/rulebook/session_notes). We need to add a local router decision layer before these expensive LLM calls.

## Phase 1: Foundation & Core Types (5 tasks, ~15 minutes total)

### Task 1: Create Local Router Core Types (3-5 min)
- **File**: __init__.py 
- **Action**: Create the core dataclasses (`LocalRoutingDecision`, `RouterPlan`) from the design
- **Success criteria**: Types compile and match the interface in section 9.1 of design

### Task 2: Create Fastpath Rules Configuration (3-5 min)
- **File**: `config/fastpath.yaml`
- **Action**: Create YAML file with the regex patterns from section 7 (greetings, AC/HP queries, dice rolls)
- **Success criteria**: YAML loads correctly with ~15 simple patterns

### Task 3: Implement Fastpath Rules Engine (4-5 min)
- **File**: `src/rag/local_router/fastpath_rules.py`
- **Action**: Create `FastpathRulesEngine` class that loads YAML and matches patterns
- **Success criteria**: Can match "hi", "what's my AC?", "roll d20" correctly

### Task 4: Create Local Router Config Extension (3-4 min)  
- **File**: Update config.py
- **Action**: Add local router config fields (enable flag, thresholds, model paths) to `RAGConfig`
- **Success criteria**: Config loads with new fields, backwards compatible

### Task 5: Create Context Detector Stub (3-5 min)
- **File**: `src/rag/local_router/context_detector.py`
- **Action**: Create `ContextDetector` class with embedding similarity method (stub implementation using dot product)
- **Success criteria**: Class structure ready for BGE-small embeddings

## Phase 2: Local Classifier Implementation (4 tasks, ~16 minutes total)

### Task 6: Install Required Dependencies (3-4 min)
- **File**: requirements.txt
- **Action**: Add `transformers`, `torch`, `sentence-transformers` for NLI pipeline
- **Success criteria**: Dependencies install without conflicts

### Task 7: Implement Zero-Shot NLI Classifier (5-6 min)
- **File**: `src/rag/local_router/nli_classifier.py`
- **Action**: Create `LocalRouterNLI` class using HuggingFace zero-shot pipeline
- **Success criteria**: Can predict multi-label probabilities for 4 categories

### Task 8: Implement Calibrated Abstention Gate (4-5 min)
- **File**: `src/rag/local_router/abstention_gate.py`
- **Action**: Create `AbstentionGate` class with risk calculation and thresholding
- **Success criteria**: Can decide to skip routing based on confidence

### Task 9: Create Router Planner (3-4 min)
- **File**: `src/rag/local_router/router_planner.py`  
- **Action**: Implement `RouterPlanner.build_plan()` method from design section 8.1
- **Success criteria**: Converts `LocalRoutingDecision` to execution plan

## Phase 3: Integration Layer (3 tasks, ~12 minutes total)

### Task 10: Create Main LocalRouter Class (4-5 min)
- **File**: `src/rag/local_router/local_router.py`
- **Action**: Combine all components into main `LocalRouter` class with `predict()` method
- **Success criteria**: Integrates fastpath, classifier, abstention, and context detection

### Task 11: Add Local Router to CentralEngine (4-5 min)
- **File**: Update central_engine.py
- **Action**: Add `LocalRouter` as optional component in `__init__` and `process_query` method
- **Success criteria**: CentralEngine can use local router with feature flag

### Task 12: Create Basic Integration Test (3-4 min)
- **File**: `test_local_router_integration.py`
- **Action**: Test fastpath hits, classifier predictions, and abstention decisions
- **Success criteria**: Can process sample queries end-to-end

## Phase 4: Telemetry & Validation (3 tasks, ~12 minutes total)  

### Task 13: Add Telemetry Structure (4-5 min)
- **File**: `src/rag/local_router/telemetry.py`
- **Action**: Create telemetry data classes and logging from design section 12
- **Success criteria**: Structured logging for latency, decisions, and costs

### Task 14: Create Demo Integration Script (4-5 min)
- **File**: `demo_local_router.py`
- **Action**: Extend existing demo to show local router decisions vs LLM routing
- **Success criteria**: Side-by-side comparison of routing decisions

### Task 15: Add Feature Flag Integration (3-4 min)
- **File**: Update central_engine.py
- **Action**: Add config-driven feature flag to enable/disable local routing
- **Success criteria**: Can toggle between old and new routing seamlessly

---

## Implementation Guidelines:

**Prerequisites Check**: 
- All tasks assume the current `CentralEngine` system is working
- BGE embeddings support is available (appears to be in existing codebase)
- HuggingFace transformers can be added as dependency

**Order Dependencies**:
- Tasks 1-5 can be done in parallel  
- Tasks 6-9 depend on Task 1 (core types)
- Tasks 10-12 depend on Tasks 6-9 (classifier components)
- Tasks 13-15 depend on Task 10-12 (integrated system)

**Testing Strategy**: 
Each task should be immediately testable with simple cases before moving to the next task.

Would you like me to start implementing these tasks? I recommend beginning with Task 1 (Core Types) since it's the foundation for everything else.