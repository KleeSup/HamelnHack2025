import os
import sys
from pathlib import Path
from openai import AzureOpenAI
import psycopg2
from typing import List
import json
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI Setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Postgres Connection
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    port=5432
)

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Teilt Text in Chunks für bessere Embeddings"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1
        
        if current_size >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def get_embedding(text: str) -> List[float]:
    """Generiert Embedding via Azure OpenAI (text-embedding-3-large = 3072 Dimensionen)"""
    response = client.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") 
    )
    return response.data[0].embedding

def ingest_document(content: str, machine_type: str = None, error_code: str = None, source_file: str = None):
    """Speichert Dokument mit Embedding in Postgres (documents Tabelle)"""
    chunks = chunk_text(content)
    cursor = conn.cursor()
    
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        
        # Metadata als JSONB
        metadata = {
            "machine_type": machine_type,
            "error_code": error_code,
            "document_type": "manual",
            "source_file": source_file,
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        
        cursor.execute("""
            INSERT INTO documents 
            (content, embedding, metadata)
            VALUES (%s, %s, %s)
        """, (
            chunk,
            embedding,
            json.dumps(metadata)
        ))
    
    conn.commit()
    cursor.close()
    return len(chunks)

def ingest_folder(folder_path: str):
    """
    Liest alle .txt Dateien aus einem Ordner und indiziert sie.
    
    Args:
        folder_path: Pfad zum Ordner mit .txt Dateien
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Ordner nicht gefunden: {folder_path}")
        return
    
    if not folder.is_dir():
        print(f"❌ Pfad ist kein Ordner: {folder_path}")
        return
    
    # Finde alle .txt Dateien
    txt_files = list(folder.glob("**/*.txt"))  # ** = rekursiv durch Unterordner
    
    if not txt_files:
        print(f"⚠️  Keine .txt Dateien gefunden in: {folder_path}")
        return
    
    print(f"\n📂 Gefundene Dateien: {len(txt_files)}")
    print("="*70)
    
    total_chunks = 0
    successful = 0
    failed = 0
    
    for txt_file in txt_files:
        try:
            print(f"\n📄 Verarbeite: {txt_file.name}")
            
            # Datei einlesen
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"   ⚠️  Datei ist leer, überspringe...")
                continue
            
            # Extrahiere Metadaten aus Dateinamen (optional)
            # z.B. "Hydraulikpresse_E42.txt" → machine_type="Hydraulikpresse", error_code="E42"
            filename_parts = txt_file.stem.split('_')
            machine_type = filename_parts[0] if len(filename_parts) > 0 else None
            error_code = filename_parts[1] if len(filename_parts) > 1 else None
            
            # Dokument indizieren
            chunks_count = ingest_document(
                content=content,
                machine_type=machine_type,
                error_code=error_code,
                source_file=str(txt_file)
            )
            
            total_chunks += chunks_count
            successful += 1
            print(f"   ✅ {chunks_count} chunks erstellt")
            
        except Exception as e:
            failed += 1
            print(f"   ❌ Fehler: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print(f"📊 ZUSAMMENFASSUNG:")
    print(f"   ✅ Erfolgreich: {successful} Dateien")
    print(f"   ❌ Fehlgeschlagen: {failed} Dateien")
    print(f"   📦 Gesamt Chunks: {total_chunks}")
    print("="*70)

def ensure_table_exists():
    """Erstellt die Tabelle falls sie nicht existiert"""
    cursor = conn.cursor()
    
    # Prüfe ob pgvector Extension installiert ist
    cursor.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding vector(3072), -- text-embedding-3-large dimension
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Index für schnellere Vektor-Suche
        CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents 
        USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        
        -- Index für Metadata-Suche
        CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING gin(metadata);
    """)
    conn.commit()
    cursor.close()
    print("✅ Tabelle 'documents' bereit\n")

# Hauptprogramm
if __name__ == "__main__":
    print("\n🚀 DOKUMENT-INGESTION-TOOL")
    print("="*70)
    
    # Stelle sicher, dass Tabelle existiert
    ensure_table_exists()
    
    # Prüfe ob Ordnerpfad als Argument übergeben wurde
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        # Interaktive Eingabe
        print("📂 Gib den Pfad zum Ordner mit .txt Dateien ein:")
        print("   (oder drücke Enter für Standard-Ordner './data')")
        folder_path = input("   Pfad: ").strip()
        
        if not folder_path:
            folder_path = "./data"
    
    print(f"\n📍 Verwende Ordner: {folder_path}\n")
    
    # Starte Ingestion
    ingest_folder(folder_path)
    
    # Verbindung schließen
    conn.close()
    print("\n✅ Fertig!")