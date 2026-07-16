from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sympy as sp
from sympy import E

# Importamos las herramientas de SymPy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# Importamos las funciones locales (lógica matemática separada)
from calculadora import proceso, recta_tangente

app = FastAPI()

# Configuración de CORS para permitir la conexión desde tu frontend (HTML)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos que espera recibir el servidor
class PeticionCalculadora(BaseModel):
    ecuacion: str
    punto_x: Optional[float] = None

@app.post("/conectar")
async def calcular_derivada_y_tangente(req: PeticionCalculadora):
    try:
        # Transformaciones para interpretar la entrada del usuario (ej. 2x -> 2*x)
        transformaciones = standard_transformations + (implicit_multiplication_application,)

        # 1. Convertimos el string a SymPy
        # FIX: Se incluye local_dict para resolver el problema de Euler ('e' y 'E')
        f_x = parse_expr(
            req.ecuacion,
            local_dict={'e': E, 'E': E},
            transformations=transformaciones
        )

        # FIX: Forzamos que la función sea estrictamente de SymPy (evita el error 'int has no attribute')
        f_x = sp.sympify(f_x)

        # 2. Derivamos utilizando tu función importada
        f_prima, pasos_json = proceso(f_x)

        # FIX: Forzamos la derivada a SymPy (Si proceso() devuelve un '0' o '1' nativo, esto lo repara)
        f_prima = sp.sympify(f_prima)

        # Preparamos la respuesta base
        respuesta = {
            "status": "success",
            "derivada": sp.latex(f_prima),
            "pasos": pasos_json
        }

        # 3. Recta tangente (Solo si el usuario envió un valor para x)
        if req.punto_x is not None:
            recta_tang = recta_tangente(f_x, req.punto_x)
            respuesta["tangente"] = sp.latex(recta_tang)
            respuesta["punto_evaluado"] = req.punto_x

        return respuesta

    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == '__main__':
    import uvicorn
    # Inicia el servidor usando Uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
