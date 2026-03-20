from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import quantum

app = FastAPI(
    title="Shor Code Quantum Error Correction API",
    description="API para simular e demonstrar o código de correção de erros de Shor (9 qubits).",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir roteadores
app.include_router(quantum.router)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do Shor Code. Acesse /docs para a documentação interativa."}