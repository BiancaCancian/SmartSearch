from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import json
import faiss
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

model = SentenceTransformer('all-MiniLM-L6-v2')

with open("produtos.json", "r", encoding="utf-8") as f:
    produtos = json.load(f)



def extrair_numeros(texto):
    return re.findall(r'\b\d+\b', texto)

def produto_contem_numeros(produto, numeros):
    texto_produto = f"{produto['nome']} {produto.get('desc','')} {' '.join(produto.get('detalhes', []))}"
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
    
    epc_keywords = ["epc", "slim", "pequeno", "sem ventoinha",
                    "motherboards", "placas mãe", "mini pc", "mini computador"]
    ark_keywords = ["ark", "sem ventoinha", "fanless", "industrial pc fanless",
                    "industrial pc", "embedded", "embarcado", 
                    "fanless embedded computers", "in-vehicle", "i/o", "ultra-small"]
    ubx_keywords = ["ubx", "advanpos", "oem/odm", "ponto de venda", "point of sale",
                    "mini edge servers", "pontos de autoatendimento"]
    air_keywords = ["air", "cpu", "npu", "ai", "integração de ia", "inteligência artificial",
                    "nvidia", "jetson", "jetson agx orin", "jetson nano", "inferência de ia",
                    "machine learning", "visão computacional"]
    ids_keywords = ["monitor sem carcaça", "ip65", "touchscreen", "tela touch", "open frame monitor",
                    "curved monitor", "monitor curvo", "all-in-one", "tudo em um", "lcd monitor", 
                    "sistemas de display", "industrial displays", "monitores industriais"]
    idk_keywords = ["kit display industrial", "industrial display kit", "lcd panels", "open frame display",
                    "saude", "saúde", "healthcare", "hospital", "medicina", "médico", "medical", 
                    "clínica", "diagnóstico", "gaming"]
    dsd_keywords = ["digital signage", "sinalização digital", "publicidade digital", "outdoor",
                    "indoor", "totem", "kiosk", "quiosque", "advertising", "advertisement"]

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
    if any(k in prompt for k in dsd_keywords):
        return "DSD"    
    
    return None

def filtrar_por_serie_detectada(produtos, serie_detectada):
    if not serie_detectada:
        return produtos
    filtrados = [p for p in produtos if p['nome'].upper().startswith(serie_detectada)]
    return filtrados

def rank_produto(produto):
    processador_peso = {"i3": 1, "i5": 2, "i7": 3, "i9": 4}
    linha_peso = {"basic": 1, "x": 2, "premium": 3}

    texto = f"{produto['nome']} {produto.get('desc','')}".lower()

    proc = max((p for p in processador_peso if p in texto), default=None)
    peso_proc = processador_peso.get(proc, 0)

    linha = max((l for l in linha_peso if l in texto), default=None)
    peso_linha = linha_peso.get(linha, 0)

    return peso_proc + peso_linha



class UserInput(BaseModel):
    texto: str

@app.post("/recomendar")
def recomendar(input: UserInput):
    texto_cliente = input.texto.lower()
    numeros_consulta = extrair_numeros(texto_cliente)
    serie_detectada = detectar_serie(texto_cliente)

    produtos_serie_filtrados = filtrar_por_serie_detectada(produtos, serie_detectada)
    if not produtos_serie_filtrados:
        produtos_serie_filtrados = produtos  

    produtos_filtrados = filtrar_produtos_por_numeros(produtos_serie_filtrados, numeros_consulta)
    if not produtos_filtrados:
        produtos_filtrados = produtos_serie_filtrados  

    produtos_textos_filtrados = [
        f"{p['nome']} {p.get('desc','')} {' '.join(p.get('detalhes', []))}" for p in produtos_filtrados
    ]
    produtos_embeddings_filtrados = model.encode(produtos_textos_filtrados, convert_to_numpy=True)
    faiss.normalize_L2(produtos_embeddings_filtrados)

    embedding_dim = produtos_embeddings_filtrados.shape[1]
    index_filtrado = faiss.IndexFlatIP(embedding_dim)
    index_filtrado.add(produtos_embeddings_filtrados)

    input_embedding = model.encode([texto_cliente], convert_to_numpy=True)
    faiss.normalize_L2(input_embedding)

    k = min(6, len(produtos_filtrados))
    distances, indices = index_filtrado.search(input_embedding, k)
    recomendados = [produtos_filtrados[i] for i in indices[0]]

    if len(texto_cliente.strip()) < 5 or len(texto_cliente.split()) < 3:
        ordenados = sorted(produtos_filtrados, key=rank_produto)
        if len(ordenados) >= 2:
            recomendados = [ordenados[0], ordenados[-1]]

    return {"recomendados": recomendados}