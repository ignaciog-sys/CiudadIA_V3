import re
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="CiudadAI v3.0 - Motor Inteligente")

# --- LÓGICA DE PRIVACIDAD MEJORADA ---
def anonimizar_texto(texto: str) -> str:
    # DNI: 8 números y 1 letra (al inicio, al final o entre texto)
    # Soporta minúsculas y no requiere espacios alrededor
    patron_dni = r'\d{8}[a-zA-Z]'
    texto = re.sub(patron_dni, '[DNI_OCULTO]', texto)
    
    # Email: Patrón más robusto
    patron_email = r'[\w\.-]+@[\w\.-]+\.\w+'
    texto = re.sub(patron_email, '[EMAIL_OCULTO]', texto)
    
    return texto

# --- LÓGICA DE CATEGORIZACIÓN (IA BÁSICA) ---
def clasificar_incidencia(texto: str) -> str:
    texto = texto.lower()
    if any(palabra in texto for palabra in ["luz", "farola", "electricidad", "oscuro"]):
        return "Alumbrado"
    if any(palabra in texto for palabra in ["bache", "calle", "acera", "agujero", "pavimento"]):
        return "Vía Pública"
    if any(palabra in texto for palabra in ["basura", "olor", "sucio", "limpieza", "contenedor"]):
        return "Limpieza"
    return "General"

class Ticket(BaseModel):
    contenido: str

@app.post("/procesar")
async def procesar_ticket(ticket: Ticket):
    # 1. Limpiamos datos sensibles
    texto_anonimo = anonimizar_texto(ticket.contenido)
    
    # 2. Clasificamos la temática
    categoria = clasificar_incidencia(texto_anonimo)
    
    return {
        "texto_limpio": texto_anonimo,
        "categoria_asignada": categoria,
        "longitud_caracteres": len(texto_anonimo)
    }

@app.get("/")
def check():
    return {"status": "ready", "engine": "Privacy + Classifier"}