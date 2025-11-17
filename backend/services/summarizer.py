from openai import OpenAI
from utils.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text: str, max_words: int = 200, expanded: bool = False) -> str:
    """
    Summarize text with optional expanded mode for more detailed summaries.
    
    Args:
        text: Text to summarize
        max_words: Maximum words for the summary (default 200, expanded uses 800)
        expanded: If True, generate a more detailed, in-depth summary
    """
    if expanded:
        max_words = 800  # Much more detailed for expanded summaries
        prompt = (
            "Provide a comprehensive, in-depth summary of the following document. "
            "Include:\n"
            "- A detailed abstract covering the main themes and purpose\n"
            "- Key concepts and ideas explained thoroughly\n"
            "- Important details, examples, and supporting information\n"
            "- Major sections or topics with explanations\n"
            "- Conclusions and implications\n\n"
            f"Aim for approximately {max_words} words. Be thorough and detailed while remaining accurate to the source material.\n\n"
            f"--- DOCUMENT ---\n{text[:20000]}\n"  # Use more text for expanded summaries
        )
        system_message = "You are a thorough and detailed technical summarizer who provides comprehensive overviews."
    else:
        prompt = (
            "Summarize the following document in bullet points and a short abstract. "
            f"Keep total under ~{max_words} words. Be faithful to the text.\n\n"
            f"--- DOCUMENT ---\n{text[:12000]}\n"
        )
        system_message = "You are a concise technical summarizer."
    
    resp = _client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    content = resp.choices[0].message.content or ""
    return content.strip()
