from llama_cpp import Llama
import re, os, functools

MODEL_PATH = os.getenv("LLAMA_MODEL", "./models/llama4-scout-q4_0.gguf")
llm = functools.lru_cache(maxsize=1)(lambda: Llama(model_path=MODEL_PATH, n_ctx=4096))()

PROMPT = "### Resumen fallo en <120 palabras y etiqueta resultado:\n"

def summarize_case(html: str) -> dict:
    # tiny html→texto
    texto = re.sub("<[^>]+>", " ", html)[:8000]
    out = llm(PROMPT + texto, max_tokens=200)
    return {"texto": texto[:160], "resumen": out["choices"][0]["text"]}
