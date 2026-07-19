FROM python:3.11-slim

WORKDIR /srv
RUN pip install --no-cache-dir "fastapi>=0.110" "uvicorn[standard]>=0.29"
COPY app ./app

# PC_DB_PATH should point at a persistent volume in production (see render.yaml).
ENV PC_DB_PATH=/data/planetary_council.db
EXPOSE 8765
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8765}"]
