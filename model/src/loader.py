import json

import requests
import numpy as np
from PIL import Image
from io import BytesIO
from typing import List, Dict, Any, Generator

from PIL.ImageFile import ImageFile
from numpy import ndarray, dtype

PROMPT = {
    "type": "text",
    "text": (
        "Przekazuję poniżej dane źródłowe plakatu.\n"
        "Tytuł: {title}\n"
        "Data: {year}\n"
        "Opis: {description}\n"
        "Przeanalizuj plakat przekazany jako obraz i zwróć wynik w TRZECH częściach.\n\n"
        "1) WERSJA PROSTA:\n"
        "- 2–4 bardzo proste zdania w stylu easy-to-read, tak jak: "
        "'Plakat przedstawia żołnierza. Kolory są czerwone i czarne. Nastrój jest poważny.'\n\n"
        "2) WERSJA BADAWCZA:\n"
        "- Dłuższa analiza: styl, epoka, emocje, przekaz, symbolika, funkcja plakatu.\n\n"
        "3) ELEMENTY (TAGI):\n"
        "- Zwróć w formacie 'Klucz: wartość, wartość'.\n"
        "- Użyj poniższych kategorii dokładnie w tej formie:\n"
        "  Postacie: ...\n"
        "  Obiekty: ...\n"
        "  Kolory: ...\n"
        "  Nastrój: ...\n"
        "  Emocje: ...\n"
        "  Styl: ...\n"
        "  Funkcja: ...\n"
        "- Po dwukropku podaj wartości oddzielone przecinkami.\n"
        "- Jeśli czegoś nie ma, wpisz BRAK.\n"
        "Staraj się ograniczyć do najwyżej trzech wartości na jeden tag. "
        "Wypisz wartości w kolejności od najważniejszej. "
        "Nie podawaj wyjaśnień w nawiasach.\n"
        "Zwróć wynik jako zwykły tekst w kolejności:\n"
        "WERSJA PROSTA:\n"
        "WERSJA BADAWCZA:\n"
        "ELEMENTY (TAGI):\n"
    )
}


def load_image_from_url(url: str) -> ImageFile:
    resp = requests.get(url)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content)).convert("RGB")
    return img


def load_posters() -> Generator[dict, Any, None]:
    poster_sources = json.load(open("/data/posters.json"))['items']
    for p in poster_sources:
        print(f"Pobieram obraz: {p['id']} → {p['imageUrl']}")
        image_array = load_image_from_url(p["imageUrl"])
        metadata = {
                    "title": p.get("title", ""),
                    "description": p.get("description", ""),
                    "year": p.get("year", "")
                }
        prompt = PROMPT.copy()
        prompt['text'] = prompt['text'].format(**metadata)
        yield {
                "id": p["id"],
                "page_url": p["pageUrl"],
                "image_url": p["imageUrl"],
                "image_array": image_array,
                "metadata": metadata,
                "prompt": prompt,
            }



if __name__ == "__main__":
    posters = load_posters()
    print("\nWczytano plakaty:")
    for poster in posters:
        print("ID:", poster["id"])
        print("Strona:", poster["page_url"])
        print("Rozmiar obrazu (tablica):", poster["image_array"].shape)
        print("Tytuł:", poster["metadata"]["title"])
        print("Prompt (początek):", poster["prompt"]["text"][:50], "...")
        print("––––––––––––––––––––––")
