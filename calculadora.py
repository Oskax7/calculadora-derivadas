from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sympy import (
    symbols, sin, cos, log, pi, E, latex, Symbol, Add, Mul, Pow, 
    Integer, exp, tan, sec, csc, Float, Number, cot, asin, acos, 
    atan, acot, asec, acsc, simplify, solve, parse_expr
)
from sympy.functions.elementary.trigonometric import TrigonometricFunction, InverseTrigonometricFunction
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

app = FastAPI()

# Configuración de CORS para permitir la conexión desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

x = symbols("x")
procedimiento = []

# =====================================================================
#                      MOTOR DE DERIVACIÓN ANALÍTICO
# =====================================================================

def derivar(funcionn):
    if isinstance(funcionn, (int, Float, Integer, Number)) or funcionn == E or funcionn == pi:
        procedimiento.append(["Se aplica regla de constante", 0])
        return 0
    elif isinstance(funcionn, Pow) and funcionn.args[0] == E:
        return derivar_euler(funcionn)
    elif isinstance(funcionn, Symbol):
        procedimiento.append(["Se aplica regla de variable", 1])
        return 1
    elif isinstance(funcionn, Pow):
        return derivar_potencia(funcionn)
    elif isinstance(funcionn, exp):
        return derivar_euler(funcionn)
    elif isinstance(funcionn, Add):
        return derivar_suma(funcionn)
    elif isinstance(funcionn, Mul):
        return derivar_multiplicacion(funcionn)
    elif isinstance(funcionn, log):
        return derivar_logaritmo(funcionn)
    elif isinstance(funcionn, TrigonometricFunction) or type(funcionn) in [sin, cos, tan, sec, csc, cot]:
        return derivar_trigonometrica(funcionn)
    elif isinstance(funcionn, InverseTrigonometricFunction) or type(funcionn) in [asin, acos, atan, asec, acsc, acot]:
        return derivar_arco_trigonometrica(funcionn)
    else:
        return funcionn._eval_derivative(x)

def derivar_potencia(potencia):
    argumentos = list(potencia.args)
    base = argumentos[0]
    exponente = argumentos[1]
    if isinstance(exponente, (Integer, int, Float)):
        nuevo_exponente = exponente - 1
        cadena = derivar(base)
        resultado = (exponente * (base**nuevo_exponente)) * cadena
        procedimiento.append(["Se aplica regla de derivacion basica", resultado])
        return resultado
    else:
        transformacion = E**(exponente * log(base))
        prueba = derivar(transformacion)
        resultado = list(prueba.args)
        for i in resultado:
            if i == transformacion:
                resultado.remove(i)
                resultado.append(base**exponente)
        procedimiento.append(["Se aplica regla de derivacion para potencias por medio de factorizacion", Mul(*resultado)])
        return Mul(*resultado)

def derivar_euler(potencia_euler):
    if isinstance(potencia_euler, exp):
        argumento = potencia_euler.args[0]
    else:
        argumento = potencia_euler.args[1]
        
    cadena = derivar(argumento)
    resultado = potencia_euler * cadena
    procedimiento.append(["Se aplica regla de derivacion Euler", resultado])
    return resultado

def derivar_suma(polinomio):
    argumentos = polinomio.as_ordered_terms()
    lista_resultado = []
    for i in argumentos:
        derivada_termino = derivar(i)
        lista_resultado.append(derivada_termino)
    resultado_real = sum(lista_resultado)
    procedimiento.append(["Se aplica regla de derivacion a cada termino en la suma", resultado_real])
    return resultado_real

def derivar_multiplicacion(multiplicacion):
    argumentos = list(multiplicacion.args)
    resultado = []
    for i in argumentos:
        derivacion = derivar(i)
        argumentos_multiplicacion = argumentos.copy()
        argumentos_multiplicacion.remove(i)
        argumentos_multiplicacion.append(derivacion)
        resultado.append(Mul(*argumentos_multiplicacion))
    procedimiento.append(["Se aplica regla de multiplicacion", sum(resultado)])
    return sum(resultado)

def derivar_logaritmo(logaritmo):
    argumento_interno = logaritmo.args[0]
    cadena = derivar(argumento_interno)
    
    if argumento_interno.is_number:
        procedimiento.append(["Se aplica regla de la constante", 0])
        return 0
        
    resultado = (1 / argumento_interno) * cadena
    procedimiento.append(["Se aplica regla de derivacion del logaritmo natural", resultado])
    return resultado

def derivar_trigonometrica(funcion):
    interno = funcion.args[0]
    cadena = derivar(interno)
    tipo = type(funcion)
    if tipo == sin:
        return cos(interno) * cadena
    elif tipo == cos:
        return -sin(interno) * cadena
    elif tipo == tan:
        return (sec(interno))**2 * cadena
    elif tipo == sec:
        return sec(interno) * tan(interno) * cadena
    elif tipo == csc:
        return -csc(interno) * cot(interno) * cadena
    elif tipo == cot:
        return -(csc(interno)**2) * cadena
    return funcion._eval_derivative(x)

def derivar_arco_trigonometrica(funcion):
    interno = funcion.args[0]
    cadena = derivar(interno)
    tipo = type(funcion)
    if tipo == asin:
        return (1 / ((1 - interno**2)**(0.5))) * cadena
    elif tipo == acos:
        return -(1 / ((1 - interno**2)**(0.5))) * cadena
    elif tipo == atan:
        return (1 / (1 + interno**2)) * cadena
    elif tipo == asec:
        return (1 / (abs(interno) * ((interno**2 - 1)**(0.5)))) * cadena
    elif tipo == acsc:
        return -(1 / (abs(interno) * ((interno**2 - 1)**(0.5)))) * cadena
    elif tipo == acot:
        return -(1 / (1 + interno**2)) * cadena
    return funcion._eval_derivative(x)


# =====================================================================
#                FUNCIONES AUXILIARES DE PROCESAMIENTO
# =====================================================================

def generar_coordenadas_grafica(funcion, derivada, variable, rango_x):
    valores_y_f = []
    valores_y_df = []
    for val_x in rango_x:
        try:
            eval_f = funcion.subs(variable, val_x).evalf()
            eval_df = derivada.subs(variable, val_x).evalf()
            valores_y_f.append(float(eval_f)) if eval_f.is_real else valores_y_f.append(None)
            valores_y_df.append(float(eval_df)) if eval_df.is_real else valores_y_df.append(None)
        except:
            valores_y_f.append(None)
            valores_y_df.append(None)
    return valores_y_f, valores_y_df

def calcular_puntos_criticos(funcion, derivada, variable):
    puntos = []
    try:
        soluciones = solve(derivada, variable)
        for sol in soluciones:
            if sol.is_real:
                coord_x = float(sol.evalf())
                coord_y = float(funcion.subs(variable, coord_x).evalf())
                puntos.append({"x": coord_x, "y": coord_y})
    except:
        pass
    return puntos


# =====================================================================
#                             ENDPOINT API
# =====================================================================

class EntradaEcuacion(BaseModel):
    ecuacion: str

@app.post("/conectar")
async def conectar(data: EntradaEcuacion):
    global procedimiento
    procedimiento = []
    
    try:
        transformaciones = standard_transformations + (implicit_multiplication_application,)
        diccionario_local = {
            "log": log, "sin": sin, "cos": cos, "tan": tan, 
            "E": E, "pi": pi, "exp": exp, "abs": abs
        }
        
        funcion_sympy = parse_expr(
            data.ecuacion, 
            local_dict=diccionario_local, 
            transformations=transformaciones
        )
        
        derivada_sympy = derivar(funcion_sympy)
        valores_x = [float(i / 10) for i in range(-50, 51)]
        valores_y_f, valores_y_df = generar_coordenadas_grafica(funcion_sympy, derivada_sympy, x, valores_x)
        puntos_criticos = calcular_puntos_criticos(funcion_sympy, derivada_sympy, x)
        
        return {
            "resultado": latex(simplify(derivada_sympy)), 
            "valores_x": valores_x,
            "valores_y_f": valores_y_f,
            "valores_y_df": valores_y_df,
            "puntos_criticos": puntos_criticos
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar la expresión: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)