
import os
import time
import json
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .core.env_init import init_env
from .core.media import preprocess_audio
from .features.acoustic import AcousticFeatures
from .features.lexical import LexicalFeatures
from .features.semantic import SemanticFeatures

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Health Speech Analysis API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize environment
init_env()

# Directories
UPLOADS_DIR = PROJECT_ROOT / "uploads"
RECORDINGS_DIR = PROJECT_ROOT / "recordings"
REPORTS_DIR = PROJECT_ROOT / "reports"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.get("/estimate")
async def estimate_time(size_bytes: int):
    # Rough estimate:
    # - Preprocessing: 1-2s
    # - ASR (Whisper Base): ~0.3x audio duration
    # - NLP: 1s
    # - Constant overhead: 2s
    # Assuming average 128kbps audio (16KB/s)
    audio_duration_guess = size_bytes / (16 * 1024)
    processing_time = 3 + (audio_duration_guess * 0.3)
    return {"estimated_seconds": round(processing_time, 1)}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOADS_DIR, f"{session_id}{ext}")
    output_wav = os.path.join(RECORDINGS_DIR, f"{session_id}.wav")

    # Start timing
    analysis_start = time.time()

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Preprocessing
        preprocess_audio(input_path, output_wav)

        # 2. Extract Acoustic & Temporal Features (Stage 1)
        acoustic_extractor = AcousticFeatures()
        acoustic_results = acoustic_extractor.extract_features(output_wav)
        acoustic_metrics = acoustic_results["metrics"]
        transcript = acoustic_results["transcript"]

        # 3. Extract Lexical Features (Stage 2)
        lexical_extractor = LexicalFeatures()
        lexical_metrics = lexical_extractor.extract_features(transcript)

        # 4. Extract Semantic Features (Stage 3 Placeholder)
        semantic_extractor = SemanticFeatures()
        semantic_metrics = semantic_extractor.extract_features(transcript)

        # Calculate actual duration
        actual_duration = round(time.time() - analysis_start, 2)

        # Final Report
        final_report = {
            "acoustic": acoustic_metrics,
            "lexical": lexical_metrics,
            "semantic": semantic_metrics,
            "transcript": transcript,
            "filename": file.filename,
            "processing_time_sec": actual_duration
        }

        # Save report to local disk
        base_name = os.path.splitext(file.filename)[0]
        timestamp = int(time.time())
        report_filename = f"{base_name}_{timestamp}_report.json"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=4, ensure_ascii=False)
        print(f"Report saved locally to: {report_path}")

        # Cleanup
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_wav): os.remove(output_wav)

        return final_report

    except Exception as e:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_wav): os.remove(output_wav)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    return FileResponse(PROJECT_ROOT / "index.html")

# Mount static files
app.mount("/css", StaticFiles(directory=PROJECT_ROOT / "css"), name="css")
app.mount("/js", StaticFiles(directory=PROJECT_ROOT / "js"), name="js")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
