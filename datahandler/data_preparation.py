import os
import pandas as pd


# ----------------------------
# Data preparation and preprocessing
# ----------------------------
def load_prepared_data():
    current_folder_path = os.path.dirname(os.path.abspath(__file__))

    # Load data, sort by date, and display first 5 entries
    data = pd.read_csv(os.path.join(current_folder_path, "data_raw.csv"), parse_dates=["date"])
    data = data.sort_values(by="date")

    # Ensure 0 missing values
    assert (
        data.isnull().sum().sum() == 0 and data.isna().sum().sum() == 0
    ), "There are null values in the dataset"

    # Separate "product_category" (prodcat) column into multiple binary columns
    # Create binary columns for each product category, but keep the original column
    # prodcat_dummies = pd.get_dummies(data["product_category"], prefix="prodcat", drop_first=False)
    # data = pd.concat([data, prodcat_dummies], axis=1)

    # Remove unused column
    data = data.drop(columns=["transaction_id"])

    # Map gender column values to binary
    data["gender"] = data["gender"].map({"Male": 1, "Female": 0})

    return data.reset_index(drop=True)
