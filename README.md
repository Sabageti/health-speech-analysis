# Health Speech Analysis

**English** | [简体中文](README.zh-CN.md)

A web demo that turns an uploaded audio or video file into a speech transcript and exploratory acoustic and lexical measures. The browser interface is the main entry point; Python runs the analysis locally.

## Features

- Select or drag and drop an audio/video file, including WAV, MP3, M4A and MP4, subject to FFmpeg decoding support.
- Convert input to 16 kHz mono WAV using FFmpeg.
- Detect speech using Silero VAD and transcribe using Whisper `base`.
- Display audio duration, recognized word count, words per minute during detected speech, mean recognized words per Whisper segment, and mean pause duration.
- Display lemma-based lexical diversity (TTR), noun/verb ratio, and noun/verb counts using spaCy English.
- Show selectable transcript text and elapsed processing time; save JSON reports locally.

Semantic analysis is a placeholder and is not displayed. There are no user accounts, database, longitudinal tracking, or production deployment. These exploratory measures are not validated clinical assessments.

## Preview vs. Analysis

Open `index.html` to preview the interface. Its relative assets also support a static host such as GitHub Pages. **Static hosting does not run Python or perform audio analysis.**

For the full demo, start the backend and open **http://127.0.0.1:8000**. A directly opened local HTML file targets that same local backend. A page served by another static server targets that server and will not analyze audio; use the backend URL instead. No hosted public analysis service is included.

## Quick Start

Prerequisites: Python 3.13+, `uv`, a browser, and internet access for initial dependency and model downloads. The existing Python requirement is retained. FFmpeg must be available on PATH; the bundled `imageio-ffmpeg` package also provides a fallback binary.

From the cloned repository root:

```bash
uv sync --locked
uv run python -m spacy download en_core_web_sm
uv run python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Keep the terminal running and open http://127.0.0.1:8000. Select a short English speech recording, click **Start Analysis**, and review the results. Initial model downloads and CPU inference may take longer than the displayed estimate. The progress bar is an estimate, not measured backend progress.

Dependencies are locked in `uv.lock`. Do not commit local environments or downloaded models. Whisper defaults to its available device; GPU/CUDA setup is optional and not covered here.

Optional command-line analysis, from the repository root:

```bash
uv run python -m backend.main /path/to/audio.wav
```

## Architecture

```text
index.html + css/ + js/
        | multipart upload
        v
FastAPI -> FFmpeg -> Silero VAD + Whisper -> spaCy -> JSON response/report
```

```text
index.html                  Web demo entry point
css/style.css               Styles
js/app.js                   Upload, progress estimate, results
backend/
  api.py                    FastAPI routes and frontend hosting
  main.py                   Optional command-line entry point
  core/                     Environment setup and media conversion
  features/                 Acoustic, lexical, and placeholder semantic analysis
README.md                   English documentation
README.zh-CN.md             Chinese documentation
pyproject.toml / uv.lock     Python dependencies and lockfile
models/                     Local model cache (excluded from publication)
uploads/ / recordings/      Temporary input/converted files (excluded)
reports/                    Generated JSON reports (excluded)
```

The backend serves only the CSS and JavaScript directories as static assets, rather than exposing the entire project directory.

## Technology

| Area | Stack |
| --- | --- |
| Frontend | HTML, CSS, vanilla JavaScript, Fetch and FormData |
| API | Python, FastAPI, Uvicorn |
| Media | FFmpeg, ffmpeg-python, SoundFile |
| Speech | PyTorch, Silero VAD via Torch Hub, OpenAI Whisper |
| Text | spaCy and `en_core_web_sm` |
| Environment | uv, pyproject.toml, uv.lock |

The existing dependency set also contains research utilities not used directly by the web request path. This cleanup does not upgrade or prune that environment.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/` | Web interface |
| GET | `/estimate?size_bytes=1920044` | Rough processing-time estimate |
| POST | `/analyze` | Multipart field `file`; returns acoustic/lexical/semantic fields, transcript, filename and processing time |

Interactive API reference: http://127.0.0.1:8000/docs.

## Limitations and Data

- Models are loaded within each request; repeated analysis can be slow. The analysis currently blocks the request, with no queue, upload limit or authentication. Run it locally, not as an unprotected public service.
- ASR errors affect all text-derived measures. WPM uses detected speech duration, not total recording duration. Whisper segments are not validated linguistic utterances.
- Pause calculation includes leading silence above the threshold and gaps between speech segments, but excludes trailing silence. Values should not be interpreted as clinical outcomes.
- Inputs and converted WAVs are deleted after analysis or handled analysis errors. JSON reports persist in `reports/` and include transcripts and original filenames. Interrupted processes can leave temporary files; review and remove local data when no longer needed.
- The source upload does not include recordings, reports, model caches, credentials or local environments. A runtime analysis request sends the selected file to the backend you run.
- The page requests Google Fonts; model downloads contact external providers. Local inference does not mean an entirely network-free first run.

## Troubleshooting

- `/estimate` returns 404 or `/analyze` returns 405: use the backend URL, not Live Server or GitHub Pages.
- Cannot reach backend: keep Uvicorn running and ensure the browser network setting is not Offline.
- Missing `en_core_web_sm`: run the spaCy download command in this project's environment.
- FFmpeg/model failure: inspect the `/analyze` response `detail` and backend terminal; check decoder support, connectivity and model availability.
- Invalid uv workspace errors from an older checkout: use this version's root `pyproject.toml`, which has no nested workspace requirement.

## Publishing

Use a **new** GitHub repository named `health-speech-analysis`. Publish a clean source snapshot with a new Git history; do not push a renamed copy of an older repository's history. Include the root web files, `backend/` source, both READMEs, `.gitignore`, `.python-version`, `pyproject.toml` and `uv.lock`. Exclude caches, generated data, bytecode and `.git`.

GitHub Pages can host the interface preview only. Full analysis requires a separately running Python backend. No license has been selected; choose one before presenting this repository as open-source software.
