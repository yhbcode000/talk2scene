# :wrench: 安装指南

## :clipboard: 前置要求

- :snake: Python 3.11+
- :package: [uv](https://docs.astral.sh/uv/) 包管理器
- :film_projector: FFmpeg（音频处理）
- :satellite: Redis（流式模式）
- :globe_with_meridians: Node.js（可选，前端开发）

## :inbox_tray: 使用 uv 安装

```bash
# 克隆仓库
git clone <repository-url>
cd talk2scene

# 安装依赖
uv sync

# 安装开发依赖
uv sync --extra dev

# 安装文档依赖
uv sync --extra docs
```

## :satellite: Redis 配置

```bash
# 安装 Redis
sudo apt install redis-server

# 启动 Redis
sudo systemctl start redis

# 验证
redis-cli ping
```

## :film_projector: FFmpeg 配置

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# 验证
ffmpeg -version
```

## :white_check_mark: 验证安装

```bash
uv run talk2scene --help
```
