import shutil
import os

def run_vton_pipeline(person_path, cloth_path):
    # Just return the uploaded person image as the output (no processing)
    output_path = "backend/static/tryon_result.png"
    shutil.copyfile(person_path, output_path)
    return output_path
