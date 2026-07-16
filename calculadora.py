from sympy import symbols, sin, cos, log, pi, E, latex, Expr, Symbol, Add, Mul, Pow, Integer, exp, tan, sec, csc, Float, Number, Rational, cot, asin, acos, atan, acot, asec, acsc, simplify, solve, Eq, parse_expr
from sympy.functions.elementary.trigonometric import TrigonometricFunction, InverseTrigonometricFunction

x = symbols("x")

def proceso(funcionn):
    pasos = []

    def derivar(funcionn):
        if isinstance(funcionn, (int, float, Number)) or funcionn == E or funcionn == pi:
            pasos.append({"tipo": "paso",
                          "regla": "Regla de la constante",
                          "explicacion": f"El numero {latex(funcionn)}, se convierte en 0",
                          "original": latex(funcionn),
                          "derivada": "0"})
            return Integer(0)
        elif isinstance(funcionn, Symbol):
            pasos.append({"tipo": "paso",
                          "regla": "Regla de la variable",
                          "explicacion": f"Las variables sin coeficientes, se convierten en 1",
                          "original": latex(funcionn),
                          "derivada": "1"})
            return Integer(1)
        elif isinstance(funcionn, Pow):
            argumentos = list(funcionn.args)
            base = argumentos[0]
            exponente = argumentos[1]
            if isinstance(exponente, (int, float, Number)) and isinstance(base, Symbol):
                nuevo_exponente = exponente - 1
                resultado = (exponente * (base**nuevo_exponente))
                pasos.append({"tipo": "paso",
                              "regla": "Regla de la potencia",
                              "explicacion": f"Como la base {latex(base)} es una variable, se les resta 1 a su indice y se baja este mismo a multiplicar",
                              "original": latex(funcionn),
                              "derivada": latex(resultado)})
                return resultado
            elif isinstance(exponente, (int, float, Number)):
                pasos.append({"tipo": "inicio",
                              "regla": "Regla de la potencia con cadena",
                              "explicacion": f"Como la base {latex(base)} es una funcion, a esta se le resta 1 al indice, se baja este mismo a multiplicar y se aplica regla de la cadena",
                              "original": latex(funcionn)})
                resul = derivar_potencia(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
            else:
                pasos.append({"tipo": "inicio",
                              "regla": "Regla de la potencia con exponente variable",
                              "explicacion": f"Como el exponente {latex(exponente)} es variable, se transforma la funcion en {latex(E**(exponente*log(base)))} que significa lo mismo, y se opera como euler",
                              "original": latex(funcionn)})
                resul = derivar_potencia(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
        elif isinstance(funcionn, exp):
            pasos.append({"tipo": "inicio",
                          "regla": "Regla de Euler",
                          "explicacion": f"Como la base es E, se deja igual y se aplica regla de la cadena, derivando el exponente y multiplicandolo",
                          "original": latex(funcionn)})
            resul = derivar_euler(funcionn)
            pasos.append({"tipo": "fin",
                          "derivada": latex(resul)})
            return resul
        elif isinstance(funcionn, Add):
            pasos.append({"tipo": "inicio",
                          "regla": "Regla de la suma",
                          "explicacion": f"Se derivan todos los termino y se operan si es el caso",
                          "original": latex(funcionn)})
            resul = derivar_suma(funcionn)
            pasos.append({"tipo": "fin",
                          "derivada": latex(resul)})
            return resul
        elif isinstance(funcionn, Mul):
            numerador, denominador = funcionn.as_numer_denom()
            if denominador != 1:
                pasos.append({"tipo": "inicio",
                              "regla": "Regla de el cociente",
                              "explicacion": f"Se deriva tanto el numerador {numerador}, como el denominador {denominador} y se aplia la regla de derivacion",
                              "original": latex(funcionn)})
                resul = derivar_division(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
            else:
                pasos.append({"tipo": "inicio",
                              "regla": "Regla de la multiplicacion",
                              "explicacion": f"Se derivan todos los miembros y se aplica la regla",
                              "original": latex(funcionn)})
                resul = derivar_multiplicacion(funcionn)
                pasos.append({"tipo": "fin",
                              "derivada": latex(resul)})
                return resul
        elif isinstance(funcionn, log):
            return derivar_logaritmo(funcionn)
        elif isinstance(funcionn, TrigonometricFunction):
            return derivar_trigonometrica(funcionn)
        elif isinstance(funcionn, InverseTrigonometricFunction):
            return derivar_arco_trigonometrica(funcionn)

    def derivar_potencia(potencia):
        argumentos = list(potencia.args)
        base = argumentos[0]
        exponente = argumentos[1]
        if isinstance(exponente, (int, float, Number)):
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
        if not isinstance(exponente, (int, float, Number)):
            resultado = (1/exponente)*cadena
            return resultado
        else:
            return Integer(0)

    def derivar_trigonometrica(funcion):
        pasos.append({"tipo": "inicio",
                      "regla": "Regla de función trigonométrica",
                      "explicacion": f"Se deriva la función trigonométrica {latex(funcion)} aplicando la regla correspondiente y multiplicando por la derivada interna",
                      "original": latex(funcion)})
        argumento = list(funcion.args)
        interno = argumento[0]
        cadena = derivar(interno)
        tipo = type(funcion)

        def derivar_seno(seno):
            return cos(interno) * cadena
        def derivar_coseno(coseno):
            return -sin(interno) * cadena
        def derivar_tangente(tangente):
            return (sec(interno))**2 * cadena
        def derivar_secante(secante):
            return (sec(interno))*(tan(interno))*cadena
        def derivar_cosecante(cosecante):
            return -csc(interno)*cot(interno)*cadena
        def derivar_cotangente(cotangente):
            return -(csc(interno)**2)*cadena

        resul = 0
        if tipo == sin:
            resul = derivar_seno(interno)
        elif tipo == cos:
            resul = derivar_coseno(interno)
        elif tipo == tan:
            resul = derivar_tangente(interno)
        elif tipo == sec:
            resul = derivar_secante(interno)
        elif tipo == csc:
            resul = derivar_cosecante(interno)
        elif tipo == cot:
            resul = derivar_cotangente(interno)

        pasos.append({"tipo": "fin",
                      "derivada": latex(resul)})
        return resul

    def derivar_arco_trigonometrica(funcion):
        pasos.append({"tipo": "inicio",
                      "regla": "Regla de función arcotrigonométrica",
                      "explicacion": f"Se deriva la función arcotrigonométrica {latex(funcion)} aplicando la regla correspondiente y multiplicando por la derivada interna",
                      "original": latex(funcion)})
        argumento = list(funcion.args)
        interno = argumento[0]
        cadena = derivar(interno)
        tipo = type(funcion)

        def derivar_arcoseno():
            multiplicador = 1/((1-interno**2)**(1/2))
            return multiplicador * cadena
        def derivar_arcocoseno():
            multiplicador = -(1/((1-interno**2)**(1/2)))
            return multiplicador * cadena
        def derivar_arcotangente():
            multiplicador = 1/(1+interno**2)
            return multiplicador * cadena
        def derivar_arcosecante():
            multiplicador = 1/(abs(interno)*(((interno**2)-1)**(1/2)))
            return multiplicador * cadena
        def derivar_arcocosecante():
            multiplicador = -(1/(abs(interno)*(((interno**2)-1)**(1/2))))
            return multiplicador * cadena
        def derivar_arcocotangente():
            multiplicador = -(1/(1+interno**2))
            return multiplicador * cadena

        resul = 0
        if tipo == asin:
            resul = derivar_arcoseno()
        elif tipo == acos:
            resul = derivar_arcocoseno()
        elif tipo == atan:
            resul = derivar_arcotangente()
        elif tipo == asec:
            resul = derivar_arcosecante()
        elif tipo == acsc:
            resul = derivar_arcocosecante()
        elif tipo == acot:
            resul = derivar_arcocotangente()

        pasos.append({"tipo": "fin",
                      "derivada": latex(resul)})
        return resul

    resultado = derivar(funcionn)
    return resultado, pasos

def recta_tangente(funcion, punto_en_x):
    funcion_derivada = proceso(funcion)[0]
    pendiente = round(funcion_derivada.subs(x, punto_en_x).evalf(), 2)
    punto_en_y = round(funcion.subs(x, punto_en_x).evalf(), 2)
    b = round(punto_en_y - (pendiente * punto_en_x), 2)
    return pendiente * x + b
