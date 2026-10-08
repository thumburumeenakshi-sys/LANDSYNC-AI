from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import tempfile
import os

from backend.processing.pipeline import run_multisource_landsync
from backend.supabase_client import supabase


app = FastAPI(
    title="LANDSYNC AI API",
    description="Intelligent Land Data Harmonization and Conflict Detection",
    version="2.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "LANDSYNC AI API is running",
        "status": "success",
        "version": "2.0.0"
    }


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# GET CONFLICTS
# ---------------------------------------------------------

@app.get("/conflicts")
def get_conflicts():

    try:

        response = (
            supabase
            .table("conflicts")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return {
            "status": "success",
            "total_conflicts": len(response.data),
            "conflicts": response.data
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------------------------------------------------
# MULTI-SOURCE PROCESSING
# ---------------------------------------------------------

@app.post("/process")
async def process_land_data(
    cadastral: UploadFile = File(...),
    drone: UploadFile = File(...),
    gnss: UploadFile = File(...)
):

    temp_cadastral = None
    temp_drone = None
    temp_gnss = None

    try:

        # ---------------------------------------------
        # Save cadastral upload
        # ---------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as file_cadastral:

            file_cadastral.write(
                await cadastral.read()
            )

            temp_cadastral = file_cadastral.name


        # ---------------------------------------------
        # Save drone upload
        # ---------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as file_drone:

            file_drone.write(
                await drone.read()
            )

            temp_drone = file_drone.name


        # ---------------------------------------------
        # Save GNSS upload
        # ---------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as file_gnss:

            file_gnss.write(
                await gnss.read()
            )

            temp_gnss = file_gnss.name


        # ---------------------------------------------
        # Run LANDSYNC multi-source pipeline
        # ---------------------------------------------

        results = run_multisource_landsync(
            temp_cadastral,
            temp_drone,
            temp_gnss
        )


        # ---------------------------------------------
        # Return results
        # ---------------------------------------------

        return {
            "status": "success",
            "message": "Multi-source land data processed successfully.",
            "total_conflicts": len(results),
            "results": results
        }


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    finally:

        # ---------------------------------------------
        # Delete temporary files
        # ---------------------------------------------

        if (
            temp_cadastral
            and os.path.exists(temp_cadastral)
        ):
            os.remove(temp_cadastral)


        if (
            temp_drone
            and os.path.exists(temp_drone)
        ):
            os.remove(temp_drone)


        if (
            temp_gnss
            and os.path.exists(temp_gnss)
        ):
            os.remove(temp_gnss)