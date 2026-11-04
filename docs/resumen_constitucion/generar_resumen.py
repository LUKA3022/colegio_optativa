"""Genera el PDF de estudio del cuestionario (segunda parcial y final).

Uso: python docs/resumen_constitucion/generar_resumen.py
Requiere reportlab y las fuentes DejaVu instaladas en el sistema.
"""
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    CondPageBreak, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pdf_estilo import (  # noqa: E402
    AMBER, AMBER_BG, BLUE, GREEN, GREEN_BG, LIGHT, LINE, NAVY, RED, RED_BG, S,
    P, box, bullets, grid, make_on_page,
)

OUT = Path(__file__).with_name("resumen_cuestionario_constitucion.pdf")


# ---------------------------------------------------------------------------
# Contenido: cada ficha = (n.º pregunta, artículo, pregunta, respuesta, idea clave, para fijar)
# ---------------------------------------------------------------------------
BLOQUES = [
    {
        "id": "A", "nombre": "Educación y cultura", "arts": "Arts. 76 a 85",
        "intro": "Hilo conductor: el Estado <b>garantiza</b> la educación básica, <b>sostiene</b> la superior, "
                 "<b>ayuda</b> a quien no tiene recursos, <b>protege</b> la cultura y la <b>financia</b> con un mínimo fijo de presupuesto.",
        "fichas": [
            (30, 76, "¿Qué establece el artículo 76 sobre la educación escolar básica?",
             "Es <b>obligatoria</b> y <b>gratuita en las escuelas públicas</b>. El Estado también fomentará la enseñanza media, técnica, agropecuaria, industrial y superior o universitaria, además de la investigación científica y tecnológica.",
             "Básica = obligatoria + gratuita (en lo público). El resto de niveles: el Estado los <b>fomenta</b>.",
             "Distingue los verbos: la básica se <b>impone</b> (obligatoria); los demás niveles se <b>fomentan</b>. La gratuidad se limita a las escuelas <b>públicas</b>."),
            (31, 79, "¿Cuáles son las finalidades principales de las universidades e institutos superiores?",
             "La <b>formación profesional superior</b>, la <b>investigación</b> científica y tecnológica y la <b>extensión universitaria</b>. Las universidades son <b>autónomas</b> y serán <b>creadas por ley</b>.",
             "Tres fines: Formar, Investigar, Extender. Dos rasgos: autónomas y creadas por ley.",
             "Mnemotecnia <b>F-I-E</b> (Formación, Investigación, Extensión). Pregunta trampa típica: «¿las crea un decreto?». No: las crea una <b>ley</b>."),
            (7, 80, "¿Para qué se constituyen los fondos para becas y otras ayudas?",
             "Para facilitar la formación <b>intelectual, científica, técnica o artística</b>, con preferencia de las personas que <b>carezcan de recursos</b>.",
             "Becas = igualdad de oportunidades; prioridad para quien no tiene recursos.",
             "Cuatro tipos de formación: <b>I-C-T-A</b> (intelectual, científica, técnica, artística). Relaciónalo con el art. 85: uno dice <i>a quién</i> ayudar, el otro <i>cuánto</i> dinero se garantiza."),
            (12, 81, "¿Qué bienes deben ser conservados como parte del patrimonio cultural de la Nación?",
             "Objetos, documentos y espacios de valor <b>histórico, arqueológico, paleontológico, artístico o científico</b>, junto con sus respectivos <b>entornos físicos</b>.",
             "Qué: objetos, documentos, espacios. Por qué: cinco tipos de valor. Además: su entorno.",
             "Mnemotecnia <b>HAPAC</b>: Histórico, Arqueológico, Paleontológico, Artístico, Científico. No olvides «y sus entornos físicos»: es el detalle que suelen pedir."),
            (24, 82, "¿Qué reconoce la Constitución sobre la Iglesia Católica?",
             "Reconoce el <b>protagonismo</b> de la Iglesia Católica en la <b>formación histórica y cultural</b> de la Nación.",
             "Se reconoce un papel histórico-cultural; no se la declara religión oficial.",
             "Palabra exacta: <b>protagonismo</b>. Ubicación lógica: está en el capítulo de cultura, no en el de religión oficial del Estado."),
            (20, 83, "¿Qué dispone la Constitución respecto de ciertos objetos y actividades culturales o educativos?",
             "Prevé la <b>exoneración de impuestos fiscales y municipales</b> para objetos, publicaciones y actividades de interés cultural o educativo, en los términos del artículo y su reglamentación.",
             "Cultura y educación no pagan impuestos (ni nacionales ni municipales).",
             "Dos niveles de impuesto: <b>fiscales</b> (nación) y <b>municipales</b>. Tres cosas exoneradas: objetos, publicaciones, actividades."),
            (17, 84, "¿Qué debe hacer el Estado para promover el deporte?",
             "Promover especialmente los <b>deportes no profesionales</b>, brindar <b>apoyo económico y exenciones impositivas</b> establecidas por ley y estimular la <b>participación nacional en competencias internacionales</b>.",
             "Tres acciones: priorizar lo no profesional, apoyar con dinero e impuestos, impulsar lo internacional.",
             "Piensa en un club de barrio que viaja a un torneo internacional: el Estado lo prioriza (no profesional), lo ayuda (dinero y exenciones) y lo impulsa (competencia internacional)."),
            (1, 85, "¿Cuál es el porcentaje mínimo del Presupuesto General de la Nación que debe destinarse a educación?",
             "No debe ser inferior al <b>20 %</b> del total asignado a la <b>Administración Central</b>, <b>excluidos los préstamos y las donaciones</b>.",
             "Mínimo 20 % de la Administración Central, sin contar préstamos ni donaciones.",
             "Tres datos que van juntos: <b>20 %</b> · <b>Administración Central</b> (no del PIB ni de todo el Estado) · <b>sin préstamos ni donaciones</b>. Si recuerdas solo «20 %», la respuesta queda incompleta."),
        ],
    },
    {
        "id": "B", "nombre": "Derechos laborales", "arts": "Arts. 86 a 100",
        "intro": "Hilo conductor: el trabajo debe ser <b>digno</b> (86), <b>accesible</b> (87), <b>sin discriminación</b> (88), "
                 "con protección especial para <b>mujeres y menores</b> (89-90), con <b>límites y pagos</b> claros (91-92), "
                 "<b>estable</b> (94), <b>organizado colectivamente</b> (96-98) y <b>controlado</b> (99). Al final, la <b>vivienda</b> (100).",
        "fichas": [
            (15, 86, "¿Qué condiciones debe reunir el trabajo según el artículo 86?",
             "Debe ser <b>lícito</b>, <b>libremente escogido</b> y realizarse en <b>condiciones dignas y justas</b>. Los derechos que la ley otorga al trabajador son <b>irrenunciables</b>.",
             "Lícito + libre + digno y justo. Derechos irrenunciables.",
             "«Irrenunciable» significa que ni firmando un contrato el trabajador puede perderlos. Es el concepto que da sentido a todo el bloque."),
            (32, 87, "¿Qué política debe promover el Estado para alcanzar el pleno empleo?",
             "Políticas orientadas al <b>pleno empleo</b> y a la <b>formación profesional</b> de los recursos humanos, dando <b>preferencia al trabajador nacional</b>.",
             "Pleno empleo + capacitación + preferencia nacional.",
             "No confundir con el art. 88 (no discriminación). La «preferencia al trabajador nacional» es una política de empleo, no una discriminación prohibida."),
            (11, 88, "¿Qué formas de discriminación prohíbe el artículo 88 en el ámbito laboral?",
             "Por motivos <b>étnicos</b>, <b>sexo</b>, <b>edad</b>, <b>religión</b>, <b>condición social</b> y <b>preferencias políticas o sindicales</b>.",
             "Seis motivos prohibidos.",
             "Frase para recordar las iniciales <b>E-S-E-R-C-P</b>: «<b>E</b>sa <b>S</b>eñora <b>E</b>stá <b>R</b>ezando <b>C</b>on <b>P</b>aciencia» (Étnicos, Sexo, Edad, Religión, Condición social, Preferencias políticas o sindicales)."),
            (5, 89, "¿Cuál es la duración mínima del descanso por maternidad?",
             "<b>No inferior a doce semanas</b>. La mujer <b>no será despedida durante el embarazo</b> ni mientras duren los descansos por maternidad.",
             "12 semanas mínimo + prohibición de despido.",
             "Doce semanas, como doce meses del año. La respuesta completa tiene dos partes: el plazo y la protección contra el despido."),
            (33, 90, "¿Qué dispone la Constitución sobre el trabajo de los menores?",
             "Se dará <b>prioridad a los derechos del menor trabajador</b> para garantizar su normal desarrollo <b>físico, intelectual y moral</b>.",
             "Prioridad al menor para proteger su desarrollo en tres dimensiones.",
             "Tres desarrollos: <b>físico, intelectual, moral</b> (cuerpo, mente, valores)."),
            (9, 91, "¿Cuál es la duración máxima de la jornada ordinaria diurna de trabajo?",
             "<b>Ocho horas diarias</b> y <b>cuarenta y ocho horas semanales</b>, salvo las excepciones legalmente establecidas.",
             "8 h por día, 48 h por semana (8 × 6 días).",
             "Truco aritmético: 8 horas × 6 días laborables = 48. Si recuerdas uno, deduces el otro."),
            (25, 92, "¿Qué conceptos de remuneración laboral menciona el artículo 92?",
             "El <b>salario vital mínimo</b>, el <b>aguinaldo</b> anual, la <b>bonificación familiar</b> y la <b>remuneración superior</b> por horas extraordinarias, trabajo nocturno y días feriados.",
             "Tres pagos base + pago extra en tres situaciones.",
             "Mnemotecnia «<b>SAB + ENF</b>»: <b>S</b>alario vital mínimo, <b>A</b>guinaldo, <b>B</b>onificación familiar, y pagan más las horas <b>E</b>xtra, el trabajo <b>N</b>octurno y los <b>F</b>eriados."),
            (21, 94, "¿Qué derecho tiene el trabajador en caso de despido injustificado?",
             "Derecho a una <b>indemnización</b>, sin perjuicio de la <b>estabilidad laboral</b> en los términos de la ley.",
             "Despido sin causa = indemnización. Además existe la estabilidad.",
             "Dos ideas del mismo artículo: <b>estabilidad</b> (regla) e <b>indemnización</b> (consecuencia si se rompe sin causa)."),
            (26, 96, "¿Qué reconoce la Constitución respecto de la libertad sindical?",
             "El derecho de los trabajadores <b>públicos y privados</b> a organizarse en sindicatos <b>sin autorización previa</b>, con las excepciones previstas constitucionalmente.",
             "Sindicarse es libre, sin pedir permiso, tanto en lo público como en lo privado.",
             "Clave: «<b>sin necesidad de autorización previa</b>». Las excepciones constitucionales recaen sobre las Fuerzas Armadas y policiales, igual que en la huelga (art. 98)."),
            (22, 98, "¿Qué derechos reconoce la Constitución en materia de conflictos laborales?",
             "El derecho de <b>huelga</b> y de <b>paro</b> en las condiciones de la ley. Los miembros de las <b>Fuerzas Armadas y policiales</b> están <b>excluidos</b>.",
             "Huelga (trabajadores) y paro (empleadores). Excluidos: militares y policías.",
             "<b>Huelga</b> = la hacen los trabajadores. <b>Paro</b> = lo hacen los empleadores. Excluidos quienes portan armas del Estado: Fuerzas Armadas y Policía."),
            (23, 99, "¿Quién fiscaliza el cumplimiento de las normas laborales y de seguridad e higiene?",
             "Las <b>autoridades creadas por la ley</b>, que también establecerá las <b>sanciones</b> correspondientes.",
             "Fiscaliza la autoridad que crea la ley; la ley fija las sanciones.",
             "La Constitución no nombra un ministerio: remite a la <b>ley</b> dos veces (crea la autoridad y fija las sanciones)."),
            (4, 100, "¿Qué derecho reconoce la Constitución en materia de vivienda?",
             "Todos los habitantes tienen derecho a una <b>vivienda digna</b>. El Estado promueve planes de <b>vivienda de interés social</b>, especialmente para familias de <b>escasos recursos</b>.",
             "Vivienda digna para todos; planes sociales para quien menos tiene.",
             "Aunque está dentro del capítulo del trabajo, es un derecho de <b>todos los habitantes</b>, no solo de los trabajadores."),
        ],
    },
    {
        "id": "C", "nombre": "Función pública", "arts": "Arts. 101 a 105",
        "intro": "Hilo conductor: el funcionario <b>sirve al país</b> (101), tiene <b>derechos laborales</b> (102) y <b>jubilación actualizada</b> (103), "
                 "pero también <b>controles</b>: declara sus bienes (104) y no cobra dos sueldos públicos (105).",
        "fichas": [
            (19, 101, "¿A quiénes están al servicio los funcionarios y empleados públicos?",
             "Están <b>al servicio del país</b>. Todos los paraguayos tienen derecho a ocupar funciones y empleos públicos conforme a la ley.",
             "Sirven al país, no a un partido ni a un gobierno.",
             "Dos ideas: <b>servicio al país</b> y <b>acceso igualitario</b> de todos los paraguayos a los cargos."),
            (34, 102, "¿Qué derechos laborales tienen los funcionarios y empleados públicos?",
             "Los establecidos en la sección de <b>derechos laborales</b> de la Constitución, dentro de un <b>régimen uniforme</b> para las distintas carreras, con los límites legales y <b>resguardo de los derechos adquiridos</b>.",
             "Mismos derechos laborales + régimen uniforme + derechos adquiridos.",
             "Conecta con el bloque B: todo lo que estudiaste para el trabajador (arts. 86-100) se aplica también al funcionario."),
            (35, 103, "¿Qué debe garantizar la ley en materia de haberes jubilatorios de funcionarios?",
             "Su <b>actualización</b> en <b>igualdad de tratamiento</b> con el funcionario público <b>en actividad</b>.",
             "Si sube el sueldo del activo, sube la jubilación.",
             "La palabra clave es <b>actualización</b>: el jubilado no debe quedar atrás respecto del funcionario activo."),
            (2, 104, "¿En qué plazo deben los funcionarios presentar su declaración jurada de bienes y rentas?",
             "Dentro de los <b>quince días</b> de tomar posesión del cargo y, en igual término, <b>al cesar</b> en él.",
             "15 días al entrar y 15 días al salir.",
             "Sirve para comparar el patrimonio de <b>entrada</b> y de <b>salida</b> y detectar enriquecimiento ilícito. Por eso hay dos declaraciones."),
            (13, 105, "¿Cuál es la regla sobre la doble remuneración pública?",
             "Nadie puede percibir <b>simultáneamente más de un sueldo</b> como funcionario o empleado público, <b>salvo la docencia</b>.",
             "Un solo sueldo público. Excepción: la docencia.",
             "Regla + excepción. La única excepción es la <b>docencia</b>: un funcionario puede además cobrar como profesor."),
        ],
    },
    {
        "id": "D", "nombre": "Propiedad, derechos políticos y deberes", "arts": "Arts. 109 a 128",
        "intro": "Hilo conductor: cómo puede el Estado tomar una propiedad (109), cómo participa el ciudadano (118, 120, 122, 125) "
                 "y qué principio está por encima de los intereses particulares (128).",
        "fichas": [
            (18, 109, "¿En qué condiciones puede realizarse una expropiación?",
             "Por <b>causa de utilidad pública o interés social</b> <b>determinada por ley</b> y con <b>justa indemnización previa</b>. Excepción: latifundios improductivos destinados a la reforma agraria.",
             "Tres requisitos: causa (utilidad pública o interés social) + ley + indemnización justa y previa.",
             "«<b>Previa</b>» es la palabra trampa: primero se paga, después se expropia. La excepción de los latifundios improductivos es la que suele aparecer como «verdadero o falso»."),
            (8, 118, "¿Cómo define la Constitución el sufragio?",
             "Como <b>derecho, deber y función pública</b> del elector.",
             "Votar es a la vez derecho, deber y función pública.",
             "Tres naturalezas a la vez: «<b>D-D-F</b>» (Derecho, Deber, Función pública)."),
            (36, 120, "¿Quiénes son electores conforme al artículo 120?",
             "Los <b>ciudadanos paraguayos</b>, sin distinción, que hayan cumplido <b>dieciocho años</b>, según la Constitución y la ley.",
             "Paraguayo + ciudadano + 18 años.",
             "Edad: <b>18 años</b>. Une este dato con el art. 118: quien cumple 18 años adquiere a la vez el derecho y el deber de votar."),
            (37, 122, "Mencione materias que no pueden someterse a referéndum.",
             "Entre otras: relaciones internacionales y tratados, <b>expropiaciones</b>, <b>defensa nacional</b>, cuestiones <b>tributarias</b> y materias <b>presupuestarias</b>.",
             "Los temas técnicos o de soberanía no se votan por referéndum.",
             "Lista completa del art. 122, iniciales <b>T-E-D-L-I-E</b>: «<b>T</b>u <b>E</b>quipo <b>D</b>efiende <b>L</b>a <b>I</b>sla <b>E</b>ntera». <b>T</b>ratados y relaciones internacionales · <b>E</b>xpropiaciones · <b>D</b>efensa nacional · <b>L</b>imitación de la propiedad inmobiliaria · <b>I</b>mpuestos, moneda, bancos, empréstitos y Presupuesto · <b>E</b>lecciones nacionales, departamentales y municipales."),
            (38, 125, "¿Para qué pueden asociarse los ciudadanos en partidos y movimientos políticos?",
             "Para concurrir, por <b>métodos democráticos</b>, a la <b>elección de autoridades</b> y a la <b>orientación de la política nacional</b>.",
             "Partidos: elegir autoridades y orientar la política, siempre democráticamente.",
             "Dos fines (elegir y orientar) + un modo obligatorio (<b>democrático</b>)."),
            (27, 128, "¿Qué principio establece el artículo 128?",
             "<b>En ningún caso</b> el interés de los particulares <b>primará</b> sobre el interés general.",
             "Interés general por encima del particular.",
             "Relaciónalo con la expropiación (art. 109): es la aplicación práctica de este principio, pero con indemnización."),
        ],
    },
    {
        "id": "E", "nombre": "Garantías constitucionales", "arts": "Arts. 131 a 136",
        "intro": "Hilo conductor: los derechos no sirven si no se pueden reclamar. Las <b>garantías</b> son las herramientas para reclamarlos ante un juez. "
                 "Cada una protege algo distinto: la ley frente a la Constitución, la libertad física, los demás derechos y los datos personales.",
        "fichas": [
            (14, 131, "¿Cuál es la finalidad de las garantías constitucionales?",
             "<b>Hacer efectivos</b> los derechos consagrados en la Constitución. Las garantías serán <b>reglamentadas por la ley</b>.",
             "Garantía = herramienta para que el derecho se cumpla.",
             "Derecho = lo que tengo. Garantía = cómo lo hago valer. Palabra clave: <b>efectivos</b>."),
            (6, 132, "¿Qué órgano puede declarar la inconstitucionalidad de normas jurídicas y resoluciones judiciales?",
             "La <b>Corte Suprema de Justicia</b>, en la forma y con los alcances que establecen la Constitución y la ley.",
             "Solo la Corte Suprema declara la inconstitucionalidad.",
             "Dos objetos de control: <b>normas jurídicas</b> (leyes, decretos) y <b>resoluciones judiciales</b> (sentencias). Un único órgano: la Corte."),
            (3, 133, "¿Qué es el hábeas corpus preventivo?",
             "La garantía que permite a quien está en <b>trance inminente</b> de ser privado ilegalmente de su <b>libertad física</b> pedir el examen de la legitimidad de la amenaza y el cese de las restricciones.",
             "Preventivo = antes de la detención, ante una amenaza inminente.",
             "El art. 133 regula <b>tres</b> tipos. <b>Preventivo</b>: aún no me detuvieron, pero estoy por serlo. <b>Reparador</b>: ya estoy ilegalmente detenido y pido recuperar la libertad. <b>Genérico</b>: pido corregir circunstancias que restringen mi libertad o seguridad, o la violencia sobre personas detenidas."),
            (28, 134, "¿Qué permite hacer la garantía del hábeas data?",
             "Acceder a la información y los datos sobre una persona que obran en <b>registros oficiales o privados de carácter público</b>, y pedir su <b>actualización, rectificación o destrucción</b> en los casos previstos.",
             "Hábeas data = mis datos: verlos y corregirlos.",
             "Verbos de la respuesta: <b>acceder</b> y luego <b>actualizar, rectificar o destruir</b>. Data = datos; corpus = cuerpo."),
            (29, 135, "¿Qué protege la acción de amparo?",
             "Derechos o garantías constitucionales frente a actos u omisiones <b>manifiestamente ilegítimos</b> de <b>autoridades o particulares</b>, cuando se cumplen los requisitos constitucionales y legales.",
             "Amparo = protección general y urgente de los demás derechos.",
             "Requisitos: acto u omisión manifiestamente ilegítimo, lesión grave o peligro inminente y urgencia que impide usar la vía ordinaria. Puede dirigirse contra el Estado <b>y también contra particulares</b>."),
            (39, 136, "¿Qué permite la garantía de la inconstitucionalidad?",
             "Solicitar el <b>control de constitucionalidad</b> en los casos, la forma y los alcances previstos. La <b>Corte Suprema de Justicia</b> tiene la facultad de declararla.",
             "Es la misma idea que la pregunta 6: el control lo ejerce la Corte.",
             "Estudia las preguntas 6 y 39 como <b>una sola</b>. Lee también el recuadro sobre la numeración al final de este bloque."),
        ],
    },
    {
        "id": "F", "nombre": "Idiomas y tratados internacionales", "arts": "Arts. 140 a 142",
        "intro": "Hilo conductor: la identidad del Estado (idiomas) y cómo entra y sale el derecho internacional del sistema paraguayo.",
        "fichas": [
            (16, 140, "¿Cuáles son los idiomas oficiales del Paraguay?",
             "El <b>castellano</b> y el <b>guaraní</b>. Las lenguas indígenas y las de otras minorías forman parte del <b>patrimonio cultural</b> de la Nación.",
             "País bilingüe: castellano y guaraní.",
             "Distingue <b>oficial</b> (castellano y guaraní) de <b>patrimonio cultural</b> (lenguas indígenas y de minorías). Conecta con el patrimonio del art. 81."),
            (10, 141, "¿Qué requisitos deben cumplir los tratados para formar parte del ordenamiento interno?",
             "Ser <b>válidamente celebrados</b>, <b>aprobados por ley del Congreso</b> y tener sus <b>instrumentos de ratificación canjeados o depositados</b>. Su jerarquía es la del art. 137.",
             "Tres pasos: Celebrar, Aprobar por ley, Ratificar.",
             "Mnemotecnia <b>C-A-R</b> (Celebrado, Aprobado, Ratificado). Jerarquía del art. 137: Constitución, luego tratados, luego leyes del Congreso y luego las demás normas."),
            (40, 142, "¿Cómo pueden denunciarse los tratados relativos a los derechos humanos?",
             "<b>Solo</b> por los procedimientos que rigen para la <b>enmienda de la Constitución</b>.",
             "Salir de un tratado de derechos humanos es tan difícil como enmendar la Constitución.",
             "«Denunciar» un tratado significa <b>retirarse</b> de él, no acusar a nadie. El art. 141 explica cómo <b>entra</b> un tratado; el art. 142, cómo <b>sale</b> uno de derechos humanos."),
        ],
    },
]

# Ejercicios ------------------------------------------------------------------
HUECOS = [
    ("El presupuesto de educación no será inferior al ______ del total asignado a la ______, excluidos los préstamos y las ______.", "20 % · Administración Central · donaciones (art. 85)"),
    ("La declaración jurada de bienes se presenta dentro de los ______ días de asumir el cargo y en igual término al ______.", "quince · cesar en él (art. 104)"),
    ("El descanso por maternidad no será inferior a ______ semanas.", "doce (art. 89)"),
    ("La jornada ordinaria diurna no excede de ______ horas diarias y ______ semanales.", "ocho · cuarenta y ocho (art. 91)"),
    ("El sufragio es derecho, ______ y ______ del elector.", "deber · función pública (art. 118)"),
    ("Son electores los ciudadanos paraguayos que hayan cumplido ______ años.", "dieciocho (art. 120)"),
    ("En ningún caso el interés de los ______ primará sobre el interés ______.", "particulares · general (art. 128)"),
    ("La expropiación exige causa de utilidad pública o interés social determinada por ______ y justa indemnización ______.", "ley · previa (art. 109)"),
    ("Nadie puede percibir más de un sueldo público simultáneamente, salvo los provenientes de la ______.", "docencia (art. 105)"),
    ("Los derechos que la ley otorga al trabajador son ______.", "irrenunciables (art. 86)"),
    ("La educación escolar básica es ______ y gratuita en las escuelas ______.", "obligatoria · públicas (art. 76)"),
    ("Los idiomas oficiales son el ______ y el ______.", "castellano · guaraní (art. 140)"),
    ("Los tratados de derechos humanos solo pueden denunciarse por el procedimiento de ______ de la Constitución.", "enmienda (art. 142)"),
    ("Las universidades son ______ y serán creadas por ______.", "autónomas · ley (art. 79)"),
    ("Los derechos de huelga y de paro no alcanzan a los miembros de las ______ ni de las fuerzas ______.", "Fuerzas Armadas · policiales (art. 98)"),
]

RELACIONAR_A = ["Art. 80", "Art. 81", "Art. 84", "Art. 90", "Art. 96", "Art. 99", "Art. 101", "Art. 103", "Art. 125", "Art. 132", "Art. 134*", "Art. 141"]
RELACIONAR_B = [
    "a) Requisitos de los tratados", "b) Jubilación actualizada", "c) Fondos para becas", "d) Partidos políticos",
    "e) Libertad sindical", "f) Patrimonio cultural", "g) Corte Suprema e inconstitucionalidad", "h) Deporte",
    "i) Funcionarios al servicio del país", "j) Fiscalización de normas laborales", "k) Hábeas data", "l) Trabajo de menores",
]
RELACIONAR_SOL = "80-c · 81-f · 84-h · 90-l · 96-e · 99-j · 101-i · 103-b · 125-d · 132-g · 134*-k · 141-a"

VF = [
    ("La educación escolar básica es gratuita en todas las escuelas, públicas y privadas.", "Falso. Es gratuita en las escuelas <b>públicas</b> (art. 76)."),
    ("El 20 % para educación se calcula sobre el presupuesto de la Administración Central, incluyendo préstamos.", "Falso. Se <b>excluyen</b> préstamos y donaciones (art. 85)."),
    ("Los policías pueden ejercer el derecho de huelga.", "Falso. Fuerzas Armadas y policiales están excluidas (art. 98)."),
    ("Un funcionario público puede cobrar además un sueldo como docente.", "Verdadero. La docencia es la excepción (art. 105)."),
    ("La indemnización por expropiación puede pagarse después de tomar el bien.", "Falso. Debe ser justa y <b>previa</b> (art. 109)."),
    ("Las tasas, impuestos y el Presupuesto pueden someterse a referéndum.", "Falso. Son materias excluidas (art. 122)."),
    ("El amparo solo procede contra actos de autoridades públicas.", "Falso. También procede contra <b>particulares</b> (amparo)."),
    ("El hábeas corpus preventivo se usa cuando la persona ya está detenida ilegalmente.", "Falso. Ese es el <b>reparador</b>. El preventivo actúa ante una amenaza inminente (art. 133)."),
    ("Las lenguas indígenas son idiomas oficiales del Paraguay.", "Falso. Son <b>patrimonio cultural</b>; oficiales son castellano y guaraní (art. 140)."),
    ("Para crear un sindicato se necesita autorización previa del Ministerio.", "Falso. Es <b>sin autorización previa</b> (art. 96)."),
    ("La declaración jurada de bienes se presenta solo al asumir el cargo.", "Falso. También al <b>cesar</b>, en igual término (art. 104)."),
    ("La Iglesia Católica es la religión oficial del Estado según el art. 82.", "Falso. Se reconoce su <b>protagonismo histórico y cultural</b> (art. 82)."),
]

INVERSAS = [
    ("«…con preferencia de las personas que carezcan de recursos.»", "Art. 80, becas"),
    ("«…remuneración superior por horas extraordinarias, trabajo nocturno y días feriados.»", "Art. 92, retribución"),
    ("«…a concurrir, por métodos democráticos, a la elección de las autoridades…»", "Art. 125, partidos"),
    ("«…objetos, documentos y espacios de valor histórico, arqueológico, paleontológico…»", "Art. 81, patrimonio cultural"),
    ("«…en igualdad de tratamiento dispensado al funcionario público en actividad.»", "Art. 103, jubilaciones"),
    ("«…válidamente celebrados, aprobados por ley del Congreso…»", "Art. 141, tratados"),
    ("«…prioridad a los derechos del menor trabajador…»", "Art. 90, menores"),
    ("«…derecho, deber y función pública del elector.»", "Art. 118, sufragio"),
]

CASOS = [
    ("Ana trabaja en una fábrica. Al avisar que está embarazada de cinco meses, la despiden. ¿Qué norma la protege y qué le corresponde?",
     "Art. 89: no puede ser despedida durante el embarazo ni durante el descanso por maternidad, que no será inferior a doce semanas. Si el despido es injustificado, además tiene derecho a indemnización (art. 94)."),
    ("Carlos fue detenido sin orden y lleva dos días en una comisaría sin ver a un juez. ¿Qué garantía corresponde?",
     "Hábeas corpus <b>reparador</b> (art. 133): ya está privado de su libertad y busca recuperarla."),
    ("Una empresa de informes crediticios registra a Laura como deudora de un préstamo que ya pagó. ¿Qué puede hacer?",
     "Hábeas data: acceder a sus datos en ese registro privado de carácter público y pedir su actualización o rectificación."),
    ("El Poder Ejecutivo quiere convocar un referéndum para aumentar el IVA. ¿Es posible?",
     "No. Las cuestiones tributarias son materias excluidas del referéndum (art. 122)."),
    ("El Estado necesita un terreno privado para construir un hospital. ¿Qué debe cumplir?",
     "Art. 109: una ley debe declarar la utilidad pública o el interés social, y debe pagarse una justa indemnización previa."),
    ("Un funcionario del Ministerio cobra un sueldo allí y otro en una municipalidad. Otro funcionario cobra su sueldo y además da clases en un colegio público. ¿Quién incumple la Constitución?",
     "El primero. El segundo está dentro de la excepción de la docencia (art. 105)."),
    ("Un adolescente de 16 años trabaja de noche en turnos de 10 horas. ¿Qué artículos se ven involucrados?",
     "Art. 90: prioridad a los derechos del menor para su desarrollo físico, intelectual y moral. Art. 91: límite de la jornada y régimen más favorable para el trabajo nocturno."),
    ("El Congreso firma la salida de Paraguay de un tratado de derechos humanos por ley ordinaria. ¿Es válido?",
     "No. Los tratados de derechos humanos solo se denuncian por el procedimiento de enmienda de la Constitución (art. 142)."),
]

AUTOEVAL = {
    "A": [("¿Qué tres datos componen la respuesta completa del art. 85?", "20 %, de la Administración Central, sin préstamos ni donaciones."),
          ("Di las cinco clases de valor del patrimonio cultural.", "Histórico, arqueológico, paleontológico, artístico y científico (HAPAC)."),
          ("¿Qué diferencia hay entre lo que el art. 76 dice de la educación básica y del resto de niveles?", "La básica es obligatoria y gratuita en lo público; los demás niveles se fomentan.")],
    "B": [("Nombra los seis motivos de discriminación prohibidos.", "Étnicos, sexo, edad, religión, condición social y preferencias políticas o sindicales."),
          ("¿Quién hace huelga y quién hace paro?", "Huelga: trabajadores. Paro: empleadores."),
          ("¿Qué pagos menciona el art. 92?", "Salario vital mínimo, aguinaldo, bonificación familiar y pago superior por horas extra, nocturno y feriados.")],
    "C": [("¿Por qué la declaración jurada se presenta dos veces?", "Para comparar el patrimonio al entrar y al salir del cargo."),
          ("¿Cuál es la única excepción a la doble remuneración?", "La docencia.")],
    "D": [("¿Qué palabra de la expropiación suele usarse como trampa?", "«Previa»: la indemnización se paga antes."),
          ("Recita las seis materias excluidas del referéndum.", "Tratados, expropiaciones, defensa, limitación de la propiedad inmobiliaria, impuestos/moneda/bancos/presupuesto, elecciones.")],
    "E": [("Distingue los tres tipos de hábeas corpus en una frase cada uno.", "Preventivo: amenaza inminente. Reparador: ya detenido ilegalmente. Genérico: corregir condiciones que restringen la libertad o la seguridad."),
          ("¿Contra quién procede el amparo?", "Contra autoridades y particulares.")],
    "F": [("¿Qué tres pasos necesita un tratado para ser derecho interno?", "Celebración válida, aprobación por ley y ratificación canjeada o depositada (C-A-R)."),
          ("¿Qué significa «denunciar» un tratado?", "Retirarse de él.")],
}


on_page = make_on_page("Resumen de estudio · Cuestionario segunda parcial y final · Constitución Nacional del Paraguay")


def ficha(n, art, q, resp, clave, fijar):
    tag = Table([[Paragraph(f"Art. {art}", S["tag"])], [Paragraph(f"Pregunta {n}", S["tagsm"])]], colWidths=[22 * mm])
    tag.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    right = [
        P(q, "q"), Spacer(1, 3),
        P(f"<b>Respuesta:</b> {resp}", "cell"), Spacer(1, 3),
        P(f"<font color='#2F6B45'><b>Idea en una línea:</b></font> {clave}", "cell"), Spacer(1, 2),
        P(f"<font color='#B7791F'><b>Para fijarlo:</b></font> {fijar}", "cell"),
    ]
    t = Table([[tag, right]], colWidths=[25 * mm, 149 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("TOPPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 7), ("RIGHTPADDING", (1, 0), (1, 0), 7),
        ("TOPPADDING", (1, 0), (1, 0), 6), ("BOTTOMPADDING", (1, 0), (1, 0), 6),
    ]))
    return KeepTogether([t, Spacer(1, 5)])


def build():
    story = []

    # Portada ---------------------------------------------------------------
    story += [Spacer(1, 45 * mm), P("Constitución Nacional del Paraguay", "title"), Spacer(1, 4),
              P("Resumen para fijar conocimientos", "subtitle"),
              P("Cuestionario de la segunda parcial y final · 40 preguntas · Arts. 76 a 142", "subtitle"),
              Spacer(1, 18 * mm)]
    story.append(box([
        P("<b>Este material no es para leerlo una vez.</b> Está pensado para que <b>recuperes</b> la información de memoria, "
          "que es lo que realmente la fija. Leer y subrayar da sensación de dominio, pero en el examen lo que cuenta es poder "
          "<b>sacarla de la cabeza</b> sin mirar."),
    ], LIGHT, NAVY))
    story += [Spacer(1, 8 * mm), P("Qué contiene", "h2")]
    story += bullets([
        "<b>Mapa general</b>: dónde se ubica cada artículo y cómo se conectan los temas.",
        "<b>Seis bloques de fichas</b>: cada pregunta con su respuesta, la idea en una línea y un recurso para fijarla.",
        "<b>Herramientas de memoria</b>: tabla de números, pares que se confunden, comparativo de garantías y mnemotecnias.",
        "<b>Práctica</b>: completar huecos, relacionar, verdadero o falso, pregunta inversa y casos prácticos.",
        "<b>Tarjetas de autoevaluación</b> de las 40 preguntas, <b>control de repasos</b> y <b>solucionario</b>.",
    ])
    story.append(PageBreak())

    # Cómo estudiar ---------------------------------------------------------
    story.append(P("1. Cómo usar este resumen", "h1"))
    story.append(P("Tres principios con evidencia sólida sobre memoria a largo plazo guían el diseño del material:"))
    story.append(grid([
        ["Principio", "Qué significa", "Cómo aplicarlo aquí"],
        ["<b>Práctica de recuperación</b>", "Recordar sin mirar fortalece la memoria más que releer.", "Tapa la respuesta de cada ficha y contéstala en voz alta o por escrito antes de leerla."],
        ["<b>Repaso espaciado</b>", "Repasar en días separados fija mejor que todo de una vez.", "Sigue el plan de abajo y marca cada repaso en la tabla de control."],
        ["<b>Elaboración y conexión</b>", "Relacionar un dato con otros le da «ganchos» a la memoria.", "Lee el «hilo conductor» de cada bloque y las conexiones entre artículos."],
    ], [38 * mm, 62 * mm, 74 * mm]))
    story.append(Spacer(1, 8))
    story.append(P("Método para cada ficha", "h2"))
    story += bullets([
        "<b>1. Lee la pregunta</b> y tapa todo lo demás con una hoja.",
        "<b>2. Responde de memoria</b>, aunque sea incompleto. Equivocarse ahora ayuda a recordar después.",
        "<b>3. Destapa y compara.</b> Fíjate en las palabras en negrita: son las que el profesor espera leer.",
        "<b>4. Lee «Para fijarlo»</b> y conecta el dato con algo que ya sepas.",
        "<b>5. Marca</b> en la tabla de control si acertaste completo, parcial o no.",
    ])
    story.append(P("Plan de estudio sugerido", "h2"))
    story.append(grid([
        ["Sesión", "Qué hacer", "Tiempo aprox."],
        ["Día 1", "Mapa general + bloques A y B con el método de la ficha. Al terminar, autoevaluación de cada bloque.", "60-75 min"],
        ["Día 2", "Bloques C, D, E y F. Tabla de números y pares que se confunden.", "60 min"],
        ["Día 4", "Ejercicios de práctica sin mirar las fichas. Corrige con el solucionario y repasa solo los fallos.", "45 min"],
        ["Día 7", "Tarjetas de las 40 preguntas. Las que falles, vuelve a la ficha correspondiente.", "30-40 min"],
        ["Día antes del examen", "Tarjetas solo de las preguntas marcadas como «parcial» o «no». Casos prácticos.", "30 min"],
    ], [34 * mm, 110 * mm, 30 * mm]))
    story.append(PageBreak())

    # Mapa general ----------------------------------------------------------
    story.append(P("2. Mapa general del contenido", "h1"))
    story.append(P("Las 40 preguntas recorren la parte dogmática de la Constitución de 1992 (derechos, deberes y garantías) "
                   "y algunas declaraciones generales del Estado. Agruparlas por tema reduce 40 datos sueltos a <b>6 historias</b>."))
    story.append(grid([
        ["Bloque", "Tema", "Artículos", "Preguntas del cuestionario"],
        ["A", "Educación y cultura", "76, 79, 80, 81, 82, 83, 84, 85", "30, 31, 7, 12, 24, 20, 17, 1"],
        ["B", "Derechos laborales", "86, 87, 88, 89, 90, 91, 92, 94, 96, 98, 99, 100", "15, 32, 11, 5, 33, 9, 25, 21, 26, 22, 23, 4"],
        ["C", "Función pública", "101, 102, 103, 104, 105", "19, 34, 35, 2, 13"],
        ["D", "Propiedad, derechos políticos y deberes", "109, 118, 120, 122, 125, 128", "18, 8, 36, 37, 38, 27"],
        ["E", "Garantías constitucionales", "131, 132, 133, 134, 135, 136", "14, 6, 3, 28, 29, 39"],
        ["F", "Idiomas y tratados internacionales", "140, 141, 142", "16, 10, 40"],
    ], [16 * mm, 52 * mm, 56 * mm, 50 * mm]))
    story.append(Spacer(1, 8))
    story.append(P("La lógica que une los bloques", "h2"))
    story.append(box([
        P("<b>1. El Estado forma a la persona</b> (A: educación y cultura) → <b>2. La persona trabaja</b> (B: derechos laborales) → "
          "<b>3. Algunas trabajan para el Estado</b> (C: función pública) → <b>4. Como ciudadana, tiene bienes y participa en política</b> "
          "(D) → <b>5. Si le violan un derecho, lo reclama</b> (E: garantías) → <b>6. Todo dentro de un Estado con identidad propia y abierto al derecho internacional</b> (F)."),
    ], LIGHT, BLUE))
    story.append(Spacer(1, 6))
    story.append(P("Ejercicio previo de 2 minutos: <b>antes de seguir</b>, escribe en una hoja todo lo que ya recuerdes de cada bloque. "
                   "Al terminar el estudio repite el ejercicio y compara. Esa diferencia es lo que aprendiste."))
    story.append(PageBreak())

    # Bloques ---------------------------------------------------------------
    for b in BLOQUES:
        story.append(CondPageBreak(120 * mm))
        story.append(P(f"Bloque {b['id']} · {b['nombre']} <font size=10 color='#5A6270'>({b['arts']})</font>", "h1"))
        story.append(box([P(b["intro"])], LIGHT, BLUE))
        story.append(Spacer(1, 7))
        for f in b["fichas"]:
            story.append(ficha(*f))
        if b["id"] == "E":
            story.append(box([
                P("<b>Atención con la numeración de las garantías.</b> El cuestionario asigna el hábeas data al art. 134, el amparo al art. 135 "
                  "y la inconstitucionalidad al art. 136. En el texto oficial de la Constitución de 1992, el orden es: "
                  "<b>132 inconstitucionalidad · 133 hábeas corpus · 134 amparo · 135 hábeas data · 136 competencia</b> "
                  "(ningún juez competente puede negarse a entender en estas acciones). "
                  "Comprueba en tu ejemplar de la Constitución y, para el examen, usa la numeración que indique tu docente. "
                  "El <b>contenido</b> de las respuestas es correcto en ambos casos."),
            ], RED_BG, RED))
            story.append(Spacer(1, 5))
        auto = [P(f"Autoevaluación del bloque {b['id']} (respuestas en el solucionario)", "cellb")]
        for i, (q, _) in enumerate(AUTOEVAL[b["id"]], 1):
            auto.append(P(f"{i}. {q}", "cell"))
        story.append(KeepTogether([box(auto, GREEN_BG, GREEN)]))
        story.append(Spacer(1, 10))
    story.append(PageBreak())

    # Herramientas de memoria -----------------------------------------------
    story.append(P("3. Herramientas de memoria", "h1"))
    story.append(P("Números y plazos que tienes que saber de memoria", "h2"))
    story.append(grid([
        ["Dato", "Qué es", "Artículo"],
        ["<b>20 %</b>", "Mínimo del presupuesto de la Administración Central para educación (sin préstamos ni donaciones)", "85"],
        ["<b>15 días</b>", "Plazo de la declaración jurada de bienes al asumir y al cesar", "104"],
        ["<b>12 semanas</b>", "Descanso mínimo por maternidad", "89"],
        ["<b>8 h / 48 h</b>", "Jornada ordinaria diurna máxima diaria / semanal", "91"],
        ["<b>18 años</b>", "Edad para ser elector", "120"],
        ["<b>1 sueldo</b>", "Máximo de remuneraciones públicas simultáneas (excepción: docencia)", "105"],
        ["<b>2 idiomas</b>", "Oficiales: castellano y guaraní", "140"],
        ["<b>3 tipos</b>", "Hábeas corpus: preventivo, reparador y genérico", "133"],
        ["<b>3 requisitos</b>", "Tratados: celebrado, aprobado por ley y ratificado", "141"],
        ["<b>6 motivos</b>", "Discriminación laboral prohibida", "88"],
        ["<b>6 materias</b>", "Excluidas del referéndum", "122"],
    ], [28 * mm, 128 * mm, 18 * mm]))
    story.append(Spacer(1, 6))
    story.append(P("Comparativo de garantías", "h2"))
    story.append(grid([
        ["Garantía", "¿Qué protege?", "¿Cuándo la uso?", "Palabra gancho"],
        ["Inconstitucionalidad", "La supremacía de la Constitución", "Una ley o sentencia contradice la Constitución", "Corte Suprema"],
        ["Hábeas corpus", "La libertad física", "Me amenazan con detenerme, ya me detuvieron o me tratan mal detenido", "Corpus = cuerpo"],
        ["Amparo", "Los demás derechos y garantías", "Un acto u omisión manifiestamente ilegítimo me causa un daño grave y urgente", "Urgencia"],
        ["Hábeas data", "Los datos personales", "Quiero ver, corregir o destruir mis datos en un registro", "Data = datos"],
    ], [32 * mm, 40 * mm, 72 * mm, 30 * mm]))
    story.append(Spacer(1, 6))
    story.append(CondPageBreak(60 * mm))
    story.append(P("Pares que suelen confundirse", "h2"))
    story.append(grid([
        ["Se confunde…", "…con…", "La diferencia"],
        ["Huelga (art. 98)", "Paro (art. 98)", "Huelga la hacen los trabajadores; paro, los empleadores."],
        ["Hábeas corpus preventivo", "Hábeas corpus reparador", "Preventivo: antes de la detención. Reparador: después."],
        ["Amparo", "Hábeas corpus", "El hábeas corpus protege solo la libertad física; el amparo, los demás derechos."],
        ["Art. 141 (tratados)", "Art. 142 (denuncia)", "141: cómo entra un tratado. 142: cómo sale uno de derechos humanos."],
        ["Art. 131", "Art. 132", "131: para qué existen las garantías. 132: quién declara la inconstitucionalidad."],
        ["Art. 102", "Art. 103", "102: derechos laborales del funcionario. 103: su jubilación."],
        ["Art. 80 (becas)", "Art. 85 (presupuesto)", "80: a quién se ayuda. 85: cuánto dinero mínimo se asigna."],
        ["Idioma oficial", "Patrimonio cultural", "Oficiales: castellano y guaraní. Las lenguas indígenas son patrimonio."],
        ["Art. 87 (preferencia nacional)", "Art. 88 (no discriminación)", "Preferir al trabajador nacional es una política de empleo, no una discriminación prohibida."],
    ], [44 * mm, 44 * mm, 86 * mm]))
    story.append(Spacer(1, 6))
    story.append(CondPageBreak(60 * mm))
    story.append(P("Mnemotecnias reunidas", "h2"))
    story.append(grid([
        ["Recurso", "Qué recuerda", "Art."],
        ["<b>F-I-E</b>", "Fines de la universidad: Formación, Investigación, Extensión", "79"],
        ["<b>I-C-T-A</b>", "Becas: formación Intelectual, Científica, Técnica, Artística", "80"],
        ["<b>HAPAC</b>", "Patrimonio: Histórico, Arqueológico, Paleontológico, Artístico, Científico", "81"],
        ["«<b>E</b>sa <b>S</b>eñora <b>E</b>stá <b>R</b>ezando <b>C</b>on <b>P</b>aciencia»", "Discriminación: Étnicos, Sexo, Edad, Religión, Condición social, Preferencias políticas o sindicales", "88"],
        ["<b>8 × 6 = 48</b>", "Jornada: 8 horas diarias, 48 semanales", "91"],
        ["<b>SAB + ENF</b>", "Salario mínimo, Aguinaldo, Bonificación + pago mayor por horas Extra, Nocturno, Feriados", "92"],
        ["<b>D-D-F</b>", "Sufragio: Derecho, Deber, Función pública", "118"],
        ["«<b>T</b>u <b>E</b>quipo <b>D</b>efiende <b>L</b>a <b>I</b>sla <b>E</b>ntera»", "Referéndum: Tratados, Expropiaciones, Defensa, Limitación inmobiliaria, Impuestos y presupuesto, Elecciones", "122"],
        ["<b>Corpus / Data</b>", "Corpus = cuerpo (libertad física). Data = datos.", "133-135"],
        ["<b>C-A-R</b>", "Tratados: Celebrado, Aprobado por ley, Ratificado", "141"],
    ], [52 * mm, 108 * mm, 14 * mm]))
    story.append(PageBreak())

    # Práctica --------------------------------------------------------------
    story.append(P("4. Práctica activa", "h1"))
    story.append(box([P("Haz los ejercicios <b>sin mirar las fichas</b>. Corrige después con el solucionario y vuelve a la ficha de cada error.")], AMBER_BG, AMBER))
    story.append(P("Ejercicio 1 · Completa los espacios", "h2"))
    for i, (t, _) in enumerate(HUECOS, 1):
        story.append(P(f"{i}. {t}"))
    story.append(CondPageBreak(90 * mm))
    rows = [["Artículo", "Tu respuesta", "Tema"]]
    for a, t in zip(RELACIONAR_A, RELACIONAR_B):
        rows.append([a, "", t])
    story.append(KeepTogether([
        P("Ejercicio 2 · Relaciona cada artículo con su tema", "h2"),
        P("<font size=8>* Según la numeración del cuestionario.</font>"),
        grid(rows, [30 * mm, 30 * mm, 114 * mm]),
    ]))
    story.append(CondPageBreak(100 * mm))
    story.append(P("Ejercicio 3 · Verdadero o falso. Si es falso, corrígelo", "h2"))
    rows = [["Afirmación", "V / F"]]
    for i, (t, _) in enumerate(VF, 1):
        rows.append([f"{i}. {t}", ""])
    story.append(grid(rows, [154 * mm, 20 * mm]))
    story.append(CondPageBreak(80 * mm))
    story.append(P("Ejercicio 4 · Pregunta inversa: ¿de qué artículo es este fragmento?", "h2"))
    rows = [["Fragmento", "Artículo"]]
    for i, (t, _) in enumerate(INVERSAS, 1):
        rows.append([f"{i}. {t}", ""])
    story.append(grid(rows, [144 * mm, 30 * mm]))
    story.append(CondPageBreak(80 * mm))
    story.append(P("Ejercicio 5 · Casos prácticos", "h2"))
    story.append(P("Indica qué artículo se aplica y por qué. Aplicar la norma a un caso es la forma más profunda de saberla."))
    for i, (c, _) in enumerate(CASOS, 1):
        story.append(KeepTogether([P(f"<b>Caso {i}.</b> {c}"), Spacer(1, 14)]))
    story.append(PageBreak())

    # Tarjetas --------------------------------------------------------------
    story.append(P("5. Tarjetas de las 40 preguntas", "h1"))
    story.append(P("Dobla la hoja por la línea central o tapa la columna derecha. Responde cada pregunta y marca el resultado en la tabla de control. "
                   "Están en el <b>orden original</b> del cuestionario, a propósito: así practicas sin la ayuda del orden temático."))
    fichas = sorted((f for b in BLOQUES for f in b["fichas"]), key=lambda f: f[0])
    rows = [["Pregunta", "Respuesta (tápala)"]]
    for n, art, q, resp, clave, _ in fichas:
        rows.append([f"<b>{n}.</b> (Art. {art}) {q}", clave])
    t = grid(rows, [87 * mm, 87 * mm])
    t.setStyle(TableStyle([("LINEAFTER", (0, 0), (0, -1), 1.5, NAVY)]))
    story.append(t)
    story.append(PageBreak())

    # Control ---------------------------------------------------------------
    story.append(P("6. Control de repasos", "h1"))
    story.append(P("Marca en cada repaso: <b>✓</b> respondida completa · <b>~</b> parcial · <b>✗</b> no la supe. "
                   "En el repaso siguiente dedica más tiempo a las que tengan ~ o ✗."))
    rows = [["Preg.", "Art.", "Tema", "Repaso 1", "Repaso 2", "Repaso 3"]]
    temas = {
        1: "Presupuesto educación", 2: "Declaración jurada", 3: "Hábeas corpus preventivo", 4: "Vivienda", 5: "Maternidad",
        6: "Inconstitucionalidad", 7: "Becas", 8: "Sufragio", 9: "Jornada", 10: "Requisitos tratados", 11: "No discriminación",
        12: "Patrimonio cultural", 13: "Doble remuneración", 14: "Finalidad garantías", 15: "Condiciones del trabajo",
        16: "Idiomas oficiales", 17: "Deporte", 18: "Expropiación", 19: "Funcionarios", 20: "Exoneración cultural",
        21: "Despido injustificado", 22: "Huelga y paro", 23: "Fiscalización laboral", 24: "Iglesia Católica", 25: "Retribución",
        26: "Libertad sindical", 27: "Interés general", 28: "Hábeas data", 29: "Amparo", 30: "Educación básica",
        31: "Universidades", 32: "Pleno empleo", 33: "Menores", 34: "Derechos funcionarios", 35: "Jubilaciones",
        36: "Electores", 37: "Referéndum", 38: "Partidos", 39: "Inconstitucionalidad (2)", 40: "Denuncia tratados DD.HH.",
    }
    for n, art, *_ in fichas:
        rows.append([str(n), str(art), temas[n], "", "", ""])
    story.append(grid(rows, [14 * mm, 14 * mm, 76 * mm, 23 * mm, 23 * mm, 24 * mm]))
    story.append(PageBreak())

    # Solucionario ----------------------------------------------------------
    story.append(P("7. Solucionario", "h1"))
    story.append(P("Autoevaluaciones de los bloques", "h2"))
    for b in BLOQUES:
        story.append(P(f"<b>Bloque {b['id']}</b>", "small"))
        for i, (_, a) in enumerate(AUTOEVAL[b["id"]], 1):
            story.append(P(f"{i}. {a}", "small"))
        story.append(Spacer(1, 3))
    story.append(P("Ejercicio 1 · Completa los espacios", "h2"))
    for i, (_, a) in enumerate(HUECOS, 1):
        story.append(P(f"{i}. {a}", "small"))
    story.append(P("Ejercicio 2 · Relaciona", "h2"))
    story.append(P(RELACIONAR_SOL, "small"))
    story.append(P("Ejercicio 3 · Verdadero o falso", "h2"))
    for i, (_, a) in enumerate(VF, 1):
        story.append(P(f"{i}. {a}", "small"))
    story.append(P("Ejercicio 4 · Pregunta inversa", "h2"))
    for i, (_, a) in enumerate(INVERSAS, 1):
        story.append(P(f"{i}. {a}", "small"))
    story.append(P("Ejercicio 5 · Casos prácticos", "h2"))
    for i, (_, a) in enumerate(CASOS, 1):
        story.append(P(f"<b>Caso {i}.</b> {a}", "small"))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 8))
    story.append(box([P("<b>Último consejo:</b> el día del examen, antes de empezar, escribe en un margen la tabla de números y las mnemotecnias. "
                        "Descargar la memoria al papel libera atención para pensar las respuestas.")], LIGHT, NAVY))

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                            title="Resumen para fijar conocimientos - Constitución Nacional", author="Resumen de estudio")
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=on_page)
    print(f"PDF generado: {OUT}")


if __name__ == "__main__":
    build()
