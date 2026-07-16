from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from calculadora import derivar
from sympy import symbols, sin, cos, log, pi, E, latex, Expr, Symbol, Add, Mul, Pow, Integer, exp, tan, sec, csc, Float, Number, cot, asin, acos, atan, acot, asec, acsc, simplify, solve, Eq, parse_expr

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

class EntradaEcuacion(BaseModel):
    ecuacion: str

@app.post("/conectar")
async def mandar_a_HTML (datos: EntradaEcuacion):
    try:
        x = Symbol('x')
        expresion = parse_expr(datos.ecuacion)
        expresion_derivada = derivar(expresion)
        respuesta = latex(expresion_derivada)
        return {"status": "success", "resultado": respuesta}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la expresión: {str(e)}")