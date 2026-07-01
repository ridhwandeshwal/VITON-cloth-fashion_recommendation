FROM python:3.11-slim

WORKDIR /app

# Try-on (IDM-VTON) and style transfer run on Modal (see modal_apps/), called
# over HTTP, so this image only needs the FastAPI app + recommendation stack —
# no GPU, no torch/tensorflow.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
