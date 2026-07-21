from sympy import symbols, sin, cos, log, pi, E, latex, Expr, Symbol, Add, Mul, Pow, Integer, exp, tan, sec, csc, Float, Number, cot, asin, acos, atan, acot, asec, acsc, simplify, solve, Eq, parse_expr
from sympy.functions.elementary.trigonometric import TrigonometricFunction, InverseTrigonometricFunction

x = symbols("x")

def proceso(funcionn):
    pasos = []

    def derivar(funcionn):
        if isinstance(funcionn, (int, Float, Integer, Number)) or funcionn == E or funcionn == pi:
            pasos.append({"tipo": "paso",
                          "regla": "Regla de la constante",
                          "explicacion": f"La derivada de una constante siempre es 0. Fórmula: $ \\frac{{d}}{{dx}}[c] = 0 $",
                          "original": latex(funcionn),
                          "derivada": "0"})
            return 0
        elif isinstance(funcionn, Symbol):
            pasos.append({"tipo": "paso",
                          "regla": "Regla de la variable",
                          "explicacion": f"La derivada de la variable de integración respecto a sí misma es 1. Fórmula: $ \\frac{{d}}{{dx}}[x] = 1 $",
                          "original": latex(funcionn),
                          "derivada": "1"})
            return 1
        elif isinstance(funcionn, Pow):
            argumentos = list(funcionn.args)
            base = argumentos[0]
            exponente = argumentos[1]
            if isinstance(exponente, (Integer, int, Float)) and isinstance(base, Symbol):
                nuevo_exponente = exponente - 1
                resultado = (exponente * (base**nuevo_exponente))
                pasos.append({"tipo": "paso",
                              "regla": "Regla de la potencia",
                              "explicacion": f"Se baja el exponente a multiplicar y se le resta 1. Fórmula: $ \\frac{{d}}{{dx}}[x^n] = n \\cdot x^{{n-1}} $",
                              "original": latex(funcionn),
                              "derivada": latex(resultado)})
                return resultado
            elif isinstance(exponente, (Integer, int, Float)):
                pasos.append({"tipo": "inicio",
                              "regla": "Regla de la potencia con regla de la cadena",
                              "explicacion": f"Fórmula: $ \\frac{{d}}{{dx}}[u^n] = n \\cdot u^{{n-1}} \\cdot u' $. La base {latex(base)} es una función, así que bajamos el exponente, le restamos 1 y multiplicamos por la derivada interna.",
                              "original": latex(funcionn)})
                resul = derivar_potencia(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
            else:
                pasos.append({"tipo": "inicio",
                              "regla": "Regla de la potencia con exponente variable",
                              "explicacion": f"Fórmula: $ \\frac{{d}}{{dx}}[u^v] = u^v \\left( v' \\ln(u) + v \\frac{{u'}}{{u}} \\right) $. Se transforma la función usando $ u^v = e^{{v \\ln(u)}} $ y se aplica la regla de la cadena exponencial.",
                              "original": latex(funcionn)})
                resul = derivar_potencia(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
        elif isinstance(funcionn, exp):
            pasos.append({"tipo": "inicio",
                          "regla": "Regla de la función exponencial (Euler)",
                          "explicacion": f"Fórmula: $ \\frac{{d}}{{dx}}[e^u] = e^u \\cdot u' $. La base exponencial queda igual y se multiplica por la derivada de su exponente.",
                          "original": latex(funcionn)})
            resul = derivar_euler(funcionn)
            pasos.append({"tipo": "fin",
                          "derivada": latex(resul)})
            return resul
        elif isinstance(funcionn, Add):
            pasos.append({"tipo": "inicio",
                          "regla": "Regla de la suma y resta",
                          "explicacion": f"Fórmula: $ \\frac{{d}}{{dx}}[u \\pm v] = u' \\pm v' $. Se deriva cada término de la expresión por separado.",
                          "original": latex(funcionn)})
            resul = derivar_suma(funcionn)
            pasos.append({"tipo": "fin",
                          "derivada": latex(resul)})
            return resul
        elif isinstance(funcionn, Mul):
            numerador, denominador = funcionn.as_numer_denom()
            if denominador != 1:
                pasos.append({"tipo": "inicio",
                              "regla": "Regla del cociente (División)",
                              "explicacion": f"Fórmula: $ \\frac{{d}}{{dx}}\\left[\\frac{{u}}{{v}}\\right] = \\frac{{u'v - uv'}}{{v^2}} $. Derivamos el numerador {latex(numerador)} y el denominador {latex(denominador)} por separado.",
                              "original": latex(funcionn)})
                resul = derivar_division(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
            else:
                pasos.append({"tipo": "inicio",
                              "regla": "Regla del producto (Multiplicación)",
                              "explicacion": f"Fórmula: $ \\frac{{d}}{{dx}}[u \\cdot v] = u'v + uv' $. Se deriva cada factor y se aplica la regla cruzada.",
                              "original": latex(funcionn)})
                resul = derivar_multiplicacion(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
        elif isinstance(funcionn, log):
            pasos.append({"tipo": "inicio",
                          "regla": "Regla del Logaritmo Natural",
                          "explicacion": f"Fórmula: $ \\frac{{d}}{{dx}}[\\ln(u)] = \\frac{{1}}{{u}} \\cdot u' $. Se coloca el argumento dividiendo a 1, y se multiplica por la derivada interna.",
                          "original": latex(funcionn)})
            resul = derivar_logaritmo(funcionn)
            pasos.append({"tipo": "fin",
                          "derivada": latex(resul)})
            return resul
        elif isinstance(funcionn, TrigonometricFunction):
            return derivar_trigonometrica(funcionn)
        elif isinstance(funcionn, InverseTrigonometricFunction):
            return derivar_arco_trigonometrica(funcionn)

    def derivar_potencia(potencia):
        argumentos = list(potencia.args)
        base = argumentos[0]
        exponente = argumentos[1]
        if isinstance(exponente, (Integer, int, Float)):
            nuevo_exponente = exponente - 1
            cadena = derivar(base)
            resultado = (exponente * (base**nuevo_exponente))*cadena
            return resultado
        else:
            transformacion = E**(exponente*log(base))
            prueba = derivar(transformacion)
            resultado = list(prueba.args)
            for i in resultado:
                if i == transformacion:
                    resultado.remove(i)
                    resultado.append(base**exponente)
                else:
                    return Mul(*resultado)

    def derivar_euler(potencia_euler):
        argumento = list(potencia_euler.args)
        cadena = derivar(argumento[0])
        resultado = potencia_euler * cadena
        return resultado

    def derivar_suma(polinomio):
        argumentos = polinomio.as_ordered_terms()
        lista_resultado = []
        for i in argumentos:
            derivada_termino = derivar(i)
            lista_resultado.append(derivada_termino)
        resultado_real = sum(lista_resultado)
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
        return sum(resultado)

    def derivar_division(division):
        numerador, denominador = division.as_numer_denom()
        derivada_numerador = derivar(numerador)
        derivada_denominador = derivar(denominador)
        izquierdo = derivada_numerador * denominador
        derecho = numerador * derivada_denominador
        return (izquierdo-derecho)/denominador**2

    def derivar_logaritmo(logaritmo):
        argumento = list(logaritmo.args)
        exponente = argumento[0]
        cadena = derivar(exponente)
        if not isinstance(exponente, (Integer, int, Float)):
            resultado = (1/exponente)*cadena
            return resultado
        else:
            return 0

    def derivar_trigonometrica(funcion):
        argumento = list(funcion.args)
        interno = argumento[0]
        tipo = type(funcion)

        reglas_trig = {
            sin: ("Regla del Seno", r"\frac{d}{dx}[\sin(u)] = \cos(u) \cdot u'"),
            cos: ("Regla del Coseno", r"\frac{d}{dx}[\cos(u)] = -\sin(u) \cdot u'"),
            tan: ("Regla de la Tangente", r"\frac{d}{dx}[\tan(u)] = \sec^2(u) \cdot u'"),
            sec: ("Regla de la Secante", r"\frac{d}{dx}[\sec(u)] = \sec(u)\tan(u) \cdot u'"),
            csc: ("Regla de la Cosecante", r"\frac{d}{dx}[\csc(u)] = -\csc(u)\cot(u) \cdot u'"),
            cot: ("Regla de la Cotangente", r"\frac{d}{dx}[\cot(u)] = -\csc^2(u) \cdot u'")
        }

        nombre_regla, formula = reglas_trig.get(tipo, ("Regla Trigonométrica", ""))

        pasos.append({"tipo": "inicio",
                      "regla": nombre_regla,
                      "explicacion": f"Fórmula: $ {formula} $. Se deriva la función principal y se multiplica por la derivada interna (regla de la cadena).",
                      "original": latex(funcion)})

        cadena = derivar(interno)

        if tipo == sin:
            resul = cos(interno) * cadena
        elif tipo == cos:
            resul = -sin(interno) * cadena
        elif tipo == tan:
            resul = (sec(interno))**2 * cadena
        elif tipo == sec:
            resul = (sec(interno))*(tan(interno))*cadena
        elif tipo == csc:
            resul = -csc(interno)*cot(interno)*cadena
        elif tipo == cot:
            resul = -(csc(interno)**2)*cadena
        else:
            resul = 0

        pasos.append({"tipo": "fin",
                      "derivada": latex(resul)})
        return resul

    def derivar_arco_trigonometrica(funcion):
        argumento = list(funcion.args)
        interno = argumento[0]
        tipo = type(funcion)

        reglas_arco = {
            asin: ("Regla del Arcoseno", r"\frac{d}{dx}[\arcsin(u)] = \frac{1}{\sqrt{1-u^2}} \cdot u'"),
            acos: ("Regla del Arcocoseno", r"\frac{d}{dx}[\arccos(u)] = -\frac{1}{\sqrt{1-u^2}} \cdot u'"),
            atan: ("Regla de la Arcotangente", r"\frac{d}{dx}[\arctan(u)] = \frac{1}{1+u^2} \cdot u'"),
            asec: ("Regla de la Arcosecante", r"\frac{d}{dx}[\text{arcsec}(u)] = \frac{1}{|u|\sqrt{u^2-1}} \cdot u'"),
            acsc: ("Regla de la Arcocosecante", r"\frac{d}{dx}[\text{arccsc}(u)] = -\frac{1}{|u|\sqrt{u^2-1}} \cdot u'"),
            acot: ("Regla de la Arcocotangente", r"\frac{d}{dx}[\text{arccot}(u)] = -\frac{1}{1+u^2} \cdot u'")
        }

        nombre_regla, formula = reglas_arco.get(tipo, ("Regla Arcotrigonométrica", ""))

        pasos.append({"tipo": "inicio",
                      "regla": nombre_regla,
                      "explicacion": f"Fórmula: $ {formula} $. Aplicamos la fórmula y multiplicamos por la derivada del argumento interno.",
                      "original": latex(funcion)})

        cadena = derivar(interno)

        if tipo == asin:
            multiplicador = 1/((1-interno**2)**(1/2))
            resul = multiplicador * cadena
        elif tipo == acos:
            multiplicador = -(1/((1-interno**2)**(1/2)))
            resul = multiplicador * cadena
        elif tipo == atan:
            multiplicador = 1/(1+interno**2)
            resul = multiplicador * cadena
        elif tipo == asec:
            multiplicador = 1/(abs(interno)*(((interno**2)-1)**(1/2)))
            resul = multiplicador * cadena
        elif tipo == acsc:
            multiplicador = -(1/(abs(interno)*(((interno**2)-1)**(1/2))))
            resul = multiplicador * cadena
        elif tipo == acot:
            multiplicador = -(1/(1+interno**2))
            resul = multiplicador * cadena
        else:
            resul = 0

        pasos.append({"tipo": "fin",
                      "derivada": latex(resul)})
        return resul

    resultado = derivar(funcionn)
    return resultado, pasos

def recta_tangente(funcion, punto_en_x):
    funcion_derivada = proceso(funcion)[0]
    pendiente = funcion_derivada.subs(x, punto_en_x).evalf()
    punto_en_y = funcion.subs(x, punto_en_x).evalf()
    b = punto_en_y-(pendiente*punto_en_x)
    return pendiente*x + b
