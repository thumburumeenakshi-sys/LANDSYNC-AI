def calculate_confidence(conflict):
    """
    Calculate an explainable confidence score
    for a detected conflict.
    """

    score = 0

    # Exact parcel ID match
    score += 30

    # Valid source values
    if conflict.get("source_a_value") is not None:
        score += 20

    if conflict.get("source_b_value") is not None:
        score += 20

    # Clear measurable difference
    if conflict.get("difference") is not None:
        score += 20

    # Known conflict type
    if conflict.get("conflict_type"):
        score += 10

    return min(score, 100)


def calculate_risk(conflict):
    """
    Determine overall risk based on conflict type
    and severity.
    """

    conflict_type = conflict.get("conflict_type")
    risk = conflict.get("risk_level")

    if conflict_type == "OWNER_MISMATCH":
        return "HIGH"

    if conflict_type == "LAND_USE_MISMATCH":
        return "MEDIUM"

    if conflict_type == "AREA_MISMATCH":
        return risk

    return "LOW"


def enrich_conflicts(conflicts):
    """
    Add confidence and final risk to every conflict.
    """

    enriched = []

    for conflict in conflicts:

        conflict_copy = conflict.copy()

        confidence = calculate_confidence(conflict_copy)
        risk = calculate_risk(conflict_copy)

        conflict_copy["confidence"] = confidence
        conflict_copy["risk_level"] = risk

        enriched.append(conflict_copy)

    return enriched