# Setup Instructions

## Prerequisites
- Python 3.8+
- Docker (for running the agent)
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd cvdp_benchmark
```

### 2. Create and Activate Virtual Environment

#### On Linux/Mac:
```bash
python3 -m venv cvdp_env
source cvdp_env/bin/activate
```

#### On Windows:
```bash
python -m venv cvdp_env
cvdp_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Build the Docker Agent Image
```bash
cd main_agent/SLM_agent
bash build_agent.sh
cd ../..
```

### 5. Start the SLM API Server (Optional - for local models)
```bash
# If you want to run with local models like Jamba, Nemotron, or DeepSeek
./start_slm_api.sh start
```

## Running Benchmarks

### Agentic Mode (with iterative refinement)
```bash
# Activate venv if not already active
source cvdp_env/bin/activate

# Run on agentic example dataset
python run_benchmark.py \
  -f example_dataset/cvdp_v1.0.1_example_agentic_code_generation_no_commercial_with_solutions.jsonl \
  -l -g slm-agent \
  -p my-test-run
```

### Non-Agentic Mode (direct LLM calls)
```bash
# Run on non-agentic example dataset
python run_benchmark.py \
  -f example_dataset/cvdp_v1.0.1_example_nonagentic_code_generation_no_commercial_with_solutions.jsonl \
  -l -m jamba-slm \
  -p my-nonagentic-run \
  --custom-factory custom_slm_factory.py
```

## Configuration

### Changing the Model
Edit `main_agent/SLM_agent/Dockerfile`:
```dockerfile
ENV SLM_MODEL=jamba  # Change to: nemotron, deepseek, etc.
```

Then rebuild:
```bash
cd main_agent/SLM_agent && bash build_agent.sh
```

### Adjusting Timeout
Edit `main_agent/SLM_agent/Dockerfile`:
```dockerfile
ENV SLM_TIMEOUT=3000  # Timeout in seconds (50 minutes)
```

## What NOT to Push to GitHub

**Do NOT commit these:**
- `cvdp_env/` - Virtual environment (recreated by users)
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files
- `.env` - Environment variables with secrets
- `deep-test*/` - Test output directories
- `*-test/`, `*-full/` - Result directories
- `.DS_Store` - macOS files

**Do commit these:**
- `requirements.txt` - Python dependencies
- `main_agent/` - Agent source code
- `example_dataset/` - Example datasets
- `*.py` - Python scripts
- `README.md`, `SETUP.md` - Documentation
- `.gitignore` - Git ignore rules
- `Dockerfile`, `docker-compose.yml` - Docker configs

## Troubleshooting

### "Module not found" errors
Make sure venv is activated and dependencies installed:
```bash
source cvdp_env/bin/activate
pip install -r requirements.txt
```

### Docker build fails
Check Docker is running:
```bash
docker ps
```

### API timeout errors
Increase timeout in `main_agent/SLM_agent/Dockerfile` and rebuild.

## Support
For issues, check the logs in `<output-dir>/reports/1_agent.txt`
