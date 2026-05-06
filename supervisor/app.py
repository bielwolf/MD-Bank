import logging
from typing import cast
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ag_ui.core import (
    RunAgentInput,
    EventType,
    RunStartedEvent,
    RunFinishedEvent,
    BaseEvent
) 
from ag_ui.encoder import EventEncoder

from src.shemas import ChatRequest
from src.services import executar_supervisor, executar_supervisor_stream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
@app.post("/")
async def agent_endpoint(input_data: RunAgentInput, request: Request):

    accept_header = request.headers.get("accept")
    if accept_header is None:
        accept_header = "text/event-stream"

    encoder = EventEncoder()

    async def event_generator():

        yield encoder.encode(
            cast(BaseEvent, RunStartedEvent(
                type=EventType.RUN_STARTED,
                thread_id=input_data.thread_id,
                run_id=input_data.run_id,
            ))
        )

        async for event in executar_supervisor_stream(input_data):
            yield encoder.encode(cast(BaseEvent, event))

        yield encoder.encode(
            cast(BaseEvent, RunFinishedEvent(
                type=EventType.RUN_FINISHED,
                thread_id=input_data.thread_id,
                run_id=input_data.run_id,
            ))
        )

    return StreamingResponse(
        event_generator(), 
        media_type=encoder.get_content_type()
    )