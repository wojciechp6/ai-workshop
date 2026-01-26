# Backend - Przetwarzanie i Analiza Plakatów

Backend odpowiada za:
- Pobieranie plakatów i ich obrazów
- Analiza obrazów za pomocą modelu sztucznej inteligencji
- Przetwarzanie wyników do formatów JSON i RDF

## Architektura

Backend składa się z dwóch serwisów Docker:
1. **vllm** - serwer modelu sztucznej inteligencji (LLM)
2. **client** - klient pobierający obrazy i wysyłający je do modelu

## Struktura katalogów

```
model/
├── src/                      # Kod źródłowy
│   ├── client.py            # Główny skrypt analizy
│   ├── loader.py            # Ładowanie plakatów i obrazów
│   └── exporter.py          # Konwersja wyników do JSON/RDF
├── docker-compose.yml        # Konfiguracja kontenerów
├── Dockerfile.client         # Obraz Docker dla klienta
├── Dockerfile.vllm           # Obraz Docker dla serwera LLM
├── requirements.txt          # Zależności Python
└── run.sh                    # Skrypt startowy
```

## Konfiguracja

### Zmienne środowiskowe

W pliku `.env` ustawić:
```
HUGGING_FACE_HUB_TOKEN=your_token
VLLM_MODEL=Qwen/Qwen2-VL-7B-Instruct  # Domyślny model
CUDA_VERSION=12.4.1                   # Wersja CUDA
TORCH_CUDA_TAG=12.4-runtime            # Tag PyTorch
```

### Docker Compose dla backendu

Konfiguracja w `docker-compose.yml`:
- **vllm** kontener: serwer modelu z obsługą GPU (NVIDIA)
  - Port: 8000 (OpenAI API compatible)
  - GPU Memory: 90% (konfigurowalny)
  - Max tokens: 2048
  - Bufor pamięci: 2GB
  
- **client** kontener: przetwarzanie plakatów
  - Czeka na dostępność serwera vllm
  - Pobiera obrazy z URL-i
  - Wysyła do modelu do analizy
  - Zapisuje wyniki do `/data/generated/`

## Szczegółowe opisy funkcji

### loader.py - Ładowanie danych

**Funkcja: `load_image_from_url(url: str) -> ImageFile`**
- Pobiera obraz z URL-a
- Konwertuje do formatu RGB
- Zwraca obiekt PIL Image

**Funkcja: `load_posters() -> Generator[dict]`**
- Ładuje listę plakatów z `/data/posters.json`
- Dla każdego plakatu:
  - Pobiera obraz
  - Przygotowuje metadane (tytuł, opis, rok)
  - Tworzy prompt z danymi
- Zwraca generator słowników z danymi plakatu

**Stała: `PROMPT`**
- Definiuje strukturę promptu dla modelu
- Określa trzy części odpowiedzi: prostą, badawczą i tagi
- Zawiera instrukcje formatowania odpowiedzi

### client.py - Główna logika analizy

**Funkcja: `numpy_to_base64(img, format="JPEG") -> str`**
- Konwertuje obraz (PIL Image) do base64
- Umożliwia wysłanie obrazu do API OpenAI

**Funkcja: `analyze_image(prompt, image) -> str`**
- Wysyła obraz i prompt do modelu vllm
- Komunikacja przez OpenAI API
- Zwraca surowy tekst odpowiedzi z analizą

**Funkcja: `main()`**
- Główna pętla przetwarzania:
  1. Ładuje plakaty przez `load_posters()`
  2. Dla każdego plakatu wywołuje `analyze_image()`
  3. Konwertuje wynik do słownika przez `llm_text_to_dict()`
  4. Zapisuje do JSON-a w `/data/generated/{id}.json`

### exporter.py - Przetwarzanie wyników

**Funkcja: `parse_llm_output(text: str) -> tuple`**
- Parsuje surową odpowiedź modelu
- Szuka trzech sekcji: WERSJA PROSTA, WERSJA BADAWCZA, ELEMENTY (TAGI)
- Zwraca tuple: (simple, research, tags_raw)

**Funkcja: `parse_tags(tags_raw: str) -> dict`**
- Parsuje sekcję ELEMENTY (TAGI)
- Rozbija linie wg kategorii (Postacie, Obiekty, Kolory itp.)
- Konwertuje wartości z ciągów na listy
- Zwraca słownik: `{kategoria: [wartości]}`

**Funkcja: `build_rdf(simple_text, research_text, tags, poster_uri) -> Graph`**
- Buduje graf RDF z danych analizy
- Tworzy zasoby z właściwościami:
  - `ex:simpleDescription` - opis prosty
  - `ex:researchDescription` - opis badawczy
  - `ex:characters`, `ex:objects`, `ex:colors` itp. - tagi kategoryzowane
- Zwraca `rdflib.Graph`

**Funkcja: `llm_text_to_dict(llm_text: str) -> dict`**
- Konwertuje surową odpowiedź LLM na słownik strukturyzowany
- Wywołuje `parse_llm_output()` i `parse_tags()`
- Zwraca:
  ```json
  {
    "simple_description": "...",
    "research_description": "...",
    "tags": {
      "Postacie": [...],
      "Obiekty": [...],
      ...
    }
  }
  ```

**Funkcja: `llm_text_to_rdf_turtle(llm_text, poster_id, base_uri) -> str`**
- Konwertuje do formatu RDF Turtle
- Przydatna dla semantic web aplikacji
- Zwraca tekst w formacie TTL

**Funkcja: `main()` (CLI)**
- Uruchamianie z linii komend:
  ```bash
  python exporter.py input.txt output.json
  python exporter.py input.txt output.ttl poster1
  ```
- Automatycznie wybiera format na podstawie rozszerzenia pliku

## Przepływ danych

```
posters.json
    ↓
load_posters() - ładuje obrazy z URL
    ↓
analyze_image() - wysyła do modelu
    ↓
parse_llm_output() - rozbija odpowiedź
    ↓
parse_tags() - strukturyzuje tagi
    ↓
llm_text_to_dict() - tworzy słownik
    ↓
Zapis do JSON: /data/generated/{id}.json
```

## Zależności

- **requests** - pobieranie obrazów z sieci
- **PIL (Pillow)** - przetwarzanie obrazów
- **numpy** - operacje na tablicach
- **openai** - komunikacja z API modelu
- **rdflib** - generowanie grafów RDF

## Uruchomienie

```bash
# Pełny proces z Docker Compose
docker compose up --build

# Lub ręczne uruchomienie
python src/client.py
```

## Dane wyjściowe

Dla każdego plakatu powstaje plik JSON w `/data/generated/{id}.json`:

```json
{
  "simple_description": "Krótki, prosty opis plakatu",
  "research_description": "Szczegółowa analiza naukowa",
  "tags": {
    "Postacie": ["ofiara", "żołnierz"],
    "Obiekty": ["ciało", "zbroja"],
    "Kolory": ["czerwony", "szary"],
    "Nastrój": ["grobowy"],
    "Emocje": ["strach", "żałoba"],
    "Styl": ["realizm", "propaganda"],
    "Funkcja": ["informacja", "manipulacja"]
  }
}
```

## Docker Compose - Konfiguracja szczegółowa

### Serwis vllm
- **Build**: Dockerfile.vllm z CUDA
- **Port**: 8000 (OpenAI API compatible)
- **GPU**: Wsparcie NVIDIA (rezerwacja wszystkich GPU)
- **Pamięć**: 2GB shared memory, 90% VRAM modelu
- **Volumy**: Cache Hugging Face, modele
- **Health check**: Co 10s sprawdzenie `/v1/models`

### Serwis client
- **Zależy od**: vllm (musi być healthy)
- **Build**: Dockerfile.client
- **Volumy**: Dostęp do `/data`
- **Zmienne**: Konfiguracja połączenia z vllm

## Troubleshooting

1. **CUDA/GPU error** - Sprawdzić NVIDIA Docker support: `docker run --rm --gpus all nvidia/cuda:12.4-runtime nvidia-smi`
2. **Timeout vllm** - Zwiększyć `start_period` w health check
3. **Brak pamięci** - Zmniejszyć `gpu-memory-utilization` w docker-compose.yml
