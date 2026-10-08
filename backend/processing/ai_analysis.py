def generate_ai_analysis(conflict):
    parcel_id = conflict["parcel_id"]
    conflict_type = conflict["conflict_type"]
    risk = conflict["risk_level"]
    confidence = conflict["confidence"]

    if conflict_type == "AREA_MISMATCH":

        percentage = conflict["difference_percentage"]

        explanation = (
            f"Parcel {parcel_id} has an area discrepancy of "
            f"{percentage}%. The two sources report different "
            f"land areas."
        )

        possible_reason = (
            "Possible reasons include an outdated record, "
            "survey variation, or a boundary discrepancy."
        )

        recommendation = (
            "Send the parcel for human verification and "
            "compare the underlying survey or boundary records."
        )

    elif conflict_type == "OWNER_MISMATCH":

        explanation = (
            f"Parcel {parcel_id} contains different owner "
            "information across the two sources."
        )

        possible_reason = (
            "The difference may be caused by an outdated "
            "ownership record or an update that has not been "
            "reflected across all sources."
        )

        recommendation = (
            "Verify the ownership information against the "
            "authorized land record."
        )

    elif conflict_type == "LAND_USE_MISMATCH":

        explanation = (
            f"Parcel {parcel_id} has different land-use "
            "classifications across the two sources."
        )

        possible_reason = (
            "The classification may have changed over time "
            "or the sources may use different classification standards."
        )

        recommendation = (
            "Review the latest approved land-use information."
        )

    else:

        explanation = (
            f"A data conflict was detected for parcel {parcel_id}."
        )

        possible_reason = (
            "The source records contain inconsistent information."
        )

        recommendation = (
            "Send the parcel for human verification."
        )

    return {
        "parcel_id": parcel_id,
        "conflict_type": conflict_type,
        "risk_level": risk,
        "confidence": confidence,
        "explanation": explanation,
        "possible_reason": possible_reason,
        "recommendation": recommendation
    }
