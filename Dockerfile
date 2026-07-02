FROM python:3.11-slim

WORKDIR /app

# Try-on (IDM-VTON) and style transfer run on Modal (see modal_apps/), called
# over HTTP, so this image only needs the FastAPI app + recommendation stack —
# no GPU, no torch/tensorflow.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# JSON-array CMD invoking `sh -c exec ...`: keeps $PORT/$WEB_CONCURRENCY
# substitution (needs a shell) while `exec` replaces the shell with gunicorn
# as PID 1, so it receives SIGTERM directly for a clean shutdown instead of
# being orphaned as sh's child. --timeout 180 matters: /tryon/selected,
# /vton, and /styletransfer/selected proxy to Modal (httpx timeout=180 in
# backend/utils/modal_client.py) and can legitimately take 30-90s+ on a cold
# Modal container — gunicorn's default 30s worker timeout would otherwise
# kill the worker mid-request before Modal ever responds.
CMD ["sh", "-c", "exec gunicorn backend.main:app -w ${WEB_CONCURRENCY:-2} -k uvicorn.workers.UvicornWorker --timeout 180 --bind 0.0.0.0:${PORT:-8000}"]
