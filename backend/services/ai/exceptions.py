class AIException(Exception):
    """Base exception for AI Services."""
    pass

class RateLimitException(AIException):
    """Raised when the AI Provider hits a 429 (Too Many Requests)."""
    pass

class ServiceUnavailableException(AIException):
    """Raised when the AI Provider hits a 503 (Server Busy)."""
    pass

class APIKeyException(AIException):
    """Raised when the API Key is invalid or expired."""
    pass
