from openai import OpenAI
from utils.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text: str, max_words: int = 200) -> str:
    prompt = (
        "Summarize the following document in bullet points and a short abstract. "
        f"Keep total under ~{max_words} words. Be faithful to the text.\n\n"
        f"--- DOCUMENT ---\n{text[:12000]}\n"
    )
    resp = _client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise technical summarizer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    content = resp.choices[0].message.content or ""
    return content.strip()
