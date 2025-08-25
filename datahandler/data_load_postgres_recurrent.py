import os
import time
import numpy as np
import pandas as pd
import sqlalchemy as sql
from sqlalchemy import engine, create_engine

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
# Random sales data generation and insertion
# ----------------------------
def insert_daily_random_sales():
    _print_prefix = "recurrent_data_load"
    # Generate randomly between 1 to 10 daily sales.
    # Ensure that you use the day after the latest date of the table as "date".
    # Also ensure that you select for each entry a random customerid of the ones contained in the table.
    latest_date_query = 'SELECT MAX("date") FROM sales_db'
    latest_date = pd.read_sql(latest_date_query, engine).iloc[0, 0]
    new_date = latest_date + pd.Timedelta(days=1)
    num_sales = np.random.randint(1, 11)
    print(
        f"{_print_prefix}: Generating {num_sales} sales for date {new_date}. Current last date is {latest_date}."
    )
    customer_ids = pd.read_sql(
        'SELECT DISTINCT "customer_id" FROM sales_db',
        engine,
    )["customer_id"].values

    product_categories = pd.read_sql(
        'SELECT DISTINCT "product_category" FROM sales_db',
        engine,
    )["product_category"].values

    data = pd.DataFrame(
        {
            "date": new_date,
            "customer_id": np.random.choice(customer_ids, num_sales),
            "gender": np.random.randint(0, 2, num_sales),
            "age": np.random.randint(18, 70, num_sales),
            "product_category": np.random.choice(product_categories, num_sales),
            "quantity": np.random.randint(1, 3, num_sales),
            "price_per_unit": np.random.uniform(10.0, 500.0, num_sales),
        }
    )
    data["total_amount"] = data["quantity"] * data["price_per_unit"]

    try:
        data.to_sql(
            "sales_db",
            engine,
            if_exists="append",
            index=False,
            dtype={
                "date": sql.types.TIMESTAMP(timezone=False),
                "customer_id": sql.types.VARCHAR(length=9),
                "gender": sql.types.SmallInteger(),
                "age": sql.types.SmallInteger(),
                "product_category": sql.types.VARCHAR(length=11),
                "quantity": sql.types.REAL(),
                "price_per_unit": sql.types.REAL(),
                "total_amount": sql.types.REAL(),
            },
        )
        print(f"{_print_prefix}: New sales inserted successfully.")
    except Exception as e:
        print(f"{_print_prefix}: Error inserting data: {e}")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    while True:
        SLEEP_SECONDS = 60 * 60 * 24

        insert_daily_random_sales()

        print(f"main: Waiting {SLEEP_SECONDS/3600} hours for the next insert...\n")
        time.sleep(SLEEP_SECONDS)
