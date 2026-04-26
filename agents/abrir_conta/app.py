from fastapi import FastAPI, Request, HTTPException
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from pydantic import BaseModel
import os

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

app = FastAPI()

agente_abertura_conta = create_agent(
    _llm,
    tools = [],
    system_prompt = (
        "Você é um especialista em abertura de contas do banco MDBank."
        "Ajude o cliente a abrir uma conta e explique os tipos disponíveis. Explique em tópicos de no maximo 3 linhas cada tipo de conta. Em pt-br."
    )
)

class AbrirContaRequest(BaseModel):
    message: str


@app.post("/send")
async def consultar(request: AbrirContaRequest):
    mensagem = request.message
    if not mensagem: 
        raise HTTPException(status_code=400, detail="Campo 'messages' é obrigatório.")
    try:
        resultado = agente_abertura_conta.invoke({
            "messages": [HumanMessage(content=mensagem)]
        })
        mensagem_ia = resultado["messages"][-1]
        return {"response": mensagem_ia.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health():
    return {"status": "ok"}