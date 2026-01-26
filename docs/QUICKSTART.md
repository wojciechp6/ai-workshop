# Szybki Start - Instrukcja dla użytkowników

Kompletna instrukcja uruchomienia całego projektu od początku.

## Wymagania wstępne

### Sprzęt
- GPU NVIDIA (dla backendu z przyspieszeniem)
- Min 8GB RAM GPU (dla modelu 7B)
- 4+ core CPU
- 20GB+ wolnej przestrzeni dysku

### Oprogramowanie
- Docker Desktop z NVIDIA Container Runtime
- Git (do klonowania/aktualizacji)
- Linux/macOS/Windows z WSL2

### Konta i tokeny
- Token Hugging Face (https://huggingface.co/settings/tokens)

## Instalacja (pierwszy raz)

### 1. Klonuj repozytorium
```bash
git clone <repo-url> warsztaty-ai
cd warsztaty-ai
```

### 2. Przygotuj zmienne środowiskowe
```bash
cd model
cp .env.example .env  # Jeśli istnieje

# Edytuj .env i wstaw token
nano .env
```

Zawartość `.env`:
```env
HUGGING_FACE_HUB_TOKEN=hf_xxxxxxxxxxxxx
VLLM_MODEL=gemma-3-4b-it-unsloth-bnb-4bit
CUDA_VERSION=12.4.1
TORCH_CUDA_TAG=12.4-runtime
```

### 3. Przygotuj dane
```bash
# /data/posters.json powinien już istnieć
ls ../data/posters.json
```

Jeśli nie istnieje, stwórz przykładowy:
```json
{
  "items": [
    {
      "id": "poster_001",
      "title": "Przykładowy plakat",
      "year": "1940",
      "description": "Opis plakatu",
      "imageUrl": "https://example.com/image.jpg",
      "pageUrl": "https://example.com/poster",
      "tags": ["propaganda", "WWII"]
    }
  ]
}
```

## Uruchomienie backendu

### Terminal 1 - Backend
```bash
cd /path/to/warsztaty-ai/model

# Build i uruchomienie
docker compose up --build

# Czekaj aż się pojawią logi:
# vllm: "Loaded model..."
# client: "Analysing poster: poster_001"
```

⏱️ **Czas**: First run 5-15 minut (pobieranie modelu)

### Co się dzieje
1. **Docker pull/build** (~2 min)
   - Pobieranie bazy Nginx Alpine
   - Budowanie obrazów

2. **vllm start** (~10 min)
   - Pobieranie modelu z Hugging Face
   - Ładowanie do GPU
   - Health check pozytywny

3. **client start** (gdy vllm ready)
   - Ładowanie posters.json
   - Pobieranie obrazów
   - Wysyłanie do modelu
   - Zapis wyników

### Monitoring
```bash
# W innym terminalu - sprawdzić logi
docker compose logs -f vllm
docker compose logs -f client

# Lub śledzić výstup
watch -n 1 'ls -la ../data/generated/ | head -20'
```

## Uruchomienie frontendu

### Terminal 2 - Frontend
```bash
cd /path/to/warsztaty-ai/web

# Build i uruchomienie
docker compose up --build

# Powinno pojawić się:
# "Listening on port 80"
```

### Dostęp z przeglądarki
1. Otwórz: `http://localhost:8080`
2. Powinna być lista plakatów
3. Kliknij na plakat → szczegóły

⏱️ **Czas**: First run 1-2 min (build Nginx)

## Kolejne uruchomienia

### Backend
```bash
cd model

# Jeśli zmieniono kod
docker compose up --build

# Bez zmian
docker compose up

# Background (bez wypisywania logów)
docker compose up -d
```

### Frontend
```bash
cd web

# Jeśli zmieniono kod/HTML
docker compose up --build

# Bez zmian
docker compose up

# Background
docker compose up -d
```

## Sprawdzanie statusu

### Backend
```bash
# Czy vllm odpowiada?
curl http://localhost:8000/v1/models

# Czy pliki JSON są generowane?
ls -l /data/generated/
cat /data/generated/poster_001.json | jq .

# Logi
docker compose logs -n 50 client
```

### Frontend
```bash
# Czy dostęp sieciowy?
curl http://localhost:8080

# F12 w przeglądarce → Console tab
# Szukać błędów CORS lub 404
```

## Zatrzymanie

### Zatrzymaj pojedyncze kontener
```bash
# Backend
cd model && docker compose down

# Frontend
cd web && docker compose down
```

### Zatrzymaj wszystko
```bash
cd model && docker compose down
cd web && docker compose down

# Lub z głównego katalogu
docker compose -f model/docker-compose.yml down
docker compose -f web/docker-compose.yml down
```

### Czyszczenie (ostrożnie!)
```bash
# Usuń kontenery
docker compose down -v

# Usuń obrazy (przebuduje się za następnym up)
docker image rm vllm-openai:auto
docker image rm <frontend-image-id>

# Pełna czystka Docker
docker system prune -a
```

## Rozwiązywanie problemów

### Problem: "CUDA out of memory"
**Rozwiązanie**:
```bash
# model/docker-compose.yml
--gpu-memory-utilization=0.7  # Zmień z 0.9
```
Przebuduj: `docker compose up --build`

### Problem: "vllm timeout"
**Rozwiązanie**:
```bash
# model/docker-compose.yml
start_period: 60s  # Zmień z 30s
```

### Problem: "Blank white page w frontend"
**Rozwiązanie**:
1. Otwórz F12 (DevTools) → Console
2. Szukaj błędów (red texts)
3. Sprawdzić Network tab → czy `/data/posters.json` ma 200 status?
4. Jeśli 404, sprawdzić czy `/data` volume jest zmapowany:
   ```bash
   docker compose exec frontend ls -la /usr/share/nginx/html/data/
   ```

### Problem: "TypeError: fetch failed"
**Rozwiązanie**:
```bash
# Sprawdzić CORS
docker compose logs frontend | grep error

# Dodać do web/nginx.conf
add_header Access-Control-Allow-Origin "*";
```

### Problem: "Docker image not found"
**Rozwiązanie**:
```bash
# Przebudować od zera
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Problem: "Port 8080 już w użyciu"
**Rozwiązanie**:
```bash
# Zmienić port w web/docker-compose.yml
ports:
  - "8081:80"

# Lub znaleźć i zabić proces
lsof -i :8080
kill -9 <PID>
```

## Workflow typowego eksperymentu

```
1. Edycja prompt w model/src/loader.py
   └─ Zmiana instrukcji dla modelu

2. Czyszczenie starych wyników
   └─ rm /data/generated/*.json

3. Restart backendu
   └─ cd model && docker compose up --build

4. Czekanie na przetwarzanie
   └─ Obserwowanie logów w innym terminalu

5. Refresh frontendu
   └─ F5 w przeglądarce

6. Sprawdzenie wyników
   └─ Przejrzenie szczegółów plakatów
```

## Performance tipy

### Szybsza analiza
1. **Zmniejszy model**:
   ```bash
   VLLM_MODEL=Qwen/Qwen2-VL-2B-Instruct
   ```

2. **Równoległa przetwarzania**:
   ```bash
   --max-num-seqs=4  # Zamiast 1
   ```

3. **Zmniejsz parametry modelu**:
   ```bash
   --max-model-len=1024  # Zamiast 2048
   --max-num-batched-tokens=512  # Zamiast 1024
   ```

### Mniej zużycia VRAM
1. Zmniejsz model
2. Zmniejsz gpu-memory-utilization
3. Zmniejsz shm_size

## Dokumentacja szczegółowa

- [README główny](./README.md) - Przegląd projektu
- [Backend dokumentacja](./models/README.md) - Opis kodu backendu
- [Frontend dokumentacja](./web/README.md) - Opis kodu frontendu
- [Backend Docker](./models/DOCKER.md) - Docker Compose dla backendu
- [Frontend Docker](./web/DOCKER.md) - Docker Compose dla frontendu
- [Architektura](./ARCHITECTURE.md) - Przegląd całego systemu

## Support

Jeśli napotkasz problem:
1. Sprawdź dokumentację wyżej
2. Przejrzyj logi (docker compose logs)
3. Sprawdź Troubleshooting sekcje w odpowiednich dokumentach
