from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI
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

load_dotenv()

agente_abertura_conta = create_agent(
    _llm,
    tools = [],
    system_prompt = (
        "Você é um especialista em abertura de contas do banco MDBank."
        "Ajude o cliente a abrir uma conta e explique os tipos disponíveis. Explique em tópicos de no maximo 3 linhas cada tipo de conta. Em pt-br."
    )
)

async def run_agent(mensagem: str):
    resultado = await agente_abertura_conta.ainvoke({
        "messages": [HumanMessage(content=mensagem)]
    })
    return resultado["messages"][-1].content