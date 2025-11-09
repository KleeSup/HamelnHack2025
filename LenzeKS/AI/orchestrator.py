import json
from typing import List, Dict, Any
from agents.chat_searcher import ChatSearcher
from agents.document_searcher import DocumentSearcher
from agents.intent_analyser import IntentAnalyzer
from agents.response_generator import ResponseGenerator
from models import AgentType, Message
from agents.base_agent import BaseAgent
from agents.email_agent import EmailAgent
import re
# ============================================================================
# ORCHESTRATOR - Nur Koordination, keine eigene Logik
# ============================================================================

class Orchestrator(BaseAgent):
    """
    Hauptkoordinator: Delegiert Aufgaben an spezialisierte Agenten.
    Enthält KEINE eigene Business-Logik.
    """
    
    def __init__(self):
        super().__init__(AgentType.ORCHESTRATOR)
        
        # Initialisiere alle Sub-Agenten
        self.intent_analyzer = IntentAnalyzer()
        self.document_searcher = DocumentSearcher()
        self.chat_searcher = ChatSearcher()
        self.response_generator = ResponseGenerator()
        self.email_agent = EmailAgent()
        
    
    def chat(self, user_message: str, user_id: str = "default_user") -> str:
        """
        Hauptmethode: Koordiniert den gesamten Workflow
        
        Workflow:
        1. Intent analysieren (IntentAnalyzer)
        2. Dokumente suchen (DocumentSearcher)
        3. Chat-History suchen (ChatSearcher) 
        4. Antwort generieren (ResponseGenerator)
        5. Email generieren (EmailAgent) [optional]
        """
        
        # 1. Intent analysieren
        intent = self.intent_analyzer.analyze(user_message)
        
        # 2. Context sammeln
        context = self._gather_context(
            user_message=user_message,
            user_id=user_id,
            intent=intent
        )
        
        # 3. Antwort generieren
        response = self.response_generator.generate(
            user_message=user_message,
            context=context,
            history=""
        )

        # Optional: E-Mail generieren und senden, wenn Intent das verlangt oder Empfänger angegeben ist
        send_email_flag = intent.get("send_email", False) or intent.get("email", False)

        if send_email_flag:
            # Body aus Kontext + generierter Antwort zusammensetzen
            content_for_email = ("\n\n".join(context) + "\n\n" + response).strip()
            try:
                email_body = self.email_agent.generate_body(content=content_for_email)
                ok = self.email_agent.send_email(
                    to_email="",
                    subject="", 
                    body=email_body
                )
            except Exception as e:
                response = response + f"\n\n(Fehler beim Erzeugen/Senden der E-Mail: {e})"
        
        
        
        return response
    
    def _gather_context(self, user_message: str, user_id: str, intent: Dict[str, Any]) -> List[str]:
        """Sammelt relevanten Context von verschiedenen Agenten"""
        context = []
        
        # Dokument-Suche
        if intent.get("needs_document_search", False):
            doc_results = self.document_searcher.search(
                query=intent.get("search_query", user_message),
                top_k=3
            )
            if doc_results:
                doc_context = "\n\n".join([
                    f"[DOKUMENT {i+1}] (Relevanz: {r.similarity:.2f})\n{r.content}"
                    for i, r in enumerate(doc_results)
                ])
                context.append(doc_context)
        
        # Chat-History Suche
        if intent.get("needs_chat_search", False):
            #Ausgabe für Tests
  
            chat_id = intent.get("chat_id")
            if chat_id:
                
                # Wenn chat_id vorhanden: gib alle Nachrichten dieses Chats zurück (chronologisch)
                db_results = self.chat_searcher.search(chat_id=chat_id, query=None, top_k=1000)
            else:
                # Sonst: suche über alle Chats nach query (Top-K)
                db_results = self.chat_searcher.search(
                    query=intent.get("search_query", user_message),
                    chat_id=None,
                    top_k=3
                )
            
            if db_results:
                chat_context = "\n\n".join([
                    f"[FRÜHERER EINTRAG] ({r.metadata.get('timestamp')}) {r.metadata.get('role')}: {r.content}"
                    for r in db_results
                ])
                context.append(chat_context)        
        
        return context