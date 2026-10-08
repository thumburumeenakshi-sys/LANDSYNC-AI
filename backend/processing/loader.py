import pandas as pd
import geopandas as gpd

REQUIRED_COLUMNS = [
    "parcel_id",
    "owner",
    "area_m2",
    "land_use",
    "village"
]


def load_land_data(file_path):
    """
    Load the existing LANDSYNC land-record CSV.
    """
    df = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
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


def load_cadastral_data(file_path):
    """
    Load cadastral reference records.
    """
    df = pd.read_csv(file_path)

    required = [
        "parcel_id",
        "owner",
        "area_m2",
        "land_use",
        "village",
        "cadastral_status"
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing cadastral columns: {missing}"
        )

    df["area_m2"] = pd.to_numeric(
        df["area_m2"],
        errors="coerce"
    )

    return df


def load_gnss_data(file_path):
    """
    Load GNSS survey observations.
    """
    df = pd.read_csv(file_path)

    required = [
        "parcel_id",
        "latitude",
        "longitude",
        "elevation_m",
        "accuracy_cm"
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing GNSS columns: {missing}"
        )

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    df["elevation_m"] = pd.to_numeric(
        df["elevation_m"],
        errors="coerce"
    )

    df["accuracy_cm"] = pd.to_numeric(
        df["accuracy_cm"],
        errors="coerce"
    )

    return df


def load_drone_data(file_path):
    """
    Load drone-derived parcel observations.
    """
    df = pd.read_csv(file_path)

    required = [
        "parcel_id",
        "observed_area_m2",
        "boundary_deviation_m",
        "land_cover",
        "flight_date"
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing drone columns: {missing}"
        )

    df["observed_area_m2"] = pd.to_numeric(
        df["observed_area_m2"],
        errors="coerce"
    )

    df["boundary_deviation_m"] = pd.to_numeric(
        df["boundary_deviation_m"],
        errors="coerce"
    )

    return df


def load_gis_data(file_path):
    """
    Load GIS parcel geometry.
    """
    gdf = gpd.read_file(file_path)

    if "parcel_id" not in gdf.columns:
        raise ValueError(
            "GIS data must contain parcel_id"
        )

    return gdf