from typing import List, Dict, Any, Optional, Iterator
from openai import OpenAI
from utils.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL
from services.web_search import search_web, format_web_context

_client = OpenAI(api_key=OPENAI_API_KEY)

def answer_with_context_stream(
    question: str, 
    contexts: List[str], 
    use_web_search: bool = False
) -> Iterator[str]:
    """
    Stream answers using document context and optionally web search.
    Returns an iterator of text chunks.
    """
    doc_context = "\n\n---\n\n".join(contexts[:3])
    
    # Perform web search if enabled
    web_results = []
    web_context = ""
    if use_web_search:
        web_results = search_web(question, max_results=5)
        web_context = format_web_context(web_results)
    
    # Build system prompt based on mode
    if use_web_search and web_results:
        system = (
            "You are Dr.Doc, an AI assistant that helps users understand documents. "
            "You have access to both the uploaded document context and web search results. "
            "When answering:\n"
            "1. FIRST try to answer using the document context provided\n"
            "2. If the answer is not in the document, you may use web search results\n"
            "3. Always clearly indicate which source you used (Document or Web)\n"
            "4. If neither source has the answer, say 'I don't have enough information to answer this question.'\n"
            "5. Cite sources using [Doc] for document snippets and [Web] for web sources"
        )
        user = (
            f"=== Document Context ===\n{doc_context}\n\n"
            f"{web_context}\n\n"
            f"Question: {question}\n\n"
            "Provide a comprehensive answer using the available sources. "
            "Clearly indicate whether your answer comes from the document or web search."
        )
    else:
        system = (
            "You are Dr.Doc, an AI assistant that answers questions strictly using the provided document context. "
            "You MUST NOT use any information outside of the provided context. "
            "If the answer is not in the document context, respond with: "
            "'I don't have enough information in the document to answer this question. "
            "Please enable web search if you'd like me to search the internet for additional information.'"
        )
        user = (
            f"Document Context:\n{doc_context}\n\n"
            f"Question: {question}\n\n"
            "Answer the question using ONLY the document context provided above. "
            "Cite which snippets you used by numbering them (e.g., [1], [2]). "
            "If the answer is not in the context, say you don't know."
        )
    
    stream = _client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.2,
        stream=True,
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def answer_with_context(
    question: str, 
    contexts: List[str], 
    use_web_search: bool = False
) -> Dict[str, Any]:
    """
    Answer questions using document context and optionally web search.
    
    Args:
        question: The user's question
        contexts: List of document context chunks
        use_web_search: Whether to enable web search for additional context
    
    Returns:
        Dictionary with answer and source information
    """
    doc_context = "\n\n---\n\n".join(contexts[:3])
    
    # Perform web search if enabled
    web_results = []
    web_context = ""
    if use_web_search:
        web_results = search_web(question, max_results=5)
        web_context = format_web_context(web_results)
    
    # Build system prompt based on mode
    if use_web_search and web_results:
        system = (
            "You are Dr.Doc, an AI assistant that helps users understand documents. "
            "You have access to both the uploaded document context and web search results. "
            "When answering:\n"
            "1. FIRST try to answer using the document context provided\n"
            "2. If the answer is not in the document, you may use web search results\n"
            "3. Always clearly indicate which source you used (Document or Web)\n"
            "4. If neither source has the answer, say 'I don't have enough information to answer this question.'\n"
            "5. Cite sources using [Doc] for document snippets and [Web] for web sources"
        )
        user = (
            f"=== Document Context ===\n{doc_context}\n\n"
            f"{web_context}\n\n"
            f"Question: {question}\n\n"
            "Provide a comprehensive answer using the available sources. "
            "Clearly indicate whether your answer comes from the document or web search."
        )
    else:
        system = (
            "You are Dr.Doc, an AI assistant that answers questions strictly using the provided document context. "
            "You MUST NOT use any information outside of the provided context. "
            "If the answer is not in the document context, respond with: "
            "'I don't have enough information in the document to answer this question. "
            "Please enable web search if you'd like me to search the internet for additional information.'"
        )
        user = (
            f"Document Context:\n{doc_context}\n\n"
            f"Question: {question}\n\n"
            "Answer the question using ONLY the document context provided above. "
            "Cite which snippets you used by numbering them (e.g., [1], [2]). "
            "If the answer is not in the context, say you don't know."
        )
    
    resp = _client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.2,
    )
    content = resp.choices[0].message.content or ""
    
    return {
        "answer": content.strip(),
        "sources": {
            "document": len(contexts) > 0,
            "web": use_web_search and len(web_results) > 0,
            "web_results": web_results[:3] if web_results else []
        }
    }
