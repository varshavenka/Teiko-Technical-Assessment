import sqlite3
import csv

# file names
DB_FILE = "cell_counts.db"
OUTPUT_FILE = "subset_analysis.csv"

# get one row per subject for relevant patients
def get_baseline_subjects(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT subjects.subject_id, subjects.project_id,
                        subjects.response, subjects.sex
        FROM samples
        JOIN subjects ON samples.subject_id = subjects.subject_id
        WHERE subjects.condition = 'melanoma'
        AND subjects.treatment = 'miraclib'
        AND samples.sample_type = 'PBMC'
        AND samples.time_from_treatment_start = 0
    """)
    return cursor.fetchall()

 # get one row per sample 
def get_baseline_samples(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT samples.sample_id, subjects.project_id
        FROM samples
        JOIN subjects ON samples.subject_id = subjects.subject_id
        WHERE subjects.condition = 'melanoma'
        AND subjects.treatment = 'miraclib'
        AND samples.sample_type = 'PBMC'
        AND samples.time_from_treatment_start = 0
    """)
    return cursor.fetchall()

# average b_cell count for melanoma males who are responders at time = 0
def get_avg_b_cells_male_responders(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(cell_counts.count)
        FROM cell_counts
        JOIN samples ON cell_counts.sample_id = samples.sample_id
        JOIN subjects ON samples.subject_id = subjects.subject_id
        WHERE subjects.condition = 'melanoma'
        AND subjects.treatment = 'miraclib'
        AND samples.sample_type = 'PBMC'
        AND samples.time_from_treatment_start = 0
        AND subjects.sex = 'M'
        AND subjects.response = 'yes'
        AND cell_counts.population = 'b_cell'
    """)
    result = cursor.fetchone()[0]
    return round(result, 2)

# get counts by project, response, and sex
def count_by_project(sample_rows):
    counts = {}
    for sample_id, project_id in sample_rows:
        if project_id not in counts:
            counts[project_id] = 0
        counts[project_id] = counts[project_id] + 1
    return counts


def count_by_response(subject_rows):
    counts = {"yes": 0, "no": 0}
    for subject_id, project_id, response, sex in subject_rows:
        counts[response] = counts[response] + 1
    return counts


def count_by_sex(subject_rows):
    counts = {"M": 0, "F": 0}
    for subject_id, project_id, response, sex in subject_rows:
        counts[sex] = counts[sex] + 1
    return counts


def main():
    conn = sqlite3.connect(DB_FILE)

    subject_rows = get_baseline_subjects(conn)
    sample_rows = get_baseline_samples(conn)
    avg_b_cells = get_avg_b_cells_male_responders(conn)

    conn.close()

    project_counts = count_by_project(sample_rows)
    response_counts = count_by_response(subject_rows)
    sex_counts = count_by_sex(subject_rows)

    # create a results csv file
    file = open(OUTPUT_FILE, "w", newline="")
    writer = csv.writer(file)
    writer.writerow(["metric", "value"])

    for project_id, count in project_counts.items():
        writer.writerow(["samples_in_" + project_id, count])

    writer.writerow(["responders", response_counts["yes"]])
    writer.writerow(["non_responders", response_counts["no"]])
    writer.writerow(["male_subjects", sex_counts["M"]])
    writer.writerow(["female_subjects", sex_counts["F"]])
    writer.writerow(["avg_b_cells_melanoma_male_responders_t0", avg_b_cells])

    file.close()

    # print results
    print("Results saved to", OUTPUT_FILE)
    print("Samples per project:", project_counts)
    print("Responders:", response_counts["yes"], "| Non-responders:", response_counts["no"])
    print("Males:", sex_counts["M"], "| Females:", sex_counts["F"])
    print("Average B cells (melanoma, male, responder, time=0):", avg_b_cells)


main()