def preprocess_audio(input_file, output_file="temp.wav", sample_rate=16000):
    """
    Convert any input media (audio/video) to 16kHz Mono WAV using ffmpeg.
    """
    print(f"Preprocessing {input_file} -> {output_file}...")
    import ffmpeg
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, ac=1, ar=sample_rate, loglevel="error")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print("FFmpeg Error:", e.stderr.decode('utf8'))
        raise
    return output_file
