"""Genera el PDF de estudio de las clases 8 (microprocesador), 9 (memorias)
y 10 (circuitos secuenciales).

Uso: python docs/resumen_hardware/generar_resumen.py
"""
import sys
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    CondPageBreak, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pdf_estilo import (  # noqa: E402
    AMBER, AMBER_BG, BLUE, GREEN, GREEN_BG, GREY, LIGHT, LINE, NAVY, RED, RED_BG, S,
    P, box, bullets, grid, make_on_page,
)

OUT = Path(__file__).with_name("resumen_clases_8_9_10.pdf")
on_page = make_on_page("Resumen de estudio · Clases 8, 9 y 10 · Microprocesador, memorias y circuitos secuenciales")


# ---------------------------------------------------------------------------
# Diagramas
# ---------------------------------------------------------------------------
def arrow(d, x1, y1, x2, y2, color=NAVY, w=1.2):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=w))
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    s = 5
    p1 = (x2 - s * math.cos(a - 0.4), y2 - s * math.sin(a - 0.4))
    p2 = (x2 - s * math.cos(a + 0.4), y2 - s * math.sin(a + 0.4))
    d.add(Polygon([x2, y2, p1[0], p1[1], p2[0], p2[1]], fillColor=color, strokeColor=color))


def block(d, x, y, w, h, text, fill, fs=8.5, fc=colors.white):
    d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=fill, strokeColor=fill))
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        yy = y + h / 2 + (len(lines) / 2 - i - 0.75) * (fs + 2)
        d.add(String(x + w / 2, yy, ln, fontName="DV-B", fontSize=fs, fillColor=fc, textAnchor="middle"))


def diagrama_proceso_cpu():
    d = Drawing(170 * mm, 30 * mm)
    w, h = 50 * mm, 22 * mm
    fills = [BLUE, GREEN, AMBER]
    txt = ["1. La CPU lee instrucciones\ndesde un dispositivo de\nentrada, las carga en la\nmemoria y las ejecuta",
           "2. El resultado queda\nalmacenado de nuevo\nen la memoria",
           "3. Se visualiza a\ntravés de un periférico\nde salida"]
    for i in range(3):
        x = i * (w + 10 * mm)
        block(d, x, 4 * mm, w, h, txt[i], fills[i], fs=7.5)
        if i < 2:
            arrow(d, x + w + 1 * mm, 15 * mm, x + w + 9 * mm, 15 * mm)
    return d


def diagrama_jerarquia():
    d = Drawing(170 * mm, 70 * mm)
    niveles = ["Registros de la CPU", "Memoria caché (L1 · L2 · L3)", "Memoria principal (RAM)",
               "Memoria secundaria", "Memoria auxiliar", "Memoria en la red"]
    fills = [colors.HexColor(c) for c in ("#3D6A9E", "#6B4E9E", "#B7791F", "#2F6B45", "#A33A3A", "#4F6B3A")]
    cx, top, bh = 85 * mm, 62 * mm, 8.5 * mm
    for i, n in enumerate(niveles):
        w = (50 + i * 16) * mm
        y = top - i * (bh + 1.5 * mm)
        block(d, cx - w / 2, y, w, bh, n, fills[i], fs=8)
    arrow(d, 8 * mm, 6 * mm, 8 * mm, 66 * mm, color=BLUE)
    d.add(String(10 * mm, 36 * mm, "más velocidad", fontName="DV-B", fontSize=7.5, fillColor=BLUE))
    d.add(String(10 * mm, 32 * mm, "y más costo", fontName="DV-B", fontSize=7.5, fillColor=BLUE))
    arrow(d, 162 * mm, 66 * mm, 162 * mm, 6 * mm, color=RED)
    d.add(String(160 * mm, 36 * mm, "más capacidad", fontName="DV-B", fontSize=7.5, fillColor=RED, textAnchor="end"))
    d.add(String(160 * mm, 32 * mm, "más lejos de la CPU", fontName="DV-B", fontSize=7.5, fillColor=RED, textAnchor="end"))
    return d


def diagrama_maquina(salida=True, entradas_a_salida=True, titulo=""):
    d = Drawing(170 * mm, 34 * mm)
    y, h, w = 9 * mm, 14 * mm, 30 * mm
    xs = [28 * mm, 72 * mm, 116 * mm]
    block(d, xs[0], y, w, h, "D.P.E.", BLUE, fs=9)
    block(d, xs[1], y, w, h, "E.M.", AMBER, fs=9)
    d.add(String(0, y + h / 2 + 3, "Entradas", fontName="DV", fontSize=7.5, fillColor=GREY))
    d.add(String(0, y + h / 2 - 7, "(X)", fontName="DV", fontSize=7.5, fillColor=GREY))
    arrow(d, 13 * mm, y + h / 2, xs[0], y + h / 2)
    arrow(d, xs[0] + w, y + h / 2, xs[1], y + h / 2)
    # reloj
    arrow(d, xs[1] + w / 2, 1 * mm, xs[1] + w / 2, y)
    d.add(String(xs[1] + w / 2 - 9 * mm, 0.5 * mm, "CLK", fontName="DV-B", fontSize=7.5, fillColor=GREY))
    # realimentación estado actual
    fx = xs[1] + w + 4 * mm
    d.add(Line(xs[1] + w, y + h * 0.75, fx, y + h * 0.75, strokeColor=NAVY))
    d.add(Line(fx, y + h * 0.75, fx, y + h + 6 * mm, strokeColor=NAVY))
    d.add(Line(fx, y + h + 6 * mm, xs[0] + w / 2, y + h + 6 * mm, strokeColor=NAVY))
    arrow(d, xs[0] + w / 2, y + h + 6 * mm, xs[0] + w / 2, y + h)
    d.add(String((fx + xs[0]) / 2, y + h + 7.5 * mm, "estado actual (Z)", fontName="DV", fontSize=7, fillColor=GREY, textAnchor="middle"))
    if salida:
        block(d, xs[2], y, w, h, "D.S.", GREEN, fs=9)
        arrow(d, xs[1] + w, y + h / 4, xs[2], y + h / 4)
        arrow(d, xs[2] + w, y + h / 2, xs[2] + w + 10 * mm, y + h / 2)
        d.add(String(xs[2] + w + 11 * mm, y + h / 2 - 3, "Salidas (Y)", fontName="DV", fontSize=7.5, fillColor=GREY))
        if entradas_a_salida:
            d.add(Line(20 * mm, y + h / 2, 20 * mm, 3 * mm, strokeColor=RED, strokeDashArray=[2, 2]))
            d.add(Line(20 * mm, 3 * mm, xs[2] + w / 2, 3 * mm, strokeColor=RED, strokeDashArray=[2, 2]))
            arrow(d, xs[2] + w / 2, 3 * mm, xs[2] + w / 2, y, color=RED)
            d.add(String(xs[2] + w / 2 + 2 * mm, 4 * mm, "entradas a la salida (solo Mealy)", fontName="DV", fontSize=6.5, fillColor=RED))
    else:
        arrow(d, xs[1] + w, y + h / 4, xs[1] + w + 22 * mm, y + h / 4)
        d.add(String(xs[1] + w + 23 * mm, y + h / 4 - 3, "Salidas = estado", fontName="DV", fontSize=7.5, fillColor=GREY))
    return d


def diagrama_contador_mod8():
    """Diagrama de tiempos de un contador asíncrono MOD-8 (FF JK, flanco negativo)."""
    d = Drawing(170 * mm, 52 * mm)
    x0, step = 22 * mm, 9 * mm
    n = 16  # semiperíodos de reloj
    rows = [("CLK", 0), ("Q0", 1), ("Q1", 2), ("Q2", 3)]
    hi, gap = 5 * mm, 11 * mm
    for name, k in rows:
        base = 44 * mm - k * gap
        d.add(String(4 * mm, base + 1 * mm, name, fontName="DV-B", fontSize=8, fillColor=NAVY))
        pts = []
        for t in range(n + 1):
            if k == 0:
                lvl = 1 if t % 2 == 0 else 0
            else:
                count = (t + 1) // 2  # flancos descendentes ocurridos hasta t
                lvl = (count >> (k - 1)) & 1
            pts.append(lvl)
        x = x0
        prev = pts[0]
        for t in range(n):
            lvl = pts[t]
            if lvl != prev:
                d.add(Line(x, base, x, base + hi, strokeColor=RED if k else NAVY, strokeWidth=1.2))
            d.add(Line(x, base + lvl * hi, x + step, base + lvl * hi, strokeColor=RED if k else NAVY, strokeWidth=1.2))
            prev = lvl
            x += step
    base = 44 * mm - 3 * gap - 7 * mm
    for c in range(8):
        cx = x0 + step / 2 if c == 0 else x0 + 2 * c * step
        d.add(String(cx, base, format(c, "03b"), fontName="DV-M", fontSize=7, fillColor=GREY, textAnchor="middle"))
    d.add(String(4 * mm, base, "Q2Q1Q0", fontName="DV-B", fontSize=7, fillColor=GREY))
    return d


# ---------------------------------------------------------------------------
# Fichas: (etiqueta, subetiqueta, pregunta, respuesta, idea en una línea, para fijarlo)
# ---------------------------------------------------------------------------
UNIDADES = [
    {
        "id": "1", "clase": "Clase 8", "nombre": "El microprocesador",
        "intro": "Hilo conductor: el microprocesador es el <b>cerebro</b> que ejecuta los programas. Para entenderlo hay que saber "
                 "<b>qué hace</b> (sus funciones), <b>de qué está hecho</b> (sus partes), <b>qué tan rápido va</b> (sus dos velocidades) "
                 "y <b>cómo evolucionó</b> desde 1971.",
        "fichas": [
            ("Micro", "Definición", "¿Qué es el microprocesador?",
             "Es el <b>cerebro de la computadora</b>: ejecuta los programas y es imprescindible para su funcionamiento. "
             "Es un <b>chip o pastilla de silicio</b> con circuitos integrados y transistores, protegido por una cobertura de <b>cerámica y plástico</b>.",
             "Chip de silicio + transistores = cerebro que ejecuta programas.",
             "Tres materiales en orden de adentro hacia afuera: <b>silicio</b> (la oblea), <b>transistores</b> (los circuitos) y <b>cerámica/plástico</b> (la protección)."),
            ("Micro", "Funciones", "¿Cuáles son las funciones del microprocesador?",
             "<b>Recuperar, interpretar y cumplir instrucciones</b>, y operar como <b>calculadora</b> del sistema: hace operaciones "
             "<b>aritméticas</b> y <b>lógicas</b>, como la unión (<b>OR</b>) o la intersección (<b>AND</b>).",
             "Busca, entiende y ejecuta instrucciones; calcula y compara.",
             "Secuencia <b>R-I-C</b>: Recupera, Interpreta, Cumple. Recuerda la pareja lógica: <b>OR = unión</b>, <b>AND = intersección</b>."),
            ("Parte", "Caché", "¿Qué es la memoria caché del micro y qué niveles tiene?",
             "Una memoria <b>ultrarrápida</b> donde el micro guarda datos que <b>probablemente usará</b> en las siguientes operaciones, "
             "para no tener que ir a la RAM. La <b>L1</b> (primer nivel) está encapsulada junto al micro. Los micros más modernos incluyen una "
             "<b>L2</b>, más grande pero algo menos rápida.",
             "Caché = atajo para no esperar a la RAM. L1 más rápida y chica; L2 más grande y lenta.",
             "Ejemplo de la clase: buscar un libro con la computadora de la biblioteca en vez de revisar el fichero de papel. "
             "Este concepto se repite en la clase 9: estúdialos juntos."),
            ("Parte", "FPU", "¿Qué es el coprocesador matemático?",
             "Su nombre correcto es <b>FPU (unidad de coma flotante)</b>. Es la parte especializada en cálculos matemáticos de coma flotante. "
             "<b>Antiguamente estaba fuera del micro</b>, en otro chip.",
             "FPU = calculadora de decimales, hoy integrada en el micro.",
             "«Coma flotante» = números con decimales. La pregunta típica: <b>¿dónde estaba antes?</b> En un chip externo."),
            ("Parte", "Encapsulado", "¿Para qué sirve el encapsulado?",
             "Rodea la oblea de silicio para <b>darle consistencia</b>, <b>impedir su deterioro</b> (por ejemplo, por oxidación con el aire) "
             "y <b>permitir el enlace con los conectores</b> externos que lo acoplan al zócalo de la placa base.",
             "Protege, da firmeza y conecta.",
             "Tres verbos: <b>proteger</b>, <b>sostener</b>, <b>conectar</b>. Piensa en la funda de un teléfono que además tuviera el cable de carga."),
            ("Parte", "Disipador", "¿Por qué es fundamental el disipador de calor?",
             "En todo semiconductor el paso de la corriente produce una <b>pérdida de energía que se transforma en calor</b>. Si la temperatura "
             "sube en exceso, primero <b>reduce la vida útil</b> del micro y, en el peor caso, <b>lo destruye</b>.",
             "Corriente → calor → menos vida útil → destrucción.",
             "Aprende la cadena causa-efecto completa: es la forma en que suelen pedirla en el examen."),
            ("Parte", "Registros", "¿Qué son los registros?",
             "Un tipo de <b>memoria pequeña con fines especiales</b> que el micro usa en operaciones particulares. Hay varios grupos: unos "
             "para control del programador y otros que usa la CPU internamente. La clase indica un total de <b>treinta y dos registros</b>.",
             "Registros = la memoria más chica y rápida, dentro del micro.",
             "Conecta con la clase 9 (están en la cima de la jerarquía de memorias) y con la clase 10 (un registro se construye con flip-flops)."),
            ("Parte", "Memoria", "¿Qué función cumple la memoria para el procesador?",
             "Es el lugar donde el procesador <b>encuentra sus instrucciones y sus datos</b>. Su función esencial es proporcionar un "
             "<b>espacio de trabajo</b> para el procesador.",
             "La memoria es la mesa de trabajo del procesador.",
             "Instrucciones <b>y</b> datos están en el mismo lugar: es la idea de la arquitectura de von Neumann que aparece en la clase 9."),
            ("Velocidad", "Interna / FSB", "¿Cuáles son las dos velocidades de un microprocesador?",
             "<b>Velocidad interna</b>: a la que funciona el micro por dentro (ejemplos de la clase: 500, 600, 800 MHz). "
             "<b>Velocidad externa o de bus (FSB)</b>: a la que se comunican el micro y la placa base (generalmente 60, 66 o 100 MHz).",
             "Interna = lo rápido que piensa. Externa (FSB) = lo rápido que habla con la placa.",
             "FSB = <i>Front Side Bus</i>. La interna siempre es mucho mayor que la externa: por eso existe la caché, para no esperar."),
        ],
    },
    {
        "id": "2", "clase": "Clase 9", "nombre": "Memorias",
        "intro": "Hilo conductor: la CPU necesita un lugar donde tener instrucciones y datos. Esa es la <b>memoria</b>. Se organiza en "
                 "<b>posiciones con dirección</b>, hay de <b>dos tipos</b> (ROM y RAM) y se ordena en una <b>jerarquía</b> según velocidad, costo y capacidad.",
        "fichas": [
            ("Memoria", "Definición", "¿Qué es la memoria?",
             "El <b>hardware que permite almacenar información temporalmente</b>, ya que <b>requiere energía constante</b> para mantenerla. "
             "Es un componente imprescindible que mantiene disponibles las instrucciones para que la <b>CPU pueda ejecutarlas</b> y almacena "
             "temporalmente el <b>resultado de los procesos</b>.",
             "Almacén temporal de instrucciones y resultados para la CPU.",
             "Dos funciones: <b>tener a mano</b> lo que la CPU va a ejecutar y <b>guardar</b> lo que ya calculó."),
            ("Memoria", "Von Neumann", "¿Qué papel cumple la memoria en el modelo de computadora?",
             "Retiene datos durante algún intervalo de tiempo. Acoplada a la <b>CPU</b>, implementa lo fundamental del modelo de "
             "<b>arquitectura de von Neumann</b>, usado <b>desde los años 1940</b>.",
             "CPU + memoria = arquitectura de von Neumann (desde 1940).",
             "Dato y fecha van juntos: <b>von Neumann · década de 1940</b>."),
            ("Memoria", "Funcionamiento", "¿Cuál es el proceso completo para que la CPU realice una operación?",
             "1) La CPU <b>lee las instrucciones</b> desde un dispositivo de entrada, <b>las carga en la memoria</b> y las ejecuta. "
             "2) El <b>resultado queda almacenado</b> de nuevo en la memoria. 3) Después se puede <b>visualizar</b> en un periférico de salida.",
             "Entrada → memoria → ejecución → memoria → salida.",
             "La memoria aparece <b>dos veces</b> en el proceso: antes de ejecutar y después de ejecutar. Mira el diagrama de abajo."),
            ("Memoria", "Posiciones", "¿Cómo se organiza internamente la memoria?",
             "En un conjunto de casillas o células llamadas <b>posiciones de memoria</b>, donde se colocan instrucciones y datos. Cada posición "
             "se identifica por un número llamado <b>dirección de memoria</b> y <b>almacena un byte</b>. Para medir la cantidad de células se usan "
             "megabytes y gigabytes.",
             "Cada casilla tiene una dirección y guarda 1 byte (8 bits).",
             "Analogía: un edificio de departamentos. Cada departamento es una posición, su número es la dirección y adentro viven 8 bits."),
            ("Tipo", "ROM", "¿Qué es la memoria ROM?",
             "<i>Read Only Memory</i>: memoria de <b>solo lectura</b>, no se puede escribir en ella. Su información la <b>grabó el fabricante</b> "
             "y <b>no desaparece al apagar</b> el ordenador. Es imprescindible y contiene instrucciones y datos técnicos de los componentes.",
             "ROM: solo lectura, de fábrica, no se borra al apagar.",
             "En la diapositiva aparece un chip <b>AMIBIOS</b>: la BIOS es el ejemplo típico de ROM."),
            ("Tipo", "RAM", "¿Qué es la memoria RAM?",
             "<i>Random Access Memory</i>, memoria de <b>acceso aleatorio</b>. Es <b>volátil</b>: al apagar, los datos se pierden. Ahí se cargan los "
             "archivos y programas que abrimos y también el <b>sistema operativo</b> al encender. Para no perder datos hay que guardarlos en un "
             "almacenamiento permanente. Se instala en los <b>zócalos de la placa base</b>.",
             "RAM: memoria de trabajo, volátil, se borra al apagar.",
             "Volátil = se «evapora» sin energía. Contraste directo con el disco duro o el pendrive, que son permanentes."),
            ("Tipo", "RAM: 3 tipos", "¿En qué tres tipos se clasifica la RAM según la clase?",
             "<b>Memoria caché</b>, <b>tarjeta de memoria RAM</b> y <b>memoria RAM de video</b>.",
             "Caché, módulo RAM y RAM de video.",
             "Ordénalas por cercanía al procesador: la caché está pegada al micro, la tarjeta en la placa y la de video en la tarjeta gráfica."),
            ("Caché", "Definición", "¿Qué es la memoria caché y dónde se sitúa?",
             "Una memoria de tipo <b>estático (SRAM)</b>, <b>rápida pero cara</b>, situada <b>entre el procesador y la memoria principal</b>. "
             "Su misión es <b>acelerar los accesos</b> del procesador a los datos que necesita, porque su tiempo de acceso es mucho menor que el de la RAM.",
             "Caché = SRAM rápida y cara entre CPU y RAM.",
             "SRAM: la S es de <b>estática</b>. Rápida y cara: por eso hay poca."),
            ("Caché", "Fallo", "¿Qué es un fallo de caché?",
             "Ocurre cuando el procesador intenta acceder a un dato que <b>no está en la caché</b>. Se subsana <b>trasladando un bloque</b> de "
             "información desde la memoria principal a la caché.",
             "No está en la caché → se trae un bloque desde la RAM.",
             "Se trae un <b>bloque</b> y no un solo dato, porque es probable que se usen también los datos vecinos."),
            ("Caché", "Para qué sirve", "¿Por qué hace falta la caché si ya existe la RAM?",
             "RAM y caché son parecidas; la diferencia está en el <b>uso</b>. Desde el <b>386</b>, los micros son tan rápidos que la RAM no da abasto "
             "y el micro tendría que esperar. Por eso se coloca una memoria muy rápida <b>estratégicamente entre el micro y la RAM</b>.",
             "El micro es más rápido que la RAM; la caché evita que espere.",
             "Dato concreto: el problema aparece <b>desde el 386</b>. Une esta idea con las dos velocidades de la clase 8."),
            ("Jerarquía", "6 niveles", "¿Cuál es la jerarquía de memorias?",
             "De arriba abajo: <b>registros de la CPU</b>, <b>caché (L1, L2, L3)</b>, <b>memoria principal</b>, <b>memoria secundaria</b>, "
             "<b>memoria auxiliar</b> y <b>memoria en la red</b>. Hacia arriba aumentan la <b>velocidad y el costo</b>; hacia abajo aumenta la "
             "<b>capacidad</b> y disminuye el acceso a la CPU.",
             "Arriba: rápido y caro. Abajo: grande y lejano.",
             "Frase para el orden: «<b>R</b>osa <b>C</b>ome <b>P</b>an <b>S</b>in <b>A</b>zúcar <b>R</b>efinado» (Registros, Caché, Principal, Secundaria, Auxiliar, Red)."),
        ],
    },
    {
        "id": "3", "clase": "Clase 10", "nombre": "Circuitos secuenciales",
        "intro": "Hilo conductor: un circuito secuencial <b>recuerda</b>. Para recordar necesita un <b>elemento de memoria</b> (latch o flip-flop) y un "
                 "<b>reloj</b> que marque cuándo cambiar. Con flip-flops se construyen <b>contadores</b> y <b>registros</b>, que son la base de la caché "
                 "y los registros del microprocesador.",
        "fichas": [
            ("Secuencial", "Definición", "¿Qué es un circuito secuencial?",
             "Un circuito cuya <b>salida depende de los valores actuales y pasados</b> de las entradas. Tiene <b>lazos de realimentación</b> (salidas que "
             "actúan como entradas), necesita una <b>señal de reloj</b> (onda cuadrada periódica), tiene <b>lógica combinacional</b> que determina la salida "
             "y el próximo estado, y un <b>elemento de memoria</b> que mantiene el estado actual.",
             "Secuencial = combinacional + memoria + reloj.",
             "La diapositiva lo llama «circuito combinacional», pero el concepto es <b>secuencial</b>: el combinacional solo depende de las entradas actuales. "
             "Esa diferencia, el <b>pasado</b>, es justo lo que define al secuencial."),
            ("Secuencial", "Reloj", "¿Qué función cumple la señal de reloj (CLK)?",
             "Da la <b>sincronización</b> del sistema: define <b>en qué instantes se leen</b> las entradas y <b>cuándo deben cambiar</b> los circuitos. "
             "Convierte una entrada en una señal síncrona: <b>dato + CLK = secuencia de bits</b>.",
             "El reloj es el director de orquesta: marca cuándo leer y cuándo cambiar.",
             "Palabra clave: <b>sincronización</b>. Sin reloj, cada parte cambiaría cuando quisiera."),
            ("FSM", "Elementos", "¿Qué es una máquina de estados finitos y cuáles son sus elementos?",
             "Una <b>FSM</b> (<i>Finite State Machine</i>) representa el comportamiento de un circuito síncrono como una secuencia de eventos en tiempos discretos. "
             "<b>No puede estar en más de un estado a la vez</b>; el cambio de estado se llama <b>transición</b> y ocurre en cada evento de reloj. "
             "Elementos: <b>X</b> entradas, <b>Y</b> salidas, <b>Z</b> estados, <b>δ</b> funciones de estado y <b>λ</b> funciones de salida.",
             "X entra, Z recuerda, Y sale; δ calcula el próximo estado y λ la salida.",
             "Orden alfabético X, Y, Z = entra, sale, se guarda. Las letras griegas: <b>δ</b> de «destino» (próximo estado) y <b>λ</b> de «luz» (lo que se ve: la salida)."),
            ("FSM", "Modelo general", "¿Cuáles son los bloques del modelo general?",
             "<b>Decodificador de próximo estado (D.P.E.)</b>, <b>elemento de memoria (E.M.)</b> y <b>decodificador de salida (D.S.)</b>. "
             "Los decodificadores son <b>circuitos combinacionales</b> que pueden depender de las entradas y del estado actual. El reloj llega al elemento de memoria.",
             "D.P.E. → E.M. → D.S.; solo el E.M. tiene reloj.",
             "Los dos decodificadores son combinacionales; la memoria es lo único secuencial. Por eso el reloj entra solo ahí."),
            ("FSM", "Moore", "¿Qué caracteriza a la máquina de Moore?",
             "Las <b>salidas dependen únicamente del estado</b>, no de las entradas. En cada flanco de reloj hay una transición; las salidas están sincronizadas; "
             "el reset solo fija el estado inicial. <b>Z = δ(X, Z)</b> y <b>Y = λ(Z)</b>. Es la <b>clase B</b>.",
             "Moore: salida = f(estado).",
             "«M<b>oo</b>re → s<b>o</b>l<b>o</b> estad<b>o</b>». En un diagrama de Moore, la salida se escribe <b>dentro del círculo</b> del estado."),
            ("FSM", "Mealy", "¿Qué caracteriza a la máquina de Mealy?",
             "Las <b>salidas dependen del estado y de las entradas</b>. <b>Z = δ(X, Z)</b> y <b>Y = λ(X, Z)</b>. Es la <b>clase A</b>, igual al modelo general.",
             "Mealy: salida = f(entradas, estado).",
             "«M<b>e</b>aly → m<b>e</b>zcla <b>e</b>ntradas». La única diferencia con Moore está en la función de salida λ. "
             "La <b>clase C</b> no tiene decodificador de salida: la salida es el propio estado."),
            ("Memoria", "Celda básica", "¿Cómo se consigue almacenar un valor con lógica combinacional?",
             "Con <b>retroalimentación</b> (<i>feedback</i>): la salida se conecta a la entrada y la señal se mantiene en el tiempo. Una sola compuerta no almacena, "
             "pero varias interconectadas sí. Ejemplo: la <b>celda básica RS con compuertas NAND</b>.",
             "Memoria = compuertas realimentadas.",
             "La realimentación es el «truco» que convierte lógica sin memoria en memoria."),
            ("Latch", "SR", "¿Cómo funcionan los latch SR con NAND y con NOR?",
             "Son biestables de <b>dos compuertas</b>. El latch <b>NAND</b> tiene entradas <b>activas en bajo</b> (S', R'): 00 ambiguo, 01 SET, 10 RESET, 11 sin cambio. "
             "El latch <b>NOR</b> tiene entradas <b>activas en alto</b>: 00 sin cambio, 01 RESET, 10 SET, 11 ambiguo.",
             "NAND: activo en bajo. NOR: activo en alto. Son espejos.",
             "Regla rápida: en el NAND, el «0» es el que actúa; en el NOR, el «1». El estado prohibido es cuando <b>ambas entradas están activas</b>."),
            ("FF", "Definición", "¿Qué es un flip-flop y en qué se diferencia de un latch?",
             "También llamado <b>biestable</b>: es el elemento de memoria más importante. Es un multivibrador que puede permanecer <b>indefinidamente en uno de dos estados</b>. "
             "Los <b>asíncronos</b> solo tienen entradas de control; los <b>síncronos</b> tienen además entrada de reloj, activada por <b>nivel</b> o por <b>flanco</b>. "
             "Los flip-flops activados por flanco se crearon para <b>eliminar las deficiencias de los latches</b>, activados por nivel.",
             "Latch = responde a un nivel. Flip-flop = responde a un flanco.",
             "Nivel = mientras la señal esté en alto. Flanco = solo en el instante en que sube o baja. El flanco es un «clic»; el nivel, un «mantener apretado»."),
            ("FF", "SR, JK y D", "¿Cómo funcionan los flip-flops SR, JK y D?",
             "<b>SR</b>: 00 sin cambio, 10 set (Q=1), 01 reset (Q=0), 11 ambiguo. <b>JK</b>: igual que el SR, pero con <b>11 conmuta</b> (Q pasa a Q'). "
             "<b>D</b>: una sola entrada; en el flanco positivo, <b>Q toma el valor de D</b>. Por dentro, los FF SR y JK tienen un latch NAND, un circuito de "
             "conducción de pulso y un <b>detector de flancos</b> (pulso de 2 a 5 ns); en el JK, Q y Q' se realimentan a las entradas.",
             "JK = SR sin estado prohibido (11 conmuta). D = copia D en el flanco.",
             "El D se obtiene de un JK con <b>J = D</b> y <b>K = D'</b> (inversor). Un FF D sirve para <b>transferir datos en paralelo</b>."),
            ("Latch D", "Transparente", "¿Qué es el latch D transparente?",
             "Es como el FF D pero <b>sin detector de flancos</b>; usa una entrada de <b>habilitación (enable)</b> en lugar del reloj. Con enable <b>en alto, Q sigue a D</b> "
             "(es «transparente»); con enable <b>en bajo, Q mantiene</b> el estado anterior.",
             "Latch D: copia D mientras enable = 1. FF D: copia D solo en el flanco.",
             "«Transparente» = mientras está habilitado, la salida es un vidrio: ves la entrada a través de ella."),
            ("FF", "Asincrónicas", "¿Qué son las entradas asincrónicas PRE y CLR?",
             "Entradas que <b>no dependen del reloj</b>: <b>PRESET</b> lleva el FF a 1 y <b>CLEAR</b> lo lleva a 0. Son <b>predominantes</b>: ignoran las entradas "
             "sincrónicas (S, R, J, K, D). Suelen ser <b>activas en bajo</b>. Si ambas se activan a la vez, el estado es <b>inválido</b>.",
             "PRE = 1 ya. CLR = 0 ya. Mandan sobre todo.",
             "La barra sobre CLK, o la burbuja en el símbolo, indica que el FF se activa en <b>flanco descendente</b>. La burbuja en PRE o CLR indica <b>activa en bajo</b>."),
            ("Contador", "Asíncrono", "¿Cómo funciona un contador asíncrono con FF JK?",
             "Con <b>J = K = 1</b>, cada FF <b>conmuta</b> en cada flanco. La salida de cada FF hace de reloj del siguiente, de modo que <b>cada FF divide la frecuencia por 2</b>. "
             "Con 3 FF hay 2<super>3</super> = 8 estados: es un contador <b>MOD-8</b>. Con un FF más, MOD-16. Su problema son los <b>retrasos de propagación acumulados</b>, "
             "porque los FF no cambian todos a la vez.",
             "N flip-flops → 2<super>N</super> estados → la frecuencia se divide por 2<super>N</super>.",
             "Mira el diagrama de tiempos de abajo: Q0 tiene la mitad de frecuencia que CLK, Q1 la mitad que Q0, y así sucesivamente."),
            ("Contador", "Síncrono", "¿Qué resuelve un contador síncrono y cómo se hace un MOD menor que 2<super>N</super>?",
             "En el síncrono <b>todos los FF reciben el mismo reloj</b> y cambian a la vez, lo que elimina el retraso acumulado. Para un módulo menor, se detecta el "
             "estado de reinicio con una <b>compuerta NAND</b> conectada a los <b>CLR</b>. Ejemplo: MOD-6 se reinicia al llegar a 6 (110), con NAND de B y C.",
             "Síncrono = un solo reloj para todos. MOD-N = NAND que detecta N y borra.",
             "El estado N aparece solo un instante (un pico): el contador cuenta de 0 a N−1. Un contador <b>BCD</b> es MOD-10 (0 a 9)."),
            ("CI", "74ALS160-163", "¿Qué características tiene el contador 74ALS161?",
             "Contador síncrono de <b>4 bits</b>, <b>MOD-16</b> binario, sincronizado en <b>flanco positivo</b>. Salidas QD (MSB) a QA (LSB). <b>CLR asíncrono</b>: al pasar a bajo "
             "pone 0000. Entrada <b>LOAD activa en bajo</b> para cargar el valor de A, B, C, D. En cascada, la salida <b>RCO</b> se activa en 1111 (con ENT en alto) y habilita "
             "la siguiente etapa a través de su <b>ENT</b>.",
             "161 = MOD-16, CLR asíncrono, LOAD activo en bajo, RCO para cascada.",
             "RCO = <i>Ripple Carry Out</i>, el «me llevo uno» de la suma: cuando la primera etapa llega a 1111, avisa a la siguiente."),
            ("Diseño", "Excitación JK", "¿Cuál es la tabla de excitación del flip-flop JK?",
             "0→0: J=0, K=x. 0→1: J=1, K=x. 1→0: J=x, K=1. 1→1: J=x, K=0. (x = no importa.)",
             "Para subir hace falta J=1; para bajar hace falta K=1.",
             "Solo importa <b>una</b> entrada por transición: si Q vale 0, mira J; si Q vale 1, mira K. La otra siempre es x."),
            ("Diseño", "6 pasos", "¿Cuál es el procedimiento para diseñar un contador síncrono?",
             "1) Determinar el número de FF y la secuencia deseada. 2) Dibujar el <b>diagrama de transición de estados</b> con todos los estados posibles. "
             "3) Hacer la tabla <b>estado presente / estado siguiente</b>. 4) Añadir columnas J y K de cada FF con la <b>tabla de excitación</b>. "
             "5) Obtener y <b>simplificar</b> la función lógica de cada J y K. 6) <b>Implementar</b> los circuitos.",
             "Secuencia → diagrama → tabla → J/K → simplificar → circuito.",
             "Más abajo tienes el ejemplo de la clase <b>resuelto paso a paso</b>. Hazlo tú primero tapando la solución."),
            ("Registro", "4 tipos", "¿Cómo se clasifican los registros de desplazamiento?",
             "Según cómo entran y salen los datos: <b>PIPO</b> (paralelo-paralelo), <b>SISO</b> (serie-serie), <b>PISO</b> (paralelo-serie) y <b>SIPO</b> (serie-paralelo).",
             "Primera letra = cómo entra; tercera = cómo sale.",
             "P = paralelo (todos los bits a la vez), S = serie (un bit por pulso de reloj). Lee las siglas como «entra… sale…»."),
            ("Bus", "Triestado", "¿Cómo funciona un bus de datos con registros triestado (74ALS173)?",
             "El 74ALS173 es un registro <b>PIPO de 4 bits</b> con salidas a <b>búferes triestado</b>. Tiene dos modos: <b>carga</b> (D0-D3 pasan a los FF en el flanco "
             "ascendente) y <b>retención</b>. En un bus, <b>solo un registro puede tener la salida habilitada</b> (OE); los demás quedan en <b>alta impedancia (Hi-Z)</b>. "
             "Si no, hay <b>colisión de bus</b>: niveles inciertos y posible daño a los búferes.",
             "Un solo registro «habla» en el bus; los demás se desconectan (Hi-Z).",
             "Analogía: una reunión con un solo micrófono abierto. OE = abrir el micrófono; IE = escuchar y anotar."),
        ],
    },
]

AUTOEVAL = {
    "1": [("Enumera las seis partes del microprocesador vistas en clase.", "Caché, coprocesador matemático (FPU), encapsulado, disipador de calor, registros y memoria."),
          ("¿Qué diferencia hay entre velocidad interna y FSB?", "La interna es la del micro por dentro; la FSB, la de comunicación entre micro y placa base."),
          ("¿Cuál fue el primer microprocesador comercial y en qué año salió?", "El Intel 4004, en 1971.")],
    "2": [("¿Por qué la RAM es volátil y la ROM no?", "La RAM pierde los datos sin energía; la ROM conserva lo grabado por el fabricante al apagar."),
          ("¿Qué es un fallo de caché y cómo se resuelve?", "El dato no está en la caché; se trae un bloque desde la memoria principal."),
          ("Ordena la jerarquía de memorias de la más rápida a la más lenta.", "Registros, caché, principal, secundaria, auxiliar y red.")],
    "3": [("¿Qué diferencia a Moore de Mealy?", "En Moore la salida depende solo del estado; en Mealy, del estado y de las entradas."),
          ("¿Qué hace un FF JK con J = K = 1?", "Conmuta: Q pasa a su complemento en cada flanco activo."),
          ("¿Cuántos FF necesita un contador MOD-12?", "Cuatro, porque 2<super>3</super> = 8 no alcanza y 2<super>4</super> = 16 sí."),
          ("¿Qué es una colisión de bus?", "Dos o más registros con la salida habilitada a la vez en el mismo bus.")],
}

LINEA_TIEMPO = [
    ["Año", "Hito", "Para recordar"],
    ["1971", "<b>Intel 4004</b>", "Primer microprocesador comercial"],
    ["1972-1979", "8008, 8080/8085, Z80 (1976), <b>8086</b> (1978), 8088 (1979)", "Nace la familia «x86»"],
    ["1982 · 1985 · 1989", "<b>80286 · 80386 · 80486</b>", "Uno cada 3-4 años: 286, 386, 486"],
    ["1993 · 1995", "<b>Pentium</b>, AMD K5 · Pentium Pro", "Fin de los números: Intel pasa a nombres"],
    ["1997 · 1999 · 2000", "<b>Pentium II</b>, AMD K6 · <b>Pentium III</b>, K6-2 · <b>Pentium 4</b>, Athlon XP, Duron", "II, III y 4 en tres años casi seguidos"],
    ["2005 · 2006 · 2007", "Pentium D, <b>Core Duo</b>, Athlon 64 X2 · <b>Core 2 Duo</b> · <b>Core 2 Quad</b>", "Era multinúcleo: 2 y luego 4 núcleos"],
    ["2008", "Intel Core <b>Nehalem</b> · AMD <b>Phenom II</b> y Athlon II", "1.ª generación Core"],
    ["2011 · 2012 · 2013", "<b>Sandy Bridge</b>, AMD Fusion · <b>Ivy Bridge</b> · <b>Haswell</b>", "2.ª, 3.ª y 4.ª generación Core"],
]

MODELOS = [
    ["Modelo", "Rasgo que lo identifica"],
    ["8086, 8088, 286", "«Prehistóricos», de rendimiento similar"],
    ["386, 386 SX", "Más modernos, aunque aún del «Neolítico informático»"],
    ["Pentium MMX", "<b>MMX</b> = MultiMedia eXtensions. Doble de caché (<b>32 KB</b>), hasta <b>60 %</b> más rendimiento"],
    ["Pentium II", "Pentium Pro renovado, en cartucho <b>SEC</b> que se conecta al <b>Slot 1</b>"],
    ["AMD K6", "Mucho mejor que el K5, con MMX y caché interna de <b>64 KB</b>"],
    ["Cyrix 6x86MX (M2)", "Bueno para <b>oficina</b>; nunca para CAD ni juegos"],
    ["AMD K6-2", "K6 + capacidades 3D: tecnología <b>3DNow!</b> (un «MMX para 3D»)"],
    ["AMD K6-III", "Casi un K6-2 pero con <b>256 KB</b> de caché secundaria integrada"],
    ["Celeron «A»", "<b>128 KB</b> de caché secundaria, la cuarta parte que el Pentium II"],
    ["Pentium III", "Instrucciones nuevas <b>SSE</b> (Streaming SIMD Extensions): más rendimiento matemático y multimedia"],
    ["AMD Athlon (K7)", "<b>128 KB</b> de caché L1 (4 veces la del P-III), bus de 200 o 266 MHz, el mejor en cálculo matemático"],
    ["AMD Duron", "Casi un Athlon, con menos caché secundaria (<b>64 KB</b>) pero integrada"],
    ["Pentium 4", "Diseñado para altas frecuencias; competitivo desde <b>1,7 GHz</b>"],
    ["Intel Core Duo", "Doble y cuádruple núcleo, arquitectura Core: <b>menos frecuencia, más eficiencia</b> que NetBurst (P4/D)"],
    ["AMD Phenom II / Athlon II", "Multinúcleo en <b>45 nm</b>, soporte DDR3, caché L3 de 2 a <b>6 MiB</b>"],
    ["Intel Core Haswell", "<b>4.ª generación</b> Core, <b>22 nm</b>, menor consumo, socket <b>1150</b>"],
]

HUECOS = [
    ("El microprocesador es un chip de ______ que contiene circuitos integrados y ______.", "silicio · transistores (clase 8)"),
    ("Las operaciones lógicas OR y AND equivalen a la ______ y la ______ de conjuntos.", "unión · intersección (clase 8)"),
    ("El nombre correcto del coprocesador matemático es ______, unidad de coma flotante.", "FPU (clase 8)"),
    ("La velocidad de comunicación entre micro y placa base se llama velocidad externa o ______.", "de bus, FSB (clase 8)"),
    ("El primer microprocesador comercial fue el ______ en el año ______.", "Intel 4004 · 1971 (clase 8)"),
    ("La memoria, acoplada a la CPU, implementa el modelo de arquitectura de ______, usado desde los años ______.", "von Neumann · 1940 (clase 9)"),
    ("Cada posición de memoria se identifica con una ______ y almacena un ______.", "dirección de memoria · byte (clase 9)"),
    ("La RAM es ______: al apagar la computadora, los datos se ______.", "volátil · pierden (clase 9)"),
    ("La caché es una memoria de tipo ______ (SRAM), rápida pero ______.", "estático · cara (clase 9)"),
    ("En la jerarquía de memorias, hacia arriba aumentan la ______ y el ______.", "velocidad · costo (clase 9)"),
    ("En la máquina de ______, las salidas dependen solo del estado: Y = λ(Z).", "Moore (clase 10)"),
    ("El latch SR con compuertas NAND tiene entradas activas en ______.", "bajo (clase 10)"),
    ("En el flip-flop JK, con J = K = 1, la salida ______.", "conmuta (clase 10)"),
    ("Con N flip-flops, un contador binario tiene ______ estados.", "2<super>N</super> (clase 10)"),
    ("Las entradas asincrónicas PRESET y CLEAR son ______ y pueden ignorar las entradas sincrónicas.", "predominantes (clase 10)"),
    ("Un registro que recibe un bit por pulso y entrega todos a la vez es de tipo ______.", "SIPO, serie-paralelo (clase 10)"),
]

VF = [
    ("La FPU siempre estuvo integrada dentro del microprocesador.", "Falso. Antiguamente estaba en un chip externo."),
    ("La caché L2 es más grande pero algo menos rápida que la L1.", "Verdadero."),
    ("La velocidad interna del micro suele ser menor que la del bus FSB.", "Falso. La interna es mucho mayor (por ejemplo, 800 MHz frente a 100 MHz)."),
    ("La ROM puede ser escrita por el usuario y se borra al apagar.", "Falso. Es de solo lectura y no se borra al apagar."),
    ("El sistema operativo se carga en la RAM al encender la computadora.", "Verdadero."),
    ("Un fallo de caché se resuelve trayendo un bloque desde la memoria principal.", "Verdadero."),
    ("La memoria en la red es la más rápida de la jerarquía.", "Falso. Es la de mayor capacidad y la más lejana a la CPU; la más rápida son los registros."),
    ("En un circuito secuencial, la salida depende solo de las entradas actuales.", "Falso. Depende de las entradas actuales y pasadas (eso es combinacional)."),
    ("Una FSM puede estar en dos estados a la vez.", "Falso. Nunca puede estar en más de un estado a la vez."),
    ("En el latch SR con NOR, S = R = 1 es el estado ambiguo.", "Verdadero."),
    ("El latch D copia la entrada solo en el flanco de subida.", "Falso. Eso es el FF D; el latch copia mientras enable está en alto."),
    ("En un contador asíncrono, todos los FF cambian exactamente al mismo tiempo.", "Falso. Eso es el síncrono; en el asíncrono se acumulan los retrasos de propagación."),
    ("El 74ALS161 tiene un CLR síncrono.", "Falso. Su CLR es asíncrono: pone 0000 de inmediato."),
    ("En un bus, varios registros triestado pueden tener la salida habilitada a la vez sin problema.", "Falso. Se produce una colisión de bus."),
]

EJ_FF = [
    ("FF JK, Q inicial = 0. Pares (J, K) en flancos sucesivos: (1,0) · (0,0) · (1,1) · (1,1) · (0,1) · (1,1). Escribe Q después de cada flanco.",
     "1 · 1 · 0 · 1 · 0 · 1 (set, sin cambio, conmuta, conmuta, reset, conmuta)."),
    ("FF D, Q inicial = 0. D en los flancos positivos: 1 · 1 · 0 · 1 · 0 · 0. Escribe Q después de cada flanco.",
     "1 · 1 · 0 · 1 · 0 · 0 (Q copia D en cada flanco)."),
    ("Latch SR con NOR, Q inicial = 0. Secuencia (S, R): (1,0) · (0,0) · (0,1) · (0,0). ¿Qué vale Q en cada paso?",
     "1 (SET) · 1 (sin cambio) · 0 (RESET) · 0 (sin cambio)."),
    ("Latch SR con NAND. ¿Qué ocurre con S' = 0 y R' = 1? ¿Y con S' = R' = 0?",
     "S' = 0, R' = 1 → SET (Q = 1). S' = R' = 0 → estado ambiguo."),
    ("FF JK con flanco descendente, PRE y CLR activos en bajo. J = K = 1 y en un momento CLR = 0. ¿Qué pasa con Q?",
     "Q pasa a 0 de inmediato, sin esperar al reloj: CLR es asíncrono y predomina sobre J y K."),
]

EJ_CONT = [
    ("Un contador asíncrono de 4 FF recibe un reloj de 16 kHz. ¿Qué módulo tiene y qué frecuencia sale del último FF?",
     "MOD-16. 16 kHz ÷ 16 = 1 kHz."),
    ("¿Cuántos flip-flops necesitas para un contador MOD-10 (BCD)? ¿En qué estado debe reiniciarse?",
     "4 FF (2<super>3</super> = 8 no alcanza). Se reinicia al llegar a 10 = 1010, con una NAND de Q3 y Q1 conectada a CLR."),
    ("En el contador MOD-6 de la clase, ¿por qué la NAND usa solo las salidas B y C?",
     "Porque 6 = 110 es el primer estado de la cuenta con B = 1 y C = 1 a la vez. Al detectarlo, la NAND pasa a 0 y borra todos los FF."),
    ("Un 74ALS161 con CLR = 1 y LOAD = 0 recibe un flanco positivo, con DCBA = 1100. ¿Qué valor toma?",
     "Carga 1100 (12): LOAD es activo en bajo. Desde ahí sigue contando 13, 14, 15 y vuelve a 0."),
    ("Se conectan dos 74ALS161 en cascada. ¿Cuántos estados tiene el conjunto y qué señal une las etapas?",
     "2<super>8</super> = 256 estados (8 bits). RCO de la primera etapa va a ENT de la segunda."),
]

EJ_REG = [
    ("Clasifica: 74ALS174, 74ALS166, 74ALS165, 74ALS164.",
     "174: PIPO. 166: SISO (también admite carga paralela). 165: PISO. 164: SIPO."),
    ("En el 74ALS166, ¿qué hacen SH/LD' = 1 y CLK INH = 1?",
     "SH/LD' = 1: desplazamiento en serie. CLK INH = 1: inhibe el desplazamiento y la carga."),
    ("En el 74ALS165, ¿la carga paralela y el desplazamiento son síncronos o asíncronos?",
     "La carga paralela es asíncrona; el desplazamiento en serie es síncrono."),
    ("En el 74ALS194, ¿qué modo corresponde a cada combinación de S1 S0?",
     "00 retención · 01 desplazamiento a la derecha (entra por SRSI) · 10 desplazamiento a la izquierda (entra por SLSI) · 11 carga paralela."),
    ("Bus con tres 74ALS173 (A, B, C). ¿Qué señales necesitas para transferir [A] → [C]?",
     "Habilitar la salida de A (OE'<sub>A</sub> = 0) y la entrada de C (IE'<sub>C</sub> = 0). Las demás OE' e IE' en 1. El dato pasa en el flanco positivo de reloj."),
]

DESARROLLO = [
    ("Explica con tus palabras por qué existe la memoria caché. Usa los conceptos de velocidad interna, FSB y jerarquía de memorias.",
     "El micro trabaja mucho más rápido que la RAM y que el bus que los comunica. Sin caché, el micro esperaría cada dato. La caché es una SRAM rápida y cara situada entre ambos, "
     "con los datos que probablemente se usarán. Por eso está en la jerarquía justo debajo de los registros."),
    ("Relaciona las tres clases: ¿qué tienen que ver los flip-flops con la memoria caché y los registros del microprocesador?",
     "Los registros del micro son grupos de flip-flops. La caché es SRAM, cuyas celdas son biestables realimentados, como el latch. Los circuitos secuenciales son el «ladrillo» de la memoria rápida."),
    ("En el ejemplo de diseño 2 de la clase 10, la salida Q1 está escrita dentro de cada estado. ¿Es una máquina de Mealy o de Moore? Justifica.",
     "Es de <b>Moore</b>: Q1 depende solo del estado (st0 y st1 → 0; st2 y st3 → 1), no de A ni de B."),
]


TAG = ParagraphStyle("tag9", parent=S["tag"], fontSize=8.8, leading=11.5)


def ficha(tag, sub, q, resp, clave, fijar):
    tg = Table([[Paragraph(tag, TAG)], [Paragraph(sub, S["tagsm"])]], colWidths=[24 * mm])
    tg.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    right = [
        P(q, "q"), Spacer(1, 3),
        P(f"<b>Respuesta:</b> {resp}", "cell"), Spacer(1, 3),
        P(f"<font color='#2F6B45'><b>Idea en una línea:</b></font> {clave}", "cell"), Spacer(1, 2),
        P(f"<font color='#B7791F'><b>Para fijarlo:</b></font> {fijar}", "cell"),
    ]
    t = Table([[tg, right]], colWidths=[27 * mm, 147 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("TOPPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 7), ("RIGHTPADDING", (1, 0), (1, 0), 7),
        ("TOPPADDING", (1, 0), (1, 0), 6), ("BOTTOMPADDING", (1, 0), (1, 0), 6),
    ]))
    return KeepTogether([t, Spacer(1, 5)])


def figura(drawing, pie):
    return KeepTogether([drawing, P(f"<font color='#5A6270'>{pie}</font>", "small"), Spacer(1, 8)])


def extras_unidad(uid):
    """Material visual y tablas que se insertan después de ciertas fichas."""
    out = {}
    if uid == "1":
        out[8] = [
            P("Línea de tiempo esencial", "h2"),
            P("No memorices las 40 fechas de la clase: fija estos <b>anclajes</b> y ubica el resto entre ellos."),
            grid(LINEA_TIEMPO, [32 * mm, 86 * mm, 56 * mm]), Spacer(1, 6),
            P("Modelos y su rasgo distintivo", "h2"),
            P("Para cada modelo, aprende <b>un solo rasgo</b>: es lo que suelen preguntar («¿qué micro introdujo las instrucciones SSE?»)."),
            grid(MODELOS, [44 * mm, 130 * mm]), Spacer(1, 4),
            box([P("<b>Contexto:</b> la clase llama «actuales» a modelos de 1999 a 2013. Para el examen, estudia los modelos tal como los presenta la clase. "
                   "Hoy existen generaciones mucho más nuevas.")], AMBER_BG, AMBER),
            Spacer(1, 6),
        ]
    if uid == "2":
        out[2] = [figura(diagrama_proceso_cpu(), "Proceso completo de una operación: la memoria interviene antes y después de ejecutar.")]
        out[6] = [
            P("ROM frente a RAM", "h2"),
            grid([
                ["", "ROM", "RAM"],
                ["Significado", "Read Only Memory (solo lectura)", "Random Access Memory (acceso aleatorio)"],
                ["¿Se puede escribir?", "No: la grabó el fabricante", "Sí: es la memoria de trabajo"],
                ["¿Al apagar?", "Conserva la información", "Pierde la información (volátil)"],
                ["¿Qué guarda?", "Instrucciones y datos técnicos de los componentes (BIOS)", "Programas y archivos abiertos, y el sistema operativo"],
                ["¿Dónde está?", "Chip soldado en la placa base", "Módulos en los zócalos de la placa base"],
            ], [34 * mm, 70 * mm, 70 * mm]), Spacer(1, 8),
        ]
        out[10] = [figura(diagrama_jerarquia(), "Jerarquía de memorias. Frase para el orden: «Rosa Come Pan Sin Azúcar Refinado».")]
    if uid == "3":
        out[3] = [figura(diagrama_maquina(), "Modelo general (Mealy, clase A). D.P.E. y D.S. son combinacionales; solo el E.M. recibe el reloj. "
                                             "Moore (clase B) elimina la línea roja: las entradas no llegan a la salida.")]
        out[5] = [
            figura(diagrama_maquina(salida=False), "Clase C: no hay decodificador de salida, la salida es el propio estado."),
            grid([
                ["Clase", "Máquina", "Bloques", "Salida"],
                ["A", "Mealy (modelo general)", "D.P.E. + E.M. + D.S.", "Y = λ(X, Z)"],
                ["B", "Moore", "D.P.E. + E.M. + D.S.", "Y = λ(Z)"],
                ["C", "Sin decodificador de salida", "D.P.E. + E.M.", "Y = Z"],
            ], [18 * mm, 52 * mm, 56 * mm, 48 * mm]), Spacer(1, 8),
        ]
        out[9] = [
            P("Tablas de verdad de los biestables", "h2"),
            P("Tapa la columna Q y reconstrúyela tú. Si lo logras con las cuatro tablas, dominas el tema."),
            grid([
                ["Entradas", "Latch NAND (S' R')", "Latch NOR (S R)", "FF SR (S R) en flanco", "FF JK (J K) en flanco"],
                ["0 0", "Ambiguo", "Sin cambio", "Sin cambio", "Sin cambio"],
                ["0 1", "SET (Q = 1)", "RESET (Q = 0)", "RESET (Q = 0)", "RESET (Q = 0)"],
                ["1 0", "RESET (Q = 0)", "SET (Q = 1)", "SET (Q = 1)", "SET (Q = 1)"],
                ["1 1", "Sin cambio", "Ambiguo", "Ambiguo", "<b>Conmuta</b> (Q')"],
            ], [22 * mm, 36 * mm, 36 * mm, 40 * mm, 40 * mm], center=True), Spacer(1, 6),
            grid([
                ["", "Latch D transparente", "Flip-flop D"],
                ["Control", "Habilitación (enable), por nivel", "Reloj, por flanco"],
                ["Detector de flancos", "No tiene", "Sí tiene"],
                ["Comportamiento", "Enable = 1: Q sigue a D. Enable = 0: Q se mantiene", "Q toma el valor de D solo en el flanco positivo"],
                ["Imagen", "Una ventana abierta mientras dura el nivel", "Una foto en el instante del flanco"],
            ], [34 * mm, 70 * mm, 70 * mm]), Spacer(1, 8),
        ]
        out[12] = [figura(diagrama_contador_mod8(), "Contador asíncrono MOD-8 con FF JK (J = K = 1, flanco descendente). Cada salida tiene la mitad "
                                                    "de frecuencia que la anterior y la cuenta Q2Q1Q0 avanza de 000 a 111.")]
        out[16] = [
            CondPageBreak(110 * mm),
            P("Ejemplo de la clase resuelto: contador 0 → 1 → 2 → 3 → 4 → 0", "h2"),
            P("Contador síncrono de 3 bits (C B A) que cuenta 000 a 100 y vuelve a 000. Los estados 101, 110 y 111 son indeseables y también van a 000. "
              "<b>Intenta completar las columnas J/K antes de mirarlas.</b>"),
            grid([
                ["C B A", "Siguiente", "JC KC", "JB KB", "JA KA"],
                ["0 0 0", "0 0 1", "0 x", "0 x", "1 x"],
                ["0 0 1", "0 1 0", "0 x", "1 x", "x 1"],
                ["0 1 0", "0 1 1", "0 x", "x 0", "1 x"],
                ["0 1 1", "1 0 0", "1 x", "x 1", "x 1"],
                ["1 0 0", "0 0 0", "x 1", "0 x", "0 x"],
                ["1 0 1", "0 0 0", "x 1", "0 x", "x 1"],
                ["1 1 0", "0 0 0", "x 1", "x 1", "0 x"],
                ["1 1 1", "0 0 0", "x 1", "x 1", "x 1"],
            ], [30 * mm, 30 * mm, 38 * mm, 38 * mm, 38 * mm], center=True), Spacer(1, 4),
            box([P("<b>Funciones simplificadas</b> (las x se usan como comodines): "
                   "<b>JA = C'</b>, <b>KA = 1</b> (la clase lo señala) · <b>JB = A·C'</b>, <b>KB = A + C</b> · <b>JC = A·B</b>, <b>KC = 1</b>. "
                   "Comprobación: desde 011, JC = 1·1 = 1 → C sube a 1; KB = 1 → B baja; KA = 1 → A baja. Resultado 100, correcto.")], GREEN_BG, GREEN),
            Spacer(1, 8),
            KeepTogether([P("Ejemplo de diseño con el 74161: cuándo cargar y cuándo contar", "h2"),
            P("En el primer ejemplo de diseño, la máquina avanza 00 → 01 → 10 → 11 → 00 con IN = 1 y se queda en su estado con IN = 0. En la tabla de la clase, "
              "<b>LD = 1 indica «cargar»</b>: con IN = 0 se recarga el mismo estado (se queda quieta), y con IN = 1 en el estado 11 se carga 00. "
              "En los demás casos el contador simplemente cuenta. Así se obtiene LD = IN' + QB·QA. Como la entrada LOAD del 74161 es <b>activa en bajo</b>, "
              "al pin se le aplica la negación: <b>(IN' + QB·QA)'</b>, que es la expresión de la diapositiva.")]),
            Spacer(1, 6),
        ]
        out[17] = [
            P("Registros de circuito integrado", "h2"),
            grid([
                ["CI", "Tipo", "Lo que tienes que recordar"],
                ["74ALS174", "PIPO", "Carga paralela en flanco ascendente. MR (Master Reset) asíncrono pone todo a 0."],
                ["74ALS166", "SISO", "Entra por SER (QA) y sale por QH. También carga en paralelo. SH/LD' = 1 desplaza, 0 carga. CLK INH = 1 inhibe."],
                ["74ALS165", "PISO", "Ocho FF. Entrada serie DS y paralela P0-P7. Carga paralela <b>asíncrona</b>, desplazamiento <b>síncrono</b>. CP INH inhibe el reloj."],
                ["74ALS164", "SIPO", "La entrada serie es la AND de A y B (símbolo &amp;). Desplaza en flanco positivo. MR asíncrono."],
                ["74ALS194", "Universal, 4 bits", "Entradas paralelas A-D, serie SRSI (derecha) y SLSI (izquierda). Modo con S1 S0: 00 retiene, 01 derecha, 10 izquierda, 11 carga."],
                ["74ALS173", "PIPO + triestado", "4 bits. Modos carga y retención. Salidas a búferes triestado para conectarse a un bus."],
                ["74ALS373", "Latch triestado", "Se usa como puerto de entrada y de salida conectado a un bus."],
            ], [24 * mm, 30 * mm, 120 * mm]), Spacer(1, 8),
        ]
    return out


def build():
    story = []
    # Portada -------------------------------------------------------------
    story += [Spacer(1, 40 * mm), P("Microprocesador, memorias y circuitos secuenciales", "title"), Spacer(1, 4),
              P("Resumen para fijar conocimientos", "subtitle"),
              P("Clase 8 · Clase 9 · Clase 10", "subtitle"), Spacer(1, 16 * mm)]
    story.append(box([P("<b>Este material está hecho para practicar, no solo para leer.</b> Cada ficha tiene una pregunta que debes responder "
                        "<b>de memoria antes</b> de mirar la respuesta. Los ejercicios de flip-flops y contadores se aprenden <b>haciéndolos</b>, "
                        "no viéndolos resueltos.")], LIGHT, NAVY))
    story += [Spacer(1, 8 * mm), P("Qué contiene", "h2")]
    story += bullets([
        "<b>Mapa</b> que conecta las tres clases en una sola historia.",
        "<b>Tres unidades de fichas</b> con pregunta, respuesta, idea en una línea y recurso para fijarla.",
        "<b>Diagramas propios</b>: proceso de la CPU, jerarquía de memorias, modelo de máquina de estados y diagrama de tiempos de un contador.",
        "<b>Tablas para reconstruir</b>: biestables, latch frente a flip-flop, registros de CI, línea de tiempo y modelos de micro.",
        "<b>Ejemplo de diseño resuelto</b> de un contador síncrono con FF JK.",
        "<b>Práctica</b>: completar, verdadero o falso, trazas de flip-flops, contadores, registros y preguntas de desarrollo.",
        "<b>Tarjetas</b> de repaso, <b>control de repasos</b> y <b>solucionario</b>.",
    ])
    story.append(PageBreak())

    # Método y mapa ---------------------------------------------------------
    story.append(P("1. Cómo estudiar con este resumen", "h1"))
    story += bullets([
        "<b>Recupera antes de leer.</b> Tapa la respuesta de cada ficha y contéstala en voz alta o por escrito. Equivocarse ahora ayuda a recordar.",
        "<b>Dibuja.</b> En la clase 10, reconstruir una tabla de verdad o un diagrama de tiempos fija mucho más que mirarlos.",
        "<b>Espacia los repasos.</b> Usa la tabla de control: día 1, día 3 y día 7, más un repaso el día antes del examen.",
        "<b>Conecta.</b> Los recuadros «Para fijarlo» señalan los puentes entre clases. Son las preguntas que mejor distinguen a quien entendió.",
    ])
    story.append(P("Plan sugerido", "h2"))
    story.append(grid([
        ["Sesión", "Qué hacer", "Tiempo"],
        ["Día 1", "Mapa + unidades 1 y 2 con el método de la ficha. Autoevaluaciones.", "60 min"],
        ["Día 2", "Unidad 3. Reconstruye las tablas de biestables y el ejemplo de diseño sin mirar.", "75 min"],
        ["Día 3", "Ejercicios de práctica 1 a 4. Corrige y vuelve a las fichas de los errores.", "45 min"],
        ["Día 5", "Ejercicios 5 a 7 y tarjetas de repaso.", "40 min"],
        ["Día antes", "Tarjetas marcadas como «parcial» o «no». Repite un diagrama de tiempos y la tabla de excitación.", "30 min"],
    ], [26 * mm, 124 * mm, 24 * mm]))
    story.append(Spacer(1, 8))
    story.append(P("2. Mapa: una sola historia en tres clases", "h1"))
    story.append(box([P("<b>Clase 8 · El que piensa.</b> El microprocesador ejecuta instrucciones, pero va más rápido que todo lo que lo rodea.<br/>"
                        "→ <b>Clase 9 · Dónde guarda.</b> Necesita memoria para instrucciones y datos. Como la RAM es lenta, aparece la caché y una jerarquía completa.<br/>"
                        "→ <b>Clase 10 · Con qué se construye.</b> Registros, caché y contadores se hacen con circuitos secuenciales: flip-flops sincronizados por un reloj.")],
                     LIGHT, BLUE))
    story.append(Spacer(1, 6))
    story.append(grid([
        ["Concepto puente", "Clase 8", "Clase 9", "Clase 10"],
        ["Caché", "Parte del micro: L1 y L2", "SRAM entre CPU y RAM; fallo de caché", "Sus celdas son biestables"],
        ["Registros", "Memoria pequeña del micro", "Cima de la jerarquía", "Grupos de flip-flops"],
        ["Velocidad / reloj", "Velocidad interna y FSB", "La RAM no da abasto desde el 386", "El reloj sincroniza todos los cambios"],
        ["Memoria", "Espacio de trabajo del procesador", "Posiciones, direcciones, ROM y RAM", "Elemento de memoria de una FSM"],
    ], [34 * mm, 46 * mm, 48 * mm, 46 * mm]))
    story.append(PageBreak())

    # Unidades --------------------------------------------------------------
    for u in UNIDADES:
        story.append(CondPageBreak(120 * mm))
        story.append(P(f"Unidad {u['id']} · {u['nombre']} <font size=10 color='#5A6270'>({u['clase']})</font>", "h1"))
        story.append(box([P(u["intro"])], LIGHT, BLUE))
        story.append(Spacer(1, 7))
        if u["id"] == "3":
            story.append(box([P("<b>Notación:</b> como en las diapositivas (Q´), la comilla indica negación o señal activa en bajo. "
                                "Q' es «Q negada» y LD' es una entrada LOAD que actúa con 0.")], AMBER_BG, AMBER))
            story.append(Spacer(1, 5))
            story.append(box([P("<b>Dos imprecisiones de las diapositivas.</b> La definición inicial dice «circuito combinacional», pero describe un circuito "
                                "<b>secuencial</b>. La diapositiva del JK repite la frase del SR; la diferencia que debes saber es que el JK <b>conmuta con J = K = 1</b> "
                                "en lugar de quedar ambiguo.")], RED_BG, RED))
            story.append(Spacer(1, 7))
        extras = extras_unidad(u["id"])
        for i, f in enumerate(u["fichas"]):
            story.append(ficha(*f))
            story += extras.get(i, [])
        auto = [P(f"Autoevaluación de la unidad {u['id']} (respuestas en el solucionario)", "cellb")]
        for i, (q, _) in enumerate(AUTOEVAL[u["id"]], 1):
            auto.append(P(f"{i}. {q}", "cell"))
        story.append(KeepTogether([box(auto, GREEN_BG, GREEN)]))
        story.append(Spacer(1, 10))
    story.append(PageBreak())

    # Herramientas ----------------------------------------------------------
    story.append(P("3. Herramientas de memoria", "h1"))
    story.append(P("Pares que suelen confundirse", "h2"))
    story.append(grid([
        ["Se confunde…", "…con…", "La diferencia"],
        ["Velocidad interna", "Velocidad FSB", "Interna: dentro del micro. FSB: entre micro y placa base."],
        ["Caché L1", "Caché L2", "L1 más cerca, más chica y más rápida. L2 más grande y algo más lenta."],
        ["ROM", "RAM", "ROM: solo lectura, no volátil. RAM: lectura y escritura, volátil."],
        ["Caché", "RAM", "Son parecidas; la caché es SRAM rápida y cara, ubicada entre CPU y RAM."],
        ["Combinacional", "Secuencial", "Combinacional: solo entradas actuales. Secuencial: también las pasadas, porque tiene memoria."],
        ["Moore", "Mealy", "Moore: salida = f(estado). Mealy: salida = f(estado, entradas)."],
        ["Latch", "Flip-flop", "Latch: actúa por nivel. Flip-flop: actúa por flanco."],
        ["Latch NAND", "Latch NOR", "NAND: entradas activas en bajo, 00 ambiguo. NOR: activas en alto, 11 ambiguo."],
        ["FF SR", "FF JK", "Con 11, el SR queda ambiguo y el JK conmuta."],
        ["Entradas sincrónicas", "Entradas asincrónicas", "Sincrónicas (S, R, J, K, D) esperan el reloj. Asincrónicas (PRE, CLR) actúan ya."],
        ["Contador asíncrono", "Contador síncrono", "Asíncrono: cada FF dispara al siguiente. Síncrono: un reloj común para todos."],
        ["PISO", "SIPO", "PISO: entra paralelo, sale serie. SIPO: entra serie, sale paralelo."],
    ], [38 * mm, 38 * mm, 98 * mm]))
    story.append(Spacer(1, 6))
    story.append(CondPageBreak(70 * mm))
    story.append(P("Mnemotecnias y fórmulas", "h2"))
    story.append(grid([
        ["Recurso", "Qué recuerda", "Clase"],
        ["<b>R-I-C</b>", "Funciones del micro: Recupera, Interpreta, Cumple instrucciones", "8"],
        ["<b>OR = unión · AND = intersección</b>", "Operaciones lógicas entre conjuntos", "8"],
        ["<b>286 → 386 → 486</b>: 1982, 1985, 1989", "Uno cada 3-4 años; Pentium en 1993", "8"],
        ["<b>N-S-I-H</b>", "Generaciones Core: Nehalem (2008), Sandy (2011), Ivy (2012), Haswell (2013)", "8"],
        ["«<b>R</b>osa <b>C</b>ome <b>P</b>an <b>S</b>in <b>A</b>zúcar <b>R</b>efinado»", "Jerarquía: Registros, Caché, Principal, Secundaria, Auxiliar, Red", "9"],
        ["<b>RAM volátil = se evapora</b>", "Sin energía, los datos se pierden", "9"],
        ["<b>X entra · Y sale · Z recuerda</b>", "Elementos de la FSM; δ próximo estado, λ salida", "10"],
        ["«M<b>oo</b>re, s<b>o</b>l<b>o</b> estad<b>o</b>» · «M<b>e</b>aly m<b>e</b>zcla <b>e</b>ntradas»", "Diferencia entre las dos máquinas", "10"],
        ["<b>Para subir, J; para bajar, K</b>", "Tabla de excitación JK: la otra entrada es x", "10"],
        ["<b>N FF → 2<super>N</super> estados</b>", "Módulo máximo y división de frecuencia (f ÷ 2<super>N</super>)", "10"],
        ["<b>FF necesarios = menor N con 2<super>N</super> ≥ módulo</b>", "MOD-6 y MOD-8: 3 FF · MOD-10 y MOD-16: 4 FF", "10"],
        ["<b>Primera letra entra, última sale</b>", "PIPO, SISO, PISO, SIPO", "10"],
    ], [64 * mm, 96 * mm, 14 * mm]))
    story.append(PageBreak())

    # Práctica --------------------------------------------------------------
    story.append(P("4. Práctica activa", "h1"))
    story.append(box([P("Haz los ejercicios <b>sin mirar las fichas</b>. Corrige con el solucionario y vuelve a la ficha de cada error.")], AMBER_BG, AMBER))
    story.append(P("Ejercicio 1 · Completa los espacios", "h2"))
    for i, (t, _) in enumerate(HUECOS, 1):
        story.append(P(f"{i}. {t}"))
    story.append(CondPageBreak(90 * mm))
    story.append(P("Ejercicio 2 · Verdadero o falso. Si es falso, corrígelo", "h2"))
    rows = [["Afirmación", "V / F"]] + [[f"{i}. {t}", ""] for i, (t, _) in enumerate(VF, 1)]
    story.append(grid(rows, [154 * mm, 20 * mm]))
    story.append(CondPageBreak(70 * mm))
    story.append(P("Ejercicio 3 · Ordena en el tiempo", "h2"))
    story.append(P("Ordena del más antiguo al más reciente y escribe el año: Pentium III · Intel 4004 · 80386 · Core 2 Duo · Haswell · Pentium · 8086 · Sandy Bridge."))
    story.append(Spacer(1, 16))
    story.append(P("Ejercicio 4 · Ordena la jerarquía", "h2"))
    story.append(P("Ordena de la más rápida a la de mayor capacidad: memoria secundaria · registros · memoria en la red · memoria principal · caché · memoria auxiliar."))
    story.append(Spacer(1, 16))
    for titulo, lista, n in (("Ejercicio 5 · Trazas de biestables", EJ_FF, 5),
                             ("Ejercicio 6 · Contadores", EJ_CONT, 6),
                             ("Ejercicio 7 · Registros y bus", EJ_REG, 7),
                             ("Ejercicio 8 · Preguntas de desarrollo", DESARROLLO, 8)):
        story.append(CondPageBreak(60 * mm))
        story.append(P(titulo, "h2"))
        for i, (q, _) in enumerate(lista, 1):
            story.append(KeepTogether([P(f"<b>{n}.{i}</b> {q}"), Spacer(1, 18 if n == 8 else 10)]))
    story.append(PageBreak())

    # Tarjetas --------------------------------------------------------------
    story.append(P("5. Tarjetas de repaso", "h1"))
    story.append(P("Dobla la hoja por la línea central o tapa la columna derecha. Responde y marca el resultado en la tabla de control."))
    rows = [["Pregunta", "Respuesta (tápala)"]]
    for u in UNIDADES:
        for tag, sub, q, _, clave, _ in u["fichas"]:
            rows.append([f"<b>[{u['clase']}]</b> {q}", clave])
    t = grid(rows, [92 * mm, 82 * mm])
    t.setStyle(TableStyle([("LINEAFTER", (0, 0), (0, -1), 1.5, NAVY)]))
    story.append(t)
    story.append(PageBreak())

    # Control ---------------------------------------------------------------
    story.append(P("6. Control de repasos", "h1"))
    story.append(P("Marca en cada repaso: <b>✓</b> lo sé completo · <b>~</b> parcial · <b>✗</b> no lo sé."))
    rows = [["Clase", "Tema", "Repaso 1", "Repaso 2", "Repaso 3"]]
    for u in UNIDADES:
        for tag, sub, *_ in u["fichas"]:
            rows.append([u["clase"], f"{tag}: {sub}", "", "", ""])
    for extra in ("Clase 8: línea de tiempo", "Clase 8: modelos y rasgos", "Clase 10: tablas de biestables",
                  "Clase 10: diagrama de tiempos MOD-8", "Clase 10: ejemplo de diseño JK", "Clase 10: registros de CI"):
        c, tema = extra.split(": ")
        rows.append([c, tema, "", "", ""])
    story.append(grid(rows, [22 * mm, 80 * mm, 24 * mm, 24 * mm, 24 * mm]))
    story.append(PageBreak())

    # Solucionario ----------------------------------------------------------
    story.append(P("7. Solucionario", "h1"))
    story.append(P("Autoevaluaciones", "h2"))
    for u in UNIDADES:
        story.append(P(f"<b>Unidad {u['id']} · {u['clase']}</b>", "small"))
        for i, (_, a) in enumerate(AUTOEVAL[u["id"]], 1):
            story.append(P(f"{i}. {a}", "small"))
        story.append(Spacer(1, 3))
    story.append(P("Ejercicio 1 · Completa los espacios", "h2"))
    for i, (_, a) in enumerate(HUECOS, 1):
        story.append(P(f"{i}. {a}", "small"))
    story.append(P("Ejercicio 2 · Verdadero o falso", "h2"))
    for i, (_, a) in enumerate(VF, 1):
        story.append(P(f"{i}. {a}", "small"))
    story.append(P("Ejercicio 3 · Línea de tiempo", "h2"))
    story.append(P("Intel 4004 (1971) · 8086 (1978) · 80386 (1985) · Pentium (1993) · Pentium III (1999) · Core 2 Duo (2006) · Sandy Bridge (2011) · Haswell (2013).", "small"))
    story.append(P("Ejercicio 4 · Jerarquía", "h2"))
    story.append(P("Registros · caché · memoria principal · memoria secundaria · memoria auxiliar · memoria en la red.", "small"))
    for titulo, lista, n in (("Ejercicio 5 · Trazas de biestables", EJ_FF, 5), ("Ejercicio 6 · Contadores", EJ_CONT, 6),
                             ("Ejercicio 7 · Registros y bus", EJ_REG, 7), ("Ejercicio 8 · Desarrollo", DESARROLLO, 8)):
        story.append(P(titulo, "h2"))
        for i, (_, a) in enumerate(lista, 1):
            story.append(P(f"<b>{n}.{i}</b> {a}", "small"))
            story.append(Spacer(1, 2))
    story.append(Spacer(1, 8))
    story.append(box([P("<b>Último consejo:</b> antes del examen, dibuja de memoria en una hoja la jerarquía de memorias, el modelo D.P.E. → E.M. → D.S. "
                        "y la tabla de excitación JK. Si puedes hacerlo en dos minutos, tienes la base de las tres clases.")], LIGHT, NAVY))

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                            title="Resumen para fijar conocimientos - Clases 8, 9 y 10", author="Resumen de estudio")
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=on_page)
    print(f"PDF generado: {OUT}")


if __name__ == "__main__":
    build()
