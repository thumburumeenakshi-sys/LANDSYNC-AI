import pandas as pd


REQUIRED_COLUMNS = [
    "parcel_id",
    "owner",
    "area_m2",
    "land_use",
    "village"
]


def load_land_data(file_path):
    df = pd.read_csv(file_path)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df["area_m2"] = pd.to_numeric(
        df["area_m2"],
        errors="coerce"
    )

    return df