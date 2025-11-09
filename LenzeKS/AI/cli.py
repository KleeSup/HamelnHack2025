"""
CLI-Tool für den Multi-Agent Orchestrator
Verwendung: python cli.py "Deine Anfrage hier"
"""
import sys
import os
import argparse

# Setze UTF-8 Encoding für Windows-Konsole
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from orchestrator import Orchestrator

class OrchestratorCLI:
    """Command-Line Interface für den Orchestrator"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        if self.verbose:
            print("Initialisiere Orchestrator...", file=sys.stderr)
        self.orchestrator = Orchestrator()
        if self.verbose:
            print("Orchestrator bereit!\n", file=sys.stderr)
    
    def execute(self, query: str, user_id: str = "cli_user") -> str:
        """
        Führt eine Anfrage aus und gibt die Antwort zurück
        
        Args:
            query: Die Benutzeranfrage
            user_id: Optionale User-ID für History-Tracking
            
        Returns:
            Die Antwort des Orchestrators
        """
        if self.verbose:
            print("\n" + "="*70, file=sys.stderr)
            print("ORCHESTRATOR CLI", file=sys.stderr)
            print("="*70, file=sys.stderr)
            print(f"Anfrage: {query}", file=sys.stderr)
            print(f"User-ID: {user_id}", file=sys.stderr)
            print("="*70 + "\n", file=sys.stderr)
        
        try:
            # Rufe die chat()-Methode auf (genau wie in test_agents.py)
            response = self.orchestrator.chat(
                user_message=query,  # Explizit als keyword argument
                user_id=user_id
            )
            
            if self.verbose:
                print("\n" + "="*70, file=sys.stderr)
                print("ANTWORT:", file=sys.stderr)
                print("="*70, file=sys.stderr)
            
            # Antwort IMMER auf stdout (für Capturing)
            print(response)
            sys.stdout.flush()
            
            if self.verbose:
                print("="*70 + "\n", file=sys.stderr)
            
            return response
            
        except Exception as e:
            error_msg = f"FEHLER bei der Verarbeitung: {str(e)}"
            
            if self.verbose:
                print(error_msg, file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
            else:
                # Im quiet-Modus auch Fehler auf stdout
                print(error_msg)
                sys.stdout.flush()
            
            sys.exit(1)

def main():
    """Hauptfunktion für CLI-Ausführung"""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Orchestrator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python cli.py "Was ist Fehlercode E42?"
  python cli.py "Fehler 20503: Nutzer ist kein Experte. Erklaere einfach."
  python cli.py "Erklaere das genauer" --user-id max
  python cli.py "Hydraulikpresse Problem" --quiet
  python cli.py --interactive
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Die Anfrage an den Orchestrator'
    )
    
    parser.add_argument(
        '--user-id', '-u',
        default='cli_user',
        help='User-ID fuer History-Tracking (Standard: cli_user)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Keine Logging-Ausgaben, nur Antwort'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interaktiver Modus (Chat-Session)'
    )
    
    args = parser.parse_args()
    
    # CLI-Instanz erstellen
    try:
        cli = OrchestratorCLI(verbose=not args.quiet)
    except Exception as e:
        print(f"FEHLER beim Initialisieren: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    # Interaktiver Modus
    if args.interactive:
        print("\n" + "="*70)
        print("INTERAKTIVER MODUS")
        print("="*70)
        print("Gib deine Anfragen ein (oder 'exit' zum Beenden)")
        print("="*70 + "\n")
        
        while True:
            try:
                query = input("Du: ").strip()
                if query.lower() in ['exit', 'quit', 'q']:
                    print("\nAuf Wiedersehen!\n")
                    break
                if not query:
                    continue
                
                cli.execute(query, user_id=args.user_id)
                
            except KeyboardInterrupt:
                print("\n\nAuf Wiedersehen!\n")
                break
            except EOFError:
                print("\nAuf Wiedersehen!\n")
                break
            except Exception as e:
                print(f"\nFEHLER: {e}\n", file=sys.stderr)
                continue
    
    # Einzel-Anfrage Modus
    elif args.query:
        cli.execute(args.query, user_id=args.user_id)
        sys.exit(0)
    
    # Keine Argumente → Hilfe anzeigen
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()