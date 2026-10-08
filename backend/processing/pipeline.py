from backend.processing.loader import (
    load_cadastral_data,
    load_drone_data,
    load_gnss_data
)

from backend.processing.conflicts import (
    detect_multisource_conflicts
)

from backend.processing.ai_analysis import (
    generate_ai_analysis
)

from backend.database import (
    save_conflict_result,
    save_source_records
)


def run_multisource_landsync(
    cadastral_path,
    drone_path,
    gnss_path
):

    # -----------------------------------------
    # LOAD SOURCES
    # -----------------------------------------

    cadastral = load_cadastral_data(
        cadastral_path
    )

    drone = load_drone_data(
        drone_path
    )

    gnss = load_gnss_data(
        gnss_path
    )

    # -----------------------------------------
    # SAVE CADASTRAL SOURCE
    # -----------------------------------------

    save_source_records(
        cadastral,
        "CADASTRAL"
    )

    # -----------------------------------------
    # DETECT CONFLICTS
    # -----------------------------------------

    conflicts = detect_multisource_conflicts(
        cadastral,
        drone,
        gnss
    )

    final_results = []

    # -----------------------------------------
    # AI + DATABASE
    # -----------------------------------------

    for conflict in conflicts:

        analysis = generate_ai_analysis(
            conflict
        )

        result = {
            **conflict,
            "ai_analysis": analysis
        }

        final_results.append(result)

        save_conflict_result(
            result
        )

    return final_results