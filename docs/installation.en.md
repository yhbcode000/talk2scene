# 🔧 Installation

## 📋 Prerequisites

- 🐍 Python 3.11+
- 📦 [uv](https://docs.astral.sh/uv/) package manager
- 📽️ FFmpeg (for audio processing)
- 📡 Redis (for streaming mode)
- 🌐 Node.js (optional, for frontend development)

## 📥 Install with uv

```bash
# Clone the repository
git clone <repository-url>
cd talk2scene

# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Install with docs dependencies
uv sync --extra docs
```

## 📡 Redis Setup

```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis

# Verify
redis-cli ping
```

## 📽️ FFmpeg Setup

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Verify
ffmpeg -version
```

## ✅ Verify Installation

```bash
uv run talk2scene --help
```
