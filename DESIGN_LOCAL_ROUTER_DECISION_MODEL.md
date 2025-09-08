Here’s a clean, implementation-ready design doc you can hand to an engineer. It bakes in the updated stack (fast local classifier, calibrated abstention, fastpath rules, similarity-based context detection, and objective router evaluation).

---

# Local Router Decision System — v2 Design

**Owner:** AI Platform
**Status:** Draft (ready for implementation)
**Goal:** Reduce LLM routing cost and latency while maintaining response quality via a calibrated, CPU-fast local classifier with safe abstention and robust context detection.

---

## 1) Executive Summary

We introduce a **three-layer router** in front of expensive LLM calls:

1. **Fastpath Rules (0–1 ms):** Regex/keyword heuristics for trivial/stock intents (hello/thanks/AC?/HP?/roll d20).
2. **Local Classifier (10–40 ms on CPU):** Multi-label classifier predicting which retrieval routers to run:
   `labels = [character, rulebook, session_notes, needs_context]`.
   Two options:

   * **Zero-shot NLI (no data)**: `MoritzLaurer/DeBERTa-v3-xsmall-mnli-*` via HF pipeline.
   * **Few-shot SetFit (preferred once we have \~50–200 labels):** `BAAI/bge-small-en-v1.5` embeddings + Logistic Regression (or SetFit trainer), exported to **ONNX (int8)**.
3. **Calibrated Abstention Gate:** Selective classification gate that **only skips** downstream LLM routers when predicted risk ≤ target (e.g., 1%). Tempered softmax + threshold learned on validation.

We also replace the old “context needed?” heuristic with **embedding similarity** to recent Q/A turns, and introduce objective evaluation with **RouterBench-style** metrics plus Frugal prompts for downstream LLMs.

---

## 2) System Diagram

```
User Query + Session Buffer
        │
        ├──▶ [L0 Fastpath Rules] ── yes ──▶ Lightweight LLM or canned reply
        │                                (no routers)
        │
        └──▶ [L1 Local Classifier]
                │          │
                │          └─▶ Calibrated Abstention Gate (risk ≤ τ?)
                │                    │
                │                    ├─ yes (skip) ──▶ Lightweight LLM (no routers)
                │                    └─ no  (route) ──▶ [L2 Router Planner]
                │
                └─ features: multi-label probs p(label), uncertainty u
                                     │
                                     └─▶ [Context Detector]
                                          (embed(q) vs recent Q/As; if similar → add context)
```

Routers run **in parallel** (character / rulebook / session\_notes) using simplified prompts. Final answer composition merges retrieved snippets and tool outputs.

---

## 3) Functional Requirements

* **FR1:** Route each query to zero or more retrieval routers: `character`, `rulebook`, `session_notes`.
* **FR2:** Detect whether conversation context is required for correct routing (`needs_context`).
* **FR3:** Provide a calibrated abstention that trades coverage for safety (skip only when safe).
* **FR4:** Execute fastpath responses without touching the classifier for obvious intents.
* **FR5:** Provide latency and cost reductions with no measurable drop in user-visible quality (as per evaluation).

---

## 4) Non-Functional Requirements

* **Latency:** P50 ≤ 50 ms, P95 ≤ 75 ms for the local layer (L0 + L1 + gate) on commodity CPU.
* **Reliability:** Graceful fallback: local failure yields the old (cloud) router.
* **Portability:** No GPU dependency. ONNX runtime on CPU with int8 quantization.
* **Observability:** Full coverage/accuracy/cost/time metrics with per-label confusion stats.

---

## 5) Models & Inference

### 5.1 Options

**Option A — Zero-shot NLI (MVP)**

* `MoritzLaurer/DeBERTa-v3-xsmall-mnli-fever-anli-ling-binary` (≈ tiny, CPU-friendly).
* Use HuggingFace `pipeline("zero-shot-classification")` with four label strings mapped to our classes.
* Pros: No labeled data. Cons: Lower ceiling than few-shot.

**Option B — SetFit Few-shot (Preferred for v2+)**

* Encoder: `BAAI/bge-small-en-v1.5` (fast, strong embeddings).
* Head: Multi-label LogisticRegression (or SetFitTrainer).
* Export: ONNX (dynamic batch=1) + int8 quantization.
* Pros: Excellent accuracy with 50–200 labeled samples; very fast CPU inference.

> Implementation Note: Start A now; switch to B as soon as we have labeled logs (Phase 2).

### 5.2 Output

For query *q*:

* `p = {character: float, rulebook: float, session_notes: float, needs_context: float}`
* `u`: calibrated uncertainty (per label or global risk score).
* `decision`: multi-label set after thresholding; plus `abstain` boolean.

### 5.3 Thresholding & Calibration

* **Temperature scaling** on validation set to map logits → calibrated probabilities.
* **Selective classification:** choose thresholds per label to achieve target **precision ≥ P\*** under desired **coverage**; compute global **risk** (e.g., max misclass prob) for the abstention gate.
* **Abstain policy:** if estimated risk ≤ τ\_skip (e.g., 1%), we **skip** routers and use a lightweight LLM/canned path. Else we route.

---

## 6) Context Detection (Session Awareness)

* Maintain a rolling buffer of last **N=10** Q/A pairs: `[(q_i, a_i)]`.
* Compute `sim(q, q_i)` using BGE-small embeddings and a dot-product.
* If `max_i sim(q, q_i) ≥ τ_context` (tunable, e.g., 0.75) or if the query contains unresolved pronouns/ellipses (“that”, “it”, “the spell”), set `needs_context = True` (override if classifier disagrees but uncertainty is high).
* If `needs_context=True`, prepend top-K most similar pairs (K=2–3) to the downstream router prompts.

---

## 7) Fastpath Rules (L0)

A tiny ruleset preempts the classifier:

* **Greetings/Closings:** `^(hi|hello|thanks|thank you|bye)$` → canned reply.
* **Common DnD shorthands:**

  * `^what'?s my AC\??$` → character router only (no cloud if local confident).
  * `^roll d(4|6|8|10|12|20)$` → local roller tool.
  * `^hp\??$` or `^how many spell slots.*\?$` → character router only.
* **Rate-limit alarms / empty input / system keepalives** → drop or canned.

Store rules as a YAML and unit-test separately. Keep this <20 patterns.

---

## 8) Router Planner (L2)

Using the classifier’s `decision` + context flag:

* If `character=True` → call **Character Router** with simplified prompt.
* If `rulebook=True` → call **Rulebook Router** with simplified prompt.
* If `session_notes=True` → call **Session Router** with simplified prompt; if `needs_context=True`, augment prompt with top-K similar Q/As.

### 8.1 Simplified Prompts (no `is_needed`)

* **Character:** “Extract user intent and entities related to character stats/inventory/spells. Return JSON with {intent, entities\[], missing\_info\[]}.”
* **Rulebook:** “Resolve the rule/mechanic asked. Return {rule\_citations\[], summary, edge\_cases\[]}.”
* **Session:** “Retrieve relevant past events/NPCs/decisions. Return {highlights\[], references\[]}.”

Downstream LLMs should use **frugal variants** first (shorter prompts, cheaper models), then escalate if answer confidence is low (FrugalGPT cascade).

---

## 9) APIs & Interfaces

### 9.1 Python Interfaces

```python
# core types
@dataclass
class LocalRoutingDecision:
    character: bool
    rulebook: bool
    session_notes: bool
    needs_context: bool
    probs: Dict[str, float]       # calibrated
    risk: float                   # selective classification risk
    abstain: bool                 # safe to skip routers?

class LocalRouter:
    async def predict(self, query: str, session: list[dict] | None) -> LocalRoutingDecision: ...
```

```python
# planner
@dataclass
class RouterPlan:
    run: list[str]                # ["character", "rulebook", "session_notes"]
    with_context: bool
    context_snippets: list[str]

class RouterPlanner:
    def build_plan(self, decision: LocalRoutingDecision, query: str, session: list[QA]) -> RouterPlan: ...
```

```python
# central engine
class CentralEngine:
    async def handle(self, user_query: str, character_name: str, session: list[QA]) -> str:
        # 1) L0 fastpath
        # 2) L1 local classifier + abstention
        # 3) L2 plan + parallel routers
        # 4) compose final response
```

### 9.2 Config (env / yaml)

```yaml
enable_local_routing: true
model:
  mode: "zero_shot"   # "setfit"
  nli_ckpt: "MoritzLaurer/DeBERTa-v3-xsmall-mnli-fever-anli-ling-binary"
  embed_ckpt: "BAAI/bge-small-en-v1.5"
  onnx_path: "models/router_head.onnx"
  quantize_int8: true

thresholds:
  character: 0.55
  rulebook: 0.55
  session_notes: 0.55
  needs_context: 0.40
  abstain_risk_tau: 0.01
  context_sim_tau: 0.75

fastpath_rules_path: "config/fastpath.yaml"
similarity_window: 10
topk_context: 3
```

---

## 10) Training & Calibration (for SetFit path)

1. **Data sourcing:** Log decisions with gold downstream usage (did we end up needing character/rulebook/session?). Manually label 200–500 queries initially (balanced across labels).
2. **Feature extraction:** Encode queries with BGE-small; optionally add light features (length, punctuation, interrogatives).
3. **Head training:** Multi-label LogisticRegression (one-vs-rest).
4. **Calibration:**

   * Split val set; fit temperature scaling (per label or shared).
   * Compute coverage–risk curve; pick thresholds to hit desired risk @ coverage.
5. **Export:** Convert to ONNX; quantize to int8; load via `onnxruntime` CPU EP.

---

## 11) Evaluation & Guardrails

### 11.1 RouterBench-style Evaluation

Define baselines:

* **Always LLM routers** (upper cost, best quality).
* **Old system** (if exists).
* **v2 router** (this design) at different abstention thresholds.

Measure:

* **Quality:** Task-specific metrics (EM/F1 for rule answers, correct tool selection rate), human side-by-sides on a sample.
* **Cost:** Avg tokens/query; router calls per query.
* **Latency:** P50/P95 local layer, end-to-end.
* **Coverage–risk curve:** Accuracy at varying skip rates.

### 11.2 Online Safeguards

* If observed live **router precision** drops > X% or **abstain skip rate** spikes unexpectedly, auto-raise thresholds or disable skip (feature flag).
* Fallback to “always route” on local model exception.

---

## 12) Telemetry & Dashboards

Emit per query:

```json
{
  "qid": "...",
  "fastpath_hit": false,
  "probs": {"character":0.12,"rulebook":0.81,"session_notes":0.07,"needs_context":0.29},
  "risk": 0.018,
  "abstain": false,
  "plan": ["rulebook"],
  "with_context": false,
  "latency_ms": {"fastpath":0,"local":23,"routers":212,"end_to_end":480},
  "cost": {"prompt_tokens":..., "completion_tokens":..., "usd_est": 0.0021},
  "labels_gold": {"rulebook": true, ...},     // offline/after human adjudication
  "result_quality": {"em":1,"f1":1}           // offline evaluation
}
```

Create dashboards for:

* Coverage–risk curve, precision/recall per label.
* Skip rate vs. quality deltas.
* Cost & latency trends (p50/p95), router hit distribution.

---

## 13) Rollout Plan

1. **Week 1 (MVP):**

   * Implement L0 rules + L1 zero-shot NLI + abstention gate (temperature via small hand-labeled val set of \~80 examples).
   * Ship feature-flagged at 10% traffic.
2. **Weeks 2–3:**

   * Collect labeled logs; run offline RouterBench-style eval; tune thresholds.
   * Expand fastpath rules (≤20 patterns).
3. **Week 4:**

   * Train SetFit head on BGE-small; export ONNX; A/B vs. zero-shot.
   * Ramp to 50–100% if quality and cost targets hold.
4. **Ongoing:**

   * Monthly recalibration or threshold tuning.
   * Add new labels if new routers are introduced.

---

## 14) Acceptance Criteria

* **Latency:** Local layer P50 ≤ 40 ms / P95 ≤ 75 ms on CPU-only instance.
* **Skipping Safety:** Calibrated abstention holds **router-error ≤ 1%** on the val set at the chosen skip rate.
* **Cost Reduction:** ≥ 40% fewer unnecessary LLM router calls vs. baseline with **no statistically significant drop** in task quality.
* **Reliability:** Zero user-visible failures due to local model; automatic fallback works.

---

## 15) Reference Implementation Sketches

### 15.1 Local Classifier (Zero-shot NLI)

```python
from transformers import pipeline
from dataclasses import dataclass
from typing import Dict, List

LABELS = {
    "character": "character data needed - stats inventory spells abilities",
    "rulebook": "rulebook information needed - rules mechanics spells descriptions",
    "session_notes": "session history needed - past events NPCs decisions campaign",
    "needs_context": "requires conversation context - depends on previous messages"
}

@dataclass
class LocalRoutingDecision:
    character: bool; rulebook: bool; session_notes: bool; needs_context: bool
    probs: Dict[str, float]; risk: float; abstain: bool

class LocalRouterNLI:
    def __init__(self, model_ckpt: str, thresholds: Dict[str, float], abstain_tau: float):
        self.clf = pipeline("zero-shot-classification", model=model_ckpt, device="cpu")
        self.th = thresholds; self.abstain_tau = abstain_tau
        self.labels = list(LABELS.values())

    def _calibrate(self, scores: Dict[str, float]) -> Dict[str, float]:
        # hook: apply temperature scaling if available; else identity
        return scores

    async def predict(self, query: str, session: List[Dict] | None) -> LocalRoutingDecision:
        res = self.clf(query, self.labels)
        scores = dict(zip(res["labels"], res["scores"]))
        probs = {k: self._calibrate({LABELS[k]: scores.get(LABELS[k], 0)})[LABELS[k]] for k in LABELS}
        decision = {k: probs[k] >= self.th[k] for k in probs}

        # simple global risk: 1 - max(prob)  (replace with calibrated selective risk as we train)
        risk = 1.0 - max(probs.values())
        abstain = (risk <= self.abstain_tau) and not any([decision["character"], decision["rulebook"], decision["session_notes"]])
        return LocalRoutingDecision(**decision, probs=probs, risk=risk, abstain=abstain)
```

### 15.2 Context Detector

```python
# precompute embeddings with BGE-small; use FAISS or in-memory vectors
def needs_context(query_vec, recent_pairs_vecs, tau: float = 0.75) -> tuple[bool, list[int]]:
    sims = [float(query_vec @ v) for v in recent_pairs_vecs]  # dot product
    idx_sorted = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
    return (sims[idx_sorted[0]] >= tau, idx_sorted[:3])
```

### 15.3 Planner

```python
def build_plan(decision: LocalRoutingDecision, with_context: bool, ctx_idxs: list[int]) -> RouterPlan:
    run = []
    if decision.character: run.append("character")
    if decision.rulebook: run.append("rulebook")
    if decision.session_notes: run.append("session_notes")
    return RouterPlan(run=run, with_context=with_context, context_snippets=ctx_idxs)
```

---

## 16) Security & Privacy

* Only store hashed query IDs and minimal telemetry; redact PII in logs.
* Session buffer is ephemeral in memory; long-term logs store **anonymized** samples for training with opt-out.

---

## 17) Risks & Mitigations

* **Mis-skips at launch:** Start with conservative thresholds; low skip rate; expand after evaluation.
* **Domain drift:** Monthly recalibration and a lightweight relabeling sprint.
* **Heuristic overreach (fastpath):** Keep rules minimal; monitor precision; remove noisy rules.
* **Cold-start for SetFit:** Use zero-shot first; transition to SetFit once enough labels accrue.

---

## 18) Open Questions

* Do we need per-tenant calibration (different campaigns / query styles)? Start global; evaluate per-tenant deltas.
* Should we add a “tools” label (dice roller, calculators) now or later? Probably later; reserve label ID.

---

## 19) Deliverables Checklist

* [ ] L0 rules YAML + unit tests
* [ ] L1 local classifier (NLI MVP) + calibration stub
* [ ] Embedding service (BGE-small) + context detector
* [ ] Abstention gate w/ telemetry (coverage–risk metrics)
* [ ] Planner + parallel router calls + simplified prompts
* [ ] ONNX export path (for SetFit phase)
* [ ] RouterBench-style offline eval + dashboards
* [ ] Feature flags & rollback switch

---

This gives your team everything needed to build the new router quickly, measure it rigorously, and evolve from zero-shot to a calibrated, ONNX-fast few-shot model without re-architecting later.
