from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain.core_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv()

_llm = init_chat_model(
    model = "gpt-4o",
    api_key = os.getenv("OPENAI_API_KEY"),
    temperature = 0.7
)

agent_cartao_credito = create_agent(
    _llm, 
    tools = [],
    system_prompt = (
        "Você é um especialista em cartões de crédito do banco MDBank."
        "Ajude o cliente com dúvidas, solicitação e limites."
    )
)

agente_abertura_conta = create_agent(
    _llm,
    tools = [],
    system_prompt = (
        "Você é um especialista em abertura de contas do banco MDBank."
        "Ajude o cliente a abrir uma conta e explique os tipos disponíveis."
    )
)

def classificar_pergunta(pergunta: str) -> str:
    prompt = f"""
Classifique a intenção do usuário.

Possíveis agentes:
cartao_credito
abrir_conta

Pergunta: {pergunta}

Responda apenas com o nome do agente.
"""
    resposta = _llm.invoke(prompt)
    return str(resposta.content).strip()

async def executar_supervisor(texto_usuario: str) -> str:
    agente = classificar_pergunta(texto_usuario)

    if agente == "cartao_credito":
        resposta = await agent_cartao_credito.invoke(HumanMessage(content=texto_usuario))
    elif agente == "abrir_conta":
        resposta = await agente_abertura_conta.invoke(HumanMessage(content=texto_usuario))
    else:
        resposta = "Desculpe, não consegui identificar a intenção da sua pergunta. Por favor, reformule ou seja mais específico."

    mensagem_ia = resposta["messages"][-1]

    return mensagem_ia.content