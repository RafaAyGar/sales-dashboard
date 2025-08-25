import os
import time

import pandas as pd
import sqlalchemy as sql
from statsmodels.tsa.arima.model import ARIMA

# ----------------------------
# Database connection
# ----------------------------
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
DB = os.getenv("POSTGRES_DB")

engine = sql.create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")


# ----------------------------
# Load data
# ----------------------------
def load_data(periods):
    query_total_amounts = f"""
        SELECT "date", "total_amount"
        FROM sales_db
        WHERE "date" >= (
            SELECT MAX("date") FROM sales_db
        ) - INTERVAL '{periods} days'
        ORDER BY "date" ASC
    """
    df = pd.read_sql(query_total_amounts, engine)
    return df.groupby("date").sum().reset_index()


# ----------------------------
# Train ARIMA model and forecast
# ----------------------------
def train_and_forecast(periods):
    data = load_data(periods)
    print(
        f"train_and_forecast: Training ARIMA on data ranging from {data['date'].min()} to {data['date'].max()}"
    )
    model = ARIMA(data["total_amount"], order=(3, 0, 0))
    model_fit = model.fit()
    print(
        f"train_and_forecast: ARIMA model fitted. Generating forecasts from {data['date'].max() + pd.Timedelta(days=1)} to {data['date'].max() + pd.Timedelta(days=7)}"
    )
    preds = model_fit.forecast(steps=7)
    forecast_dates = pd.date_range(start=data["date"].max() + pd.Timedelta(days=1), periods=7)
    print("train_and_forecast: Forecasts generated.")
    return pd.DataFrame(
        {
            "model": "ARIMA",
            "trained_at": pd.Timestamp.now(),
            "hyperparams": "{order=(3,0,0)}",
            "n_training_days": str(periods),
            "last_training_date": data["date"].max(),
            "forecast_date": forecast_dates,
            "predicted_total_amount": preds,
        }
    )


# ----------------------------
# Save forecasts to database
# ----------------------------
def save_forecasts_to_db(forecasts):
    # engine = sql.create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/forecasts")
    print("save_forecasts_to_db: Trying to save forecasts to database.")
    forecasts.to_sql(
        "forecasts",
        engine,
        if_exists="append",
        index=False,
        dtype={
            "model": sql.types.VARCHAR(length=32),
            "trained_at": sql.types.TIMESTAMP(timezone=False),
            "hyperparams": sql.types.VARCHAR(length=128),
            "n_training_days": sql.types.INTEGER(),
            "last_training_date": sql.types.TIMESTAMP(timezone=False),
            "forecast_date": sql.types.TIMESTAMP(timezone=False),
            "predicted_total_amount": sql.types.REAL(),
        },
    )
    print("save_forecasts_to_db: Forecasts saved to database.")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    TRAIN_PERIODS = 270
    SLEEP_SECONDS = 60 * 60 * 0.5
    current_last_id = 0

    while True:
        new_last_id = pd.read_sql("SELECT COALESCE(MAX(id), 0) AS last_id FROM audit_log;", engine).iloc[0][
            "last_id"
        ]
        if new_last_id != current_last_id:
            print("main: New data detected. Generating forecasts...")
            current_last_id = new_last_id
            forecasts = train_and_forecast(periods=TRAIN_PERIODS)
            save_forecasts_to_db(forecasts)
            print(f"main: Forecasts generated and saved. Sleeping for {SLEEP_SECONDS/3600} hours.\n")
        else:
            print(f"main: No new data detected. Sleeping {SLEEP_SECONDS/3600} hours...\n")

        time.sleep(SLEEP_SECONDS)
