# Loblaw Bio Immune Cell Population Analysis

## Project Status
Parts 1–4 and Dashboard are complete.

### Running the Full Pipeline
Run each step in order:
```bash
python3 load_data.py
python3 data_overview.py
python3 stat_analysis.py
python3 subset_analysis.py
```
This creates `cell_counts.db` and generates all output files
(`data_overview.csv`, `stats_analysis.csv`, `boxplots/`, `subset_analysis.csv`)

### Part 1
1. Make sure `cell-count.csv` is in the repo root
2. Run:
```bash
   python3 load_data.py
```
3. This creates `cell_counts.db` in the repo root

### Part 2
1. Run:
```bash
python3 data_overview.py
```
This reads from `cell_counts.db` and produces `data_overview.csv`, a
long-format table where each row is one population from one sample:

| Column | Description |
|---|---|
| `sample` | sample ID |
| `total_count` | total cell count across all 5 populations for that sample |
| `population` | immune cell population (e.g. `b_cell`) |
| `count` | raw cell count for that population in that sample |
| `percentage` | `count` as a percentage of `total_count` |

### Part 3
1. Run:
```bash
python3 stat_analysis.py
```
This compares relative frequencies of each immune cell population between
miraclib responders and non-responders, restricted to:
- melanoma patients
- treated with miraclib
- PBMC samples only

#### Method
For each of the 5 populations, a Welch's t-test was used to compare the
mean percentage between responders and non-responders. A Welch's t-test was
chosen over a standard t-test because it doesn't assume both groups have
equal variance. With about 985 samples per group, the sample size is large enough
that the t-test is reasonably robust even if the underlying data isn't
perfectly normally distributed.

#### Outputs
- `boxplots/` — one boxplot per population (`b_cell_boxplot.png`,
  `cd8_t_cell_boxplot.png`, etc.), visually comparing responders vs
  non-responders.
- `stats_analysis.csv` — for each population: sample sizes, mean
  percentage for each group, p-value, and whether the result is
  significant at p < 0.05.

#### Finding
`cd4_t_cell` was the only population with a statistically significant
difference, meaning responders had a higher mean relative frequency
(about 30.5%) than non-responders (about 29.9%). The other 4 populations
(`b_cell`, `cd8_t_cell`, `nk_cell`, `monocyte`) did not show a
significant difference.

### Part 4: Baseline Subset Analysis
1. Run:
```bash
python3 subset_analysis.py
```
This filters the data to melanoma patients, treated with miraclib, with
a PBMC sample at baseline (`time_from_treatment_start = 0`), and reports:

- How many samples come from each project
- How many subjects are responders vs non-responders
- How many subjects are male vs female
- The average B cell count for melanoma male responders at baseline

### Results

| Metric | Value |
|---|---|
| Samples in prj1 | 384 |
| Samples in prj3 | 272 |
| Responders | 331 |
| Non-responders | 325 |
| Male subjects | 344 |
| Female subjects | 312 |
| Avg B cells (melanoma, male, responder, t=0) | 10401.28 |

Full output saved to `subset_analysis.csv`.
## Makefile
This project includes a `Makefile` with three targets used for grading via GitHub Codespaces:
```bash
make setup      # installs all dependencies from requirements.txt
make pipeline   # loads data to display visuals
make dashboard  # starts the dashboard 
```
To run the entire project from scratch:
```bash
make setup
make pipeline
make dashboard
```
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
Each part is its own script rather than one combined file, so each stays
focused on a single question and can be rerun independently. All four scripts query the same database rather
than rereading the CSV each time.

Run in order:
```bash
python3 load_data.py
python3 data_overview.py
python3 stat_analysis.py
python3 subset_analysis.py
```

## Dashboard
1. Run:
```bash
python3 dashboard.py
```
Then open http://127.0.0.1:8050/ in your browser to view

The dashboard displays results from Parts 1–4 and runs locally by default.

Since grading is done via GitHub Codespaces, running `make dashboard` will start the server there, and Codespaces will automatically provide a link to view it.
