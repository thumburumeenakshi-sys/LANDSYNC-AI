from backend.supabase_client import supabase


def save_conflict_result(result):
    """
    Save a LANDSYNC multi-source conflict
    and its AI analysis into Supabase.
    """

    # -----------------------------------------
    # 1. ENSURE PARCEL EXISTS
    # -----------------------------------------

    parcel_data = {
        "parcel_id": result["parcel_id"],
        "owner_name": result.get("owner"),
        "land_use": result.get("land_use")
    }

    parcel_response = (
        supabase
        .table("parcels")
        .upsert(
            parcel_data,
            on_conflict="parcel_id"
        )
        .execute()
    )

    if not parcel_response.data:
        raise Exception(
            "Unable to create or retrieve parcel record."
        )

    parcel_id = parcel_response.data[0]["parcel_id"]

    # -----------------------------------------
    # 2. SAVE CONFLICT
    # -----------------------------------------

    conflict_data = {
        "parcel_id": parcel_id,

        "conflict_type": result.get(
            "conflict_type",
            "MULTI_SOURCE_DISCREPANCY"
        ),

        "mismatch_percentage": result.get(
            "area_difference_percentage"
        ),

        "risk_level": result.get(
            "risk_level"
        ),

        "confidence": result.get(
            "confidence"
        ),

        "status": result.get(
            "status",
            "PENDING"
        )
    }

    conflict_response = (
        supabase
        .table("conflicts")
        .insert(conflict_data)
        .execute()
    )

    if not conflict_response.data:
        raise Exception(
            "Unable to save conflict."
        )

    conflict_id = conflict_response.data[0]["id"]

    # -----------------------------------------
    # 3. SAVE AI ANALYSIS
    # -----------------------------------------

    analysis = result.get(
        "ai_analysis",
        {}
    )

    analysis_data = {
        "conflict_id": conflict_id,

        "explanation": analysis.get(
            "explanation"
        ),

        "recommendation": analysis.get(
            "recommendation"
        )
    }

    supabase \
        .table("ai_analysis") \
        .insert(analysis_data) \
        .execute()

    return {
        "parcel_id": parcel_id,
        "conflict_id": conflict_id
    }


def save_source_records(
    source_df,
    source_name
):
    """
    Save cadastral/source records into Supabase.
    """

    # -----------------------------------------
    # 1. CREATE PARCEL RECORDS
    # -----------------------------------------

    parcel_records = []

    for _, row in source_df.iterrows():

        parcel_records.append({
            "parcel_id": row["parcel_id"]
        })

    if parcel_records:

        (
            supabase
            .table("parcels")
            .upsert(
                parcel_records,
                on_conflict="parcel_id"
            )
            .execute()
        )

    # -----------------------------------------
    # 2. CREATE SOURCE RECORDS
    # -----------------------------------------

    records = []

    for _, row in source_df.iterrows():

        records.append({
            "parcel_id": row["parcel_id"],
            "source_name": source_name,
            "owner_name": row.get("owner"),
            "land_use": row.get("land_use"),
            "area": float(row["area_m2"])
        })

    if records:

        (
            supabase
            .table("source_records")
            .insert(records)
            .execute()
        )