import logging
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

load_dotenv()

_llm = ChatOllama(
    model="llama3", 
    base_url="http://host.docker.internal:11434",
    temperature=0.7
)

class RouterOutput(BaseModel):
    agents: List[str] = Field(
        description="Lista de agentes que devem responder a pergunta."
    )

parser = JsonOutputParser(pydantic_object=RouterOutput)

def classifique_intencao_do_usuario(query: str) -> List[dict]:
    """
    Classifica a pergunta e retorna quais agentes devem ser chamados
    """

    prompt = f"""
Você é um roteador de agentes de um banco.

Agentes disponíveis:
- cartão_credito: Responde perguntas relacionadas a cartão de crédito
-abrir_conta: Responde perguntas relacionadas a abertura de conta

Uma pergunta pode exigir mais de um agente.

Responda apenas em JSON.

Pergunta: 
{query}

{parser.get_format_instructions()}
"""
    resposta = _llm.invoke(prompt)
    resultado = parser.parse(str(resposta.content))
    agentes = resultado["agents"]
    logger.info(f"Agentes selecionados para a pergunta: {agentes}")

    return [
        {
            "query": query,
            "agent": agente
        }

        for agente in agentes
    ]