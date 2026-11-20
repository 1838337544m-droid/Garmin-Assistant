# Recovery Prompt Explanations — Design

## Intent

Make each generated next-day running report explain why it reached a training recommendation, what information remains uncertain, what the report cannot establish, and what the user should do next. Add evidence-backed wording about tissue-specific loading and recovery techniques without changing any training decision threshold.

## Goals

- Render a dedicated explanation-and-boundaries section in every report.
- Distinguish global recovery signals from local tissue/symptom concerns.
- State that recovery techniques do not prove readiness for quality training.
- Add the two newly reviewed sources to the existing reviewed-source registry.
- Preserve the rule that new research and candidates never modify implemented heuristics automatically.

## Non-goals

- No changes to `readiness.assess` decisions, thresholds, Garmin sync, user data access, or external integrations.
- No medical diagnosis, return-to-sport clearance, or fixed individual recovery duration.
- No automatic adoption of newly retrieved PubMed candidates as rules.

## Approach

Add a small pure formatter in `training.py` that derives explanation copy from the already-produced result fields (`flags`, `missing`, and `morning_recheck`). Render the formatter's output immediately after the existing decision clues. Extend the reviewed registry in `research.py` with the selected tissue-load review and endurance-recovery umbrella review; preserve them as explanatory evidence only.

## Constraints

- All report copy remains Chinese and explicitly provisional.
- Missing data must remain visible rather than becoming a normal/healthy inference.
- Source additions must have a stable PubMed link, year, evidence type, and limited application statement.
- Tests use synthetic report data only; no API key, health data, or network request.
