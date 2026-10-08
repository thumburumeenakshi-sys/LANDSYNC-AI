from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os

from backend.processing.pipeline import run_landsync


app = FastAPI(
    title="LANDSYNC AI API",
    description="Intelligent Land Data Harmonization and Conflict Detection",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "LANDSYNC AI API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/process")
async def process_land_data(
    source_a: UploadFile = File(...),
    source_b: UploadFile = File(...)
):

    temp_a = None
    temp_b = None

    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as file_a:

            file_a.write(await source_a.read())
            temp_a = file_a.name

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as file_b:

            file_b.write(await source_b.read())
            temp_b = file_b.name

        # Run LANDSYNC pipeline
        results = run_landsync(
            temp_a,
            temp_b
        )

        return {
            "status": "success",
            "total_conflicts": len(results),
            "results": results
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    finally:

        if temp_a and os.path.exists(temp_a):
            os.remove(temp_a)

        if temp_b and os.path.exists(temp_b):
            os.remove(temp_b)