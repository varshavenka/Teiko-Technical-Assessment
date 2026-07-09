import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
import os

# file names
DB_FILE = "cell_counts.db"
STATS_OUTPUT_FILE = "stats_analysis.csv"
BOXPLOT_FOLDER = "boxplots"

# immune cell populations 
POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

# pull filtered data from database and return a dataframe
def get_filtered_data(conn):
    query = """
        SELECT samples.sample_id, subjects.response, cell_counts.population, cell_counts.count
        FROM samples
        JOIN subjects ON samples.subject_id = subjects.subject_id
        JOIN cell_counts ON cell_counts.sample_id = samples.sample_id
        WHERE subjects.condition = 'melanoma'
        AND subjects.treatment = 'miraclib'
        AND samples.sample_type = 'PBMC'
        AND subjects.response IN ('yes', 'no')
    """
    return pd.read_sql_query(query, conn)

#add count percentage column to df
def add_percentage_column(df):
    totals = df.groupby("sample_id")["count"].sum()
    df["total_count"] = df["sample_id"].map(totals)
    df["percentage"] = (df["count"] / df["total_count"]) * 100
    return df

# created a folder for boxplot visuals
def make_boxplots(df):
    if not os.path.exists(BOXPLOT_FOLDER):
        os.makedirs(BOXPLOT_FOLDER)

    # make one boxplot per population, responders vs non-responders
    for population in POPULATIONS:
        subset = df[df["population"] == population]

        plt.figure(figsize=(5, 4))
        sns.boxplot(data=subset, x="response", y="percentage", order=["yes", "no"])
        plt.xticks([0, 1], ["Responder", "Non-responder"])
        plt.title(population + " relative frequency")
        plt.ylabel("% of total cells")
        plt.xlabel("")

        # save each plot as a PNG file
        file_path = os.path.join(BOXPLOT_FOLDER, population + "_boxplot.png")
        plt.savefig(file_path)
        plt.close() 

# run a separate statistical test for each population
def run_stats(df):
    results = []
    for population in POPULATIONS:
        subset = df[df["population"] == population]

        responders = subset[subset["response"] == "yes"]["percentage"]
        non_responders = subset[subset["response"] == "no"]["percentage"]

        stat, p_value = ttest_ind(responders, non_responders, equal_var=False)

        results.append({
            "population": population,
            "n_responders": len(responders),
            "n_non_responders": len(non_responders),
            "responder_mean_pct": round(responders.mean(), 2),
            "non_responder_mean_pct": round(non_responders.mean(), 2),
            "p_value": round(p_value, 4),
            "significant": p_value < 0.05
        })
    return pd.DataFrame(results)


def main():
    # connect to database and pull filtered rows
    conn = sqlite3.connect(DB_FILE)
    df = get_filtered_data(conn)
    conn.close()

    # calculate percentage for each row
    df = add_percentage_column(df)

    # make one boxplot per population
    make_boxplots(df)

    # run the t-test for each population and save results
    results_df = run_stats(df)
    results_df.to_csv(STATS_OUTPUT_FILE, index=False)

    # print a summary of results
    print("Boxplots saved in", BOXPLOT_FOLDER)
    print("Stats results saved to", STATS_OUTPUT_FILE)
    print(results_df)


main()