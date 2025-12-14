import re
import sys
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS


PROMPT_PATTERN = (
    r"WERSJA PROSTA:\s*(.*?)\s*"
    r"WERSJA BADAWCZA:\s*(.*?)\s*"
    r"ELEMENTY \(TAGI\):\s*(.*)"
)


def parse_llm_output(text: str):
    """
    Oczekuje tekstu w formacie:

    WERSJA PROSTA:
    ...
    WERSJA BADAWCZA:
    ...
    ELEMENTY (TAGI):
    ...

    Zwraca: (wersja_prosta, wersja_badawcza, tags_raw)
    """
    match = re.search(PROMPT_PATTERN, text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(
            "Nie udało się dopasować sekcji. "
            "Upewnij się, że odpowiedź ma nagłówki: "
            "'WERSJA PROSTA:', 'WERSJA BADAWCZA:', 'ELEMENTY (TAGI):'"
        )

    simple_part = match.group(1).strip()
    research_part = match.group(2).strip()
    tags_raw = match.group(3).strip()

    return simple_part, research_part, tags_raw


def parse_tags(tags_raw: str):
    """
    Parsuje sekcję ELEMENTY (TAGI), oczekując linii w formacie:

      Postacie: ...
      Obiekty: ...
      Kolory: ...
      Nastrój: ...
      Emocje: ...
      Styl: ...
      Funkcja: ...

    Zwraca słownik: {klucz: [lista_wartości]}
    """
    tags = {}
    for line in tags_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, values = line.split(":", 1)
        key = key.strip()
        value_list = [v.strip() for v in values.split(",") if v.strip()]
        tags[key] = value_list
    return tags


def build_rdf(simple_text: str,
              research_text: str,
              tags: dict,
              poster_uri: str) -> Graph:
    """
    Buduje graf RDF reprezentujący analizę plakatu.

    - simple_text -> ex:simpleDescription
    - research_text -> ex:researchDescription
    - tagi -> właściwości na obiekcie plakatu

    Zwraca rdflib.Graph
    """
    g = Graph()

    # Przykładowa własna przestrzeń nazw – możesz zmienić na swoją
    EX = Namespace("http://example.org/poster#")
    g.bind("ex", EX)
    g.bind("rdfs", RDFS)

    poster = URIRef(poster_uri)

    # Typ zasobu – dowolna klasa, np. ex:Poster
    g.add((poster, RDF.type, EX.Poster))

    # Opisy główne
    g.add((poster, EX.simpleDescription, Literal(simple_text, lang="pl")))
    g.add((poster, EX.researchDescription, Literal(research_text, lang="pl")))

    # Mapowanie polskich nazw kategorii na nazwy właściwości
    TAG_PROPERTY_MAP = {
        "Postacie": EX.characters,
        "Obiekty": EX.objects,
        "Kolory": EX.colors,
        "Nastrój": EX.mood,
        "Emocje": EX.emotions,
        "Styl": EX.style,
        "Funkcja": EX.function,
    }

    # Dodajemy tagi jako osobne literale
    for key, values in tags.items():
        prop = TAG_PROPERTY_MAP.get(key)
        if prop is None:
            # Jeśli pojawi się nowy klucz, tworzymy generyczną właściwość
            # np. ex:tag_PostacieNowe
            safe_key = re.sub(r"\W+", "_", key).strip("_")
            prop = EX[f"tag_{safe_key}"]

        for v in values:
            g.add((poster, prop, Literal(v, lang="pl")))

    return g


def llm_text_to_rdf_turtle(llm_text: str,
                           poster_id: str = "poster1",
                           base_uri: str = "http://example.org/poster/") -> str:
    """
    Przyjmuje surowy tekst z odpowiedzi LLM,
    zwraca RDF w formacie Turtle (str).
    """
    simple, research, tags_raw = parse_llm_output(llm_text)
    tags = parse_tags(tags_raw)

    poster_uri = base_uri.rstrip("/") + "/" + poster_id
    g = build_rdf(simple, research, tags, poster_uri)

    return g.serialize(format="turtle").decode("utf-8") \
        if isinstance(g.serialize(format="turtle"), bytes) \
        else g.serialize(format="turtle")


def main():
    """
    Użycie z linii komend:

    python llm_to_rdf.py input.txt output.ttl poster1
    """
    if len(sys.argv) < 3:
        print("Użycie: python llm_to_rdf.py input.txt output.ttl [poster_id]")
        sys.exit(1)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    poster_id = sys.argv[3] if len(sys.argv) > 3 else "poster1"

    llm_text = in_path.read_text(encoding="utf-8")
    ttl = llm_text_to_rdf_turtle(llm_text, poster_id=poster_id)

    out_path.write_text(ttl, encoding="utf-8")
    print(f"Zapisano RDF (Turtle) do: {out_path}")


if __name__ == "__main__":
    main()
