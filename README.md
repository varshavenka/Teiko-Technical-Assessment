# Loblaw Bio Immune Cell Population Analysis

## Project Status
Part 1: Data Management complete
Parts 2–4 and dashboard in progress

## How to Run Part 1
1. Make sure `cell-count.csv` is in the repo root
2. Run:
```bash
   python load_data.py
```
3. This creates `cell_counts.db` in the repo root


## Database Schema
Four tables:
- **`projects`** — one row per project (`project_id`).
- **`subjects`** — one row per patient. Stores `condition`, `age`, `sex`,
  `treatment`, and `response`. Linked to `projects` via `project_id`
- **`samples`** — one row per sample draw. Stores `sample_type` and
  `time_from_treatment_start`. Linked to `subjects` via `subject_id`
- **`cell_counts`** — one row per (sample, population) pair, storing the
  raw `count`. Linked to `samples` via `sample_id`

### Rationale
- Subject-level attributes (age, sex, response) are stored once per
  subject rather than repeated on every cell-count row to avoid
  duplication and keeps updates consistent
- `cell_counts` is stored in long format (one row per population)
  rather than wide format (one column per population). Adding a 6th
  population later means inserting new rows, not altering the table
  structure
- Foreign keys (`project_id`, `subject_id`, `sample_id`) preserve the
  natural hierarchy: project, subject, sample, cell count

### Scaling to hundreds of projects / thousands of samples
- Indexes on `subject_id` and `sample_id` to keep joins fast as row counts
  grow
- The long `cell_counts` format supports new populations or panels
  without schema migrations needed
- For very large sample volumes, a pre-aggregated summary table (e.g.
  percentages per sample, computed once) could sit alongside
  `cell_counts` to keep downstream queries/dashboards fast

## Code Structure

## Link to Dashboard
