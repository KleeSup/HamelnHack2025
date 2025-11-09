from typing import Optional
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import Config
from models import AgentType
from agents.base_agent import BaseAgent

class EmailAgent(BaseAgent):
    """
    Erzeugt einen E-Mail-Body mittels LLM und sendet die E-Mail per SMTP.
    Achtung: SMTP-Zugangsdaten müssen in Config (oder Umgebungsvariablen) hinterlegt sein.
    """

    def __init__(self):
        super().__init__(getattr(AgentType, "EMAIL_AGENT", AgentType.RESPONSE_GENERATOR))

    def generate_body(self, content: str, purpose: str = "Statusmeldung", tone: str = "neutral") -> str:
        """
        Generiert einen E-Mail-Text basierend auf `content`.
        purpose: kurzer Hinweis (z.B. 'Fehlermeldung', 'Wartungshinweis')
        tone: 'neutral' | 'formal' | 'urgent' | 'friendly'
        """
        system = (
            "Du bist ein Assistent, der professionelle E-Mail-Bodies auf Deutsch erstellt. "
            "Erzeuge einen klaren, prägnanten Text basierend auf den bereitgestellten Informationen."
        )
        user = (
            f"Zweck: {purpose}\nTon: {tone}\n\nInhalt:\n{content}\n\n"
            "Erzeuge einen vollständigen, gut strukturierten E-Mail-Text (Betreff nicht nötig)."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        body = self._call_llm(messages, temperature=0.6)
        return body.strip()

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        from_email = 'errormachine@gmx.de'  # Deine GMX-Adresse
        to_email = 'robert.jende@hsw-stud.de'
        password = 'maschienenfehler'           # Dein GMX-Passwort
        subject = 'fehler in der Maschine'

         # MIME Objekt erstellen
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # E-Mail-Body hinzufügen
        msg.attach(MIMEText(body, 'plain'))

        # Verbindung zum SMTP-Server und E-Mail senden
        try:
            server = smtplib.SMTP('mail.gmx.net', 587)  # SMTP-Server für GMX
            server.starttls()  # TLS aktivieren
            server.login(from_email, password)  # Anmeldung
            server.send_message(msg)  # E-Mail senden
        finally:
            server.quit()  

# Beispielnutzung (nur als Referenz, nicht automatisch ausgeführt):
# agent = EmailAgent()
# body = agent.generate_body(content="Maschine X hat Fehler E42. Temperatur 120°C.", purpose="Fehlermeldung", tone="urgent")
# ok = agent.send_email(to_email="technik@example.com", subject="Fehler in Maschine X", body=body)