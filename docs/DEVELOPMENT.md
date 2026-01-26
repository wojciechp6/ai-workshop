# Instrukcje dla Deweloperów

Poradnik dla osób chcących rozwijać, modyfikować i debugować projekt.

## Setup Development Environment

### 1. Klonuj i struktura
```bash
git clone <repo-url>
cd warsztaty-ai

# Struktura
tree -L 2
# warsztaty-ai/
# ├── docs/                 # Ta dokumentacja
# ├── data/
# │   ├── posters.json
# │   └── generated/       # Output backendu
# ├── model/               # Backend
# │   ├── src/
# │   │   ├── client.py
# │   │   ├── loader.py
# │   │   └── exporter.py
# │   └── docker-compose.yml
# └── web/                 # Frontend
#     ├── Web/
#     │   ├── app.js
#     │   ├── index.html
#     │   └── poster.html
#     └── docker-compose.yml
```

### 2. Python virtual env (opcjonalnie dla dev)
```bash
# Jeśli chcesz testować bez Dockera
cd model
python -m venv venv
source venv/bin/activate  # Linux/macOS
# lub
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Pre-commit hooks (opcjonalnie)
```bash
pip install pre-commit
pre-commit install

# W .pre-commit-config.yaml:
# - repos:
#   - repo: https://github.com/psf/black
#     rev: 23.0.0
#     hooks:
#     - id: black
#   - repo: https://github.com/PyCQA/flake8
#     rev: 6.0.0
#     hooks:
#     - id: flake8
```

## Struktura modułów

### loader.py - Analiza
```python
# Główne funkcje do poznania
PROMPT              # Instrukcja dla LLM
load_image_from_url()  # HTTP fetch
load_posters()      # Generator - main entry point
```

**Modyfikacje**:
- Zmiana `PROMPT` → inne instrukcje dla modelu
- Zmiana `load_image_from_url()` → inne źródła obrazów
- Zmiana `load_posters()` → inne API/formaty

**Testowanie**:
```bash
cd model/src
python loader.py

# Outputs:
# Pobieram obraz: poster_001 → https://...
# Wczytano plakaty:
# ID: poster_001
# ...
```

### client.py - Główna logika
```python
# Główne funkcje
numpy_to_base64()      # Konwersja obrazu
analyze_image()        # Wysyłanie do LLM
main()                 # Pętla przetwarzania
```

**Modyfikacje**:
- Zmiana `analyze_image()` → inne parametry LLM
- Zmiana `main()` → filtrowanie/walidacja
- Dodanie logowania, retry-u, itp.

**Testowanie bez Dockera**:
```bash
# Potrzeba vllm dostępnego
export VLLM_HOST=localhost
export VLLM_PORT=8000
export VLLM_MODEL=Qwen/Qwen2-VL-7B-Instruct
export OUT_PATH=/tmp/output

python client.py
```

### exporter.py - Przetwarzanie
```python
# Główne funkcje
parse_llm_output()     # Rozbijanie odpowiedzi
parse_tags()           # Parsing kategorii
llm_text_to_dict()     # Konwersja do JSON
llm_text_to_rdf_turtle() # Konwersja do RDF
```

**Modyfikacje**:
- Zmiana `PROMPT_PATTERN` → inny format odpowiedzi
- Dodanie nowych kategorii w `TAG_PROPERTY_MAP`
- Zmiana formatu wyjściowego

**Testowanie CLI**:
```bash
cd model/src

# Przygotuj example input (skopiuj z logów)
cat > /tmp/input.txt << EOF
WERSJA PROSTA:
Plakat pokazuje...

WERSJA BADAWCZA:
...

ELEMENTY (TAGI):
Postacie: ofiara, żołnierz
Obiekty: ciało, zbroja
...
EOF

# Test JSON
python exporter.py /tmp/input.txt /tmp/output.json poster_001

# Test RDF
python exporter.py /tmp/input.txt /tmp/output.ttl poster_001
```

## Modyfikacje Frontendu

### app.js - Główna logika
```javascript
// Części do poznania
const BASE_LIST_URL      // URL do posters.json
const GENERATED_DIR      // Ścieżka do generated/

renderTagsArray()        // Renderowanie zwykłych tagów
renderTagGroups()        // Renderowanie kategoryzowanych tagów
renderGrid()             // Renderowanie gridu
renderDetails()          // Renderowanie szczegółów

initIndex()              // Inicjalizacja index.html
initPoster()             // Inicjalizacja poster.html
```

**Modyfikacje**:
1. **Zmiana API**:
   ```javascript
   // Dodaj config.js z custom URL
   const BASE_LIST_URL = window.__API_URL__ || "/data/posters.json"
   ```

2. **Zmiana renderowania tagów**:
   ```javascript
   // W renderTagGroups - dodaj custom CSS classes
   return `<div class="tag-group ${key.toLowerCase()}">...`
   ```

3. **Dodanie filtrowania zaawansowanego**:
   ```javascript
   function advancedFilter(items) {
     return items.filter(p => {
       // Custom logic
       return true
     })
   }
   ```

4. **Zmiana layoutu**:
   ```javascript
   // W renderDetails - zmień HTML strukturę
   box.innerHTML = `<div class="new-layout">...</div>`
   ```

**Testowanie**:
```bash
cd web
docker compose up

# Otwórz http://localhost:8080
# F12 → Console
# Testuj funkcje:
# - qs('search')
# - renderTagsArray(['tag1', 'tag2'])
# - applySearch([...])
```

### style.css - Design

**Workflow**:
1. Edytuj style.css
2. F5 refresh w przeglądarce (lub ctrl+F5 hard refresh)
3. Zmiana widoczna od razu (nie trzeba rebuild)

**Responsive breakpoints** (dodaj jeśli brak):
```css
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .card { font-size: 0.9em; }
}
```

### nginx.conf - Routing

**Modyfikacje**:
```nginx
# SPA routing (404 → index.html)
location / {
  try_files $uri $uri/ /index.html;
}

# Cache control
location ~* \.(js|css)$ {
  expires 1d;
}
```

**Testowanie zmian**:
```bash
# Zaaplikuj zmiany
docker compose down
docker compose up --build

# Sprawdź
curl -i http://localhost:8080/poster.html
```

## Debugging

### Backend - Print debugging
```python
# client.py
print(f"Image shape: {image.size}")
print(f"Response: {response.choices[0].message.content[:100]}")

# Run
docker compose logs -f client | grep "Image shape"
```

### Backend - Logging properly
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing {poster['id']}")
logger.error(f"Failed to process: {e}")
```

### Frontend - DevTools
```javascript
// Console logging
console.log('Items loaded:', CURRENT_ITEMS);
console.table(applySearch(CURRENT_ITEMS));

// Breakpoints
debugger;  // W kodzie
// Lub kliknij w DevTools

// Network tab
// Sprawdzaj żądania i odpowiedzi
```

### Docker debugging
```bash
# Wejdź do kontenera
docker compose exec client bash
cd /app/src
python -i client.py  # Interactive mode

# Lub interaktywnie
python
>>> from loader import load_posters
>>> for p in load_posters():
...     print(p['id'])
```

## Testing

### Unit testy (sample)
```python
# model/src/test_exporter.py
import unittest
from exporter import parse_llm_output, parse_tags

class TestExporter(unittest.TestCase):
    def test_parse_llm_output(self):
        text = """WERSJA PROSTA:
Test simple

WERSJA BADAWCZA:
Test research

ELEMENTY (TAGI):
Postacie: a, b
"""
        simple, research, tags_raw = parse_llm_output(text)
        self.assertEqual(simple, "Test simple")
        self.assertIn("Postacie", tags_raw)

if __name__ == '__main__':
    unittest.main()
```

**Uruchomienie**:
```bash
python -m pytest model/src/test_*.py -v
```

### Frontend tests (sample)
```javascript
// web/Web/test.js
function testNormalize() {
  const result = normalize("  HELLO  ");
  console.assert(result === "hello", "normalize failed");
}

function testEscapeHtml() {
  const result = escapeHtml("<script>");
  console.assert(result === "&lt;script&gt;", "escapeHtml failed");
}

// Run w console
testNormalize();
testEscapeHtml();
console.log("All tests passed!");
```

## CI/CD Integration

### GitHub Actions workflow
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - run: pip install -r model/requirements.txt
      - run: python -m pytest model/src/ -v
```

## Performance Profiling

### Backend - timing
```python
import time

start = time.time()
analysis = analyze_image(prompt, image)
elapsed = time.time() - start
print(f"Analysis took {elapsed:.2f}s")
```

### Backend - memory
```bash
# Monitoruj zmianę GPU memory
watch -n 1 'nvidia-smi'

# Lub
docker stats client
```

### Frontend - performance
```javascript
// W DevTools
performance.mark('start-load');
fetch('/data/posters.json')
  .then(() => {
    performance.mark('end-load');
    performance.measure('load', 'start-load', 'end-load');
    console.log(performance.getEntriesByName('load')[0]);
  });
```

## Version Control Best Practices

### .gitignore
```
# Python
__pycache__/
*.pyc
venv/
.env
.pytest_cache/

# Node/Frontend
node_modules/
dist/
build/

# IDE
.vscode/
.idea/
*.swp

# Docker
.docker/
docker-compose.override.yml

# Data
/data/generated/
/data/*.cache
```

### Commit messages
```
# Format: <type>(<scope>): <subject>

feat(backend): dodaj support dla RDF export
fix(frontend): napraw CSS responsiveness
docs(readme): update instrukcje
test(loader): dodaj unit testy

# Describe co i dlaczego, nie jak
```

## Extending projektu

### Dodanie nowego modelu
1. Edytuj `model/src/loader.py` → zmień `PROMPT`
2. Edytuj `.env` → zmień `VLLM_MODEL`
3. Przebuduj: `docker compose up --build`

### Dodanie nowego formatu wyjścia
1. Edytuj `model/src/exporter.py` → dodaj funkcję `llm_text_to_xyz()`
2. Edytuj `client.py` → użyj nowej funkcji
3. Testuj

### Dodanie API backendu
1. Dodaj Flask/FastAPI do `requirements.txt`
2. Stwórz `model/src/api.py` z endpointami
3. Zmień `Dockerfile.client` → uruchom API zamiast client.py
4. Expose port w docker-compose.yml
5. Frontend fetch z API zamiast z JSON plików

### Integracja z bazą danych
1. Dodaj PostgreSQL do docker-compose.yml
2. Dodaj migracje (Alembic/SQLAlchemy)
3. Edytuj `exporter.py` → zapis do DB
4. Frontend fetch z API zamiast z plików

## Dokumentacja kodu

### Docstrings (Python)
```python
def analyze_image(prompt: dict, image: PIL.Image) -> str:
    """
    Analizuje obraz przy pomocy modelu LLM.
    
    Args:
        prompt: Słownik z type i text dla modelu
        image: Obraz PIL do analizy
        
    Returns:
        Surowy tekst odpowiedzi z modelu
        
    Raises:
        ConnectionError: Jeśli vllm niedostępny
        
    Example:
        >>> response = analyze_image(prompt, image)
        >>> print(response[:100])
    """
```

### Comments (JavaScript)
```javascript
/**
 * Renderuje gratkę plakatów
 * @param {Array} items - Lista plakatów
 * @returns {void}
 */
function renderGrid(items) {
  // Implementation
}
```

## Troubleshooting Development

### "Module not found" (Python)
```bash
# Upewnij się że jesteś w dobrym katalogu
cd model/src

# Lub dodaj do path
export PYTHONPATH=/home/user/warsztaty-ai/model/src:$PYTHONPATH
```

### "Port already in use"
```bash
# Frontend
lsof -i :8080
kill -9 <PID>

# Backend vllm
lsof -i :8000
```

### Docker image layers
```bash
# Sprawdź co zawiera image
docker image inspect vllm-openai:auto

# Rozmiar
docker image ls -a
```

### vllm slow loading
```bash
# Sprawdzuj CUDA
docker compose exec vllm nvidia-smi

# Czy model się downloaduje?
docker compose logs -f vllm | grep -i "download\|loading"
```

## Resources

- [Python style guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [JavaScript style (Airbnb)](https://github.com/airbnb/javascript)
- [Docker best practices](https://docs.docker.com/develop/dev-best-practices/)
- [vllm documentation](https://github.com/vllm-project/vllm)
- [nginx documentation](https://nginx.org/en/docs/)
