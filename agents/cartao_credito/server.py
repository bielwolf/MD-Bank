from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from executor import CartaoCreditoExecutor 

skill = AgentSkill(
    id="cartao_credito",
    name="Cartões de Crédito MDBank",
    description="Ajuda clientes com dúvidas sobre dúvidas, solicitação e limites de cartões de crédito",
    tags=[
        "cartão",
        "credito",
        "limite",
        "platinum",
        "gold",
        "silver",
        "mdzao"
    ],
    examples=[
        "quais cartões vocês têm?",
        "quero solicitar um cartão platinum?",
        "qual é o limite do meu cartão?",
        "posso aumentar meu limite?",
        "quero um cartão mdzão",
    ],
)

agent_card = AgentCard(
    name="Agent de Cartão de Crédito MDBank",
    description="Especialista em cartões de crédito do MDBank.",
    url="http://cartao_credito_agent:8000/",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    skills=[skill],
    version="1.0.0",
    capabilities=AgentCapabilities()
)

handler = DefaultRequestHandler(
    agent_executor=CartaoCreditoExecutor(),
    task_store=InMemoryTaskStore()
)

server = A2AStarletteApplication(
    http_handler=handler,
    agent_card=agent_card,
)

app = server.build()