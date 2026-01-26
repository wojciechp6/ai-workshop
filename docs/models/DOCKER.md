# Docker Compose - Backend (Model)

Szczegółowa dokumentacja konfiguracji Docker dla backendu.

## Przegląd

Backend wykorzystuje dwa kontenery Docker:
- **vllm** - Serwer modelu LLM z API OpenAI-compatible
- **client** - Aplikacja Python analizująca plakaty

## Konfiguracja vllm

### Obraz i build

```yaml
build:
  context: .
  dockerfile: Dockerfile.vllm
  args:
    CUDA_VERSION: ${CUDA_VERSION}
    TORCH_CUDA_TAG: ${TORCH_CUDA_TAG}
```

- Budowany z `Dockerfile.vllm`
- Zmienne budowania do konfiguracji CUDA/PyTorch
- Obsługa GPU NVIDIA

### Networking i porty

```yaml
ports:
  - "8000:8000"
```

- **Port 8000** - API OpenAI-compatible
- Dostępne dla `client` kontenera na `http://vllm:8000`

### GPU

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

- Wymaga Docker Desktop z NVIDIA Container Runtime
- `count: all` - rezerwuje wszystkie dostępne GPU

### Pamięć

```yaml
ipc: host
shm_size: "2gb"
```

- **ipc: host** - Komunikacja między procesami z hoście
- **shm_size: 2gb** - Shared memory dla PyTorch
- Istotne dla dużych modeli

### Volumy

```yaml
volumes:
  - ${HF_CACHE_DIR:-~/.cache/huggingface}:/root/.cache/huggingface
  - ${MODELS_DIR:-./models}:/models
```

- **HF_CACHE_DIR** - Cache Hugging Face (domyślnie `~/.cache/huggingface`)
- **MODELS_DIR** - Lokalna kopia modeli (domyślnie `./models`)
- Oszczędzanie przepustowości, ponowne użycie modeli

### Zmienne środowiskowe

```yaml
environment:
  - HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN}
  - HF_TOKEN=${HUGGING_FACE_HUB_TOKEN}
  - HF_HOME=/root/.cache/huggingface
  - TRANSFORMERS_CACHE=/root/.cache/huggingface
```

- **HUGGING_FACE_HUB_TOKEN** - Token do pobierania modeli
- Duplikacja zmiennych dla kompatybilności różnych bibliotek

### Command (Uruchomienie)

```yaml
command:
  - --port=8000
  - --model=${VLLM_MODEL}
  - --gpu-memory-utilization=0.9
  - --max-num-seqs=1
  - --max-num-batched-tokens=1024
  - --max-model-len=2048
```

| Opcja | Wartość | Opis |
|-------|---------|------|
| `--port` | 8000 | Port API |
| `--model` | `${VLLM_MODEL}` | Model (np. Qwen2-VL-7B) |
| `--gpu-memory-utilization` | 0.9 | 90% VRAM GPU |
| `--max-num-seqs` | 1 | Jedno request jednocześnie |
| `--max-num-batched-tokens` | 1024 | Max tokens w batchu |
| `--max-model-len` | 2048 | Max długość sekwencji |

### Health check

```yaml
healthcheck:
  test: ["CMD", "curl", "-sf", "http://localhost:8000/v1/models"]
  interval: 10s
  timeout: 5s
  retries: 30
  start_period: 30s
```

- Sprawdza `/v1/models` co 10 sekund
- Timeout 5 sekund
- 30 prób (5 minut czekania)
- 30 sekund początkowego opóźnienia (ładowanie modelu)

## Konfiguracja client

### Build

```yaml
build:
  context: .
  dockerfile: Dockerfile.client
```

- Budowany z `Dockerfile.client` (Python 3.12)

### Zależności

```yaml
depends_on:
  vllm:
    condition: service_healthy
```

- Czeka aż `vllm` będzie healthy
- Nie startuje zanim vllm nie będzie gotów

### Zmienne środowiskowe

```yaml
environment:
  - VLLM_HOST=vllm
  - VLLM_PORT=8000
  - VLLM_MODEL=${VLLM_MODEL}
  - OUT_PATH=/data/generated
```

| Zmienna | Wartość | Opis |
|---------|---------|------|
| `VLLM_HOST` | vllm | Nazwa hosta (DNS w Docker) |
| `VLLM_PORT` | 8000 | Port serwera |
| `VLLM_MODEL` | `${VLLM_MODEL}` | Model |
| `OUT_PATH` | /data/generated | Katalog wyjściowy |

### Volumy

```yaml
volumes:
  - ../data:/data
```

- Montuje `/data` z hosta
- Dostęp do `posters.json` i zapis do `/data/generated`

## Zmienne .env

Przykładowy `.env`:

```env
HUGGING_FACE_HUB_TOKEN=hf_xxx...xxx
VLLM_MODEL=Qwen/Qwen2-VL-7B-Instruct
CUDA_VERSION=12.4.1
TORCH_CUDA_TAG=12.4-runtime
HF_CACHE_DIR=~/.cache/huggingface
MODELS_DIR=./models
```

## Uruchamianie

```bash
# Build i start
docker compose up --build

# Tylko start (bez build)
docker compose up

# Background
docker compose up -d

# Logi
docker compose logs -f vllm
docker compose logs -f client

# Stop
docker compose down
```

## Workflow uruchomienia

1. **Docker Compose start**
   ```bash
   docker compose up --build
   ```

2. **Build kontenerów**
   - vllm: pobranie bazy CUDA → instalacja bibliotek → gotowość do pracy
   - client: Python 3.12 slim → pip install requirements → gotowość

3. **Start vllm**
   - Ładowanie modelu (może trwać kilka minut)
   - Health check: czeka 30s, potem co 10s sprawdza `/v1/models`

4. **Start client** (gdy vllm healthy)
   - Ładowanie `posters.json`
   - Dla każdego plakatu:
     - Pobierz obraz z URL
     - Wyślij do vllm
     - Czekaj na analizę
     - Zapisz wynik do JSON

5. **Koniec**
   - client się kończy
   - vllm zostaje uruchomiony (można uruchomić client ponownie)

## Optimization tipy

### GPU memory
```yaml
--gpu-memory-utilization=0.85  # Zmniejsz z 0.9
```

### Szybsza przetwarzanie (mniej precyzji)
```yaml
--dtype=float16  # Zamiast float32
```

### Równoległa przetwarzanie
```yaml
--max-num-seqs=4  # Zamiast 1 (jeśli starcza RAM)
```

### Zmniejszenie modelu
```yaml
VLLM_MODEL=Qwen/Qwen2-VL-2B-Instruct  # Zamiast 7B
```

## Troubleshooting

### GPU not found
```bash
# Sprawdzić NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:12.4-runtime nvidia-smi

# Jeśli nie działa, zainstalować NVIDIA Container Runtime
```

### vllm timeout
```yaml
start_period: 60s  # Zwiększyć z 30s
```

### Out of Memory
1. Zmniejszyć `--gpu-memory-utilization`
2. Zmniejszyć model
3. Zmniejszyć `--max-num-batched-tokens`

### Brak tokenu Hugging Face
```bash
# Sprawdzić .env
echo $HUGGING_FACE_HUB_TOKEN

# Lub dodać ręcznie
export HUGGING_FACE_HUB_TOKEN=hf_xxx...xxx
docker compose up --build
```

### Client nie łączy się z vllm
```bash
# Sprawdzić logi
docker compose logs client

# Ręczny test
docker compose exec client curl -sf http://vllm:8000/v1/models
```
