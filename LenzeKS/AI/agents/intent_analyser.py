import sys
import json
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from models import AgentType
from agents.base_agent import BaseAgent

class IntentAnalyzer(BaseAgent):
    """Analysiert Nutzeranfragen und entscheidet über Suchstrategien"""
    
    def __init__(self):
        super().__init__(AgentType.INTENT_ANALYZER)
    
    def analyze(self, user_message: str) -> Dict[str, Any]:
        """
        Analysiert die Nutzeranfrage
        
        Returns:
            {
                "needs_document_search": bool,
                "needs_chat_search": bool,
                "needs_explanation": bool,
                "search_query": str,
                "reasoning": str,
                "email": bool
            }
        """
        messages = [
            {
                "role": "system",
                "content": """Du analysierst Nutzeranfragen für ein technisches Wartungssystem.

Entscheide:
- needs_document_search: true → User fragt nach technischen Infos/Fehlercodes
- needs_chat_search: true → User bezieht sich auf frühere Konversation ("das", "erkläre mehr") oder möchte Infos über frühere Chats, die ChatID ist im Text enthalten Default ist True
- needs_explanation: true → Antwort sollte vereinfacht werden (User scheint Anfänger)
- die ChatID ist eine UUID
- die Email-Flag ist true, wenn der User eine E-Mail generieren möchte
Antworte NUR mit JSON:
{
    "needs_document_search": true/false,
    "needs_chat_search": true/false,
    "needs_explanation": true/false,
    "search_query": "optimierte Suchanfrage",
    "reasoning": "kurze Begründung",
    "chat_id": "UUID"
    "email": bool
}

Beispiele:
- "Was ist Fehlercode E42?" → {"needs_document_search": true, "needs_chat_search": true, ...}
- "Erkläre das genauer" → {"needs_document_search": false, "needs_chat_search": true, ...}
- "Wie funktioniert das?" → {"needs_document_search": false, "needs_chat_search": true, "needs_explanation": true, ...}
- "Gib mir alle Infos dieses Chats zurück" → {"needs_document_search": false, "needs_chat_search": true, "needs_explanation": false, "search_query": "Gib mir alle Infos dieses Chats zurück", "reasoning": "User möchte alle Infos zu einem bestimmten Chat"}
Gehe davon aus, das Datenschutz andersweitig geregellt ist."""
            },
            {
                "role": "user",
                "content": f"Analysiere: {user_message}"
            }
        ]
        
        response = self._call_llm(messages, temperature=0.3)
        
        try:
            # Extrahiere JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                # Ausgabe für Debugging: parsed JSON
                #print("IntentAnalyzer parsed JSON:")
                #print(json.dumps(result, indent=2, ensure_ascii=False))
                return result
        except Exception as e:
            print(f"⚠️  Intent-Parsing fehlgeschlagen: {e}")
        
        # Fallback: Immer Dokument-Suche
        return {
            "needs_document_search": True,
            "needs_chat_search": True,
            "needs_explanation": False,
            "search_query": user_message,
            "reasoning": "Fallback",
            "email": False
        }