from typing import List, Dict
from openai import AzureOpenAI
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config import Config
from models import AgentType

class BaseAgent:
    """Basisklasse für alle Agenten mit Logging"""
    
    def __init__(self, agent_type: AgentType, verbose: bool = False):
        self.agent_type = agent_type
        self.verbose = verbose
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_KEY,
            api_version="2024-02-01",
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )

    def _log(self, emoji: str, message: str):
        """Logging-Helper"""
        if self.verbose:
            print(f"  {emoji} [{self.agent_type.value}] {message}")
    
    def _call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Ruft Azure OpenAI API auf"""
        response = self.client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generiert Embedding für Text"""
        response = self.client.embeddings.create(
            model=Config.AZURE_OPENAI_EMBEDDING,
            input=text
        )
        return response.data[0].embedding