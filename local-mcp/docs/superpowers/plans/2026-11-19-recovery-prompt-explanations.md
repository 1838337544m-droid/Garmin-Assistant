# Recovery Prompt Explanations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add evidence-bounded explanation sections to every next-day training report without changing training decisions.

**Architecture:** A pure helper in `training.py` maps the existing assessment result into four explanation fields and `render_report` formats them. `research.py` remains the sole reviewed-source registry and gains two fixed, appraised explanatory sources; PubMed discoveries remain candidates.

**Tech Stack:** Python 3.13, unittest/pytest, Markdown reports.

**Spec:** `docs/superpowers/specs/2026-11-19-recovery-prompt-explanations-design.md`

## Global Constraints

- Do not change `readiness.assess` decisions, thresholds, sync behavior, or data access.
- No network calls or personal data in tests.
- Reports must state uncertainty, non-diagnostic status, and a next action.
- Newly discovered literature remains `not_appraised` and cannot alter rules automatically.

## Review Focus

- No flags: explanation must still say that absence of a flag is not medical clearance.
- Missing subjective feedback: report must display it as unknown and request a recheck.
- Local pain: no text may let normal wearable metrics override local symptoms.
- Recovery tools: no text may promise readiness or performance improvement.
- Existing report sections: source lists and candidate status remain unchanged.

---

### Task 1: Report explanation helper

**Files:**
- Modify: `training.py`
- Modify: `test_training.py`

**Interfaces:**
- Produces: `build_prompt_explanation(result: dict) -> dict[str, str | list[str]]`
- Consumes: assessment `flags`, `missing`, and `morning_recheck` fields.

- [ ] **Step 1: Write failing tests**

```python
def test_rendered_report_explains_basis_uncertainty_boundary_and_recheck():
    report = render_report(sample_result_with_missing_subjective_feedback())
    assert '## 提示解释与边界' in report
    assert '本次依据' in report
    assert '未知或不确定' in report
    assert '不等于医疗放行' in report
    assert '下一步' in report
```

- [ ] **Step 2: Run the targeted test and verify it fails because the section is absent**

Run: `python -m pytest test_training.py::ReportExplanationTests::test_rendered_report_explains_basis_uncertainty_boundary_and_recheck -q`

- [ ] **Step 3: Implement `build_prompt_explanation` and render its four fields**

Use existing result fields only. Explicitly mention local symptoms separately from global wearable signals and state that recovery techniques do not establish readiness.

- [ ] **Step 4: Run the targeted test and verify it passes**

- [ ] **Step 5: Commit**

### Task 2: Reviewed explanatory sources

**Files:**
- Modify: `research.py`
- Modify: `test_research.py`

**Interfaces:**
- Produces: two reviewed source records, each with `id`, `year`, `title`, `url`, `type`, and `application`.

- [ ] **Step 1: Write failing tests**

```python
def test_reviewed_sources_include_tissue_load_and_recovery_boundaries():
    ids = {source['id'] for source in research.REVIEWED}
    assert {'tissue_load2025', 'recovery_umbrella2024'} <= ids
```

- [ ] **Step 2: Run the targeted test and verify it fails because source IDs are absent**

- [ ] **Step 3: Add the two appraised explanatory records to `REVIEWED`**

Use the cited PubMed records and state that they inform wording, not automatic decision rules.

- [ ] **Step 4: Run the targeted test and verify it passes**

- [ ] **Step 5: Commit**

### Task 3: Full regression verification

**Files:**
- Verify only: `test_*.py`

- [ ] **Step 1: Run the full suite**

Run: `python -m pytest -q`

Expected: all tests pass with no network access.

- [ ] **Step 2: Compile all Python files**

Run: `python -m compileall -q .`

- [ ] **Step 3: Review the report fixture output for the four required explanation elements**

- [ ] **Step 4: Commit final changes**
