import csv
import sqlite3
import os

# file names
DB_FILE = "cell_counts.db"
CSV_FILE = "cell-count.csv"

# listed columns in cell-count.csv
POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def create_tables(conn):
    cursor = conn.cursor()

    # table for projects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY
        )
    """)

    # table for subjects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id TEXT PRIMARY KEY,
            project_id TEXT,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT
        )
    """)

    # table for samples
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            sample_id TEXT PRIMARY KEY,
            subject_id TEXT,
            sample_type TEXT,
            time_from_treatment_start INTEGER
        )
    """)

    # table for cell counts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cell_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT,
            population TEXT,
            count INTEGER
        )
    """)

    conn.commit()


def load_data(conn):
    cursor = conn.cursor()

    # open and read csv file
    file = open(CSV_FILE, "r")
    reader = csv.DictReader(file)

    # track which projects/subjects/samples have been added
    projects_added = []
    subjects_added = []
    samples_added = []

    for row in reader:
        project = row["project"]
        subject = row["subject"]
        sample = row["sample"]

        # turn blanks into None to have NULLs in database
        response = row["response"] if row["response"] != "" else None

        # add the project, if not already done
        if project not in projects_added:
            cursor.execute("INSERT INTO projects (project_id) VALUES (?)", (project,))
            projects_added.append(project)

        # add the subject, if not already done
        if subject not in subjects_added:
            cursor.execute("""
                INSERT INTO subjects (subject_id, project_id, condition, age, sex, treatment, response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (subject, project, row["condition"], row["age"], row["sex"], row["treatment"], response))
            subjects_added.append(subject)

        # add the sample if not already done
        if sample not in samples_added:
            cursor.execute("""
                INSERT INTO samples (sample_id, subject_id, sample_type, time_from_treatment_start)
                VALUES (?, ?, ?, ?)
            """, (sample, subject, row["sample_type"], row["time_from_treatment_start"]))
            samples_added.append(sample)

        # add a row in cell_counts for each of the 5 populations
        for population in POPULATIONS:
            count = row[population]
            cursor.execute("""
                INSERT INTO cell_counts (sample_id, population, count)
                VALUES (?, ?, ?)
            """, (sample, population, count))

    file.close()
    conn.commit()


def main():
    # delete old database if it exists 
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)

    create_tables(conn)
    load_data(conn)

    conn.close()
    print("Done! Data loaded into", DB_FILE)


main()