"""Carga los scripts didácticos de RA3, cuyos nombres no son módulos importables."""
import importlib.util
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def cargar_modulo(relativo: str):
    ruta = RAIZ / relativo
    nombre = "ra3_" + ruta.stem.replace("-", "_")
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    # dataclass (y otros) buscan la clase en sys.modules durante la definición.
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo
