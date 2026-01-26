# Format Danych i Struktura JSON

Szczegółowy opis struktury danych używanych w projekcie.

## Plik źródłowy: posters.json

### Lokalizacja
```
/data/posters.json
```

### Struktura
```json
{
  "items": [
    {
      "id": "poster_001",
      "title": "Katyn",
      "year": "1944",
      "description": "Plakat przedstawia scenę z zabójstw...",
      "imageUrl": "https://example.com/images/katyn.jpg",
      "pageUrl": "https://example.com/poster/katyn",
      "tags": ["propaganda", "WWII", "historia"]
    },
    ...
  ]
}
```

### Pola

| Pole | Typ | Opis | Przykład |
|------|-----|------|---------|
| `id` | string | Unikatowy identyfikator plakatu | "poster_001" |
| `title` | string | Tytuł plakatu | "Katyn" |
| `year` | string/number | Rok powstania | "1944" |
| `description` | string | Wstępny opis (opcjonalny) | "Opis..." |
| `imageUrl` | string | URL do obrazu (HTTP/HTTPS) | "https://..." |
| `pageUrl` | string | URL do źródła w internecie | "https://..." |
| `tags` | array[string] | Tagi bazowe (opcjonalne) | ["propaganda"] |

### Walidacja

**Wymagane pola**:
- `id` - musi być unikatowe
- `imageUrl` - musi być dostępnym URL-em
- `title` - nie może być puste

**Opcjonalne pola**:
- `description`
- `tags`
- `pageUrl`
- `year`

### Przykład kompletny

```json
{
  "items": [
    {
      "id": "poster_001",
      "title": "Katyn",
      "year": 1944,
      "description": "Niemiecki plakat propagandowy z czasów II wojny",
      "imageUrl": "https://example.com/katyn.jpg",
      "pageUrl": "https://historia.org/katyn",
      "tags": ["propaganda", "WWII"]
    },
    {
      "id": "poster_002",
      "title": "Armia Krajowa",
      "year": 1943,
      "description": "Plakat AK",
      "imageUrl": "https://example.com/ak.jpg",
      "pageUrl": "https://historia.org/ak",
      "tags": ["AK", "underground"]
    }
  ]
}
```

## Plik wyników analizy: generated/{id}.json

### Lokalizacja
```
/data/generated/poster_001.json
/data/generated/poster_002.json
...
```

### Struktura
```json
{
  "simple_description": "Krótki, prosty opis plakatu w 2-4 zdaniach",
  "research_description": "Szczegółowa analiza naukowa z kontekstem historycznym",
  "tags": {
    "Postacie": ["ofiara", "żołnierz", "mężczyzna"],
    "Obiekty": ["ciało", "zbroja", "drzewa"],
    "Kolory": ["czerwony", "szary", "brązowy"],
    "Nastrój": ["grobowy", "ponury"],
    "Emocje": ["strach", "żałoba", "obrzydzenie"],
    "Styl": ["realizm", "propaganda", "ekspresjonizm"],
    "Funkcja": ["informacja", "propaganda", "manipulacja"]
  }
}
```

### Pola

#### simple_description (string)
- **Opis**: Bardzo prosty, laicki opis plakatu
- **Długość**: 2-4 zdania
- **Styl**: "Plakat przedstawia X. Kolory to Y. Nastrój jest Z."
- **Język**: Polski
- **Rola**: Dla użytkowników niezaznajomionych z tematem

#### research_description (string)
- **Opis**: Naukowa, szczegółowa analiza
- **Długość**: 4-10 zdań
- **Zawartość**:
  - Styl i epoka
  - Emocje i psychologia
  - Symbolika i przekaz
  - Funkcja (propaganda, informacja, etc.)
- **Język**: Polski
- **Rola**: Dla badaczy i studentów

#### tags (object)
- **Typ**: Słownik (kategorii → lista wartości)
- **Kategorie** (zawsze te same):

| Kategoria | Opis | Przykłady |
|-----------|------|----------|
| `Postacie` | Typy osób na plakacie | "żołnierz", "ofiara", "dzieci" |
| `Obiekty` | Obiekty/rzeczy widoczne | "broń", "martwice", "flaga" |
| `Kolory` | Dominujące kolory | "czerwony", "czarny", "biały" |
| `Nastrój` | Ogólne uczucie | "grobowy", "zwycięski", "straszny" |
| `Emocje` | Wyzwolane emocje | "strach", "duma", "żałoba" |
| `Styl` | Styl artystyczny | "realizm", "ekspresjonizm", "propaganda" |
| `Funkcja` | Cel plakatu | "propaganda", "informacja", "manipulacja" |

- **Format wartości**:
  - Max 3 wartości na kategorię
  - Sorted od najważniejszej do najmniej ważnej
  - Bez dodatkowych wyjaśnień w nawiasach
  - Jeśli kategoria niezbędna: "BRAK"

### Przykład pełny

```json
{
  "simple_description": "Plakat przedstawia scenę z zabójstw. Użyto tekstu \"Katyn\" w dużej czcionce. Na obrazku widoczne są ludzie i ciała. Plakat ma poważny ton.",
  "research_description": "Plakat niemieckich władz okupacyjnych z 1944 roku jest propagandowym materiałem mającym na celu zmanipulowanie opinii publicznej i ukrycie winy w sprawie katastrofy w Katyniu. Wykorzystuje on obraz zmasakrowanych żołnierzy, aby stworzyć wrażenie ofiar radzieckiej agresji, a jednocześnie oskarżyć Związek Radziecki o odpowiedzialność za zabójstwo.",
  "tags": {
    "Postacie": ["ofiara", "żołnierz", "mężczyzna"],
    "Obiekty": ["ciało", "zbroja", "drzewa"],
    "Kolory": ["czerwony", "szary", "brązowy"],
    "Nastrój": ["grobowy", "ponury"],
    "Emocje": ["strach", "żałoba", "obrzydzenie"],
    "Styl": ["realizm", "propaganda", "ekspresjonizm"],
    "Funkcja": ["informacja", "propaganda", "manipulacja"]
  }
}
```

## Przekształcenia danych

### loader.py → client.py → exporter.py

```
1. posters.json (ładowanie)
   └─ load_posters() generator
      ├─ id: str
      ├─ image_url: str
      ├─ image_array: PIL Image
      ├─ metadata: dict{title, description, year}
      ├─ page_url: str
      └─ prompt: dict{type, text}

2. analyze_image() → surowy tekst LLM

3. parse_llm_output() → rozbicie
   ├─ simple: str
   ├─ research: str
   └─ tags_raw: str

4. parse_tags() → struktura
   └─ dict{categoria: [wartości]}

5. llm_text_to_dict() → JSON gotowy
   └─ /data/generated/{id}.json
```

## Frontend - transformacja dla UI

### Wczytanie danych
```javascript
// index.html
fetch('/data/posters.json')
  → items: array

// poster.html
fetch('/data/generated/poster_001.json')
  → {simple_description, research_description, tags}
```

### Renderowanie

**Tagi bazowe** (z posters.json):
```javascript
renderTagsArray(base.tags)
→ <span class="tag">propaganda</span>
  <span class="tag">WWII</span>
```

**Tagi kategoryzowane** (z generated/{id}.json):
```javascript
renderTagGroups(gen.tags)
→ <div class="tag-group">
    <div class="tag-group-title">Postacie</div>
    <span>ofiara</span>
    <span>żołnierz</span>
  </div>
```

## Ekspport alternatywny: RDF/Turtle

### Funkcja llm_text_to_rdf_turtle()

```turtle
@prefix ex: <http://example.org/poster#> .

<http://example.org/poster/poster_001>
    a ex:Poster ;
    ex:simpleDescription "Plakat przedstawia..."@pl ;
    ex:researchDescription "Plakat niemieckich..."@pl ;
    ex:characters "ofiara"@pl, "żołnierz"@pl ;
    ex:objects "ciało"@pl, "zbroja"@pl ;
    ex:colors "czerwony"@pl, "szary"@pl ;
    ex:mood "grobowy"@pl ;
    ex:emotions "strach"@pl, "żałoba"@pl ;
    ex:style "realizm"@pl, "propaganda"@pl ;
    ex:function "propaganda"@pl .
```

### Użycie
```bash
python exporter.py input.txt output.ttl poster_001
```

## Schemat walidacji

### posters.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "title", "imageUrl"],
        "properties": {
          "id": {"type": "string", "pattern": "^poster_[0-9]{3}$"},
          "title": {"type": "string", "minLength": 1},
          "year": {"oneOf": [{"type": "string"}, {"type": "number"}]},
          "description": {"type": "string"},
          "imageUrl": {"type": "string", "format": "uri"},
          "pageUrl": {"type": "string", "format": "uri"},
          "tags": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

### generated/{id}.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["simple_description", "research_description", "tags"],
  "properties": {
    "simple_description": {
      "type": "string",
      "minLength": 20
    },
    "research_description": {
      "type": "string",
      "minLength": 50
    },
    "tags": {
      "type": "object",
      "properties": {
        "Postacie": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "Obiekty": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "Kolory": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "Nastrój": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "Emocje": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "Styl": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "Funkcja": {"type": "array", "items": {"type": "string"}, "maxItems": 3}
      }
    }
  }
}
```

## Wspólne błędy

### posters.json

❌ **Zła struktura**:
```json
{
  "items": "not an array"
}
```
✅ **Poprawnie**:
```json
{
  "items": [...]
}
```

❌ **Brakujący obraz**:
```json
{
  "id": "poster_001",
  "imageUrl": "https://invalid-url.com/404.jpg"
}
```
✅ **Poprawnie**:
- Sprawdzić czy URL faktycznie istnieje
- Testować: `curl -I https://url.jpg`

❌ **Duplikowane ID**:
```json
"items": [
  {"id": "poster_001", ...},
  {"id": "poster_001", ...}
]
```
✅ **Poprawnie**:
- Każde `id` musi być unikatowe

### generated/{id}.json

❌ **Puste tagi**:
```json
{
  "tags": {
    "Postacie": [],
    "Obiekty": []
  }
}
```
✅ **Poprawnie** (jeśli brak):
```json
{
  "tags": {
    "Postacie": ["BRAK"]
  }
}
```

❌ **Za wiele wartości**:
```json
{
  "Postacie": ["a", "b", "c", "d", "e"]
}
```
✅ **Poprawnie** (max 3):
```json
{
  "Postacie": ["a", "b", "c"]
}
```

## Conversion tools

### Python - czytanie
```python
import json

# Posters
with open('/data/posters.json') as f:
    data = json.load(f)
    for poster in data['items']:
        print(poster['id'], poster['title'])

# Generated
with open('/data/generated/poster_001.json') as f:
    analysis = json.load(f)
    print(analysis['simple_description'])
    for category, values in analysis['tags'].items():
        print(f"{category}: {values}")
```

### jq - command line
```bash
# Liczba plakatów
jq '.items | length' /data/posters.json

# Wszystkie ID-ki
jq '.items[].id' /data/posters.json

# Wyciągnij tagi z plakatu
jq '.tags.Postacie' /data/generated/poster_001.json

# Połącz tagi z dwóch źródeł
jq -s '
  [ .[] | 
    {
      id: .id,
      base_tags: .tags,
      ai_categories: input.tags
    }
  ]
' /data/posters.json /data/generated/poster_001.json
```

### SQL (jeśli konwertujesz na bazę danych)
```sql
-- Posters table
CREATE TABLE posters (
  id VARCHAR(20) PRIMARY KEY,
  title VARCHAR(255),
  year INT,
  description TEXT,
  image_url VARCHAR(500),
  page_url VARCHAR(500)
);

-- Tags (normalizacja)
CREATE TABLE tags (
  id INT PRIMARY KEY,
  poster_id VARCHAR(20) REFERENCES posters(id),
  category VARCHAR(50),
  value VARCHAR(100)
);

-- Analysis results
CREATE TABLE analysis (
  poster_id VARCHAR(20) PRIMARY KEY REFERENCES posters(id),
  simple_description TEXT,
  research_description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```
