import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.shemas import ChatRequest
from src.services import executar_supervisor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    if not payload.message:
        return JSONResponse(status_code=400, content={"error": "Campo 'message' é obrigatório."})
    try:
        logger.info(f"Recebida mensagem no /chat: {payload.message}")
        resposta = await executar_supervisor(texto_usuario=payload.message)
        logger.info(f"Resposta gerada: {resposta}")
        return {"resposta": resposta}
    
    except Exception as e:
        logger.exception(f"Erro ao processar a requisição no endpoint /chat: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})