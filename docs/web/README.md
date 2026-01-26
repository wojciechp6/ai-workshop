# Frontend - Interfejs Użytkownika

Frontend odpowiada za prezentację plakatów i ich analiz użytkownikowi. Jest to aplikacja webowa oparta na HTML, CSS i JavaScript, uruchamiana w kontenerze Nginx.

## Architektura

Frontend jest aplikacją single-page bez backendu (poza statycznymi plikami). Dane są ładowane bezpośrednio z plików JSON:
- Główna lista plakatów: `/data/posters.json`
- Analiza dla każdego plakatu: `/data/generated/{id}.json`

## Struktura katalogów

```
web/
├── Web/                     # Aplikacja frontendowa
│   ├── index.html          # Strona główna (lista plakatów)
│   ├── poster.html         # Strona szczegółów plakatu
│   ├── app.js              # Logika aplikacji
│   ├── style.css           # Style CSS
│   └── config.js           # Konfiguracja (tworzona)
├── docker-compose.yml       # Konfiguracja Docker
├── Dockerfile              # Obraz Docker
├── nginx.conf              # Konfiguracja serwera Nginx
└── entrypoint.sh           # Skrypt startowy
```

## Szczegółowe opisy funkcji

### app.js - Logika aplikacji

#### Funkcje pomocnicze

**`qs(id) -> Element`**
- Skrót do `document.getElementById()`
- Pobiera element z DOM-u

**`normalize(s) -> string`**
- Konwertuje do lowercase
- Usuwa spacje
- Przygotowuje do wyszukiwania

**`getParam(name) -> string`**
- Pobiera parametr z URL-a
- Używane do identyfikacji plakatu

**`escapeHtml(str) -> string`**
- Bezpieczne wyświetlanie tekstu
- Escape'uje znaki: `&`, `<`, `>`, `"`, `'`
- Chroni przed XSS

**`stripMarkdown(s) -> string`**
- Usuwa formatowanie markdown
- Usuwa: `**`, `__`, backtick, `*`

#### Rendering tagów

**`renderTagsArray(tags: Array) -> string`**
- Renderuje tagi jako prostą listę (`<span class="tag">`)
- Używane dla tagów bazowych z `posters.json`
- Filtruje puste wartości

Przykład: `["propaganda", "wojna"]` → `<span>propaganda</span><span>wojny</span>`

**`renderTagGroups(tagsObj: Object) -> string`**
- Renderuje tagi z kategoryzacją
- Struktura: `{Postacie: [...], Obiekty: [...], ...}`
- Każda kategoria w osobnym div
- Puste kategorie pokazuje jako "—"
- Używane dla wyników z `/data/generated/{id}.json`

#### Wyszukiwanie

**`applySearch(items: Array) -> Array`**
- Filtruje plakaty wg. aktywnego zapytania
- Przeszukuje: tytuł, opis, tagi
- Case-insensitive

#### Lista plakatów (Grid)

**`renderGrid(items: Array) -> void`**
- Renderuje główną siatkę plakatów
- Dla każdego plakatu:
  - Obraz (thumbnail)
  - Tytuł
  - Rok
  - Tagi (jeśli są)
  - Click → przejście do `poster.html?id={id}`
- Obsługuje puste stany (brak danych)

#### Odświeżanie

**`refreshList() -> void`**
- Re-renderuje listę po zmianach
- Zapisuje dane do `localStorage` ("posters_items")
- Uwzględnia aktywne wyszukiwanie

#### Auto-load listy

**`autoLoad() -> Promise`**
- Async pobieranie `/data/posters.json`
- Try-catch obsługa błędów
- Ustawia `CURRENT_ITEMS`
- Wywołuje `refreshList()`

#### Inicjalizacja strony głównej

**`initIndex() -> void`**
- Uruchamiany na `index.html`
- Setup event listenerów:
  - Search input → `ACTIVE_QUERY`
  - Reset button → czyszczenie
- Calls `autoLoad()`

#### Renderowanie szczegółów plakatu

**`renderDetails(base, gen) -> void`**
- Wyświetla pełne informacje o plakacie
- Parame:
  - `base`: dane z `posters.json` (tytuł, opis, URL)
  - `gen`: wyniki analizy z `/data/generated/{id}.json`
- Renderuje:
  - Obraz
  - Tytuł i rok
  - Opis prosty (jeśli dostępny z analizy)
  - Tagi bazowe
  - Tagi z kategoryzacją (elementy analizy)
  - Opis badawczy
  - Link do źródła

#### Inicjalizacja strony plakatu

**`initPoster() -> Promise`**
- Uruchamiany na `poster.html`
- Pobiera `id` z URL-a
- Ładuje dane z `localStorage` (zapisane z index.html)
- Ładuje `/data/generated/{id}.json` (jeśli istnieje)
- Calls `renderDetails()`

#### Auto-start

```javascript
if (qs("grid")) initIndex();      // Strona główna
if (qs("details")) initPoster();  // Strona plakatu
```

### HTML struktury

**index.html** - Lista plakatów
```html
<header>
  <h1>Plakaty</h1>
  <input id="search">
  <button id="reset">Reset</button>
</header>
<main id="grid"></main>  <!-- Grid plakatów -->
```

**poster.html** - Szczegóły plakatu
```html
<a href="index.html">← Wróć</a>
<div id="details"></div>  <!-- Szczegóły -->
```

### CSS struktury (style.css)

Definiuje style dla:
- `.grid` - układ siatki plakatów
- `.card` - pojedynczy plakat w siatce
- `.details` - strona szczegółów
- `.tag`, `.tag-group` - tagów
- `.topbar` - nagłówka
- Responsive design

## Docker Compose dla frontendu

```yaml
services:
  frontend:
    build: .                        # Dockerfile
    ports:
      - "8080:80"                   # Nginx na porcie 8080
    volumes:
      - ../data:/usr/share/nginx/html/data:ro
```

- **Build**: Alpine Nginx
- **Port**: 8080 (host) → 80 (kontener)
- **Volume**: `/data` dostępne jako `/data` (read-only)
- **Web root**: `/usr/share/nginx/html`

## Dockerfile

```dockerfile
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY Web ./
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

- Bazowy obraz: Nginx Alpine (lekki)
- Kopiowalnie aplikacji do `Web/`
- Konfiguracja Nginx z `nginx.conf`

## nginx.conf

Konfiguracja serwera webowego:
- Hosting plików statycznych z `/usr/share/nginx/html`
- SPA routing (index.html dla nieznanych ścieżek)
- CORS headers dla dostępu do `/data`
- Caching dla statycznych zasobów

## Przepływ danych w UI

```
1. Użytkownik otwiera localhost:8080
   ↓
2. initIndex() ładuje /data/posters.json
   ↓
3. renderGrid() wyświetla listę
   ↓
4. Kliknięcie na plakat → poster.html?id=poster_001
   ↓
5. initPoster() ładuje /data/generated/poster_001.json
   ↓
6. renderDetails() wyświetla szczegóły
```

## Struktura danych

### posters.json (bazowe dane)
```json
{
  "items": [
    {
      "id": "poster_001",
      "title": "Katyn",
      "year": "1944",
      "description": "Plakat niemieckich władz...",
      "imageUrl": "https://example.com/image.jpg",
      "pageUrl": "https://example.com/poster",
      "tags": ["propaganda", "WWII"]
    }
  ]
}
```

### /data/generated/{id}.json (wyniki analizy)
```json
{
  "simple_description": "Prosty opis",
  "research_description": "Analiza naukowa",
  "tags": {
    "Postacie": ["ofiara", "żołnierz"],
    "Obiekty": ["ciało"],
    "Kolory": ["czerwony"],
    "Nastrój": ["ponury"],
    "Emocje": ["strach"],
    "Styl": ["realizm"],
    "Funkcja": ["propaganda"]
  }
}
```

## Uruchomienie

```bash
# W katalogu web/
docker compose up

# Następnie otwórz:
# http://localhost:8080
```

## Obsługiwane funkcjonalności

- ✅ Lista plakatów w siatce
- ✅ Wyszukiwanie (tytuł, opis, tagi)
- ✅ Strona szczegółów plakatu
- ✅ Wyświetlanie analiz (gdy dostępne)
- ✅ Kategoryzowane tagi
- ✅ Responsywny design
- ✅ Obsługa brakujących danych

## Troubleshooting

1. **Blank strona** - Sprawdzić console (F12) pod kątem błędów CORS
2. **Brak tagów** - Sprawdzić czy pliki w `/data/generated/` istnieją
3. **Brak obrazów** - Sprawdzić czy `/data` volume jest prawidłowo zmapowany
4. **Slow loading** - Optimize obrazy w `posters.json`
