from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import faiss
import re
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Lazy load do modelo para economizar memória no deploy
model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

# Carregando produtos
with open("produtos.json", "r", encoding="utf-8") as f:
    produtos = json.load(f)

def extrair_numeros(texto):
    return re.findall(r'\b\d+\b', texto)

def produto_contem_numeros(produto, numeros):
    texto_produto = f"{produto['nome']} {produto['desc']} {' '.join(produto['detalhes'])}"
    for num in numeros:
        if re.search(rf'\b{re.escape(num)}\b', texto_produto):
            return True
    return False

def filtrar_produtos_por_numeros(produtos, numeros):
    if not numeros:
        return produtos
    produtos_filtrados = [p for p in produtos if produto_contem_numeros(p, numeros)]
    return produtos_filtrados if produtos_filtrados else produtos

def detectar_serie(prompt):
    prompt = prompt.lower()

    ark_keywords = [
        "ark", "fanless", "intel core", "xeon", "embedded box pc", "industrial",
        "automacao industrial", "iot", "visao computacional", "i/o expansivel",
        "modular", "robusto", "temperatura ampla", "gerenciamento remoto",
        "pci", "pc industrial", "expansao pci", "machine vision", "ai", "gpu",
        "data acquisition", "comunicacao", "cabinet integration"
    ]

    epc_keywords = [
        "epc", "epc-", "epc fanless", "epc intel", "epc box", "edge pc",
        "edge computing", "computador compacto", "servidor compacto", "alto desempenho",
        "computacao de borda", "din-rail", "m2", "m.2", "usb", "lan", "rs232",
        "rs485", "isolado", "canbus", "iot gateway", "edge ai", "gateway"
    ]

    ubx_keywords = [
        "ubx", "ubx series", "ubx fanless", "ubx industrial", "mini pc",
        "ultra compacto", "tiny pc", "pc pequeno", "formato reduzido",
        "sem ventoinha pequeno", "kiosk pc", "pdv", "pos system",
        "display", "touchscreen", "hmi", "interface homem maquina",
        "sinalizacao digital", "retalho", "ponto de venda"
    ]

    air_keywords = [
        "air", "ai inference system", "ai inference", "gpu", "deep learning",
        "visao computacional", "inteligencia artificial", "edge ai",
        "processamento de imagem", "ai pc", "sdk", "ros", "openvino",
        "intel edge insights", "robotic sdk", "iot analytics",
        "manufacturing ai", "healthcare ai", "retail ai"
    ]

    ids_keywords = [
        "monitor industrial", "display industrial", "tela robusta",
        "touchscreen industrial", "hmi", "painel de controle", "painel touch",
        "interface homem maquina", "painel mount", "ip65", "ip67",
        "resistente a agua", "resistente a poeira", "industria", "automacao"
    ]

    idk_keywords = [
        "open frame", "display leve", "tela fina", "kit de display",
        "display embutido", "modulo de tela", "display para integracao",
        "sem moldura", "integracao personalizada", "OEM", "panel mount",
        "display industrial", "touchscreen", "automacao", "manufatura"
    ]

    if any(k in prompt for k in epc_keywords):
        return "EPC"
    if any(k in prompt for k in ark_keywords):
        return "ARK"
    if any(k in prompt for k in ubx_keywords):
        return "UBX"
    if any(k in prompt for k in air_keywords):
        return "AIR"
    if any(k in prompt for k in ids_keywords):
        return "IDS"
    if any(k in prompt for k in idk_keywords):
        return "IDK"
    return None

def filtrar_por_serie_detectada(produtos, serie_detectada):
    if not serie_detectada:
        return produtos
    return [p for p in produtos if p['nome'].upper().startswith(serie_detectada)]

class UserInput(BaseModel):
    texto: str

@app.post("/recomendar")
def recomendar(input: UserInput):
    texto_cliente = input.texto.lower()
    numeros_consulta = extrair_numeros(texto_cliente)
    serie_detectada = detectar_serie(texto_cliente)
    
    produtos_serie_filtrados = filtrar_por_serie_detectada(produtos, serie_detectada)
    produtos_filtrados = filtrar_produtos_por_numeros(produtos_serie_filtrados, numeros_consulta)

    model = get_model()
    produtos_textos_filtrados = [
        f"{p['nome']} {p['desc']} {' '.join(p['detalhes'])}" for p in produtos_filtrados
    ]
    produtos_embeddings_filtrados = model.encode(produtos_textos_filtrados, convert_to_numpy=True)
    faiss.normalize_L2(produtos_embeddings_filtrados)

    embedding_dim = produtos_embeddings_filtrados.shape[1]
    index_filtrado = faiss.IndexFlatIP(embedding_dim)
    index_filtrado.add(produtos_embeddings_filtrados)

    input_embedding = model.encode([texto_cliente], convert_to_numpy=True)
    faiss.normalize_L2(input_embedding)

    k = 6
    distances, indices = index_filtrado.search(input_embedding, k)
    recomendados = [produtos_filtrados[i] for i in indices[0]]

    for p in recomendados:
        if 'product_url' not in p or not p['product_url']:
            p['product_url'] = "#"  

    return {"recomendados": recomendados}

# Configuração do uvicorn para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)