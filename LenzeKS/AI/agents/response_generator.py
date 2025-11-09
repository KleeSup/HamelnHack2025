import sys
from pathlib import Path
from typing import List

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from models import AgentType, Message
from agents.base_agent import BaseAgent

class ResponseGenerator(BaseAgent):
    """Agent für die Generierung der finalen Antwort"""
    
    def __init__(self):
        super().__init__(AgentType.RESPONSE_GENERATOR)
    
    def generate(self, user_message: str, context: List[str], history: List[Message]) -> str:
        """
        Generiert finale Antwort basierend auf Context und History
        
        Args:
            user_message: Aktuelle Nutzerfrage
            context: Relevante Informationen aus Dokumenten/Chat
            history: Bisherige Konversation
            
        Returns:
            Generierte Antwort
        """
        messages = []
        
        # System-Prompt
        messages.append({
            "role": "system",
            "content": """Du bist ein hilfreicher AI-Assistent für technische Maschinenwartung.

Du hast Zugriff auf:
- Wartungshandbücher und Dokumentation
- Fehlercodes und Lösungen
- Frühere Konversationen mit dem Nutzer

Antworte:
- Präzise und hilfreich
- Auf Deutsch
- Basierend auf den bereitgestellten Informationen
- Ehrlich, wenn du unsicher bist"""
        })
        
        # Context hinzufügen
        if context:
            combined_context = "\n\n---\n\n".join(context)
            messages.append({
                "role": "system",
                "content": f"Relevante Informationen:\n\n{combined_context}"
            })
        
        # Letzte 6 Nachrichten als Kontext
        recent_history = history[-6:] if history else []
        for msg in recent_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Aktuelle Frage
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generiere Antwort
        return self._call_llm(messages, temperature=0.7)