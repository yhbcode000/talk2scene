# :wrench: Installation

## :clipboard: Prerequisites

- :snake: Python 3.11+
- :package: [uv](https://docs.astral.sh/uv/) package manager
- :film_projector: FFmpeg (for audio processing)
- :satellite: Redis (for streaming mode)
- :globe_with_meridians: Node.js (optional, for frontend development)

## :inbox_tray: Install with uv

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

## :satellite: Redis Setup

```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis

# Verify
redis-cli ping
```

## :film_projector: FFmpeg Setup

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Verify
ffmpeg -version
```

## :white_check_mark: Verify Installation

```bash
uv run talk2scene --help
```
