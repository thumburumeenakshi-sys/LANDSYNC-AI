from backend.processing.loader import load_land_data
from backend.processing.conflicts import detect_conflicts
from backend.processing.scoring import enrich_conflicts
from backend.processing.ai_analysis import generate_ai_analysis


def run_landsync(source_a_path, source_b_path):

    # 1. Load data
    source_a = load_land_data(source_a_path)
    source_b = load_land_data(source_b_path)

    # 2. Detect conflicts
    conflicts = detect_conflicts(source_a, source_b)

    # 3. Add risk and confidence
    enriched_conflicts = enrich_conflicts(conflicts)

    # 4. Generate AI analysis
    final_results = []

    for conflict in enriched_conflicts:
        analysis = generate_ai_analysis(conflict)

        result = {
            **conflict,
            "ai_analysis": analysis
        }

        final_results.append(result)

    return final_results