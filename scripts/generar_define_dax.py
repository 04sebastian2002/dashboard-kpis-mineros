"""
Convierte powerbi/dax/02_medidas.dax en un solo bloque DEFINE para pegar en la
Vista de consultas DAX de Power BI y crear todas las medidas de una vez.

Uso:
    python scripts/generar_define_dax.py
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "powerbi" / "dax" / "02_medidas.dax"
DESTINO = RAIZ / "powerbi" / "dax" / "03_todas_las_medidas.dax"


def leer_medidas(lineas):
    medidas, actual, linea_anterior_vacia = [], None, True
    for linea in lineas:
        if linea.startswith("//"):
            if actual:
                medidas.append(actual)
                actual = None
            linea_anterior_vacia = True
            continue
        if not linea.strip():
            linea_anterior_vacia = True
            if actual:
                actual[1].append(linea)
            continue
        inicio = re.match(r"^(\S[^=]*?) =(?: (.*))?$", linea)
        if linea_anterior_vacia and inicio:
            if actual:
                medidas.append(actual)
            actual = [inicio.group(1).strip(), [inicio.group(2)] if inicio.group(2) else []]
        elif actual is not None:
            actual[1].append(linea)
        linea_anterior_vacia = False
    if actual:
        medidas.append(actual)
    return medidas


def main():
    medidas = leer_medidas(ORIGEN.read_text(encoding="utf-8").splitlines())
    n = len(medidas)
    salida = [
        f"// TODAS LAS MEDIDAS DE UNA VEZ ({n} medidas). Archivo generado por scripts/generar_define_dax.py",
        "// 1. Crea la tabla _Medidas (Inicio > Introducir datos > nombre _Medidas > Cargar).",
        "// 2. Abre la Vista de consultas DAX (4.º ícono de la barra izquierda).",
        "// 3. Pega TODO este archivo y haz clic en el enlace que aparece arriba de DEFINE:",
        f'//    "Actualizar modelo: agregar {n} medidas nuevas".',
        "// 4. (Opcional) Clic en Ejecutar para ver una prueba con 4 KPIs.",
        "",
        "DEFINE",
    ]
    for nombre, cuerpo in medidas:
        while cuerpo and not cuerpo[-1].strip():
            cuerpo.pop()
        if len(cuerpo) == 1:
            salida.append(f"    MEASURE _Medidas[{nombre}] = {cuerpo[0]}")
        else:
            salida.append(f"    MEASURE _Medidas[{nombre}] =")
            salida.extend("        " + c if c.strip() else "" for c in cuerpo)
        salida.append("")
    salida += [
        "EVALUATE",
        "    ROW (",
        '        "Cu Fino (t)", [Cu Fino (t)],',
        '        "Ley Cu (%)", [Ley Cu (%)],',
        '        "OEE (%)", [OEE (%)],',
        '        "Costo C1 (US$/lb)", [Costo C1 (US$/lb)]',
        "    )",
        "",
    ]
    DESTINO.write_text("\n".join(salida), encoding="utf-8")
    print(f"{n} medidas -> {DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
