# R&D Notes System

This folder is the operational memory of the project.

## Why this structure works

- `Fast capture`: daily notes can be written in minutes.
- `Easy retrieval`: decisions and experiments are separated from raw notes.
- `Publication-ready`: communication assets can be generated from logs.
- `Low overhead`: one place for planning, evidence, and messaging.

## Files and roles

- `00_INDEX.md` - map and workflow (this file)
- `01_roadmap.md` - strategic sequence and milestones
- `02_decisions_log.md` - architectural/product decisions and rationale
- `03_experiment_log.md` - experiment design, results, validation notes
- `04_media_strategy.md` - communication plan and content pipeline
- `use_cases/UC-OFFGRID-H2-FORECAST-CONTROL.md` - industrial-style use case definition
- `04-05-2026.md` - existing daily note (now normalized)
- `templates/daily_note_template.md` - template for day-by-day progress
- `templates/experiment_template.md` - template for reproducible experiments

## Weekly operating routine (recommended)

1. Start day with `templates/daily_note_template.md`.
2. For any meaningful test, add one entry in `03_experiment_log.md`.
3. For design choices, add one record in `02_decisions_log.md`.
4. On Friday, update `01_roadmap.md` and pick next week's top 1-3 priorities.
5. Convert one log entry into a public post draft using `04_media_strategy.md`.

## Quality rules

- Keep entries short but specific.
- Prefer evidence over opinions.
- Always write assumptions explicitly.
- If a result is uncertain, mark it clearly (`confidence: low/medium/high`).
