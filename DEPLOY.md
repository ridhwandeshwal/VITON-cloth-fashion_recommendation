# Deploying ReVeRa (self-hosted)

VTON (IDM-VTON) and neural style transfer already run on Modal (see
`modal_apps/`), and the database is Neo4j Aura — both cloud-hosted already.
The only thing you're deploying here is the FastAPI backend + static
frontend, which needs no GPU.

## 1. Get the code + dataset images onto the server

```bash
git clone https://github.com/ridhwandeshwal/VITON-cloth-fashion_recommendation.git
cd VITON-cloth-fashion_recommendation
```

`frontend/cloth/` and `frontend/images/` (the product catalog images) are
gitignored and were never pushed to GitHub — the clone above will **not**
have them. Copy your local copies into the checkout at these exact paths
before building:

```
VITON-cloth-fashion_recommendation/frontend/cloth/    <- ~1.3GB, product garment images
VITON-cloth-fashion_recommendation/frontend/images/   <- ~1.5GB, other product images
```

(`backend/HD-ViTON/VITON-HD/datasets/test/image/` — the 122 model photos used
by try-on — is already committed to git, no action needed for that one.)

## 2. Set real secrets

```bash
cp .env.example .env
```

Fill in `.env` with the real values (Neo4j Aura creds, Modal URLs + proxy
auth token) — same file you've been using for local dev. This file is
excluded from the Docker build (`.dockerignore`) and only gets into the
container via `--env-file` at run time, never baked into the image.

## 3. Build and run

```bash
docker build -t revera .
docker run -d -p 80:8000 --env-file .env --name revera revera
```

- Default port inside the container is 8000; `-p 80:8000` maps it to 80 on
  the host. Override with `-e PORT=...` if you need the container to listen
  on something else.
- `-e WEB_CONCURRENCY=4` to bump worker count if your box has the RAM/CPU to
  spare (default is 2, sized for a small VM).

## 4. Verify

```bash
curl http://localhost/healthz          # {"status":"ok"} — no Neo4j/Modal dependency
curl http://localhost/models           # real list of model image filenames
```

Then a full browser pass against `http://<server-ip>/`: style quiz → home
page recommendations → a cloth page (garment image should load — this is
what proves `frontend/cloth` copied correctly) → try-on (pick a model,
upload a photo, use camera) → style transfer. Confirm none of these 404 and
that try-on/style-transfer actually round-trip to Modal (check
`docker logs revera` for the `httpx` request lines).

## Notes on where to actually run this

Two genuinely free options discussed, in case you haven't picked one yet:

- **Render.com free web service** — easiest (git-push deploy), but sleeps
  after 15 min idle; next request pays a cold-start delay.
- **Oracle Cloud "Always Free" VM** (4 ARM cores / 24GB RAM, free forever,
  no metering) — never sleeps, but you're fully responsible for ops (this
  Docker workflow is exactly what you'd run on it via SSH).

Camera capture (`getUserMedia`, used by the "Use Camera" try-on option)
requires either `localhost` or HTTPS — put this behind a reverse proxy with
a real TLS cert (e.g. Caddy or nginx + Let's Encrypt) if you want that
feature to work from other devices over plain HTTP won't do it.
