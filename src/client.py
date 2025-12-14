import base64
import io
import os
from pathlib import Path

from openai import OpenAI

from loader import load_posters, PROMPT
from exporter import llm_text_to_rdf_turtle

client = OpenAI(base_url=f"http://{os.getenv('VLLM_HOST','vllm')}:{os.getenv('VLLM_PORT','8000')}/v1", api_key="")

def numpy_to_base64(img, format="JPEG") -> str:
    """
    Konwertuje numpy array (H, W, C) do base64 dla OpenAI.
    """
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return b64


def analyze_image(prompt, image) -> str:
    image_b64 = numpy_to_base64(image)

    response = client.chat.completions.create(
        model=os.getenv("VLLM_MODEL"),
        messages=[
            {
                "role": "user",
                "content": [
                    prompt,
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content


def main():
    posters = load_posters()
    for poster in posters:
        analysis = analyze_image(poster['prompt'], poster['image_array'])
        ttl = llm_text_to_rdf_turtle(analysis, poster['id'], poster['page_url'])
        out = Path(os.getenv('OUT_PATH','out')) / f"{poster['id']}.ttl"
        out.write_text(ttl, encoding="utf-8")



if __name__ == "__main__":
    main()