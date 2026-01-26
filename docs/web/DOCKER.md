# Docker Compose - Frontend (Web)

Szczegółowa dokumentacja konfiguracji Docker dla frontendu.

## Przegląd

Frontend wykorzystuje jeden kontener Docker:
- **frontend** - Serwer webowy Nginx z aplikacją

## Konfiguracja frontend

### Obraz i build

```yaml
build: .
```

- Budowany z `Dockerfile` w bieżącym katalogu
- Bazuje na Alpine Nginx (lekki obraz ~40MB)

### Networking i porty

```yaml
ports:
  - "8080:80"
```

- **Port 8080** (host) → **Port 80** (kontener)
- Dostępy przez `http://localhost:8080`

### Volumy

```yaml
volumes:
  - ../data:/usr/share/nginx/html/data:ro
```

- Montuje `/data` z gałęzi głównej projektu
- Dostęp jako `/data` wewnątrz kontenera
- `:ro` = read-only (brak ryzyka modyfikacji z kontenera)

## Dockerfile

```dockerfile
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY Web ./
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

| Linia | Opis |
|-------|------|
| `FROM nginx:alpine` | Alpine Linux + Nginx (~40MB) |
| `WORKDIR ...` | Web root Nginx |
| `COPY Web ./` | Aplikacja do web root |
| `COPY nginx.conf ...` | Custom konfiguracja Nginx |

## nginx.conf

Typowa konfiguracja:

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache dla statycznych zasobów
    location ~* \.(js|css|png|jpg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # Data directory (JSON files)
    location /data/ {
        alias /usr/share/nginx/html/data/;
        add_header Access-Control-Allow-Origin "*";
        types {
            application/json json;
        }
    }

    # GZIP compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

### Kluczowe opcje

| Opcja | Opis |
|-------|------|
| `try_files $uri $uri/ /index.html` | SPA routing (404 → index.html) |
| `expires 7d` | Cache na 7 dni |
| `gzip on` | Kompresja odpowiedzi |
| `add_header CORS` | Obsługa CORS dla /data |

## Uruchamianie

```bash
# Build i start
docker compose up --build

# Tylko start
docker compose up

# Background
docker compose up -d

# Logi
docker compose logs -f frontend

# Stop
docker compose down

# Rebuild (bez cache)
docker compose build --no-cache frontend
```

## Workflow uruchomienia

1. **Dockerfile build**
   - Pobierz Alpine Nginx
   - Skopiuj aplikację (Web/)
   - Skopiuj konfigurację Nginx

2. **Container start**
   - Nginx słucha na porcie 80
   - Mount `/data` z hosta

3. **User access**
   - Otwórz `http://localhost:8080`
   - Nginx serwuje index.html
   - JavaScript ładuje `/data/posters.json`

4. **Data flow**
   ```
   localhost:8080 (przeglądar)
        ↓
   Nginx (port 80 w kontenerze)
        ↓
   index.html + app.js
        ↓
   fetch(/data/posters.json)
        ↓
   /usr/share/nginx/html/data/posters.json
        ↓
   ../data/posters.json (z hosta)
   ```

## Optimizacje

### Zmniejszenie rozmiaru obrazu

```dockerfile
# Remove nginx logs
RUN touch /var/log/nginx/access.log && \
    ln -sf /dev/null /var/log/nginx/access.log

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf
```

### Multi-stage build (dla przyszłych zmian)

```dockerfile
FROM node:18 AS builder
WORKDIR /build
COPY Web .
# RUN npm run build  # Jeśli będzie transpilacja

FROM nginx:alpine
COPY --from=builder /build /usr/share/nginx/html
```

### Performance tuning

```nginx
# W nginx.conf:
http {
    # Zwiększ buffer dla dużych odpowiedzi
    client_max_body_size 50M;
    
    # Timeouts
    client_body_timeout 10s;
    client_header_timeout 10s;
    keepalive_timeout 65s;
    send_timeout 10s;

    # Worker processes
    worker_processes auto;
    worker_connections 1024;
}
```

## Troubleshooting

### Blank white page
```bash
# Sprawdzić console (F12) → Network
# Szukać 404 na posters.json

# Sprawdzić volume mount
docker compose exec frontend ls -la /usr/share/nginx/html/data/
```

### Port 8080 już zajęty
```bash
# Zmienić port w docker-compose.yml
ports:
  - "8081:80"  # Zamiast 8080

# Lub znaleźć i zabić proces
lsof -i :8080
kill -9 <PID>
```

### Brak plików JSON
```bash
# Sprawdzić strukturę
tree ../data/

# Lub list
docker compose exec frontend ls -la /usr/share/nginx/html/data/
```

### CORS error (cross-origin)
```nginx
# Dodać do nginx.conf pod location /data/:
add_header Access-Control-Allow-Origin "*";
add_header Access-Control-Allow-Methods "GET, OPTIONS";
add_header Access-Control-Allow-Headers "Content-Type";
```

### Nginx 502 Bad Gateway
```bash
# Sprawdzić logi
docker compose logs frontend

# Restart
docker compose down
docker compose up --build
```

## Obsługa zmian

### Zmiana plików statycznych (HTML, CSS, JS)
```bash
# Zmiana automatycznie widoczna (nie trzeba rebuild)
# Może trzeba F5 refresh w przeglądarce (ctrl+F5 hard refresh)
```

### Zmiana nginx.conf
```bash
# Trzeba rebuild
docker compose down
docker compose up --build

# Lub reload bez przerwy
docker compose exec frontend nginx -s reload
```

### Dodanie nowych bibliotek JavaScript
```bash
# Edytuj app.js
# Dodaj <script> tag w HTML
# Reload w przeglądarce
```

## Security

### HTTPS (dla produkcji)
```yaml
# Dodać certyfikat SSL
volumes:
  - ./certs:/etc/nginx/certs:ro

# W nginx.conf:
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;
}
```

### Restrictive CORS
```nginx
# Zamiast "*" - specyficzny host
add_header Access-Control-Allow-Origin "http://localhost:8080";
```

### Disable directory listing
```nginx
location / {
    autoindex off;  # Default: off
}
```

## Monitoring

### Logi
```bash
# Real-time
docker compose logs -f frontend

# Ostatnie 100 linii
docker compose logs --tail 100 frontend

# Grep
docker compose logs frontend | grep error
```

### Stats
```bash
# CPU, RAM, Network
docker stats frontend

# Detail
docker inspect frontend
```

### Health check (manualna)
```bash
# Sprawdzić czy serwer odpowiada
curl -i http://localhost:8080

# Sprawdzić wewnątrz kontenera
docker compose exec frontend curl -i http://localhost/index.html
```
