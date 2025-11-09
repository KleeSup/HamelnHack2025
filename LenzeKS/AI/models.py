from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class AgentType(Enum):
    """Typen der verfügbaren Agenten"""
    ORCHESTRATOR = "orchestrator"
    INTENT_ANALYZER = "intent_analyser"
    DOCUMENT_SEARCHER = "document_searcher"
    CHAT_SEARCHER = "chat_searcher"
    RESPONSE_GENERATOR = "response_generator"
    EMAIL_AGENT = "email_agent"

@dataclass
class Message:
    """Repräsentiert eine Chat-Nachricht"""
    role: str  # "user" oder "assistant"
    content: str

@dataclass
class SearchResult:
    """Ergebnis einer Dokumentensuche"""
    content: str
    similarity: float
    metadata: Optional[Dict[str, Any]] = None