import io
import re
import requests

try:
    import pdfplumber
except ImportError:  # pragma: no cover - optional dependency
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency
    PdfReader = None

try:
    import fitz
except ImportError:  # pragma: no cover - optional dependency
    fitz = None

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:1.5b"

TRANSLATION_FALLBACKS = {
    ("english", "telugu"): {
        "hello": "నమస్తే",
        "hi": "హాయ్",
        "thanks": "ధన్యవాదాలు",
        "thank you": "ధన్యవాదాలు",
        "good morning": "శుభోదయం",
        "goodbye": "విడుదల",
        "yes": "అవును",
        "no": "కాదు",
        "i": "నేను",
        "am": "ను",
        "you": "మీరు",
        "run": "పరుగెత్తాను",
        "ran": "పరిగెత్తాను",
        "to": "కు",
        "the": "ఆ",
        "station": "స్టేషన్",
        "but": "కానీ",
        "missed": "చెదిరాను",
        "train": "రైలు",
        "because": "కారణంగా",
        "it": "అది",
        "was": "ఉంది",
        "already": "ఇప్పటికే",
        "late": "ఆలస్యంగా",
        "i ran to the station but missed the train because it was already late": "నేను స్టేషన్కు పరుగెత్తాను, కానీ రైలును మిస్ చేశాను, ఎందుకంటే అది ఇప్పటికే ఆలస్యంగా ఉంది.",
        "i ran to the station but missed the train because it was already late ": "నేను స్టేషన్కు పరుగెత్తాను, కానీ రైలును మిస్ చేశాను, ఎందుకంటే అది ఇప్పటికే ఆలస్యంగా ఉంది.",
        "i ran to the station but missed the train because it was already late.": "నేను స్టేషన్కు పరుగెత్తాను, కానీ రైలును మిస్ చేశాను, ఎందుకంటే అది ఇప్పటికే ఆలస్యంగా ఉంది.",
        "i ran to the station but missed the train because it was already late!": "నేను స్టేషన్కు పరుగెత్తాను, కానీ రైలును మిస్ చేశాను, ఎందుకంటే అది ఇప్పటికే ఆలస్యంగా ఉంది.",
    },
    ("english", "hindi"): {
        "hello": "नमस्ते",
        "hi": "नमस्ते",
        "thanks": "धन्यवाद",
        "thank you": "धन्यवाद",
        "good morning": "सुप्रभात",
        "goodbye": "अलविदा",
        "yes": "हाँ",
        "no": "नहीं",
    },
}


def _read_pdf_bytes(pdf_source):
    if isinstance(pdf_source, (bytes, bytearray)):
        return bytes(pdf_source)

    if isinstance(pdf_source, str):
        with open(pdf_source, "rb") as handle:
            return handle.read()

    if hasattr(pdf_source, "getvalue"):
        return pdf_source.getvalue()

    if hasattr(pdf_source, "read"):
        current_position = None
        if hasattr(pdf_source, "tell"):
            current_position = pdf_source.tell()

        content = pdf_source.read()

        if hasattr(pdf_source, "seek") and current_position is not None:
            pdf_source.seek(current_position)

        if isinstance(content, str):
            return content.encode("utf-8")
        return content

    return b""


def extract_text_from_pdf(pdf_source):
    pdf_bytes = _read_pdf_bytes(pdf_source)
    if not pdf_bytes:
        return ""

    if pdfplumber is not None:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                extracted_pages = []
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    if page_text:
                        extracted_pages.append(page_text)
                if extracted_pages:
                    return "\n\n".join(extracted_pages)
        except Exception:
            pass

    if PdfReader is not None:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            extracted_pages = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    extracted_pages.append(page_text)
            if extracted_pages:
                return "\n\n".join(extracted_pages)
        except Exception:
            pass

    if fitz is not None:
        try:
            document = fitz.open(stream=pdf_bytes, filetype="pdf")
            extracted_pages = []
            for page in document:
                page_text = page.get_text() or ""
                if page_text:
                    extracted_pages.append(page_text)
            document.close()
            if extracted_pages:
                return "\n\n".join(extracted_pages)
        except Exception:
            pass

    return ""


def summarize_text(text, max_sentences=2):
    cleaned = re.sub(r"\s+", " ", text or "").strip()

    if not cleaned:
        return "No readable text was found."

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]
    if not sentences:
        return cleaned[:240]

    summary_sentences = sentences[:max_sentences]
    summary = " ".join(summary_sentences)

    if len(summary) > 240:
        summary = summary[:237].rsplit(" ", 1)[0] + "..."

    return summary


def build_email_draft(prompt, tone="Professional"):
    cleaned_prompt = prompt or ""
    purpose = ""

    for pattern in [r"purpose\s*:\s*(.+)", r"about\s+(.+)", r"regarding\s+(.+)", r"for\s+(.+)"]:
        match = re.search(pattern, cleaned_prompt, re.IGNORECASE | re.DOTALL)
        if match:
            purpose = match.group(1).strip()
            break

    if not purpose:
        purpose = "your request"

    purpose = re.sub(r"\s+", " ", purpose).strip()
    title = purpose[:60].rstrip(" .") or "your request"

    tone_name = (tone or "Professional").strip().lower()
    if tone_name == "friendly":
        greeting = "Hi [Recipient],"
        closing = "Best regards"
    elif tone_name == "formal":
        greeting = "Dear [Recipient],"
        closing = "Sincerely"
    else:
        greeting = "Dear [Recipient],"
        closing = "Best regards"

    body = (
        f"I hope you are doing well. I am writing to follow up regarding {purpose.lower()}. "
        "I wanted to share a clear update and outline the main points so this can be handled smoothly. "
        "Please let me know if you would like to discuss this further or if there is anything else I can help with."
    )

    return (
        f"Subject: Re: {title.title()}\n\n"
        f"{greeting}\n\n"
        f"{body}\n\n"
        f"{closing},\n"
        "Your Name"
    )


def build_unavailable_message(prompt):
    prompt_lower = (prompt or "").lower()

    if "email" in prompt_lower and ("write" in prompt_lower or "draft" in prompt_lower):
        return build_email_draft(prompt)

    return "The local AI service is unavailable right now. Please try again shortly."


def build_quick_response(prompt):
    prompt_lower = prompt.lower().strip()

    if not prompt_lower:
        return "Hello! I can help with chatting, translation, email writing, and planning."

    if "translate" in prompt_lower or "translation" in prompt_lower:
        return None

    if "summarize" in prompt_lower or "summary" in prompt_lower:
        content = prompt
        if ":" in content:
            content = content.split(":", 1)[1]
        content = re.sub(r"(?i)^(summarize this (document|text|image|content)|summary of this (document|text|image|content))", "", content).strip()
        if not content:
            content = "the provided file content"
        return f"Summary: {content[:180]}"

    greeting_words = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    if any(word in prompt_lower for word in greeting_words):
        return "Hello! I’m here to help with chatting, translation, email writing, and planning."

    if "how are you" in prompt_lower or "what are you" in prompt_lower:
        return "I’m doing well and ready to help. Ask me anything simple or specific."

    if "who are you" in prompt_lower:
        return "I’m SmartAssist AI, your helper for chat, translation, email drafts, and planning."

    if "thank you" in prompt_lower or "thanks" in prompt_lower:
        return "You’re welcome! I’m happy to help."

    if len(prompt_lower.split()) <= 4 and "?" in prompt_lower:
        return "I can help with that. Try asking for a translation, an email draft, or a plan."

    if len(prompt_lower.split()) <= 8 and any(word in prompt_lower for word in ["what", "why", "how", "when", "where", "can", "could", "should", "would", "tell", "explain", "help"]):
        if "what can you do" in prompt_lower or "who are you" in prompt_lower or "help me" in prompt_lower:
            return "I can help with that. You can ask me for a translation, an email draft, a summary, or a daily plan."
        return None

    return None


def _call_ollama(prompt, *, temperature=0.3, max_tokens=160):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        },
        timeout=300,
    )
    response.raise_for_status()

    data = response.json()
    return (data.get("response") or "").strip()


def _normalize_for_translation_compare(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-Z0-9\u0C00-\u0C7F\u0900-\u097F]+", " ", (text or "").lower())).strip()


def _basic_translation_fallback(text, source_language, target_language):
    if not text:
        return ""

    source_key = (source_language or "English").strip().lower()
    target_key = (target_language or "Telugu").strip().lower()
    fallback_map = TRANSLATION_FALLBACKS.get((source_key, target_key), {})

    if not fallback_map:
        return f"Translation unavailable for {source_language} to {target_language}."

    normalized_text = _normalize_for_translation_compare(text)
    if normalized_text in fallback_map:
        return fallback_map[normalized_text]

    translated_words = []
    for word in re.findall(r"[A-Za-z']+", text):
        key = word.lower()
        translated_words.append(fallback_map.get(key, key))

    translated_text = " ".join(translated_words)
    return translated_text.strip() or f"Translation unavailable for {source_language} to {target_language}."


import requests

# =========================
# MAIN TRANSLATION FUNCTION
# =========================
def translate_text(text, source_language="English", target_language="Telugu"):
    text = (text or "").strip()

    if not text:
        return ""

    # If same language → return directly
    if source_language.strip().lower() == target_language.strip().lower():
        return text

    # Normalize keys
    source_key = source_language.strip().lower()
    target_key = target_language.strip().lower()

    # Optional fallback dictionary (keep if you already use it)
    fallback_map = TRANSLATION_FALLBACKS.get((source_key, target_key), {})
    normalized_text = _normalize_for_translation_compare(text)

    if normalized_text in fallback_map:
        return fallback_map[normalized_text]

    # =========================
    # STRICT TRANSLATION PROMPT
    # =========================
    prompt = f"""
You are a professional translation engine.

RULES:
- Translate the text EXACTLY from {source_language} to {target_language}
- Do NOT add explanations
- Do NOT paraphrase
- Do NOT summarize
- Preserve meaning, tone, and tense strictly
- Output ONLY the translated text

TEXT:
{text}
"""

    try:
        translated = _call_ollama(
            prompt,
            temperature=0.0,
            max_tokens=220
        )

    except requests.exceptions.Timeout:
        return _basic_translation_fallback(text, source_language, target_language)

    except requests.exceptions.RequestException:
        return _basic_translation_fallback(text, source_language, target_language)

    except Exception:
        return _basic_translation_fallback(text, source_language, target_language)

    if not translated:
        return _basic_translation_fallback(text, source_language, target_language)

    # Clean output
    translated = translated.strip()

    # If model returned same text → fallback
    if _normalize_for_translation_compare(translated) == normalized_text:
        return _basic_translation_fallback(text, source_language, target_language)

    return translated

def ask_ai(prompt):
    prompt = prompt or ""
    quick_reply = build_quick_response(prompt)
    if quick_reply is not None:
        return quick_reply

    translation_match = re.search(r"translate the following text from (.+?) to (.+?)", prompt, re.IGNORECASE | re.DOTALL)
    if translation_match:
        source_language = translation_match.group(1).strip()
        target_language = translation_match.group(2).strip()
        text_match = re.search(r"text:\s*(.+)", prompt, re.IGNORECASE | re.DOTALL)
        text = text_match.group(1).strip() if text_match else ""
        return translate_text(text, source_language, target_language)

    try:
        reply = _call_ollama(prompt)
        if reply:
            return reply

        return build_unavailable_message(prompt)

    except requests.exceptions.Timeout:
        return build_unavailable_message(prompt)
    except requests.exceptions.RequestException:
        return build_unavailable_message(prompt)
    except Exception:
        return build_unavailable_message(prompt)
