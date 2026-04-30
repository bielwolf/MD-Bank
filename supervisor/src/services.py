import logging
import httpx
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated
from operator import add

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import Message, Part, Role, TextPart, SendMessageRequest, MessageSendParams

from src.agents import classifique_intencao_do_usuario

logger = logging.getLogger(__name__)

HTTPX_CLIENT = httpx.AsyncClient(timeout=120)

AGENTS = {
    "cartao_credito": "http://cartao_credito_agent:8000",
    "abrir_conta": "http://abrir_conta_agent:8000"
}

CLIENT_CACHE = {}

class State(TypedDict):
    query: str
    responses: Annotated[list[str], add]

async def request_agent(message: str, agent_url: str) -> str:
    if agent_url not in CLIENT_CACHE:
        logger.info(f"Descobrindo AgentCard em {agent_url}")

        resolver = A2ACardResolver(
            HTTPX_CLIENT,
            agent_url
        )

        agent_card = await resolver.get_agent_card()

        logger.info(f"Agent encontrado: {agent_card.name}")

        CLIENT_CACHE[agent_url] = A2AClient(
            httpx_client=HTTPX_CLIENT,
            agent_card=agent_card
        )

    client = CLIENT_CACHE[agent_url]

    request = SendMessageRequest(
        id=str(uuid.uuid4()),
        params=MessageSendParams(
            message=Message(
                role=Role.user,
                messageId=str(uuid.uuid4()),
                parts=[
                    Part(
                        root=TextPart(
                            text=message
                        )
                    )
                ]
            ),  
        )
    )

    logger.info(f"Enviando mensagem para agente: {message}")

    response = await client.send_message(request)

    if hasattr(response, "root"):
        result = response.root
        if hasattr(result, "result"):
            result_msg = result.result
            if hasattr(result_msg, "parts"):
                for part in result_msg.parts:
                    if hasattr(part.root, "text"):
                        return part.root.text
                
    return 'Sem resposta do agente'

def no_de_roteamento(state: State):

    query = state.get("query", "")

    classifications = classifique_intencao_do_usuario(query)

    logger.info(f"Classificações obtidas: {classifications}")

    return [
        Send(c["agent"], {"query": c["query"]})
        for c in classifications
    ]

async def cartao_credito_node(state: State):

    query = state.get("query", "")

    logger.info("Executando agente CARTAO_CREDITO")

    resposta = await request_agent(
        query, 
        AGENTS["cartao_credito"]
    )

    return {"responses": [resposta]}

async def abrir_conta_node(state: State):

    query = state.get("query", "")

    logger.info("Executando agente ABRIR_CONTA")

    resposta = await request_agent(
        query, 
        AGENTS["abrir_conta"]
    )

    return {"responses": [resposta]}

builder = StateGraph(State)

builder.add_node("cartao_credito", cartao_credito_node)
builder.add_node("abrir_conta", abrir_conta_node)

builder.add_conditional_edges(
    START,
    no_de_roteamento
)

builder.add_edge("cartao_credito", END)
builder.add_edge("abrir_conta", END)

graph = builder.compile()

async def executar_supervisor(texto_usuario: str):

    input_state: State = {
        "query": texto_usuario,
        "responses": []
    }

    result = await graph.ainvoke(input_state)

    return "\n\n".join(result["responses"])