from backend.supabase_client import supabase


def save_conflict_result(result):
    """
    Save the latest LANDSYNC conflict result
    and its AI analysis into Supabase.

    Existing conflict records for the same parcel
    and conflict type are updated instead of duplicated.
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
    # 2. CHECK FOR EXISTING CONFLICT
    # -----------------------------------------

    conflict_type = result.get(
        "conflict_type",
        "MULTI_SOURCE_DISCREPANCY"
    )

    existing_response = (
        supabase
        .table("conflicts")
        .select("*")
        .eq("parcel_id", parcel_id)
        .eq("conflict_type", conflict_type)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    conflict_data = {
        "parcel_id": parcel_id,

        "conflict_type": conflict_type,

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

    # -----------------------------------------
    # 3. UPDATE OR CREATE CONFLICT
    # -----------------------------------------

    if existing_response.data:

        existing_conflict = existing_response.data[0]

        conflict_id = existing_conflict["id"]

        conflict_response = (
            supabase
            .table("conflicts")
            .update(conflict_data)
            .eq("id", conflict_id)
            .execute()
        )

    else:

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
    # 4. UPDATE AI ANALYSIS
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

    existing_analysis = (
        supabase
        .table("ai_analysis")
        .select("id")
        .eq("conflict_id", conflict_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if existing_analysis.data:

        analysis_id = existing_analysis.data[0]["id"]

        (
            supabase
            .table("ai_analysis")
            .update(analysis_data)
            .eq("id", analysis_id)
            .execute()
        )

    else:

        (
            supabase
            .table("ai_analysis")
            .insert(analysis_data)
            .execute()
        )

    return {
        "parcel_id": parcel_id,
        "conflict_id": conflict_id
    }


def save_source_records(
    source_df,
    source_name
):
    """
    Save source records into Supabase.

    Existing source records for the same parcel/source
    are replaced by the latest uploaded observation.
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
    # 2. SAVE SOURCE RECORDS
    # -----------------------------------------

    for _, row in source_df.iterrows():

        parcel_id = row["parcel_id"]

        # Remove previous record for this
        # parcel + source combination.

        (
            supabase
            .table("source_records")
            .delete()
            .eq("parcel_id", parcel_id)
            .eq("source_name", source_name)
            .execute()
        )

        record = {
            "parcel_id": parcel_id,
            "source_name": source_name,
            "owner_name": row.get("owner"),
            "land_use": row.get("land_use"),
            "area": float(row["area_m2"])
        }

        (
            supabase
            .table("source_records")
            .insert(record)
            .execute()
        )