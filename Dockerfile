FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first
COPY requirements.txt* pyproject.toml* uv.lock* ./

# Install dependencies directly to system Python (faster and simpler)
RUN if [ -f requirements.txt ]; then \
        uv pip install --system --no-cache -r requirements.txt; \
    elif [ -f pyproject.toml ]; then \
        uv pip install --system --no-cache .; \
    fi

# Copy application code
COPY config.py ./
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]