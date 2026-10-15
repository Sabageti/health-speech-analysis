import os
from pathlib import Path

def init_env():
    """
    Initialize environment variables and platform-specific patches.
    """
    # Set model cache directory locally
    os.environ["XDG_CACHE_HOME"] = str(Path(__file__).resolve().parents[2] / "models")

    # Ensure imageio-ffmpeg provides the ffmpeg binary to the PATH for Windows
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        target_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        target_exe = os.path.join(ffmpeg_dir, target_name)
        if not os.path.exists(target_exe):
            import shutil
            shutil.copy(ffmpeg_exe, target_exe)

        os.environ["PATH"] += os.pathsep + ffmpeg_dir
    except ImportError:
        pass
