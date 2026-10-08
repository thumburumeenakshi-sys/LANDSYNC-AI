def generate_ai_analysis(conflict):
    """
    Generate an explainable AI-style analysis
    for multi-source land conflicts.
    """

    parcel_id = conflict["parcel_id"]
    risk = conflict["risk_level"]
    status = conflict["status"]

    area_difference = conflict.get(
        "area_difference_percentage", 0
    )

    boundary_deviation = conflict.get(
        "boundary_deviation_m", 0
    )

    gnss_accuracy = conflict.get(
        "gnss_accuracy_cm"
    )

    # -----------------------------------------
    # RISK-BASED EXPLANATION
    # -----------------------------------------

    if risk == "HIGH":

        explanation = (
            f"Parcel {parcel_id} shows a significant "
            f"multi-source discrepancy. The cadastral and "
            f"drone area values differ by "
            f"{area_difference}%, while the observed "
            f"boundary deviation is {boundary_deviation} m."
        )

        possible_reason = (
            "The discrepancy may indicate an outdated "
            "cadastral record, boundary modification, "
            "survey variation, or an unrecorded land change."
        )

        recommendation = (
            "Immediate human review is recommended. "
            "Verify the official cadastral boundary against "
            "the latest authorized survey and drone evidence."
        )

        action = "HUMAN_REVIEW_REQUIRED"

    elif risk == "MEDIUM":

        explanation = (
            f"Parcel {parcel_id} shows a moderate discrepancy "
            f"between independent land-data sources. "
            f"The area difference is {area_difference}% and "
            f"the boundary deviation is "
            f"{boundary_deviation} m."
        )

        possible_reason = (
            "The difference may result from survey tolerance, "
            "boundary measurement variation, or an outdated "
            "source record."
        )

        recommendation = (
            "Verify the parcel against the latest survey "
            "or geospatial record before updating the "
            "authoritative land database."
        )

        action = "VERIFICATION_REQUIRED"

    else:

        explanation = (
            f"Parcel {parcel_id} shows only a minor "
            f"multi-source variation. The area difference "
            f"is {area_difference}% and the boundary "
            f"deviation is {boundary_deviation} m."
        )

        possible_reason = (
            "The variation is likely within a small "
            "measurement or data synchronization range."
        )

        recommendation = (
            "Continue monitoring the parcel and verify "
            "the record during the next routine update."
        )

        action = "MONITOR"

    # -----------------------------------------
    # GNSS QUALITY
    # -----------------------------------------

    if gnss_accuracy is not None:

        if gnss_accuracy <= 3:
            gnss_quality = "HIGH"
        elif gnss_accuracy <= 10:
            gnss_quality = "MEDIUM"
        else:
            gnss_quality = "LOW"

    else:
        gnss_quality = "UNKNOWN"

    # -----------------------------------------
    # FINAL AI RESULT
    # -----------------------------------------

    return {
        "parcel_id": parcel_id,
        "risk_level": risk,
        "status": status,

        "explanation": explanation,

        "possible_reason": possible_reason,

        "recommendation": recommendation,

        "recommended_action": action,

        "gnss_quality": gnss_quality,

        "area_difference_percentage": area_difference,

        "boundary_deviation_m": boundary_deviation
    }