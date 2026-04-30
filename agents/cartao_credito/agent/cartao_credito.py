from dotenv import load_dotenv
from langchain.agents import create_agent
# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import os

load_dotenv()

# _llm = chatOpenAI = ChatOpenAI(
#     model_name="gpt-3.5-turbo",
#     temperature=0.7,
#     openai_api_key=os.getenv("OPENAI_API_KEY")
# )

_llm = ChatOllama(
    model = "llama3",
    base_url="http://host.docker.internal:11434",
    temperature = 0.7
)

agente_cartao_credito = create_agent(
    _llm,
    tools = [],
    system_prompt = (
        "Você é um especialista em cartao de credito do banco MDBank."
        "Os cartões que existem no MDBank são: [platinum, gold, silver, mdzao]."
        "Quando o cliente solicitar um cartão do tipo platinum, você deve recomendar o cartão platinum, que tem os seguintes benefícios: [Hotel, Restaurante, pontos de cashback]."
        "Quando o cliente informar que gostaria do platinum, você deve informar que o cartão possui uma anuidade de R$ 500,00 e um limite de R$ 50.000,00."
        "Ajude o cliente com dúvidas, solicitação e limites"
        "Explique em tópicos de no maximo 3 linhas cada tipo de conta. Em pt-br."
    )
)

async def run_agent(mensagem: str):
    resultado = await agente_cartao_credito.ainvoke({
        "messages": [HumanMessage(content=mensagem)]
    })
    return resultado["messages"][-1].content