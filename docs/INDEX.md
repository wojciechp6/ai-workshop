# Índeks Dokumentacji
Pełny spis treści dokumentacji projektu analizy plakatów.
## 📑 Spis dokumentów
### 🚀 Szybki Start
- **[QUICKSTART.md](./QUICKSTART.md)** - Instrukcja szybkiego startu dla nowych użytkowników
  - Wymagania systemowe
  - Instalacja krok po kroku
  - Uruchamianie backendu i frontendu
  - Rozwiązywanie problemów
  - Performance tipy
### 📋 Przegląd Projektu
- **[README.md](./README.md)** - Główny wstęp do projektu (ZACZNIJ TUTAJ!)
  - Cel projektu i architektura
  - Szybki start (5 minut)
  - Komponenty (backend, frontend, data)
  - Przykład output JSON
### 🏗️ Architektura
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Przegląd architekektury systemu
  - Diagram przepływu danych
  - Komponenty (backend, frontend, dane)
  - Przepływ danych
  - Techniczny stack
  - Rozszerzalność
  - Performance considerations
  - Deployment
  - Security
  - Monitoring
### 📊 Format Danych
- **[DATA_FORMAT.md](./DATA_FORMAT.md)** - Szczegółowy opis struktury danych
  - Format `posters.json` (dane wejściowe)
  - Format `/data/generated/{id}.json` (wyniki analizy)
  - Transformacje danych między komponentami
  - Ekspport alternatywny (RDF/Turtle)
  - Schematy walidacji JSON
  - Wspólne błędy
  - Conversion tools
  - SQL schema
## 📂 Backend (Model)
### Dokumentacja Kodu
- **[models/README.md](./models/README.md)** - Kompletna dokumentacja backendu
  - Architektura systemu
  - Struktura katalogów
  - Konfiguracja (zmienne środowiskowe)
  - **loader.py** - Ładowanie danych
    - `load_image_from_url()` - Pobieranie obrazów
    - `load_posters()` - Generator plakatów
    - Stała `PROMPT` - Instrukcja dla modelu
  - **client.py** - Główna logika analizy
    - `numpy_to_base64()` - Konwersja obrazu
    - `analyze_image()` - Wysyłanie do modelu
    - `main()` - Pętla przetwarzania
  - **exporter.py** - Przetwarzanie wyników
    - `parse_llm_output()` - Rozbijanie odpowiedzi
    - `parse_tags()` - Parsing kategorii
    - `llm_text_to_dict()` - Konwersja do JSON
    - `llm_text_to_rdf_turtle()` - Konwersja do RDF
    - `build_rdf()` - Budowanie grafu RDF
  - Przepływ danych (pipeline)
  - Zależności Python
  - Docker Compose overview
  - Troubleshooting
### Docker Compose Backend
- **[models/DOCKER.md](./models/DOCKER.md)** - Szczegółowa konfiguracja Docker backendu
  - Przegląd architekury (vllm + client)
  - **Serwis vllm**
    - Build i image
    - Networking i porty
    - GPU support
    - Pamięć (IPC, shared memory)
    - Volumy (cache, modele)
    - Zmienne środowiskowe
    - Command (opcje uruchomienia)
    - Health check
  - **Serwis client**
    - Build
    - Zależności (depends_on)
    - Zmienne środowiskowe
    - Volumy
  - Zmienne .env
  - Uruchamianie (docker compose commands)
  - Workflow uruchomienia
  - Optimization tipy
  - Troubleshooting
## 🌐 Frontend (Web)
### Dokumentacja Kodu
- **[web/README.md](./web/README.md)** - Kompletna dokumentacja frontendu
  - Architektura
  - Struktura katalogów
  - **app.js** - Logika aplikacji
    - Funkcje pomocnicze
    - Rendering tagów
    - Wyszukiwanie
    - Grid/Lista plakatów
    - Strona szczegółów
    - Auto-load
  - **HTML struktury**
    - index.html - lista plakatów
    - poster.html - szczegóły plakatu
  - **CSS struktury** (style.css)
  - Docker Compose overview
  - Przepływ danych w UI
  - Struktura danych wejściowych
  - Troubleshooting
### Docker Compose Frontend
- **[web/DOCKER.md](./web/DOCKER.md)** - Szczegółowa konfiguracja Docker frontendu
  - Obraz i build
  - Networking i porty
  - Volumy
  - **Dockerfile** - Obraz Docker
  - **nginx.conf** - Konfiguracja serwera
    - SPA routing
    - Caching
    - GZIP compression
    - CORS headers
  - Uruchamianie
  - Workflow uruchomienia
  - Optimizacje
  - Multi-stage build
  - Performance tuning
  - Troubleshooting
  - Obsługa zmian (hot reload)
  - Security
  - Monitoring
## 👨‍💻 Dla Deweloperów
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Instrukcje dla deweloperów
  - Setup development environment
  - Struktura modułów
    - loader.py - modyfikacje i testowanie
    - client.py - modyfikacje i testowanie
    - exporter.py - modyfikacje i testowanie
  - Modyfikacje frontendu
    - app.js - logika
    - style.css - design
    - nginx.conf - routing
  - Debugging
    - Backend (print, logging)
    - Frontend (DevTools)
    - Docker debugging
  - Testing (unit testy, frontend tests)
  - CI/CD integration (GitHub Actions)
  - Performance profiling
  - Version control best practices
  - Extending projektu
    - Dodanie nowego modelu
    - Nowy format wyjścia
    - API backend
    - Integracja z bazą danych
  - Dokumentacja kodu (docstrings, comments)
  - Troubleshooting development
  - Resources
## 🔍 Quick Links
**Wszystkie informacje, FAQ, mapy czytania i troubleshooting znajdują się w [README.md](./README.md) - to jest punkt wejścia do całej dokumentacji!**
Szukasz konkretnego tematu? Użyj **Ctrl+F** aby znaleźć go w tym pliku.
## 📝 O tym indeksie
Ten plik zawiera **pełny spis wszystkich dokumentów** z ich szczegółową zawartością.  
Każdy dokument jest opisany razem z listą najważniejszych sekcji.
---
**Ostatnia aktualizacja**: 2026-01-26  
**Wersja dokumentacji**: 1.0  
**Punkt wejścia**: [README.md](./README.md)
