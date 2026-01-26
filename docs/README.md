# Dokumentacja Projektu - Analiza Plakatów Historycznych

Projekt umożliwia automatyczną analizę plakatów historycznych za pomocą modelu sztucznej inteligencji. System składa się z dwóch głównych komponentów: **backendu** (przetwarzania danych i analizy AI) oraz **frontendu** (interfejsu użytkownika).

## 🎯 Cel Projektu

Automatyczne analizowanie plakatów historycznych przy użyciu modelu wizji LLM (Qwen2-VL), generowanie opisów w trzech wariantach:
- Wersja prosta (dla użytkowników)
- Wersja badawcza (dla naukowców)
- Kategoryzowane elementy/tagi

## 🚀 Szybki Start (5 minut)

### Wymagania
- Docker Desktop z NVIDIA GPU support
- Token Hugging Face (https://huggingface.co/settings/tokens)
- 8GB+ VRAM GPU 

### Generowanie danych
```bash
cd model
echo "HUGGING_FACE_HUB_TOKEN=your_token" > .env
bash run.sh
# Czekaj aż proces się zakończy
```

### Frontend
```bash
cd web
docker compose up
# Otwórz: http://localhost:8080
```

Szczegółowe instrukcje: **[QUICKSTART.md](./QUICKSTART.md)**

## 🏗️ Architektura Systemu

```
posters.json
    ↓
[BACKEND - model/]
  ├─ loader.py      → Pobieranie obrazów z URL
  ├─ client.py      → Wysyłanie do modelu LLM (vllm)
  └─ exporter.py    → Konwersja do JSON
    ↓
/data/generated/{id}.json
    ↓
[FRONTEND - web/]
  ├─ index.html     → Lista plakatów (grid)
  ├─ poster.html    → Szczegóły plakatu
  └─ app.js         → Logika UI
    ↓
http://localhost:8080
```

## 📦 Komponenty Projektu

### Backend (model/)
- **loader.py** - Ładowanie plakatów, pobieranie obrazów z URL
- **client.py** - Główna pętla: pobierz → wyślij do LLM → zapisz wynik
- **exporter.py** - Przetwarzanie: konwersja tekstem LLM → JSON/RDF
- **Docker**: vllm serwer (GPU) + client aplikacja (Python)

### Frontend (web/)
- **app.js** - Ładowanie JSON-ów, rendering UI, wyszukiwanie, filtrowanie
- **index.html** - Strona główna (grid plakatów)
- **poster.html** - Strona szczegółów plakatu
- **style.css** - Responsive design
- **Docker**: Nginx Alpine (serwer statyczny)

### Data
- **Wejście**: `/data/posters.json` - metadata plakatów + URL obrazów
- **Wyjście**: `/data/generated/{id}.json` - wyniki analizy

## 📊 Co Otrzymujesz?

Po analizie każdego plakatu otrzymujesz JSON z:

```json
{
  "simple_description": "Krótki, prosty opis w 2-4 zdaniach",
  "research_description": "Szczegółowa analiza naukowa",
  "tags": {
    "Postacie": ["ofiara", "żołnierz"],
    "Obiekty": ["ciało", "zbroja"],
    "Kolory": ["czerwony", "szary"],
    "Nastrój": ["grobowy"],
    "Emocje": ["strach", "żałoba"],
    "Styl": ["realizm", "propaganda"],
    "Funkcja": ["informacja", "propaganda"]
  }
}
```