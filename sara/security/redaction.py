import re

SECRET_PATTERNS = [
    # Telegram tokens
    (r"\b[0-9]{8,10}:[a-zA-Z0-9_-]{35}\b", "[REDACTED_TELEGRAM_TOKEN]"),
    # General Bearer tokens
    (r"Bearer\s+[a-zA-Z0-9_\-\.]+", "Bearer [REDACTED_TOKEN]"),
    # Basic Auth
    (r"Basic\s+[a-zA-Z0-9+/=]+", "Basic [REDACTED_AUTH]"),
    # OpenAI/Anthropic/Gemini keys (generic AI key pattern)
    (r"(?:sk-[a-zA-Z0-9]{48}|AIza[0-9A-Za-z\-_]{35})", "[REDACTED_API_KEY]"),
    # Passwords in URLs
    (r"(://[^:]+:)([^@]+)(@)", r"\1[REDACTED_PASSWORD]\3")
]

def redact(text: str) -> str:
    """Redact sensitive information from text suitable for logs or UI."""
    if not text:
        return text
    
    redacted_text = text
    for pattern, replacement in SECRET_PATTERNS:
        redacted_text = re.sub(pattern, replacement, redacted_text)
        
    return redacted_text
