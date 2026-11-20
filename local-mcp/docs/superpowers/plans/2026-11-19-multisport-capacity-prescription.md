# Multisport Capacity Prescription Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a locally configured primary sport plus session sport so the MCP produces safe, explainable next-day capability prescriptions for running, cycling, swimming and climbing.

**Architecture:** A focused profile module persists the user-provided sport/goal configuration under the existing local data directory. A sport-prescription module converts shared safety-gate output plus safely classified same-sport history into structured recommendation fields. `TrainingWorkflow` orchestrates the new path; the existing running tool remains a compatibility wrapper with its current response shape.

**Tech Stack:** Python 3, FastMCP/Pydantic, local JSON via existing `atomic_json`, pytest.

**Spec:** `docs/superpowers/specs/2026-11-19-multisport-capacity-prescription-design.md`

## Global Constraints

- Support only `running`, `cycling`, `swimming`, `climbing` as primary sports; allow `other` only as a session sport.
- Profile is local at `%LOCALAPPDATA%/GarminLocalMCP/athlete_profile.json`; never read keys or raw private data outside existing workflow.
- Analyses prescribe for tomorrow and require a morning recheck; safety/critical-missing gates override every sport.
- Cycling, swimming and climbing v1 must never emit `quality_candidate`; climbing never infers finger/tendon/skin readiness.
- Unknown Garmin activity types remain unknown; never perform cross-sport equivalent-load conversion.
- `garmin_assess_tomorrow` keeps its parameters, return fields, filename and running behavior unchanged.
- `garmin_set_athlete_profile` is the sole non-destructive state-writing MCP tool; Garmin data tools remain read-only.

## Review Focus

- Missing/malformed profile must produce an explicit setup requirement, never a guessed primary sport — Task 1 test.
- A running primary sport with cycling session must describe cycling as cross-training, not running-specific work — Task 2 test.
- Red-flag symptoms, stale/incomplete sync, or required swimming safety answers override every requested sport/session intent — Task 3 test.
- Unknown/raw mixed Garmin activity types must not enter same-sport summaries or produce equivalence claims — Task 2 test.
- The legacy tool’s report name and running-specific fields must remain byte-for-byte compatible where existing tests assert them — Task 3 regression test.

---

## File Structure

- Create: `profile.py` — profile validation, atomic persistence and required-profile errors.
- Create: `prescription.py` — sport enums, Garmin activity classification, capability dictionaries and structured conservative prescriptions.
- Modify: `readiness.py` — expose shared safety-gate result independently of running-only aggregation while retaining `assess()` compatibility.
- Modify: `training.py` — orchestrate generic next-day reports and render new sections without changing legacy renderer behavior.
- Modify: `server.py` — add profile/session Pydantic models and MCP tools/annotations.
- Modify: `menu.py`, `README.md` — expose the new workflow and read/write distinction.
- Modify/Create tests: `test_profile.py`, `test_prescription.py`, `test_training.py`, `test_workflow.py`, `test_session_policy.py`.

### Task 1: Local athlete profile contract

**Files:**
- Create: `profile.py`
- Create: `test_profile.py`

**Interfaces:**
- Produces `load_profile(folder: Path) -> dict | None`, `save_profile(folder: Path, primary_sport: str, goal: str, goal_date: str | None = None, experience_note: str | None = None) -> dict`, and `ProfileValidationError(ValueError)`.
- Uses `research.atomic_json` for writes.

- [ ] **Step 1: Write failing profile tests**

```python
def test_save_profile_normalizes_and_round_trips(tmp_path):
    saved = save_profile(tmp_path, "running", "10 km", "2027-01-01", "beginner")
    assert saved["primary_sport"] == "running"
    assert load_profile(tmp_path)["schema_version"] == 1

def test_profile_rejects_unknown_sport_blank_goal_and_bad_date(tmp_path):
    for args in [("other", "goal", None), ("running", " ", None), ("running", "goal", "bad")]:
        with pytest.raises(ProfileValidationError): save_profile(tmp_path, *args)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest test_profile.py -v`  
Expected: FAIL because `profile` does not exist.

- [ ] **Step 3: Implement profile persistence**

Implement the declared functions; canonicalize four primary-sport values, enforce ISO dates and bounded optional notes, write `schema_version: 1` and UTC `profile_effective_at`.

- [ ] **Step 4: Run profile tests to verify pass**

Run: `pytest test_profile.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -am "feat: persist athlete sport profile"`

### Task 2: Sport classification and conservative prescription engine

**Files:**
- Create: `prescription.py`
- Create: `test_prescription.py`

**Interfaces:**
- Consumes shared safety decision, profile, `session_sport`, `session_intent`, and cached activities.
- Produces `classify_activity(activity: dict) -> str` and `build_prescription(profile: dict, session_sport: str, safety: dict, activities: list[dict], session_intent: str | None = None, swimming_safety: dict | None = None) -> dict`.

- [ ] **Step 1: Write failing engine tests**

```python
def test_cross_training_names_primary_capacity_without_claiming_running_work():
    result = build_prescription({"primary_sport": "running", "goal": "10 km"}, "cycling", safe, [])
    assert result["prescription_status"] in {"easy", "base"}
    assert "交叉训练" in result["capacity_summary"]
    assert "跑步专项" not in result["capacity_summary"]

def test_unknown_activity_and_climbing_never_enable_quality_candidate():
    assert classify_activity({"activityType": {"typeKey": "mystery"}}) == "unknown"
    assert build_prescription(climbing, "climbing", safe, [])["prescription_status"] != "quality_candidate"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest test_prescription.py -v`  
Expected: FAIL because `prescription` does not exist.

- [ ] **Step 3: Implement classification and templates**

Define canonical session/intent sets; map only known Garmin type keys; produce sport-specific `session_action`, RPE/dose boundary, capacity focus, downgrade rule and evidence boundary. For `other`, output only generic recovery guidance. For swimming, missing `shoulder_pain` or `swimming_alone` returns no swimming-specific prescription.

- [ ] **Step 4: Run prescription tests to verify pass**

Run: `pytest test_prescription.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -am "feat: add conservative multisport prescriptions"`

### Task 3: Integrate generic next-day assessment while preserving legacy running assessment

**Files:**
- Modify: `readiness.py`
- Modify: `training.py`
- Modify: `test_training.py`, `test_workflow.py`

**Interfaces:**
- Adds `TrainingWorkflow.assess_session(session_sport: str | None, session_intent: str | None, subjective: dict | None, swimming_safety: dict | None, ...) -> dict`.
- Keeps `TrainingWorkflow.tomorrow(...) -> dict` unchanged externally.

- [ ] **Step 1: Write failing integration tests**

```python
def test_session_requires_profile_and_red_flag_overrides_cycling(tmp_path):
    with pytest.raises(ProfileRequiredError): workflow.assess_session("cycling", None)
    save_profile(tmp_path, "cycling", "endurance")
    result = workflow.assess_session("cycling", None, {"chest_pain": True})
    assert result["prescription"]["prescription_status"] == "avoid"

def test_legacy_tomorrow_keeps_running_report_contract(workflow):
    result = workflow.tomorrow(as_of="2026-11-19", sync_first=False, research_refresh=False)
    assert result["goal"]["distance_km"] == 10
    assert Path(result["report_markdown"]).name == "readiness_2026-11-20.md"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest test_training.py test_workflow.py -v`  
Expected: FAIL for missing generic assessment/profile requirement.

- [ ] **Step 3: Implement orchestration and report renderer**

Factor only shared gates needed by the prescription engine. Save generic reports with unique sport/timestamp filenames and render the five approved sections; retain the existing legacy `render_report` path for `tomorrow()`.

- [ ] **Step 4: Run focused integration tests to verify pass**

Run: `pytest test_training.py test_workflow.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -am "feat: add multisport next-day assessment"`

### Task 4: MCP surface, documentation, and full regression

**Files:**
- Modify: `server.py`, `menu.py`, `README.md`
- Modify: `test_session_policy.py`, `test_training.py`

**Interfaces:**
- Adds `garmin_get_athlete_profile`, `garmin_set_athlete_profile`, and `garmin_assess_session`.
- Adds Pydantic literals for supported sports/intents and explicit swimming safety fields.

- [ ] **Step 1: Write failing MCP contract tests**

```python
def test_profile_setter_is_not_read_only_but_garmin_queries_remain_read_only():
    assert set_profile_annotations.readOnlyHint is False
    assert daily_summary_annotations.readOnlyHint is True

def test_session_tool_accepts_only_supported_sports():
    assert "other" in SESSION_SPORTS and "other" not in PRIMARY_SPORTS
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest test_session_policy.py -v`  
Expected: FAIL because tools/models are missing.

- [ ] **Step 3: Implement MCP models, tools, menu and README**

Use a non-read-only annotation only for the local profile setter; do not expose secret/config paths. Document the primary/session distinction, safe swimming checks, limited v1 quality behavior and exact legacy compatibility.

- [ ] **Step 4: Run full verification**

Run: `pytest -q; python -m compileall -q .`  
Expected: all tests PASS and compilation exits 0.

- [ ] **Step 5: Commit**

`git commit -am "feat: expose multisport prescription tools"`

## Self-Review

- Spec coverage: Tasks 1–4 cover profile persistence, sports scope, common gates, report hierarchy, explicit boundaries, compatibility, MCP annotations and documentation.
- Step scan: every task begins RED, implements one declared interface, verifies GREEN, and commits.
- Type consistency: profile returns canonical strings consumed by `build_prescription`; `assess_session` consumes its structured result; MCP Pydantic literals guard public inputs.
- Review focus: each of the five listed risks is assigned to a concrete test task.
- Proportion: tasks define interfaces and assertions without reproducing implementation bodies.
