# Health Speech Analysis

[English](README.md) | **简体中文**

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

完整体验需要先运行后端，再打开 **http://127.0.0.1:8000**。直接双击打开的本地 HTML 也会连接该本地后端。如果通过其他静态服务器打开页面，请改用后端网址进行分析。本项目不附带已部署的公共分析服务。

## 快速开始

需要 Python 3.13+、`uv`、浏览器，以及首次安装依赖和下载模型所需的网络。保留项目现有 Python 版本要求。FFmpeg 应在 PATH 中；依赖 `imageio-ffmpeg` 也提供备用可执行文件。

在克隆后的项目根目录运行：

```bash
uv sync --locked
uv run python -m spacy download en_core_web_sm
uv run python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

保持终端运行，访问 http://127.0.0.1:8000。选择一段简短的英语录音，点击 **Start Analysis**，等待结果。首次下载模型及 CPU 推理可能超过页面估计时间；进度条是模拟估计，不是后端实时进度。

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
README.md                   英文说明
README.zh-CN.md             中文说明
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

交互式接口文档：http://127.0.0.1:8000/docs。

## 限制与数据处理

- 每次请求重新加载模型，重复分析可能较慢；分析会阻塞请求，目前没有队列、上传大小限制或认证。应在本地使用，不适合直接开放为公共服务。
- 转写错误会影响文本指标。WPM 分母是检测到的语音时长，而非总录音时长；Whisper 片段不等同于经验证的语言学语句。
- 停顿计算包含达到阈值的开头静音及语音间隔，不包含结尾静音，不能直接解释为临床结论。
- 分析完成或捕获分析异常后会删除输入与转换文件。`reports/` 中的 JSON 报告会保留，包含转写和原始文件名；进程中断可能留下临时文件，不再需要时请清理。
- 发布源码不包含录音、报告、模型缓存、凭据或本地环境。执行分析时，浏览器会将所选文件发送给你运行的后端。
- 页面会请求 Google Fonts，模型下载会访问外部提供方；首次运行并非完全离线。

## 常见问题

- `/estimate` 返回 404 或 `/analyze` 返回 405：请使用后端网址，不要在 Live Server 或 GitHub Pages 上执行分析。
- 无法连接后端：确认 Uvicorn 仍在运行，浏览器开发者工具未设置 Offline。
- 缺少 `en_core_web_sm`：在本项目环境中运行上述 spaCy 模型下载命令。
- FFmpeg 或模型报错：查看 `/analyze` 响应的 `detail` 和后端终端，检查音频解码支持、网络与模型是否可用。
- 旧版本 uv workspace 错误：使用本版本根目录的 `pyproject.toml`，不再依赖不存在的嵌套 workspace。

## GitHub 发布

使用全新的 `health-speech-analysis` 仓库，以干净源码快照建立新的 Git 历史，不要仅更名后推送旧仓库历史。发布根目录网页、`backend/` 源码、双语 README、`.gitignore`、`.python-version`、`pyproject.toml` 和 `uv.lock`。排除缓存、生成数据、Python 字节码和旧 `.git`。

GitHub Pages 只能提供页面预览；完整分析需要单独运行 Python 后端。项目尚未选择许可证，公开展示不等于已授予开源使用许可。
