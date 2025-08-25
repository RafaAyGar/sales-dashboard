import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# ----------------------------
# Database connection
# ----------------------------
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
DB = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")

# ----------------------------
# Streamlit config
# ----------------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard")


# ----------------------------
# Load data
# ----------------------------
@st.cache_data(
    ttl=60
)  #! Cache data for 60 seconds, if you reload during this time, the dashboard won't fetch new data
def load_data():
    # Last 7 days sales
    query_last_week_sales = f"""
    SELECT * FROM sales_db
    ORDER BY "date" DESC
    LIMIT 10
    """
    df_last_week = pd.read_sql(query_last_week_sales, engine).reset_index()

    # All sales for totals
    query_total_amounts = f"""
        SELECT "date", "total_amount", "product_category"
        FROM sales_db
        ORDER BY "date"
    """
    df_total = pd.read_sql(query_total_amounts, engine)

    # Top 5 sales
    df_top_5 = df_total.nlargest(5, "total_amount")

    # Forecasts
    forecasts = pd.read_sql(
        f"""
        SELECT forecast_date AS date, predicted_total_amount AS total_amount, last_training_date
        FROM forecasts
        WHERE last_training_date = (SELECT MAX(last_training_date) FROM forecasts)
        ORDER BY forecast_date DESC
        """,
        engine,
    )

    return df_last_week, df_total, df_top_5, forecasts


# ----------------------------
# Draw dashboard
# ----------------------------
def draw_dashboard():
    df_last_week, df_total, df_top_5, forecasts = load_data()

    # Display Top 5 sales
    st.subheader("Top 5 Sales")
    st.dataframe(df_top_5)

    # Last month sales with forecasts
    last_training_date = forecasts["last_training_date"].iloc[0]
    last_month = df_total[
        (df_total["date"] <= last_training_date)
        & (df_total["date"] >= last_training_date - pd.Timedelta(days=30))
    ]
    last_month = last_month.drop(columns=["product_category"]).groupby("date").sum().reset_index()
    assert forecasts["date"].min() == last_month["date"].max() + pd.Timedelta(
        days=1
    ), "Forecasts do not start the day after the last historical date"
    # Append the exact last row of last_month as the first row of forecasts
    forecasts = pd.concat([last_month.iloc[[-1]].copy(), forecasts], ignore_index=True)
    # Merge last_month and forecasts on the "date" column
    merged_df = pd.merge(
        last_month[["date", "total_amount"]],
        forecasts[["date", "total_amount"]],
        on="date",
        how="outer",
        suffixes=("_historical", "_forecast"),
    ).reset_index(drop=True)
    # Draw
    st.subheader("Last Month Sales with Forecasts")
    st.line_chart(
        merged_df.rename(
            columns={
                "total_amount_historical": "Last month sales",
                "total_amount_forecast": "ARIMA forecast 7 next days",
            }
        ),
        x="date",
        y=["ARIMA forecast 7 next days", "Last month sales"],
        x_label="Date",
        y_label="Total Amount",
        color=["#ff9380", "#80b3ff"],
    )

    # Monthly total amount per product category stacked bar chart
    monthly_total = (
        df_total.groupby([pd.Grouper(key="date", freq="ME"), "product_category"])["total_amount"]
        .sum()
        .reset_index()
        .pivot(index="date", columns="product_category", values="total_amount")
        .fillna(0)
    )
    st.subheader("Monthly Total Amount per Product Category")
    st.bar_chart(monthly_total)

    # Display last 10 sales
    st.subheader("Last 10 Sales")
    st.dataframe(df_last_week)

    # # Weekly total amount line chart
    # weekly_total = df_total[["date", "total_amount"]].groupby(pd.Grouper(key="date", freq="W")).sum().reset_index()
    # st.subheader("Weekly Total Amount Sold")
    # st.line_chart(weekly_total, x="date", y="total_amount", x_label="Date", y_label="Total Amount", color="#80b3ff")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    draw_dashboard()
