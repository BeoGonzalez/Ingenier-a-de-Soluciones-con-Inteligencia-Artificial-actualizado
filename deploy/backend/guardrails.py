"""Guardrails de entrada/salida del backend.

Reutiliza los patrones didácticos de RA3/IL3.3 (PII y filtro ético) y añade
normalización anti-evasión, detección de prompt injection y validación de
longitud. Sin dependencias de FastAPI para poder testearse de forma aislada.

===========================================================================
LEE ESTO ANTES DE COPIARLO A PRODUCCIÓN: qué defiende y qué NO
===========================================================================

Esto es un **filtro por patrones**. Es la primera barrera: barata, rápida y
auditable (cualquiera puede leer las listas y saber qué bloquea). Sirve para:

- Frenar el intento "de manual": el copiar-pegar de un tutorial de jailbreak.
- Frenar las evasiones triviales que rompían la versión anterior de este
  archivo: MAYÚSCULAS,  espacios  repetidos, caracteres invisibles
  (zero-width) y homoglifos cirílicos ("ignоra" con о de Cirílico). De eso se
  encarga `normalizar()`.
- Redactar PII evidente (correo, RUT, tarjeta, teléfono chileno) antes de que
  acabe en un log o en el prompt que se envía al modelo.

**Lo que NO detecta** — asumido a propósito, no es un bug pendiente:

- Paráfrasis y sinónimos: "haz caso omiso de lo que te dijeron antes".
- Idiomas fuera de español/inglés: "oublie les instructions précédentes".
- Hex, texto invertido y un idioma que no esté en las listas.
- Una paráfrasis que no usa las frases ya escritas ("caso omiso" sí está).
- Prompt injection **indirecta**: instrucciones escondidas en un documento,
  un correo o una web que el agente lea más tarde. El filtro solo ve lo que
  escribe el usuario.

Antes de comparar, el filtro decodifica tres disfraces baratos: un bloque
base64, rot13 y letras separadas por puntos (`i.g.n.o.r.a`). Eso cierra
evasiones mecánicas. No entiende el texto.

Un filtro léxico no puede cerrar eso: la lista de formas de decir "ignora tus
instrucciones" es infinita, y la de textos benignos que contienen esas mismas
palabras también. Subir la agresividad del filtro no lo arregla, solo cambia
falsos negativos por falsos positivos (ver `EXCEPCIONES_BENIGNAS` más abajo:
"arma" sin límites de palabra bloqueaba *farmacia*, *alarma* y *karma*).
`tests/deploy/test_guardrails_evasion.py` fija las evasiones mecánicas que
sí se bloquean (base64, rot13, letras separadas, una frase en francés, la
paráfrasis "caso omiso"). Lo que sigue abierto no lleva `xfail`: es la
inyección indirecta y cualquier reformulación que no esté escrita.

**Defensa en profundidad** — lo que hace falta de verdad en producción:

1. Normalización + filtro por patrones (esto): descarta el ruido barato.
2. Un clasificador o un LLM-as-judge sobre la entrada Y sobre la salida:
   entiende paráfrasis, que es justo lo que aquí falta.
3. Mínimo privilegio del agente: sin herramientas, credenciales ni accesos
   que no necesite. Si el jailbreak igual pasa, que no pueda hacer daño.
4. Observabilidad (RA3.1 / RA3.2): trazas y métricas para detectar el abuso
   que el filtro dejó pasar. Se asume que algo pasará.
"""
import base64
import codecs
import re
import unicodedata
from dataclasses import dataclass
from typing import Sequence

# ---------------------------------------------------------------------------
# 1) Normalización: sube el listón antes de comparar
# ---------------------------------------------------------------------------
# Un `"frase" in texto.lower()` se evade con cualquier cosa que cambie los
# bytes sin cambiar lo que el humano (y el modelo) leen. Normalizamos primero
# y comparamos después.

# Caracteres invisibles usados para partir una palabra por dentro:
# zero-width space/non-joiner/joiner, word joiner, BOM y guion suave.
# Un ZWSP entre "in" y "strucciones" se ve igual que "instrucciones"
# en pantalla, pero el substring-match ya no encontraba la palabra.
# Se escriben con escapes \uXXXX a propósito: pegados como caracteres reales
# serían invisibles también en este archivo.
_INVISIBLES = dict.fromkeys(
    map(
        ord,
        "\u00ad"                          # soft hyphen (guion suave)
        "\u200b\u200c\u200d"              # zero-width space / non-joiner / joiner
        "\u2060\u2061\u2062\u2063\u2064"  # word joiner e invisibles matematicos
        "\u202a\u202b\u202c\u202d\u202e"  # controles de direccion (bidi override)
        "\u2066\u2067\u2068\u2069"        # aislantes bidi
        "\ufeff",                         # BOM / zero-width no-break space
    ),
    None,
)

# Homoglifos: letras cirílicas y griegas que se DIBUJAN como latinas.
# "ignоra" con о cirílica (U+043E) es indistinguible a ojo de "ignora".
_HOMOGLIFOS = str.maketrans(
    {
        # cirílico
        "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y",
        "і": "i", "ј": "j", "ѕ": "s", "ԁ": "d", "һ": "h", "ԛ": "q", "ѵ": "v",
        "ԝ": "w", "ᴏ": "o", "ⅼ": "l", "ᴠ": "v", "ɡ": "g",
        # griego
        "α": "a", "ο": "o", "ρ": "p", "ε": "e", "ι": "i", "ν": "v", "κ": "k",
        "τ": "t", "υ": "u", "χ": "x", "μ": "u", "β": "b", "γ": "y", "σ": "o",
        "ѡ": "w",
    }
)


def normalizar(texto: str) -> str:
    """Deja el texto en una forma canónica para comparar patrones.

    NO se usa para reenviar el texto al modelo (para eso está el original
    saneado): solo para DECIDIR si se bloquea.

    Ojo con lo que esto es: sube el listón, no cierra el problema. Sigue
    pasando hex, texto invertido, un idioma que no esté en las listas o un
    sinónimo que no hayamos escrito. Ver el docstring del módulo.
    """
    # 1) NFKC unifica variantes de compatibilidad: ﬁ→fi, ８→8, ｉ→i, ⅰ→i…
    t = unicodedata.normalize("NFKC", texto)
    # 2) fuera los caracteres invisibles (después de NFKC, que no los toca)
    t = t.translate(_INVISIBLES)
    # 3) minúsculas: "Ignora TUS instrucciones" == "ignora tus instrucciones"
    t = t.lower()
    # 4) homoglifos → su equivalente latino (ya en minúscula)
    t = t.translate(_HOMOGLIFOS)
    # 5) quitar tildes y diacríticos: "actúa"=="actua", "engaño"=="engano".
    #    Así una sola entrada en la lista cubre las dos escrituras.
    t = "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )
    # 6) colapsar espacios/tabs/saltos repetidos: "ignora  las instrucciones"
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _regex_frase(frase: str) -> re.Pattern:
    r"""Compila una frase de las listas a regex con límites de palabra (\b).

    LECCIÓN: sin `\b` el substring-match produce falsos positivos que rompen la
    app. "arma" bloqueaba *farmacia*, *alarma*, *armario*, *desarmar* y *karma*;
    "bomba" bloqueaba "bomba de agua". Entre palabras aceptamos `\s+` porque el
    texto ya viene normalizado, pero así el patrón aguanta cualquier separación.
    """
    partes = [re.escape(p) for p in normalizar(frase).split(" ") if p]
    return re.compile(r"\b" + r"\s+".join(partes) + r"\b")


# ---------------------------------------------------------------------------
# 2) PII — el ORDEN de aplicación importa
# ---------------------------------------------------------------------------
# Es una tupla, no un dict, para que el orden sea explícito y difícil de
# romper sin darse cuenta.
#
# LECCIÓN (bug real que había aquí): `telefono_chile` matcheaba cualquier
# secuencia de 9 dígitos y se aplicaba ANTES que `numero_tarjeta`. Resultado:
#   "Mi Visa es 4539578763621486" -> "Mi Visa es [TELEFONO_CHILE_REDACTADO]3621486"
# El patrón genérico se comía la cabeza del número y dejaba en claro los
# últimos dígitos, que son justo los que confirman una tarjeta. Regla general:
# aplicar SIEMPRE los patrones de más específico a más genérico.

# Segunda decisión: exigir FORMATO reconocible, no solo "n dígitos seguidos".
# Un número pelado de 9 cifras es ambiguo — ¿un RUT? ¿un id de pedido? ¿el
# resultado de un cálculo? Antes se redactaba siempre, así que "x = 123456789"
# llegaba al modelo destruido y la app quedaba inservible para cualquier
# pregunta con números. Coste asumido: un RUT o un móvil escritos sin puntos,
# guion ni prefijo NO se redactan. En un despliegue real esta decisión se toma
# según el dominio (una fintech elegiría lo contrario).

# Móvil y fijo chilenos: prefijo de país (+56) O al menos un separador entre
# grupos. El patrón anterior tampoco cubría el formato con guion, así que
# "+56 9 1234-5678" pasaba sin redactar.
_TEL_MOVIL_CON_PREFIJO = r"\+?56[\s.\-]?9[\s.\-]?\d{4}[\s.\-]?\d{4}"
_TEL_FIJO_CON_PREFIJO = r"\+?56[\s.\-]?[2-8][\s.\-]?\d{3,4}[\s.\-]?\d{4}"
_TEL_MOVIL_CON_SEPARADOR = r"\b9[\s.\-]\d{4}[\s.\-]?\d{4}\b|\b9\d{4}[\s.\-]\d{4}\b"

# RUT: exigimos el dígito verificador separado por guion, o los puntos de
# miles, o la K final. "12.345.678-9", "12345678-9" y "12345678K" sí; el
# número suelto "123456789", no.
_RUT_CON_PUNTOS = r"\b\d{1,2}\.\d{3}\.\d{3}-?[\dkK]\b"
_RUT_CON_GUION = r"\b\d{7,8}-[\dkK]\b"
_RUT_CON_K = r"\b\d{7,8}[kK]\b"

PATRONES_PII: tuple[tuple[str, re.Pattern], ...] = (
    # 1º el correo: es el más específico y no colisiona con los numéricos.
    ("correo_electronico", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
    # 2º la tarjeta: 16 dígitos. ANTES que teléfono y RUT, o se la comen.
    ("numero_tarjeta", re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")),
    # 3º el RUT: formato propio (puntos y/o dígito verificador).
    ("rut_chile", re.compile(f"(?:{_RUT_CON_PUNTOS}|{_RUT_CON_GUION}|{_RUT_CON_K})")),
    # 4º el teléfono: el más genérico, va al final.
    (
        "telefono_chile",
        re.compile(
            f"(?:{_TEL_MOVIL_CON_PREFIJO}|{_TEL_FIJO_CON_PREFIJO}|{_TEL_MOVIL_CON_SEPARADOR})"
        ),
    ),
)


# ---------------------------------------------------------------------------
# 3) Prompt injection
# ---------------------------------------------------------------------------
# Dos capas: familias verbo+objeto (cubren declinaciones y determinantes) y
# una lista de frases literales para lo que no encaja en una familia.

# Determinantes/adjetivos que pueden colarse entre el verbo y el objeto:
# "ignora LAS instrucciones", "ignora TUS instrucciones", "forget ALL your rules".
_RELLENO = (
    r"(?:\s+(?:de|del|el|la|los|las|les|des|mes|tes|ces|un|una|tu|tus|su|sus|mi|mis|todo|toda|todos"
    r"|todas|anterior|anteriores|previo|previa|previos|previas|the|a|an|your|my"
    r"|all|any|previous|prior|above|earlier|first|initial|of))*"
)
_VERBOS_IGNORAR = (
    r"(?:ignora[rs]?|ignore[sd]?|ignorez|olvida[rt]?e?|olvidate|omite|omitir|descarta"
    r"|descartar|saltate|oublie[rz]?|oublier|disregard|forget|bypass|override)"
)
_VERBOS_REVELAR = (
    r"(?:revela(?:me)?|muestra(?:me)?|dime|imprime|repite|escribe|comparte"
    r"|filtra|reveal|show|print|repeat|tell\s+me|output|display|dump)"
)
_OBJETO_INSTRUCCIONES = (
    r"(?:instrucciones|instruccion|indicaciones|directrices|reglas|restricciones"
    r"|instructions|rules|guidelines|constraints|system\s+prompt"
    r"|prompt\s+del?\s+sistema|prompt\s+inicial|initial\s+prompt)"
)
# Para "revelar" exigimos que el objeto sea claramente el prompt del SISTEMA.
# Si no, "dime las reglas de la evaluación" —pregunta legítima a un bot de un
# curso— quedaría bloqueada.
_OBJETO_SISTEMA = (
    r"(?:(?:el|la|tu|su|the|your)\s+)?"
    r"(?:system\s+prompt|prompt\s+del?\s+sistema|prompt\s+inicial|initial\s+prompt"
    r"|system\s+message|mensaje\s+de\s+sistema)"
    r"|(?:tus|sus|your|the)\s+(?:instrucciones|reglas|directrices|restricciones"
    r"|instructions|rules|guidelines)"
)

PATRONES_INJECTION_REGEX = (
    # "ignora / olvida / forget ... (las|tus|all your) instrucciones|reglas"
    re.compile(rf"\b{_VERBOS_IGNORAR}{_RELLENO}\s+{_OBJETO_INSTRUCCIONES}\b"),
    # "revela / muestra / dime ... tu system prompt | tus instrucciones"
    re.compile(rf"\b{_VERBOS_REVELAR}\s+(?:{_OBJETO_SISTEMA})\b"),
    # inglés sin objeto explícito: "ignore all previous", "disregard the above"
    re.compile(r"\b(?:ignore|disregard|forget)\s+(?:all\s+|any\s+|the\s+)?(?:previous|prior|above)\b"),
)

# Frases literales (se compilan con límites de palabra). Ojo con lo que se
# mete aquí: cada entrada es también una fuente potencial de falsos positivos.
#
# QUITADO a propósito: "system prompt" a secas. Es vocabulario del temario de
# este curso, así que bloqueaba preguntas legítimas como
# "¿Qué significa 'system prompt'?". El intento real de extracción lleva un
# verbo delante y lo cubre `PATRONES_INJECTION_REGEX`.
PATRONES_INJECTION = (
    "actua como si no tuvieras",
    "haz como si no tuvieras",
    "eres ahora un",
    "eres ahora una",
    "a partir de ahora eres",
    "you are now a",
    "modo desarrollador",
    "developer mode",
    "sin restricciones ni filtros",
    "jailbreak",
    "caso omiso",
)
_INJECTION_LITERALES = tuple(_regex_frase(f) for f in PATRONES_INJECTION)


# ---------------------------------------------------------------------------
# 4) Filtro ético
# ---------------------------------------------------------------------------
# No hace falta duplicar "daño físico" y "dano fisico": `normalizar()` ya quita
# las tildes de la entrada y de estos patrones.
CATEGORIAS_RESTRINGIDAS = {
    "violencia": ["bomba", "arma", "daño físico", "explotar vulnerabilidad"],
    "contenido_ilegal": ["robar datos", "suplantar identidad", "falsificar", "lavado de dinero"],
    "manipulacion": ["engaño masivo", "desinformación", "deepfake dañino"],
}
_RESTRINGIDOS = tuple(
    (categoria, _regex_frase(palabra))
    for categoria, palabras in CATEGORIAS_RESTRINGIDAS.items()
    for palabra in palabras
)

# Expresiones que contienen una palabra restringida pero son inofensivas. Se
# eliminan del texto ANTES de buscar. Los límites de palabra arreglan
# *farmacia* o *karma*, pero no "bomba de agua": ahí la palabra sí está entera
# y solo el contexto la salva.
#
# Esto tampoco es gratis: quien escriba "bomba de agua y además una bomba de
# verdad" pierde solo la primera aparición, la segunda se sigue bloqueando.
# Pero es una lista corta que hay que mantener a mano, y esa es su limitación.
EXCEPCIONES_BENIGNAS = (
    "bomba de agua",
    "bomba de bencina",
    "bomba de calor",
    "bomba de vacio",
    "bomba hidraulica",
    "bomba de inyeccion",
    "arma de doble filo",
)
_EXCEPCIONES = tuple(_regex_frase(f) for f in EXCEPCIONES_BENIGNAS)


@dataclass
class ResultadoValidacion:
    es_valida: bool
    motivo: str = ""
    texto_sanitizado: str = ""


def sanitizar_pii(texto: str) -> str:
    """Reemplaza PII detectada por marcadores, de patrón más específico a más genérico.

    Trabaja sobre el texto ORIGINAL (no normalizado): lo que devuelve se le
    pasa al modelo, así que no podemos alterarlo más de lo necesario.
    """
    limpio = texto
    for tipo, patron in PATRONES_PII:
        limpio = patron.sub(f"[{tipo.upper()}_REDACTADO]", limpio)
    return limpio


def _parece_injection(normalizado: str) -> bool:
    """Compara un texto ya normalizado contra las listas. No decodifica."""
    if any(p.search(normalizado) for p in PATRONES_INJECTION_REGEX):
        return True
    return any(p.search(normalizado) for p in _INJECTION_LITERALES)


def _juntar_letras(texto: str) -> str:
    """i.g.n.o.r.a → ignora. Solo letras sueltas separadas por puntos."""

    def unir(coincidencia: re.Match) -> str:
        return coincidencia.group(0).replace(".", "")

    return re.sub(r"\b(?:[a-z]\.){2,}[a-z]\b", unir, texto)


def _textos_base64(texto: str):
    """Decodifica bloques que parecen base64. Ignora lo que no es UTF-8."""
    for coincidencia in re.finditer(r"[A-Za-z0-9+/]{16,}={0,2}", texto):
        blob = coincidencia.group(0)
        relleno = "=" * ((-len(blob)) % 4)
        try:
            crudo = base64.b64decode(blob + relleno, validate=False)
            decodificado = crudo.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            continue
        if decodificado.strip():
            yield decodificado


def hay_injection(texto: str) -> bool:
    """¿El texto parece un intento de prompt injection?

    Mira el texto normalizado y tres disfraces baratos: letras separadas por
    puntos, rot13 y un bloque base64. No recorre hex ni texto invertido, y no
    entiende una paráfrasis que no esté en las listas.
    """
    normalizado = normalizar(texto)
    if _parece_injection(normalizado):
        return True
    junto = _juntar_letras(normalizado)
    if junto != normalizado and _parece_injection(junto):
        return True
    if _parece_injection(normalizar(codecs.encode(normalizado, "rot13"))):
        return True
    return any(_parece_injection(normalizar(decodificado)) for decodificado in _textos_base64(texto))


def es_no_etico(texto: str) -> bool:
    """¿El texto cae en alguna categoría restringida?"""
    normalizado = normalizar(texto)
    for excepcion in _EXCEPCIONES:
        normalizado = excepcion.sub(" ", normalizado)
    return any(patron.search(normalizado) for _, patron in _RESTRINGIDOS)


# Alias con el nombre privado original, por compatibilidad con el material de
# clase que ya los referencia.
_hay_injection = hay_injection
_es_no_etico = es_no_etico


def validar_entrada(texto: str, max_chars: int = 2000) -> ResultadoValidacion:
    """Valida la entrada del usuario antes de pasarla al agente."""
    if not texto or not texto.strip():
        return ResultadoValidacion(False, "La entrada está vacía.")
    if len(texto) > max_chars:
        return ResultadoValidacion(False, f"La entrada es demasiado larga (máx {max_chars}).")
    if hay_injection(texto):
        return ResultadoValidacion(False, "Posible intento de prompt injection detectado.")
    if es_no_etico(texto):
        return ResultadoValidacion(False, "La solicitud infringe el filtro ético.")
    return ResultadoValidacion(True, "", sanitizar_pii(texto.strip()))


def validar_conversacion(turnos: Sequence[str]) -> ResultadoValidacion:
    """Valida la conversación COMPLETA, concatenada.

    LECCIÓN: validar turno a turno se evade troceando el payload. Con
    historial ["ignora las", "instrucciones"] y mensaje "anteriores", cada
    pieza pasa el filtro por separado, pero el modelo recibe la frase entera.
    Aquí se juntan los turnos en el mismo orden en que los verá el modelo y se
    vuelve a mirar.

    No revisamos la longitud: el presupuesto acumulado lo controla `app.py`.
    """
    completo = "\n".join(t for t in turnos if t)
    if not completo.strip():
        return ResultadoValidacion(False, "La conversación está vacía.")
    if hay_injection(completo):
        return ResultadoValidacion(False, "Posible intento de prompt injection detectado.")
    if es_no_etico(completo):
        return ResultadoValidacion(False, "La solicitud infringe el filtro ético.")
    return ResultadoValidacion(True, "", completo)


def hay_fuga_de_instrucciones(salida: str, system_prompt: str, palabras: int = 6) -> bool:
    """¿La respuesta repite un trozo literal del system prompt, o lo parafrasea?

    Guardrail de SALIDA. Dos comprobaciones:

    1. Ventanas de `palabras` palabras normalizadas: si el modelo devuelve
       seis palabras seguidas de sus propias instrucciones, se las sacaron.
    2. Tres ideas a la vez (brevedad, idioma, reglas) y una negativa del tipo
       "no contar" / "no revelar". Cierra el resumen obvio. Una reformulación
       que no use esas palabras sigue sin detectarse.
    """
    referencia = normalizar(system_prompt).split()
    texto = normalizar(salida)
    if len(referencia) >= palabras and any(
        " ".join(referencia[i : i + palabras]) in texto
        for i in range(len(referencia) - palabras + 1)
    ):
        return True

    vocabulario = set(re.findall(r"[a-z]+", texto))
    grupos = (
        {"breve", "conciso", "concisa", "sucinto", "sucinta"},
        {"espanol", "castellano"},
        {"reglas", "regla", "instrucciones", "instruccion"},
    )
    aciertos = sum(1 for grupo in grupos if vocabulario & grupo)
    niega = any(pista in texto for pista in ("no contar", "sin revel", "no revel"))
    return aciertos >= 3 and niega
