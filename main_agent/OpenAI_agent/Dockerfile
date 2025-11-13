# Use the open-source verification base image which includes Verilator, Icarus, etc.
FROM ghcr.io/hdl/sim/osvb

WORKDIR /app

# Install Python dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-requests \
    && rm -rf /var/lib/apt/lists/*

# Install OpenAI library for API calls
RUN pip3 install --no-cache-dir openai

# Create /code directory for mounted volumes
RUN mkdir -p /code && chmod 777 /code
RUN mkdir -p /app/config
RUN mkdir -p /app/core
RUN mkdir -p /app/hdl
RUN mkdir -p /app/llm
RUN mkdir -p /app/prompts
RUN mkdir -p /app/testing
RUN mkdir -p /app/utils


# Copy dirs
COPY config/ /app/config/
COPY core/ /app/core/
COPY hdl/ /app/hdl/
COPY llm/ /app/llm/
COPY prompts/ /app/prompts/
COPY testing/ /app/testing/
COPY utils/ /app/utils/

# Copy the agent code
COPY __init__.py /app/__init__.py
COPY main.py /app/main.py

# Make it executable
RUN chmod +x /app/main.py


# Set Python path to find modules
ENV PYTHONPATH=/app

# Set environment variables for OpenAI
ENV OPENAI_MODEL=gpt-4o-mini
ENV OPENAI_MAX_TOKENS=16000
ENV OPENAI_TIMEOUT=300
# OPENAI_API_KEY will be passed at runtime

# Set the entrypoint
ENTRYPOINT ["python3", "/app/main.py"]
