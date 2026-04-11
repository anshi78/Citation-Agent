FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Download the SQLite database at build time from HF Datasets
RUN python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='ruby56/Citation-Database', filename='citation_db.sqlite', repo_type='dataset', local_dir='/app')"

COPY . .

EXPOSE 7860

# Run the OpenEnv FastAPI server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
