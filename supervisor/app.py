import logging 
from fastapi import FastAPI
from fastApi.responses import JSONResponse

from src.schemas import ChatRequest
from src.agents import executar_supervisor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    if not payload.message:
        return JSONResponse(content={"error": "Campo 'message' é obrigatório"}, status_code=400)
    try:
        logger.info(f"Mensagem recebida no /chat: {payload.message}")
        resposta = await executar_supervisor(texto_usuario=payload.message)
        logger.info(f"Resposta gerada: {resposta}")
        return {"resposta": resposta}
    except Exception as e:
        logger.error(f"Erro ao processar requisição no endpoint /chat: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)