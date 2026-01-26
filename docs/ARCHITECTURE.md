# Architektura Projektu

Przegląd ogólnej architektury systemu analizy plakatów.

## Diagram przepływu

```
┌─────────────────────────────────────────────────────────────┐
│  ŹRÓDŁO DANYCH                                              │
│  /data/posters.json (lista plakatów z URL-ami)             │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND - Model (Docker Compose)                           │
│  ┌──────────────────────┐        ┌──────────────────────┐   │
│  │ client (Python)      │        │ vllm (LLM Server)    │   │
│  │ - load_posters()     │◄──────►│ - Port 8000          │   │
│  │ - analyze_image()    │        │ - OpenAI API compat  │   │
│  │ - export to JSON     │        │ - GPU support        │   │
│  └──────────────────────┘        └──────────────────────┘   │
│           │                                                   │
│           └──► /data/generated/{id}.json (wyniki analizy)   │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND - Web (Docker)                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Nginx (port 8080)                                  │    │
│  │ - index.html (strona główna - lista plakatów)     │    │
│  │ - poster.html (strona szczegółów)                 │    │
│  │ - app.js (logika - fetch JSON-ów)                 │    │
│  │ - style.css (styling)                             │    │
│  └────────────────────────────────────────────────────┘    │
│           │                                                  │
│           └──► http://localhost:8080 (przeglądar)          │
└─────────────────────────────────────────────────────────────┘
```

## Komponenty

### 1. Backend (model/)
**Technologia**: Python + LLM (vllm) + GPU

**Rola**: 
- Pobieranie i przetwarzanie obrazów plakatów
- Analiza za pomocą modelu sztucznej inteligencji
- Generowanie opisów i kategoryzacji tagów

**Komponenty**:
- `loader.py` - Ładowanie plakatów
- `client.py` - Pętla przetwarzania
- `exporter.py` - Konwersja do JSON/RDF
- `vllm` - Serwer modelu
- Docker Compose - Orchestracja

**Wejście**: `/data/posters.json`
**Wyjście**: `/data/generated/{id}.json`

### 2. Frontend (web/)
**Technologia**: HTML + CSS + JavaScript + Nginx

**Rola**:
- Wyświetlanie listy plakatów
- Wyszukiwanie i filtrowanie
- Prezentacja szczegółów i analiz

**Komponenty**:
- `index.html` - Strona główna
- `poster.html` - Strona szczegółów
- `app.js` - Logika aplikacji
- `style.css` - Style
- `nginx.conf` - Konfiguracja serwera
- Docker - Konteneryzacja

**Wejście**: `/data/posters.json`, `/data/generated/{id}.json`
**Wyjście**: Interfejs webowy (localhost:8080)

### 3. Dane (data/)
**Struktura**:
```
data/
├── posters.json          # Bazowe dane plakatów
└── generated/
    ├── poster_001.json   # Wyniki analizy
    ├── poster_002.json
    └── ...
```

## Przepływ danych

### 1. Inicjalizacja
```
1. Użytkownik uruchamia: cd model && docker compose up --build
2. vllm buduje i startuje (ładowanie modelu)
3. client czeka na vllm (health check)
```

### 2. Przetwarzanie (backend)
```
1. client.main():
   - load_posters() ← posters.json
   - for each poster:
     - load_image_from_url(imageUrl)
     - analyze_image(image) → vllm API
     - parse_llm_output() → struktura
     - llm_text_to_dict() → dict
     - save to generated/{id}.json
```

### 3. Prezentacja (frontend)
```
1. Użytkownik uruchamia: cd web && docker compose up
2. Frontend dostępny: http://localhost:8080
3. initIndex():
   - autoLoad() → fetch posters.json
   - renderGrid() → wyświetla listę
4. Użytkownik klika plakat
5. initPoster():
   - fetch generated/{id}.json (jeśli istnieje)
   - renderDetails() → wyświetla szczegóły
```

## Integracja komponentów

### API komunikacji
- **Backend → Frontend**: JSON pliki w `/data`
- **Frontend → Backend**: BRAK (read-only statyczne dane)
- **Client → vllm**: OpenAI API compatible (REST, JSON)

### Shared Storage
- **Volume**: `../data` zamontowany w obu kontenerach
- **Format**: JSON
- **Czytanie**: Frontend i user
- **Pisanie**: Backend (client)

## Technologiczny stack

| Warstwa | Technologia | Opis |
|---------|-------------|------|
| **Frontend** | HTML | Struktura |
| | CSS | Styling |
| | JavaScript | Logika |
| | Nginx | Serwer webowy |
| | Docker | Konteneryzacja |
| **Backend** | Python | Język |
| | PIL/numpy | Przetwarzanie obrazów |
| | openai-python | Komunikacja z LLM |
| | rdflib | RDF/Turtle export |
| | vllm | LLM inference |
| | PyTorch | Deep learning (w vllm) |
| | CUDA | GPU compute |
| | Docker | Konteneryzacja |
| **Dane** | JSON | Format danych |
| **Hosting** | Docker Compose | Orchestracja |

## Rozszerzalność

### Dodanie nowego LLM modelu
```bash
# .env
VLLM_MODEL=mistral/mistral-7b-instruct
# Automatycznie pobierze nowy model
```

### Zmiana promptu
```python
# loader.py - PROMPT stała
# Edytuj instrukcje dla modelu
# Wyniki będą w nowym formacie
```

### Dodanie nowych kategorii tagów
```python
# exporter.py - TAG_PROPERTY_MAP
# Dodaj nową kategorię
"Nowa Kategoria": EX.new_category,
```

### Nowe strony frontend
```html
# Web/new_page.html
# <script src="app.js"></script>
# Dodaj nową funkcję initPage()
```

## Performance considerations

### Backend
- GPU: Kluczowe dla szybkości analizy
- Batch processing: `--max-num-seqs=1` → można zwiększyć
- Memory: Depends on model size (7B/2B/etc.)

### Frontend
- Lazy loading: Nie implementowany (możliwość)
- Caching: Browser cache 7 dni dla statycznych
- Compression: gzip dla JSON-ów

### Storage
- `posters.json`: KB (metadane)
- `/generated/`: Zależy od liczby plakatów (KB per file)
- Obrazy: Domyślnie z URL-i (nie cachowane lokalnie)

## Deployment

### Local development
```bash
# Terminal 1 - Backend
cd model
docker compose up

# Terminal 2 - Frontend (gdy backend gotów)
cd web
docker compose up
```

### Production
- Backend: Kubernetes/Docker Swarm dla GPU nodes
- Frontend: Static hosting (S3, Netlify, etc.)
- Data: Shared volume / database
- Monitoring: Prometheus, Grafana

## Security considerations

- ✅ Frontend read-only do /data
- ⚠️ CORS disabled dla /data (allow all)
- ⚠️ Input validation: Minimal
- ⚠️ Authentication: Brak
- ⚠️ HTTPS: Nie skonfigurowane (localhost dev)

### Recommendations
1. Dodać authentication dla backendu
2. Restrictive CORS dla production
3. Input validation w exporter.py
4. HTTPS dla serwera webowego
5. Monitoring i logging dla production

## Monitoring i debugging

### Backend logs
```bash
docker compose logs -f client
docker compose logs -f vllm
```

### Frontend logs
```bash
# Browser DevTools (F12)
# Console tab
# Network tab (fetch requests)
```

### Data inspection
```bash
# Sprawdzić outputs
cat /data/generated/poster_001.json | jq .

# Sprawdzić inputs
cat /data/posters.json | jq '.items | length'
```

## Future improvements

1. **Caching**: Cache model results locally
2. **Batch processing**: Przetwarzanie równoległo
3. **Database**: PostgreSQL dla metadanych
4. **API**: Expose REST API dla backendu
5. **Authentication**: Secure access
6. **Monitoring**: Health checks, metrics
7. **Logging**: Centralized logging (ELK, etc.)
8. **Testing**: Unit tests, integration tests
