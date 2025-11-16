# Dockerfile for Claude Telegram Bot
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bot.py claude_client.py config.py ./

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Run the bot
CMD ["python", "bot.py"]

