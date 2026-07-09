import sqlite3
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table
import os

# file names
DB_FILE = "cell_counts.db"

app = Dash(__name__)
app.title = "Loblaw Bio: Immune Cell Analysis"

# ---------- simple style settings, reused across the page ----------
PAGE_STYLE = {
    "maxWidth": "1000px",
    "margin": "0 auto",           # centers the page content
    "padding": "30px 20px",
    "fontFamily": "Arial, sans-serif",
    "color": "#2c2c2c",
}

SECTION_STYLE = {
    "backgroundColor": "#ffffff",
    "border": "1px solid #e0e0e0",
    "borderRadius": "8px",
    "padding": "20px",
    "marginBottom": "25px",
}

HEADER_STYLE = {
    "borderBottom": "2px solid #4a7c59",
    "paddingBottom": "8px",
    "color": "#2c2c2c",
}

TABLE_STYLE = {
    "style_header": {"backgroundColor": "#4a7c59", "color": "white", "fontWeight": "bold"},
    "style_cell": {"padding": "8px", "fontFamily": "Arial, sans-serif", "fontSize": "14px"},
    "style_table": {"overflowX": "auto"},
}


# load in tables
def load_summary_table():
    if os.path.exists("data_overview.csv"):
        return pd.read_csv("data_overview.csv")
    return None


def load_stats_table():
    if os.path.exists("stats_analysis.csv"):
        return pd.read_csv("stats_analysis.csv")
    return None


def load_subset_table():
    if os.path.exists("subset_analysis.csv"):
        return pd.read_csv("subset_analysis.csv")
    return None


# fetch boxplot data
def get_boxplot_data():
    conn = sqlite3.connect(DB_FILE)
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
    df = pd.read_sql_query(query, conn)
    conn.close()

    totals = df.groupby("sample_id")["count"].sum()
    df["total_count"] = df["sample_id"].map(totals)
    df["percentage"] = (df["count"] / df["total_count"]) * 100
    return df


# load dashboard sections
summary_df = load_summary_table()
stats_df = load_stats_table()
subset_df = load_subset_table()
boxplot_df = get_boxplot_data()

# display part 2 table
if summary_df is not None:
    part2_table = dash_table.DataTable(
        data=summary_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in summary_df.columns],
        filter_action="native",   # lets the user type filters directly in the table
        sort_action="native",     # lets the user click column headers to sort
        page_size=10,
        **TABLE_STYLE,
    )
else:
    part2_table = html.P("data_overview.csv not found. Run data_overview.py first.")

# display part 3 table and plots
if stats_df is not None:
    part3_table = dash_table.DataTable(
        data=stats_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in stats_df.columns],
        sort_action="native",
        page_size=10,
        **TABLE_STYLE,
    )

    boxplot_figure = px.box(
        boxplot_df,
        x="response",
        y="percentage",
        facet_col="population",
        facet_col_wrap=3,
        category_orders={"response": ["yes", "no"]},
        labels={"response": "Response", "percentage": "% of total cells"},
        color="response",
        color_discrete_map={"yes": "#4a7c59", "no": "#c96f52"},
    )
    boxplot_figure.update_layout(
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(t=40, l=40, r=20, b=40),
    )
else:
    part3_table = html.P("stats_analysis.csv not found. Run stat_analysis.py first.")
    boxplot_figure = None

# display part 4 table
if subset_df is not None:
    part4_table = dash_table.DataTable(
        data=subset_df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in subset_df.columns],
        page_size=10,
        **TABLE_STYLE,
    )
else:
    part4_table = html.P("subset_analysis.csv not found. Run subset_analysis.py first.")


def section(title, *content):
    """Small helper so every section looks the same without repeating style code."""
    return html.Div([html.H2(title, style=HEADER_STYLE), *content], style=SECTION_STYLE)


# adjust page layout
app.layout = html.Div([
    html.Div([
        html.H1("Immune Cell Population Analysis", style={"marginBottom": "0px"}),
        html.P("Miraclib Trial — Loblaw Bio", style={"color": "#666", "marginTop": "4px"}),
    ], style={"marginBottom": "20px"}),

    section("1. Cell Population Frequencies by Sample", part2_table),

    section(
        "2. Responders vs Non-Responders",
        html.P("Melanoma patients, treated with miraclib, PBMC samples only.",
               style={"color": "#666", "marginTop": "-10px"}),
        html.H3("Statistical test results (t-test)", style={"fontSize": "16px"}),
        part3_table,
        html.H3("Boxplots by population", style={"fontSize": "16px", "marginTop": "20px"}),
        dcc.Graph(figure=boxplot_figure) if boxplot_figure else html.P("No boxplot data available."),
    ),

    section("3. Baseline Subset (time = 0)", part4_table),

    html.P(
        "Data source: cell_counts.db, built from cell-count.csv by load_data.py",
        style={"color": "#999", "fontSize": "13px", "textAlign": "center"},
    ),
], style=PAGE_STYLE)


if __name__ == "__main__":
    app.run(debug=True)