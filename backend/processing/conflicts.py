def calculate_percentage_difference(reference, observed):
    if reference == 0:
        return 0

    return round(
        abs(reference - observed) / reference * 100,
        2
    )


def calculate_risk(
    area_percentage,
    boundary_deviation
):
    """
    Determine overall parcel risk.
    """

    if area_percentage > 10 or boundary_deviation > 3:
        return "HIGH"

    if area_percentage >= 5 or boundary_deviation >= 1:
        return "MEDIUM"

    return "LOW"


def calculate_confidence(
    area_percentage,
    gnss_accuracy,
    boundary_deviation
):
    """
    Calculate explainable confidence score.

    Higher confidence means the system has
    stronger and more reliable supporting evidence.
    """

    score = 70

    # GNSS measurement quality
    if gnss_accuracy <= 2:
        score += 15

    elif gnss_accuracy <= 5:
        score += 10

    elif gnss_accuracy <= 10:
        score += 5

    # Clear measurable discrepancy
    if area_percentage >= 10:
        score += 10

    elif area_percentage >= 1:
        score += 5

    # Boundary evidence
    if boundary_deviation >= 3:
        score += 5

    elif boundary_deviation >= 1:
        score += 3

    return min(score, 100)


def detect_multisource_conflicts(
    cadastral,
    drone,
    gnss
):
    """
    Compare cadastral, drone and GNSS
    observations for each parcel.
    """

    conflicts = []

    # -----------------------------------------
    # MERGE CADASTRAL + DRONE
    # -----------------------------------------

    merged = cadastral.merge(
        drone,
        on="parcel_id",
        how="left"
    )

    # -----------------------------------------
    # MERGE GNSS
    # -----------------------------------------

    merged = merged.merge(
        gnss,
        on="parcel_id",
        how="left"
    )

    # -----------------------------------------
    # ANALYZE EACH PARCEL
    # -----------------------------------------

    for _, row in merged.iterrows():

        parcel_id = row["parcel_id"]

        cadastral_area = float(
            row["area_m2"]
        )

        drone_area = float(
            row["observed_area_m2"]
        )

        area_percentage = (
            calculate_percentage_difference(
                cadastral_area,
                drone_area
            )
        )

        boundary_deviation = float(
            row["boundary_deviation_m"]
        )

        gnss_accuracy = float(
            row["accuracy_cm"]
        )

        risk = calculate_risk(
            area_percentage,
            boundary_deviation
        )

        confidence = calculate_confidence(
            area_percentage,
            gnss_accuracy,
            boundary_deviation
        )

        # -------------------------------------
        # DETECT DISCREPANCY
        # -------------------------------------

        conflict_detected = (
            area_percentage > 0
            or boundary_deviation > 0
        )

        if not conflict_detected:
            continue

        # -------------------------------------
        # STATUS
        # -------------------------------------

        if risk == "HIGH":

            status = "HUMAN_REVIEW"

        elif risk == "MEDIUM":

            status = "VERIFICATION_REQUIRED"

        else:

            status = "MONITOR"

        # -------------------------------------
        # RESULT
        # -------------------------------------

        conflicts.append({

            "parcel_id": parcel_id,

            "conflict_type":
                "MULTI_SOURCE_DISCREPANCY",

            "cadastral_area_m2":
                cadastral_area,

            "drone_area_m2":
                drone_area,

            "area_difference_percentage":
                area_percentage,

            "boundary_deviation_m":
                boundary_deviation,

            "gnss_accuracy_cm":
                gnss_accuracy,

            "risk_level":
                risk,

            "confidence":
                confidence,

            "status":
                status,

            "owner":
                row["owner"],

            "land_use":
                row["land_use"],

            "village":
                row["village"]
        })

    return conflicts