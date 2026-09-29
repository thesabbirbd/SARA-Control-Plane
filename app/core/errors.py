from enum import Enum

class SARAError(Enum):
    PROCESS_TIMEOUT = ("PROCESS_TIMEOUT", "⏱ Process timed out.")
    PROCESS_EXIT_FAILURE = ("PROCESS_EXIT_FAILURE", "❌ Process exited with failure.")
    OLLAMA_TIMEOUT = ("OLLAMA_TIMEOUT", "⏱ Ollama took too long to respond.")
    OLLAMA_UNAVAILABLE = ("OLLAMA_UNAVAILABLE", "🔴 Ollama is not reachable.")
    INVALID_INTENT = ("INVALID_INTENT", "🤷 I could not understand that command.")
    UNKNOWN_PROJECT = ("UNKNOWN_PROJECT", "❌ That project does not exist.")
    DATABASE_ERROR = ("DATABASE_ERROR", "💾 Database error occurred.")
    ANTIGRAVITY_UNAVAILABLE = ("ANTIGRAVITY_UNAVAILABLE", "🔴 Antigravity CLI is missing.")
    CONFIG_ERROR = ("CONFIG_ERROR", "⚙️ Configuration error.")
    AUTH_ERROR = ("AUTH_ERROR", "🔒 Unauthorized.")

def get_error_message(err: SARAError) -> str:
    return err.value[1]
