from dotenv import load_dotenv
from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
import os

load_dotenv()

# _llm = chatOpenAI = ChatOpenAI(
#     model_name="gpt-3.5-turbo",
#     temperature=0.7,
#     openai_api_key=os.getenv("OPENAI_API_KEY")
# )

_llm = ChatOllama(
    model = "llama3.1:8b",
    base_url="http://host.docker.internal:11434",
    temperature = 0.7
)

# SMITHERY_URL = "https://ddg_search--oevortex.run.tools"
# SMITHERY_API_KEY = "98347f3c-4aa0-482a-86de-817ad5217b98"

client = MultiServerMCPClient(
    {
        "conta": {
            "transport": "streamable_http",
            "url": "http://recursos:8000/mcp_gateway"
        },

        # "smithery": {
        #     "transport": "streamable_http",
        #     "url": f"{SMITHERY_URL}/?api_key={SMITHERY_API_KEY}",
        #     "api_key": SMITHERY_API_KEY
        # }
    }
)

memory = InMemorySaver()

load_dotenv()

async def build_agent():
    tools = await client.get_tools()

    agent = create_react_agent(
        _llm,
        tools = tools,
        prompt = (
            "Você é um assistente do MDBank.\n\n"

            "Você deve SEMPRE usar tools para decisões reais.\n\n"

            "Fluxo obrigatório:\n"
            "1. Se cliente pedir cartão:\n"
            "   - Use consultar_conta\n"
            "   - Se não existir:\n"
            "       → informe o problema\n"
            "       → ofereça abrir conta\n\n"

            "2. Para abrir conta:\n"
            "   - Use gerar_prompt_abertura\n"
            "   - Depois criar_ou_buscar_conta\n\n"

            "3. Após conta criada:\n"
            "   - Use solicitar_cartao\n\n"

            "Regras:\n"
            "- Nunca invente dados\n"
            "- Sempre use tools\n"
            "- Use mensagens claras para o cliente\n"
            "- Para buscas externas use a tool search do smitherry, sempre que alguem falar quero buscar\n"
        ),
        checkpointer=memory,
    )

    return agent

async def run_agent(mensagem: str, thread_id: str = "1"):
    agent = await build_agent()

    resultado = await agent.ainvoke(
        {"messages": [HumanMessage(content=mensagem)]},
        {"configurable": {"thread_id": thread_id}}
    )

    return resultado["messages"][-1].content    