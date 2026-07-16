// =====================================================================
// 1. VARIABLES GLOBALES Y LISTENERS DE PANTALLA
// =====================================================================
const pantalla = document.getElementById('pantalla');
const cursor = document.getElementById('cursor');
let datos = [];
let rutaCursor = [0];
let miGrafica = null; // Instancia global del gráfico de Chart.js

pantalla.addEventListener('focus', () => {
    cursor.classList.remove('oculto');
});

pantalla.addEventListener('blur', () => {
    cursor.classList.add('oculto');
});

pantalla.addEventListener('click', (event) => {
    if (event.target === pantalla) {
        rutaCursor = [datos.length];
        actualizarPantalla();
    }
});

pantalla.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Evita el salto de línea en el div
        enviarAPython();
    }
});

// =====================================================================
// 2. LOGÍSICA DEL ÁRBOL Y CURSOR VIRTUAL
// =====================================================================
function cambiarPestana(pestanaClickeda, idTecladoDestino) {
    const todasLasPestanas = document.querySelectorAll('.pestana');
    todasLasPestanas.forEach(p => p.classList.remove('activa'));

    pestanaClickeda.classList.add('activa');

    const todosLosTeclados = document.querySelectorAll('#contenedor-teclados .cuadrante-botones');
    todosLosTeclados.forEach(t => t.style.display = 'none');

    document.getElementById(idTecladoDestino).style.display = 'grid';
}

function obtenerContenedorPorRuta(arbol, ruta, profundidad = 0) {
    if (profundidad === ruta.length - 1) {
        return arbol;
    }
    let idxComponente = ruta[profundidad];
    let idxSublista = ruta[profundidad + 1];
    return obtenerContenedorPorRuta(arbol[idxComponente].hijos[idxSublista], ruta, profundidad + 2);
}

function renderizarEstructura(arbol, rutaActual, profundidad = 0) {
    let html = "";
    for (let i = 0; i <= arbol.length; i++) {
        if (rutaActual.length - 1 === profundidad && rutaActual[profundidad] === i) {
            html += '<span class="cursor-virtual"></span>';
        }

        if (i === arbol.length) break;

        let nodo = arbol[i];

        if (nodo.tipo === 'texto') {
            html += `<span class="caracter-clicable" onclick="posicionarCursorDesdeRaton(event, ${i}, ${profundidad})">${nodo.valor}</span>`;
        }
        else if (nodo.tipo === 'potencia') {
            let htmlHijos = renderizarEstructura(nodo.hijos[0], rutaActual, profundidad + 2);
            html += `<sup class="estructura-clicable" onclick="posicionarCursorDesdeRaton(event, ${i}, ${profundidad})">${htmlHijos}</sup>`;
        }
        else if (nodo.tipo === 'logsub') {
            let htmlSub = renderizarEstructura(nodo.hijos[0], rutaActual, profundidad + 2);
            let htmlCuerpo = renderizarEstructura(nodo.hijos[1], rutaActual, profundidad + 2);
            html += `<span onclick="posicionarCursorDesdeRaton(event, ${i}, ${profundidad})">log</span><sub onclick="posicionarCursorDesdeRaton(event, ${i}, ${profundidad})">${htmlSub}</sub><span onclick="posicionarCursorDesdeRaton(event, ${i}, ${profundidad})">(${htmlCuerpo}</span>`;
        }
    }
    return html;
}

function posicionarCursorDesdeRaton(event, indiceNodo, profundidadNodo) {
    event.stopPropagation();
    const elemento = event.target;
    const rectangulo = elemento.getBoundingClientRect();
    const clicX = event.clientX - rectangulo.left;
    const mitadAncho = rectangulo.width / 2;

    rutaCursor = rutaCursor.slice(0, profundidadNodo + 1);

    if (clicX > mitadAncho) {
        rutaCursor[rutaCursor.length - 1] = indiceNodo + 1;
    } else {
        rutaCursor[rutaCursor.length - 1] = indiceNodo;
    }

    pantalla.focus();
    actualizarPantalla();
}

function actualizarPantalla() {
    pantalla.innerHTML = renderizarEstructura(datos, rutaCursor);
}

// =====================================================================
// 3. INSERCIÓN Y BORRADO DE DATOS
// =====================================================================
function insertarTexto(caracter) {
    let listaDestino = obtenerContenedorPorRuta(datos, rutaCursor);
    let idxInsercion = rutaCursor[rutaCursor.length - 1];

    listaDestino.splice(idxInsercion, 0, { tipo: 'texto', valor: caracter });
    rutaCursor[rutaCursor.length - 1]++;
    actualizarPantalla();
}

function insertarEstructura(tipo) {
    let listaDestino = obtenerContenedorPorRuta(datos, rutaCursor);
    let idxInsercion = rutaCursor[rutaCursor.length - 1];

    if (tipo === 'potencia2') {
        listaDestino.splice(idxInsercion, 0, { tipo: 'potencia', hijos: [[{tipo:'texto', valor:'2'}]] });
        rutaCursor[rutaCursor.length - 1]++;
    }
    else if (tipo === 'potencia') {
        listaDestino.splice(idxInsercion, 0, { tipo: 'potencia', hijos: [[]] });
        rutaCursor.push(0, 0);
    }
    else if (tipo === 'ex') {
        listaDestino.splice(idxInsercion, 0, { tipo: 'texto', valor: 'e' });
        rutaCursor[rutaCursor.length - 1]++;
        listaDestino = obtenerContenedorPorRuta(datos, rutaCursor);
        idxInsercion = rutaCursor[rutaCursor.length - 1];
        listaDestino.splice(idxInsercion, 0, { tipo: 'potencia', hijos: [[{tipo:'texto', valor:'x'}]] });
        rutaCursor[rutaCursor.length - 1]++;
    }
    else if (tipo === 'elibre') {
        listaDestino.splice(idxInsercion, 0, { tipo: 'texto', valor: 'e' });
        rutaCursor[rutaCursor.length - 1]++;
        listaDestino = obtenerContenedorPorRuta(datos, rutaCursor);
        idxInsercion = rutaCursor[rutaCursor.length - 1];
        listaDestino.splice(idxInsercion, 0, { tipo: 'potencia', hijos: [[]] });
        rutaCursor.push(0, 0);
    }
    else if (tipo === 'logsub') {
        listaDestino.splice(idxInsercion, 0, { tipo: 'logsub', hijos: [[], []] });
        listaDestino.splice(idxInsercion + 1, 0, { tipo: 'texto', valor: ')' });
        rutaCursor.push(0, 0);
    }
    actualizarPantalla();
}

function moverCursor(dir) {
    let listaActual = obtenerContenedorPorRuta(datos, rutaCursor);
    let idx = rutaCursor[rutaCursor.length - 1];

    if (dir === 'izq') {
        if (idx > 0) {
            let elementoPrevio = listaActual[idx - 1];
            if (elementoPrevio && (elementoPrevio.tipo === 'potencia' || elementoPrevio.tipo === 'logsub')) {
                rutaCursor[rutaCursor.length - 1]--;
                let subListaIdx = elementoPrevio.hijos.length - 1;
                rutaCursor.push(subListaIdx, elementoPrevio.hijos[subListaIdx].length);
            } else {
                rutaCursor[rutaCursor.length - 1]--;
            }
        } else if (rutaCursor.length > 1) {
            rutaCursor.pop();
            rutaCursor.pop();
        }
    }
    else if (dir === 'der' || dir === 'arr' || dir === 'aba') {
        if (idx < listaActual.length) {
            let elementoSiguiente = listaActual[idx];
            if (elementoSiguiente && (elementoSiguiente.tipo === 'potencia' || elementoSiguiente.tipo === 'logsub')) {
                rutaCursor.push(0, 0);
            } else {
                rutaCursor[rutaCursor.length - 1]++;
            }
        } else if (rutaCursor.length > 1) {
            let subListaIdx = rutaCursor[rutaCursor.length - 2];
            rutaCursor.pop();
            rutaCursor.pop();
            let padreLista = obtenerContenedorPorRuta(datos, rutaCursor);
            let padreIdx = rutaCursor[rutaCursor.length - 1];
            let nodoPadre = padreLista[padreIdx];

            if (nodoPadre && nodoPadre.tipo === 'logsub' && subListaIdx === 0) {
                rutaCursor.push(1, 0);
            } else {
                rutaCursor[rutaCursor.length - 1]++;
            }
        }
    }
    actualizarPantalla();
}

function ejecutarBorrado() {
    let listaActual = obtenerContenedorPorRuta(datos, rutaCursor);
    let idx = rutaCursor[rutaCursor.length - 1];

    if (idx > 0) {
        let nodoABorrar = listaActual[idx - 1];
        listaActual.splice(idx - 1, 1);
        rutaCursor[rutaCursor.length - 1]--;
    } else if (rutaCursor.length > 1) {
        rutaCursor.pop();
        rutaCursor.pop();
        let listaPadre = obtenerContenedorPorRuta(datos, rutaCursor);
        let idxPadre = rutaCursor[rutaCursor.length - 1];
        listaPadre.splice(idxPadre, 1);
    }
    actualizarPantalla();
}

// =====================================================================
// 4. TRADUCCIÓN DE ÁRBOL A SINTAXIS PYTHON (CON SOPORTE VALOR ABSOLUTO)
// =====================================================================
function procesarArbolParaPython(arbol) {
    let texto = "";
    let dentroDeAbs = false;

    for (let i = 0; i < arbol.length; i++) {
        let nodo = arbol[i];

        if (nodo.tipo === 'texto') {
            if (nodo.valor === '|') {
                if (!dentroDeAbs) {
                    texto += "abs(";
                    dentroDeAbs = true;
                } else {
                    texto += ")";
                    dentroDeAbs = false;
                }
            } 
            else if (nodo.valor === 'e' && arbol[i + 1] && arbol[i + 1].tipo === 'potencia') {
                let contenidoExponente = procesarArbolParaPython(arbol[i + 1].hijos[0]);
                texto += `exp(${contenidoExponente})`;
                i++; 
            } else {
                texto += nodo.valor;
            }
        } else if (nodo.tipo === 'potencia') {
            let contenidoExponente = procesarArbolParaPython(nodo.hijos[0]);
            texto += `**(${contenidoExponente})`;
        } else if (nodo.tipo === 'logsub') {
            let base = procesarArbolParaPython(nodo.hijos[0]);
            let cuerpo = procesarArbolParaPython(nodo.hijos[1]);
            texto += `(log(${cuerpo})/log(${base}))`;
        }
    }

    if (dentroDeAbs) {
        texto += ")";
    }
    return texto;
}

// =====================================================================
// 5. COMUNICACIÓN CON EL SERVIDOR PYTHON
// =====================================================================
async function enviarAPython() {
    const ecuacionLimpia = procesarArbolParaPython(datos);
    if (ecuacionLimpia.trim() === "") return;

    try {
        mostrarResultadoEnCelda("Calculando derivada...");

        const respuesta = await fetch('https://calculadorad-derivadas.onrender.com/conectar',  {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ecuacion: ecuacionLimpia })
        });

        const resultadoData = await respuesta.json();

        if (respuesta.ok) {
            mostrarResultadoEnCelda(`f'(x) = ${resultadoData.resultado}`);
            
            if (resultadoData.valores_x && resultadoData.valores_y_f) {
                inicializarOGraficar(resultadoData);
            } else {
                generarGraficaSimuladaDemo();
            }
        } else {
            mostrarResultadoEnCelda(`Error: ${resultadoData.detail || "Ecuación inválida"}`);
        }

    } catch (error) {
        console.error("Error de conexión:", error);
        mostrarResultadoEnCelda("Error: No se pudo conectar con el servidor de Python.");
    }
}

// =====================================================================
// 6. MOTOR GRÁFICO (CHART.JS Y RENDERS MATHJAX)
// =====================================================================
function mostrarResultadoEnCelda(mensaje) {
    const zonaResultado = document.getElementById('zona-resultado');

    if (mensaje.startsWith("Error:") || mensaje.startsWith("Calculando")) {
        zonaResultado.innerHTML = mensaje;
    } else {
        zonaResultado.innerHTML = `\\[ ${mensaje} \\]`;
    }

    zonaResultado.style.display = 'block';

    if (window.MathJax) {
        MathJax.typesetClear([zonaResultado]);
        MathJax.typesetPromise([zonaResultado]).catch((err) => console.error("Error de MathJax:", err));
    }
}

function inicializarOGraficar(datosDesdePython) {
    const contenedor = document.getElementById('zona-grafica-container');
    if(contenedor) contenedor.style.display = 'block';

    const canvas = document.getElementById('graficaDerivadas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const chartData = {
        labels: datosDesdePython.valores_x,
        datasets: [
            {
                label: 'Función f(x)',
                data: datosDesdePython.valores_y_f,
                borderColor: '#4b0082',
                borderWidth: 3,
                pointRadius: 0,
                showLine: true
            },
            {
                label: "Derivada f'(x)",
                data: datosDesdePython.valores_y_df,
                borderColor: '#00d2d3',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                showLine: true
            },
            {
                label: 'Puntos Críticos',
                data: datosDesdePython.puntos_criticos,
                backgroundColor: '#ff6b6b',
                borderColor: '#ff4757',
                pointRadius: 6,
                showLine: false
            }
        ]
    };

    if (miGrafica) {
        miGrafica.destroy();
    }

    miGrafica = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { type: 'linear', position: 'center' },
                y: { type: 'linear', position: 'center' }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });

    const btnF = document.getElementById('btn-toggle-f');
    const btnDf = document.getElementById('btn-toggle-df');
    const btnPts = document.getElementById('btn-toggle-puntos');

    if(btnF) btnF.className = 'btn-toggle-capa activo-f';
    if(btnDf) btnDf.className = 'btn-toggle-capa activo-df';
    if(btnPts) btnPts.className = 'btn-toggle-capa activo-pts';
}

function alternarCapa(indiceDataset) {
    if (!miGrafica) return;

    const estaVisible = miGrafica.isDatasetVisible(indiceDataset);
    const botones = document.querySelectorAll('.btn-toggle-capa');
    const botonEspecifco = botones[indiceDataset];
    const clasesActivas = ['activo-f', 'activo-df', 'activo-pts'];

    if (estaVisible) {
        miGrafica.hide(indiceDataset);
        if(botonEspecifco) botonEspecifco.className = 'btn-toggle-capa capa-oculta';
    } else {
        miGrafica.show(indiceDataset);
        if(botonEspecifco) botonEspecifco.className = `btn-toggle-capa ${clasesActivas[indiceDataset]}`;
    }
}

function generarGraficaSimuladaDemo() {
    let mockX = [], mockYf = [], mockYdf = [];
    for (let x_val = -3; x_val <= 3; x_val += 0.2) {
        mockX.push(parseFloat(x_val.toFixed(1)));
        mockYf.push(Math.pow(x_val, 3) - 3 * x_val); 
        mockYdf.push(3 * Math.pow(x_val, 2) - 3); 
    }
    inicializarOGraficar({
        valores_x: mockX,
        valores_y_f: mockYf,
        valores_y_df: mockYdf,
        puntos_criticos: [{x: -1, y: 2}, {x: 1, y: -2}]
    });
}

// Inicialización inicial de pantalla vacía al cargar el script
actualizarPantalla();