from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp

# Importamos las herramientas de SymPy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# Tus funciones locales
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
        transformaciones = standard_transformations + (implicit_multiplication_application,)

        # 1. Convertimos el string a SymPy
        f_x = parse_expr(req.ecuacion, transformations=transformaciones)

        # FIX: Forzamos que la función sea estrictamente de SymPy (evita el error 'int has no attribute')
        f_x = sp.sympify(f_x)

        # 2. Derivamos con tu función
        f_prima, pasos_json = proceso(f_x)

        # FIX: Forzamos la derivada a SymPy (Si proceso() devuelve un '0' o '1' nativo, esto lo repara)
        f_prima = sp.sympify(f_prima)

        # 3. Recta tangente
        recta_tang = recta_tangente(f_x, req.punto_x)

        return {
            "status": "success",
            "resultado": sp.latex(f_prima),
            "tangente": sp.latex(recta_tang),
            "punto_evaluado": req.punto_x,
            "pasos": pasos_json
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}
