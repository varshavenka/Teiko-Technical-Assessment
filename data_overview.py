import sqlite3
import csv

# file names
DB_FILE = "cell_counts.db"
OUTPUT_FILE = "data_overview.csv"


def get_cell_counts(conn):
    cursor = conn.cursor()
    # join samples and cell_counts to get sample_id
    cursor.execute("""
        SELECT samples.sample_id, cell_counts.population, cell_counts.count
        FROM cell_counts
        JOIN samples ON cell_counts.sample_id = samples.sample_id
    """)
    return cursor.fetchall()

def build_summary(rows):
    # find total count for each sample
    totals = {}
    for sample, population, count in rows:
        if sample not in totals:
            totals[sample] = 0
        totals[sample] = totals[sample] + count

    # build one row per sample & population pair with percentage
    summary_rows = []
    for sample, population, count in rows:
        total_count = totals[sample]
        percentage = round((count / total_count) * 100, 2)

        summary_rows.append({
            "sample": sample,
            "total_count": total_count,
            "population": population,
            "count": count,
            "percentage": percentage
        })
    return summary_rows

# save results to csv
def save_to_csv(summary_rows):
    file = open(OUTPUT_FILE, "w", newline="")
    fieldnames = ["sample", "total_count", "population", "count", "percentage"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    for row in summary_rows:
        writer.writerow(row)
    file.close()


def main():
    conn = sqlite3.connect(DB_FILE)

    rows = get_cell_counts(conn)
    summary_rows = build_summary(rows)
    save_to_csv(summary_rows)
    conn.close()
    
# print first 5 rows of overview table
    print("Overview table saved to", OUTPUT_FILE)
    print("These are the first 5 rows:")
    for row in summary_rows[:5]:
        print(row)

main()