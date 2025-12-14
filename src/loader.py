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
    poster_sources = [
        {
            "id": "poster_001",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/666375",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630677",
            "title": "Katyn",
            "year": "1944",
            "description": "Plakat niemieckich władz okupacyjnych"
        },
        {
            "id": "poster_002",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/563689",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630758",
            "title": "Wolność bolszewicka : polski plakat z 1920 roku",
            "year": "[1944]",
            "description": "Plakat powstał w czasie wojny polsko-bolszewickiej w 1920 r., wykorzystany w latach okupacji przez propagandę niemiecką"
        },
        {
            "id": "poster_003",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/555517",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630720",
            "title": "Dostaw na czas i jak najwięcej!",
            "year": "[1944]",
            "description": "-"
        },
        {
            "id": "poster_004",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/681105",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/686254",
            "title": "Warsaw 1939 1944",
            "year": "1944",
            "description": "-"
        },
        {
            "id": "poster_005",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/563522",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630719",
            "title": "Bolszewizm grozi! Stawaj do pracy!",
            "year": "1944",
            "description": "-"
        },
        {
            "id": "poster_006",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/555525",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630722",
            "title": "Piramida sowiecka",
            "year": "1944",
            "description": "Brak dolnej połowy plakatu"
        },
        {
            "id": "poster_007",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/555516",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630721",
            "title": "Oswobodziciel",
            "year": "1944",
            "description": "-"
        },
        {
            "id": "poster_008",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/563503",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630718",
            "title": "Bandy bolszewickie zagrażają Tobie i Twemu mieniu! Dlatego o osobach podejrzanych winieneś zawiadomić policję",
            "year": "1944",
            "description": "Plakat powstał w czasie wojny polsko-bolszewickiej w 1920 r., wykorzystany w latach okupacji przez propagandę niemiecką"
        },
        {
            "id": "poster_009",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/564214",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630733",
            "title": "Krwawe fale bolszewizmu",
            "year": "1944",
            "description": "-"
        },
        {
            "id": "poster_010",
            "page_url": "https://jbc.bj.uj.edu.pl/publication/564219",
            "image_url": "https://jbc.bj.uj.edu.pl/image/edition/thumbnail:result_item/630713",
            "title": "Katyń przestroga Europy!",
            "year": "ca 1943",
            "description": "Antysowiecki plakat propagandowy"
        },
        {
            "id": "poster_011",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/bf2b905f53b3be44f3db?width=474&height=600",
            "title": "Bolszewizm grozi! Stawaj do pracy!",
            "year": "1944",
            "description": "Tylko dolna połowa plakatu;plakat"
        },
        {
            "id": "poster_012",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/47f741526c19658b19fc?width=474&height=600",
            "title": "Katyń przestroga Europy!",
            "year": "1943",
            "description": "Antysowiecki plakat propagandowy;plakat"
        },
        {
            "id": "poster_013",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/2ab2d5a8e157f7104eab?width=474&height=600",
            "title": "Lublin-Poland-Polen-Pologne",
            "year": "1930",
            "description": "rotografia barwna, kolor niebieski"
        },
        {
            "id": "poster_014",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/712c6d1da55cdfccd326?width=474&height=600",
            "title": "[Plakat] : [Inc.:] Marmur s.z.o.o. w Kielcach ulica 3go Maja 28 [...].",
            "year": "0192",
            "description": "na plakacie podpis IB."
        },
        {
            "id": "poster_015",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/712c6d1da55cdfccd326?width=474&height=600",
            "title": "[Plakat] : [Inc.:] Anglio - Twoje dzieło! [...].",
            "year": "0194",
            "description": "-"
        },
        {
            "id": "poster_016",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/748249e11b9a31d12d4e?width=474&height=600",
            "title": "Jesteśmy dumą i nadzieją Polski Ludowej",
            "year": "1951.01.01 - ...",
            "description": "Fot. plakatu.;Sygn. piecz. na rew.;fotografia polska;odbitka na papierze srebrowo-żelatynowym"
        },
        {
            "id": "poster_017",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/8cc11c33571c02a987e9?width=474&height=600",
            "title": "Robotnicy pomagają chłopom dzielić ziemię",
            "year": "1951.01.01 - ...",
            "description": "Fot. plakatu.;Sygn. piecz. na rew.;fotografia polska;odbitka na papierze srebrowo-żelatynowym"
        },
        {
            "id": "poster_018",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/f1c3ecc2e1e2696fad46?width=474&height=600",
            "title": "Podpisanie umowy kontraktacyjnej",
            "year": "1951.01.01 - ...",
            "description": "Fot. plakatu.;Sygn. piecz. na rew.;fotografia polska;odbitka na papierze srebrowo-żelatynowym"
        },
        {
            "id": "poster_019",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/2917bcdae4235b858770?width=474&height=600",
            "title": "W spółdzielni produkcyjnej kobieta ma więcej czasu na zajęcie się własnym gospodarstwem domowym",
            "year": "1951.01.01 - ...",
            "description": "Fot. plakatu.;Sygn. piecz. na rew.;fotografia polska;odbitka na papierze srebrowo-żelatynowym"
        },
        {
            "id": "poster_020",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/d8165c1d5cf54997bcf4?width=474&height=600",
            "title": "Nasze pokolenie wcieli w życie marzenia wielu pokoleń rewolucjonistów polskich. Buduje Polskę socjalistyczną",
            "year": "1951.01.01 - ...",
            "description": "Fot. plakatu.;Sygn. piecz. na rew.;fotografia polska;odbitka na papierze srebrowo-żelatynowym"
        },
        {
            "id": "poster_021",
            "page_url": "-",
            "image_url": "https://thumbnail-provider-fbc-test.apps.dcw1.paas.psnc.pl/thumbnails/47fcaf4d16abe6913665?width=474&height=600",
            "title": "[Plakat] : Sieg um jeden Preis!",
            "year": "1942",
            "description": "Rok wydania z pieczątki eo."
        },

    ]


    for p in poster_sources:
        print(f"Pobieram obraz: {p['id']} → {p['image_url']}")
        image_array = load_image_from_url(p["image_url"])
        metadata = {
                    "title": p.get("title", ""),
                    "description": p.get("description", ""),
                    "year": p.get("year", "")
                }
        prompt = PROMPT.copy()
        prompt['text'] = prompt['text'].format(**metadata)
        yield    {
                "id": p["id"],
                "page_url": p["page_url"],
                "image_url": p["image_url"],
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
