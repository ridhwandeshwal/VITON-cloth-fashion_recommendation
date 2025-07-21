from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import sys

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
HD_VITON_DIR = "backend/HD-VITON/VITON-HD"
PAIRS_FILE = os.path.join(HD_VITON_DIR, "datasets", "test_pairs.txt")
FIXED_MODEL = "03615_00.jpg"
# RESULT_IMAGE = os.path.join(HD_VITON_DIR, "results", "results", "03615_08348_00.jpg")

# Serve basic HTML
@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/index_vton.html", "rb") as f:
        content = f.read().decode("utf-8", errors="replace")
    return HTMLResponse(content=content)


# Try-on endpoint
@app.post("/tryon/")
async def run_tryon(cloth_id: str = Form(...)):
    # Update pair file
    try:
        with open(PAIRS_FILE, "w") as f:
            f.write(f"{FIXED_MODEL} {cloth_id}\n")
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to update test_pairs.txt: {e}"})

    # Run test.py using the current Python interpreter (from myenv)
    try:
        subprocess.run(
            [sys.executable, "test.py", "--name", "results"],
            cwd=HD_VITON_DIR,
            check=True,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": "0"}
        )
    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"message": f"HD-VITON crashed: {e}"})

    model_base = FIXED_MODEL.replace("_00.jpg", "")
    result_filename = f"{model_base}_{cloth_id}"
    result_path = os.path.join(HD_VITON_DIR, "results", "results", result_filename)

    # Return file if exists
    if not os.path.exists(result_path):
        return JSONResponse(status_code=404, content={"message": f"Try-on result not found: {result_filename}"})

    return FileResponse(result_path, media_type="image/jpeg")