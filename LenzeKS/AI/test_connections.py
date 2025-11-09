"""
Umfassendes Test-Skript für alle API-Verbindungen
"""
import sys
from openai import AzureOpenAI
import psycopg2
from config import Config

print("="*70)
print("API CONNECTION TESTS")
print("="*70)

# ============================================================================
# TEST 1: Konfiguration laden
# ============================================================================
print("\nTEST 1: Konfiguration")
print("-"*70)

try:
    print(f"AZURE_OPENAI_KEY: {Config.AZURE_OPENAI_KEY[:15]}...")
    print(f"AZURE_OPENAI_ENDPOINT: {Config.AZURE_OPENAI_ENDPOINT}")
    print(f"AZURE_OPENAI_DEPLOYMENT: {Config.AZURE_OPENAI_DEPLOYMENT}")
    print(f"AZURE_OPENAI_EMBEDDING: {Config.AZURE_OPENAI_EMBEDDING}")
    print(f"POSTGRES_HOST: {Config.POSTGRES_HOST}")
    print(f"POSTGRES_DB: {Config.POSTGRES_DB}")
    print(f"POSTGRES_USER: {Config.POSTGRES_USER}")
    print("Konfiguration erfolgreich geladen")
except Exception as e:
    print(f"Fehler beim Laden der Konfiguration: {e}")
    sys.exit(1)

# ============================================================================
# TEST 2: Azure OpenAI Chat Completion
# ============================================================================
print("\n TEST 2: Azure OpenAI Chat Completion")
print("-"*70)

try:
    client = AzureOpenAI(
        api_key=Config.AZURE_OPENAI_KEY,
        api_version="2024-02-01",
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
    )
    
    print(f"🔄 Teste Deployment: {Config.AZURE_OPENAI_DEPLOYMENT}")
    
    response = client.chat.completions.create(
        model=Config.AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
            {"role": "user", "content": "Sage 'Hallo Welt' auf Deutsch."}
        ],
        max_tokens=50,
        temperature=0.5
    )
    
    answer = response.choices[0].message.content
    print(f"  Chat API funktioniert!")
    print(f"   Antwort: {answer}")
    print(f"   Tokens verwendet: {response.usage.total_tokens}")
    
except Exception as e:
    print(f" Chat API Fehler: {e}")
    print(f"\n Mögliche Ursachen:")
    print(f"   - Deployment '{Config.AZURE_OPENAI_DEPLOYMENT}' existiert nicht")
    print(f"   - Falscher API Key")
    print(f"   - Falscher Endpoint")
    print(f"\n Überprüfe im Azure Portal:")
    print(f"   https://portal.azure.com → Azure OpenAI → Model deployments")

# ============================================================================
# TEST 3: Azure OpenAI Embeddings
# ============================================================================
print("\n TEST 3: Azure OpenAI Embeddings")
print("-"*70)

try:
    print(f" Teste Embedding-Deployment: {Config.AZURE_OPENAI_EMBEDDING}")
    
    response = client.embeddings.create(
        model=Config.AZURE_OPENAI_EMBEDDING,
        input="Test-Text für Embedding"
    )
    
    embedding = response.data[0].embedding
    print(f" Embedding API funktioniert!")
    print(f"   Embedding-Dimension: {len(embedding)}")
    print(f"   Erste 5 Werte: {embedding[:5]}")
    
except Exception as e:
    print(f" Embedding API Fehler: {e}")
    print(f"\n Mögliche Ursachen:")
    print(f"   - Deployment '{Config.AZURE_OPENAI_EMBEDDING}' existiert nicht")
    print(f"   - Falsches Modell (muss ein Embedding-Modell sein)")

# ============================================================================
# TEST 4: PostgreSQL Verbindung
# ============================================================================
print("\n  TEST 4: PostgreSQL Verbindung")
print("-"*70)

try:
    conn = psycopg2.connect(
        host=Config.POSTGRES_HOST,
        database=Config.POSTGRES_DB,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        port=Config.POSTGRES_PORT,
        connect_timeout=10
    )
    
    print(f" PostgreSQL Verbindung erfolgreich!")
    
    # Test Query
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"   PostgreSQL Version: {version[:50]}...")
    
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f" PostgreSQL Verbindungsfehler: {e}")
    print(f"\n Mögliche Ursachen:")
    print(f"   - Server nicht erreichbar")
    print(f"   - Firewall blockiert Port {Config.POSTGRES_PORT}")
    print(f"   - Falsche Credentials")
    print(f"   - Datenbank '{Config.POSTGRES_DB}' existiert nicht")
except Exception as e:
    print(f" PostgreSQL Fehler: {e}")

# ============================================================================
# TEST 5: pgvector Extension
# ============================================================================
print("\n TEST 5: pgvector Extension")
print("-"*70)

try:
    conn = psycopg2.connect(
        host=Config.POSTGRES_HOST,
        database=Config.POSTGRES_DB,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        port=Config.POSTGRES_PORT
    )
    
    with conn.cursor() as cur:
        # Prüfe ob pgvector Extension existiert
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            );
        """)
        has_pgvector = cur.fetchone()[0]
        
        if has_pgvector:
            print(" pgvector Extension ist installiert")
            
            # Prüfe Tabellen
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%langchain%';
            """)
            tables = cur.fetchall()
            
            if tables:
                print(f" LangChain Tabellen gefunden: {len(tables)}")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("  Keine LangChain Tabellen gefunden")
                print("   Führe 'python ingest.py' aus, um Dokumente zu indizieren")
        else:
            print(" pgvector Extension nicht installiert!")
            print("\n Installiere die Extension:")
            print("   1. Verbinde dich mit psql als Admin")
            print("   2. Führe aus: CREATE EXTENSION vector;")
    
    conn.close()
    
except Exception as e:
    print(f" Fehler beim Prüfen von pgvector: {e}")

# ============================================================================
# TEST 6: Dokumente in Datenbank
# ============================================================================
print("\n TEST 6: Indizierte Dokumente")
print("-"*70)

try:
    conn = psycopg2.connect(
        host=Config.POSTGRES_HOST,
        database=Config.POSTGRES_DB,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        port=Config.POSTGRES_PORT
    )
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) 
            FROM langchain_pg_embedding
        """)
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f" {count} Dokumente in der Datenbank gefunden")
            
            # Zeige Beispiel
            cur.execute("""
                SELECT document, metadata 
                FROM langchain_pg_embedding 
                LIMIT 1
            """)
            doc = cur.fetchone()
            if doc:
                print(f"\n   Beispiel-Dokument:")
                print(f"   {doc[0][:100]}...")
        else:
            print("  Keine Dokumente in der Datenbank")
            print("   Führe 'python ingest.py' aus, um Dokumente zu indizieren")
    
    conn.close()
    
except psycopg2.errors.UndefinedTable:
    print("  Tabelle 'langchain_pg_embedding' existiert noch nicht")
    print("   Führe 'python ingest.py' aus, um sie zu erstellen")
except Exception as e:
    print(f" Fehler beim Prüfen der Dokumente: {e}")

# ============================================================================
# ZUSAMMENFASSUNG
# ============================================================================
print("\n" + "="*70)
print(" ZUSAMMENFASSUNG")
print("="*70)
print("\nWenn alle Tests sind, kannst du starten:")
print("  python test_agents.py")
print("\nWenn Fehler auftreten:")
print("  1. Überprüfe .env Datei")
print("  2. Prüfe Azure Portal (Deployments, Keys)")
print("  3. Teste PostgreSQL-Verbindung")
print("  4. Installiere pgvector Extension falls nötig")
print("="*70)