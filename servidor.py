from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)
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

        f_x = parse_expr(req.ecuacion, transformations=transformaciones)
        f_x = sp.sympify(f_x)

        f_prima, pasos_json = proceso(f_x)
        f_prima = sp.sympify(f_prima)

        recta_tang = recta_tangente(f_x, req.punto_x)

        return {
            "status": "success",
            "derivada": sp.latex(f_prima),
            "tangente": sp.latex(recta_tang),
            "punto_evaluado": req.punto_x,
            "pasos": pasos_json
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}
