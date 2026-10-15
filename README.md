# Health Speech Analysis

[English](#english) | [简体中文](#简体中文)

## English

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

For the full demo, start the backend and open [http://127.0.0.1:8000](http://127.0.0.1:8000). A directly opened local HTML file targets that same local backend. A page served by another static server targets that server and will not analyze audio; use the backend URL instead. No hosted public analysis service is included.

## Quick Start

Prerequisites: Python 3.13+, `uv`, a browser, and internet access for initial dependency and model downloads. The existing Python requirement is retained. FFmpeg must be available on PATH; the bundled `imageio-ffmpeg` package also provides a fallback binary.

From the cloned repository root:

```bash
uv sync --locked
uv run python -m spacy download en_core_web_sm
uv run python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

Keep the terminal running and open [http://127.0.0.1:8000](http://127.0.0.1:8000). Select a short English speech recording, click **Start Analysis**, and review the results. Initial model downloads and CPU inference may take longer than the displayed estimate. The progress bar is an estimate, not measured backend progress.

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
README.md                   English and Chinese documentation
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

Interactive API reference: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 简体中文

[English](#english) | [简体中文](#简体中文)

一个网页演示：上传音频或视频，查看语音转写及探索性的声学、词汇指标。网页是主要入口，Python 在本地执行分析。

## 当前功能

- 点击选择或拖放音视频，支持 WAV、MP3、M4A、MP4 等 FFmpeg 可解码的格式。
- 使用 FFmpeg 转换为 16 kHz 单声道 WAV。
- 使用 Silero VAD 检测语音，使用 Whisper `base` 转写。
- 展示音频时长、识别词数、有效语音期间的每分钟词数、每个 Whisper 片段的平均词数和平均停顿时长。
- 使用 spaCy 英语模型计算基于词形还原的词汇多样性 TTR、名词/动词比例和数量。
- 展示可选择复制的转写文本及处理耗时，将 JSON 报告保存到本地。

语义分析仍是占位模块，网页不展示其结果。目前没有账户、数据库、长期跟踪或生产部署。这些探索性指标未经临床验证。

## 网页预览与完整分析

直接打开根目录的 `index.html` 可以预览页面。资源使用相对路径，也可以部署到 GitHub Pages 等静态托管服务。**静态托管不能运行 Python，也不能完成真实音频分析。**

完整体验需要先运行后端，再打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。直接双击打开的本地 HTML 也会连接该本地后端。如果通过其他静态服务器打开页面，请改用后端网址进行分析。本项目不附带已部署的公共分析服务。

## 快速开始

需要 Python 3.13+、`uv`、浏览器，以及首次安装依赖和下载模型所需的网络。保留项目现有 Python 版本要求。FFmpeg 应在 PATH 中；依赖 `imageio-ffmpeg` 也提供备用可执行文件。

在克隆后的项目根目录运行：

```bash
uv sync --locked
uv run python -m spacy download en_core_web_sm
uv run python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

保持终端运行，访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)。选择一段简短的英语录音，点击 **Start Analysis**，等待结果。首次下载模型及 CPU 推理可能超过页面估计时间；进度条是模拟估计，不是后端实时进度。

依赖由 `uv.lock` 锁定。不要提交本地环境和模型。Whisper 默认使用可用设备；GPU/CUDA 配置可选，本说明不涉及安装。

可选的命令行分析，同样从根目录运行：

```bash
uv run python -m backend.main /path/to/audio.wav
```

## 项目架构

```text
index.html + css/ + js/
        | 上传文件
        v
FastAPI -> FFmpeg -> Silero VAD + Whisper -> spaCy -> JSON 响应/报告
```

```text
index.html                  网页入口
css/style.css               页面样式
js/app.js                   上传、时间估计、结果展示
backend/
  api.py                    FastAPI 接口及网页托管
  main.py                   可选命令行入口
  core/                     环境初始化与媒体转换
  features/                 声学、词汇及占位语义分析
README.md                   中英文说明
pyproject.toml / uv.lock     Python 依赖与锁文件
models/                     本地模型缓存，不发布
uploads/ / recordings/      输入与转换临时文件，不发布
reports/                    生成的 JSON 报告，不发布
```

后端只将 CSS 和 JavaScript 目录作为静态资源提供，不会把整个项目目录暴露给浏览器。

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 网页 | HTML、CSS、原生 JavaScript、Fetch、FormData |
| 后端 | Python、FastAPI、Uvicorn |
| 媒体处理 | FFmpeg、ffmpeg-python、SoundFile |
| 语音处理 | PyTorch、通过 Torch Hub 加载的 Silero VAD、OpenAI Whisper |
| 文本处理 | spaCy、en_core_web_sm |
| 环境管理 | uv、pyproject.toml、uv.lock |

现有依赖还包含网页请求流程未直接使用的研究工具。本次整理保留原有依赖环境，没有升级或大规模裁剪。

## 接口

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/` | 网页界面 |
| GET | `/estimate?size_bytes=1920044` | 粗略估计处理时间 |
| POST | `/analyze` | multipart 文件字段 `file`；返回声学、词汇、语义字段、转写、文件名及耗时 |

交互式接口文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。
