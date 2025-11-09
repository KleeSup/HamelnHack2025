from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config
from models import AgentType, SearchResult
from .base_agent import BaseAgent

class DocumentSearcher(BaseAgent):
    """Sucht in der Vector DB nach relevanten Dokumenten"""
    
    def __init__(self):
        super().__init__(AgentType.DOCUMENT_SEARCHER)
        self._init_db_connection()
    
    def _init_db_connection(self):
        """Initialisiert Postgres-Verbindung mit pgvector"""
        self.conn = psycopg2.connect(
            host=Config.POSTGRES_HOST,
            database=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            port=Config.POSTGRES_PORT,
            sslmode='require'
        )
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Sucht nach relevanten Dokumenten mittels Vector-Similarity
        
        Annahme: Tabelle 'documents' mit Spalten:
        - id, content, embedding (vector), metadata (jsonb)
        """
        query_embedding = self._get_embedding(query)
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verwende pgvector's <=> Operator für Cosine Distance
            cur.execute("""
                SELECT 
                    id,
                    content,
                    metadata,
                    1 - (embedding <=> %s::vector) as similarity
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (str(query_embedding), str(query_embedding), top_k))
            
            results = cur.fetchall()
        
        return [
            SearchResult(
                content=row['content'],
                similarity=row['similarity'],  # Geändert von 'score' zu 'similarity'
                metadata=row.get('metadata', {})
            )
            for row in results
        ]
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
