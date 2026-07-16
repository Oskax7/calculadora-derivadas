from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp

# Importamos las herramientas de SymPy para entender el "2x" sin asterisco
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# 1. Importamos TUS funciones desde tu archivo calculadora.py
# (Asegúrate de que calculadora.py esté en la misma carpeta que este archivo)
from calculadora import proceso, recta_tangente

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PeticionCalculadora(BaseModel):
    ecuacion: str
    punto_x: float = 1.0

@app.post("/conectar")
async def calcular_derivada_y_tangente(req: PeticionCalculadora):
    try:
        # --- AQUÍ ESTÁ EL CAMBIO CLAVE ---
        # Configuramos SymPy para que entienda multiplicaciones implícitas (ej: "2x" -> "2*x")
        transformaciones = standard_transformations + (implicit_multiplication_application,)

        # Convertimos el string que llega de JS a una expresión matemática de SymPy
        f_x = parse_expr(req.ecuacion, transformations=transformaciones)
        # ---------------------------------

        # 2. Usamos TU función para derivar y obtener los pasos
        # Asumiendo que retorna dos valores: la derivada y el JSON/diccionario de los pasos
        f_prima, pasos_json = proceso(f_x)

        # 3. Usamos TU función para la recta tangente
        # Le pasamos la función original de sympy y el punto que llegó del frontend
        recta_tang = recta_tangente(f_x, req.punto_x)

        # 4. Convertimos los resultados a formato LaTeX para que se vean bien en el HTML
        derivada_latex = sp.latex(f_prima)
        tangente_latex = sp.latex(recta_tang)

        return {
            "status": "success",
            "resultado": derivada_latex,        # Derivada general en LaTeX
            "tangente": tangente_latex,         # Recta tangente en LaTeX
            "punto_evaluado": req.punto_x,      # Punto x utilizado
            "pasos": pasos_json                 # ¡Aquí enviamos tus pasos al frontend!
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}