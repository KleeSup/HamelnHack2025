from orchestrator import Orchestrator

# System initialisieren
orch = Orchestrator()

# Einfache Anfrage
print("\nAnfrage 1: Was steht in den Dokumenten über das Budget?")
print("="*60)
antwort = orch.chat(
    "Schreibe einne Mail über den Fehler 17000",
    user_id="max_mustermann"
)
print("\nAntwort:")
print(antwort)
print("="*60)
