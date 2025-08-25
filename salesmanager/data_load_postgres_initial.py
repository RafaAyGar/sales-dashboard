import os
import sqlalchemy as sql
from sqlalchemy import create_engine, text
from data_preparation import load_prepared_data


# ----------------------------
# Initial data load (if table is empty)
# ----------------------------
def load_prepared_data_to_postgresql():
    _print_prefix = "initial_data_load"
    # Connect to PostgreSQL docker container database
    USER = os.getenv("POSTGRES_USER")
    PASSWORD = os.getenv("POSTGRES_PASSWORD")
    HOST = os.getenv("POSTGRES_HOST")
    PORT = os.getenv("POSTGRES_PORT")
    DB = os.getenv("POSTGRES_DB")
    engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")

    # check if "sales_db" table exists
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 FROM sales_db LIMIT 1"))
        sales_table_has_data = result.first() is not None
        if sales_table_has_data:
            print(f"{_print_prefix}: Table 'sales_db' is not empty. No new initial data will be loaded.")
            return
        else:
            # Load prepared data to postgres
            data = load_prepared_data()
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
                print(f"{_print_prefix}: Initial data loaded into sales_db successfully.")
            except Exception as e:
                print(f"{_print_prefix}: Error loading data: {e}")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    load_prepared_data_to_postgresql()
