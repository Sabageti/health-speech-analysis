import argparse
import json
import os
import time

from .core.env_init import init_env
from .core.media import preprocess_audio
from .features.acoustic import AcousticFeatures
from .features.lexical import LexicalFeatures
from .features.semantic import SemanticFeatures

def main():
    parser = argparse.ArgumentParser(description="Health Speech Analysis CLI")
    parser.add_argument("input_file", help="Path to input audio/video file")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found.")
        return

    # 1. Init environment setup
    init_env()

    # Create workspace dir for temp files
    os.makedirs("recordings", exist_ok=True)
    temp_wav = os.path.join("recordings", "temp_analysis.wav")

    print(f"\n--- STEP 1: Preprocessing '{args.input_file}' ---")
    start_time = time.time()
    preprocess_audio(args.input_file, temp_wav)
    print(f"Preprocessing completed in {time.time() - start_time:.2f}s")

    # 2. Extract Acoustic & Temporal Features (Stage 1)
    print(f"\n--- STEP 2: Extracting Acoustic Features (Stage 1) ---")
    start_time = time.time()
    acoustic_extractor = AcousticFeatures()
    acoustic_results = acoustic_extractor.extract_features(temp_wav)
    acoustic_metrics = acoustic_results["metrics"]
    transcript = acoustic_results["transcript"]
    print(f"Acoustic features extraction completed in {time.time() - start_time:.2f}s")

    # Extracting Lexical Features (Stage 2)
    print(f"\n--- STEP 3: Extracting Lexical Features (Stage 2) ---")
    start_time = time.time()
    lexical_extractor = LexicalFeatures()
    lexical_metrics = lexical_extractor.extract_features(transcript)
    print(f"Lexical features extraction completed in {time.time() - start_time:.2f}s")

    # Placeholder for Stage 3
    print(f"\n--- STEP 4: Extracting Semantic Features (Stage 3 - Placeholder) ---")
    semantic_extractor = SemanticFeatures()
    semantic_metrics = semantic_extractor.extract_features(transcript)

    # Final Report Generation
    final_report = {
        "Acoustic_and_Temporal_Metrics (Stage 1)": acoustic_metrics,
        "Lexical_Metrics (Stage 2)": lexical_metrics,
        "Semantic_Metrics (Stage 3)": semantic_metrics,
        "Transcript": transcript
    }

    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    print(json.dumps(final_report, indent=4, ensure_ascii=False))

    # Save the output to JSON as well
    os.makedirs("reports", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(args.input_file))[0]
    report_path = os.path.join("reports", base_name + "_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=4, ensure_ascii=False)
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    main()
