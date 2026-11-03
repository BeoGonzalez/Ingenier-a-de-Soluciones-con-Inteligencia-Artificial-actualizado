"""Los 20 ítems OWASP 2026 quedan mapeados y los controles que existen corren."""

from cargar import cargar_modulo

ejemplos = cargar_modulo("RA3/IL3.5/3-ejemplos-owasp.py")


def test_estan_las_dos_listas_completas():
    filas = ejemplos.evaluar()
    codigos = [f.codigo for f in filas]
    assert codigos == [f"LLM{i:02d}:2026" for i in range(1, 11)] + [
        f"ASI{i:02d}:2026" for i in range(1, 11)
    ]
    assert {f.estado for f in filas} <= {"aplicado", "parcial", "en la defensa"}


def test_los_aplicados_dejan_evidencia_del_control():
    por_codigo = {f.codigo: f for f in ejemplos.evaluar()}

    pii = por_codigo["LLM02:2026"]
    assert pii.estado == "aplicado"
    assert "ana@duoc.cl" not in pii.evidencia.split("texto=")[-1]
    assert "REDACTADO" in pii.evidencia

    consumo = por_codigo["LLM06:2026"]
    assert "rechazada=True" in consumo.evidencia
    assert "segunda=False" in consumo.evidencia

    salida = por_codigo["LLM10:2026"]
    assert "html crudo escapado=True" in salida.evidencia
    assert "aritmética=20" in salida.evidencia
    assert salida.evidencia.endswith("Error: operacion no permitida (Call)")

    codigo = por_codigo["ASI05:2026"]
    assert codigo.estado == "aplicado"
    assert "→ 20" in codigo.evidencia


def test_la_inyeccion_directa_se_bloquea_y_el_hueco_queda_dicho():
    fila = next(f for f in ejemplos.evaluar() if f.codigo == "LLM01:2026")
    assert fila.estado == "parcial"
    assert "frase completa bloqueada=True" in fila.evidencia
    assert "cada pieza pasa=True" in fila.evidencia
    assert "conversación concatenada se bloquea=True" in fila.evidencia
    assert "tool" in fila.evidencia


def test_lo_que_no_esta_en_el_artefacto_no_se_marca_aplicado():
    por_codigo = {f.codigo: f for f in ejemplos.evaluar()}
    for codigo in ("LLM03:2026", "LLM05:2026", "LLM07:2026", "LLM09:2026", "ASI10:2026"):
        assert por_codigo[codigo].estado == "en la defensa"
        assert por_codigo[codigo].evidencia
