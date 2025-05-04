FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy uv
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy the rest of the code
COPY . .

RUN uv tool install . 

# Default command
CMD ["mcp-terminal", "--mode", "sse", "--host", "0.0.0.0", "--port", "8000"]
