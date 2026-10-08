def calculate_area_difference(area_a, area_b):
    difference = abs(area_a - area_b)

    if area_a == 0:
        percentage = 0
    else:
        percentage = (difference / area_a) * 100

    return round(difference, 2), round(percentage, 2)


def get_area_risk(difference_percentage):
    if difference_percentage < 5:
        return "LOW"
    elif difference_percentage <= 10:
        return "MEDIUM"
    else:
        return "HIGH"


def detect_conflicts(source_a, source_b):
    conflicts = []

    merged = source_a.merge(
        source_b,
        on="parcel_id",
        suffixes=("_a", "_b")
    )

    for _, row in merged.iterrows():

        parcel_id = row["parcel_id"]

        # -------------------------
        # AREA MISMATCH
        # -------------------------
        area_a = row["area_m2_a"]
        area_b = row["area_m2_b"]

        if area_a != area_b:

            difference, percentage = calculate_area_difference(
                area_a,
                area_b
            )

            risk = get_area_risk(percentage)

            conflicts.append({
                "parcel_id": parcel_id,
                "conflict_type": "AREA_MISMATCH",
                "source_a_value": area_a,
                "source_b_value": area_b,
                "difference": difference,
                "difference_percentage": percentage,
                "risk_level": risk
            })

        # -------------------------
        # OWNER MISMATCH
        # -------------------------
        if row["owner_a"] != row["owner_b"]:

            conflicts.append({
                "parcel_id": parcel_id,
                "conflict_type": "OWNER_MISMATCH",
                "source_a_value": row["owner_a"],
                "source_b_value": row["owner_b"],
                "difference": None,
                "difference_percentage": None,
                "risk_level": "HIGH"
            })

        # -------------------------
        # LAND USE MISMATCH
        # -------------------------
        if row["land_use_a"] != row["land_use_b"]:

            conflicts.append({
                "parcel_id": parcel_id,
                "conflict_type": "LAND_USE_MISMATCH",
                "source_a_value": row["land_use_a"],
                "source_b_value": row["land_use_b"],
                "difference": None,
                "difference_percentage": None,
                "risk_level": "MEDIUM"
            })

    return conflicts