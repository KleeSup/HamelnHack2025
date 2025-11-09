from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config
from models import AgentType, SearchResult
from .base_agent import BaseAgent
from types import SimpleNamespace

class ChatSearcher(BaseAgent):
    """Sucht in relationaler Chat-History und liefert alle Nachrichten eines Chats zurück"""
    
    def __init__(self):
        super().__init__(AgentType.CHAT_SEARCHER)
        self._init_db_connection()
    
    def _init_db_connection(self):
        try:
            self.conn = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                port=Config.POSTGRES_PORT,
                sslmode=getattr(Config, "POSTGRES_SSLMODE", "require")
            )
        except Exception as e:
            # Verbindung fehlgeschlagen -> None setzen, Aufrufer muss prüfen
            print(f"⚠️  ChatSearcher DB connection failed: {e}")
            self.conn = None
    
    def search(self, query: Optional[str] = None, chat_id: Optional[str] = None, top_k: int = 10) -> List[SearchResult]:
        """
        Suche in chat_messages oder gib alle Nachrichten eines Chats zurück.
        
        Erwartete Spalten in chat_messages: id, chat_id, zeitstempel, rolle, content
        """
     
        if not getattr(self, "conn", None):
            return []
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Wenn chat_id angegeben und keine Query -> alle Nachrichten dieses Chats (chronologisch)
            if chat_id and not query:
                cur.execute("""
                    SELECT id, chat_id, rolle, content, zeitstempel
                    FROM chat_messages
                    WHERE chat_id = %s
                    ORDER BY zeitstempel ASC
                """, (chat_id,))
            else:
                # Suche nach query, optional innerhalb eines Chats, order by zeitstempel DESC mit Limit
                if chat_id:
                    cur.execute("""
                        SELECT id, chat_id, rolle, content, zeitstempel
                        FROM chat_messages
                        WHERE chat_id = %s
                          AND content ILIKE %s
                        ORDER BY zeitstempel DESC
                        LIMIT %s
                    """, (chat_id, f'%{query}%', top_k))
                else:
                    cur.execute("""
                        SELECT id, chat_id, rolle, content, zeitstempel
                        FROM chat_messages
                        WHERE content ILIKE %s
                        ORDER BY zeitstempel DESC
                        LIMIT %s
                    """, (f'%{query}%', top_k))
            
            results = cur.fetchall()
        
        return [
            SimpleNamespace(
                content=row['content'],
                metadata={
                    'chat_id': row.get('chat_id'),
                    'role': row.get('rolle'),
                    'timestamp': str(row.get('zeitstempel')),
                },
                source="chat"
            )
            for row in results
        ]
    
    def get_recent_context(self, chat_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Holt die letzten N Nachrichten eines Chats als Kontext (chronologisch)"""
        if not getattr(self, "conn", None):
            return []
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT rolle, content
                FROM chat_messages
                WHERE chat_id = %s
                ORDER BY zeitstempel DESC
                LIMIT %s
            """, (chat_id, limit))
            results = cur.fetchall()
        return [{"role": r['rolle'], "content": r['content']} for r in reversed(results)]
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except Exception:
                pass