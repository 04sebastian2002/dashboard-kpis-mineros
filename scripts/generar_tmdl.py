"""
Convierte powerbi/dax/02_medidas.dax en un script TMDL que crea la tabla
_Medidas con todas las medidas, su formato y sus carpetas.

Uso en Power BI: Vista TMDL > pegar powerbi/dax/04_medidas.tmdl > Aplicar.

    python scripts/generar_tmdl.py
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "powerbi" / "dax" / "02_medidas.dax"
DESTINO = RAIZ / "powerbi" / "dax" / "04_medidas.tmdl"


def formato(nombre: str):
    if nombre.startswith(("Color", "Título", "Última")):
        return None
    if nombre == "Ley Cu (%)":
        return "0.00%"
    if "(%)" in nombre:
        return "0.0%"
    if nombre.startswith(("Ranking", "N° ", "Incidentes", "Lesiones", "Cuasi")):
        return "0"
    if any(u in nombre for u in ("US$/lb", "US$/oz", "US$/t", "m3/t", "tCO2e/t")):
        return "#,0.00"
    if nombre in ("TRIFR", "LTIFR", "Ratio Desmonte/Mineral", "MTBF (h)", "MTTR (h)"):
        return "#,0.00"
    if nombre.startswith(("Precio", "Valor")):
        return "#,0.00"
    return "#,0"


def leer_medidas(lineas):
    medidas, actual, carpeta, anterior_vacia = [], None, "General", True
    for linea in lineas:
        encabezado = re.match(r"^// \[([^\]]+)\]", linea)
        if encabezado:
            carpeta = encabezado.group(1)
        if linea.startswith("//"):
            if actual:
                medidas.append(actual)
                actual = None
            anterior_vacia = True
            continue
        if not linea.strip():
            anterior_vacia = True
            continue
        inicio = re.match(r"^(\S[^=]*?) =(?: (.*))?$", linea)
        if anterior_vacia and inicio:
            if actual:
                medidas.append(actual)
            actual = [inicio.group(1).strip(), carpeta, [inicio.group(2) or ""]]
        elif actual is not None:
            actual[2].append(linea)
        anterior_vacia = False
    if actual:
        medidas.append(actual)
    return medidas


def main():
    medidas = leer_medidas(ORIGEN.read_text(encoding="utf-8").splitlines())
    t = "\t"
    salida = ["createOrReplace", "", f"{t}table _Medidas", ""]
    for nombre, carpeta, cuerpo in medidas:
        expresion = " ".join(p.strip() for p in cuerpo if p.strip())
        salida.append(f"{t*2}measure '{nombre}' = {expresion}")
        fmt = formato(nombre)
        if fmt:
            salida.append(f"{t*3}formatString: {fmt}")
        salida.append(f"{t*3}displayFolder: {carpeta}")
        salida.append("")
    salida += [
        f"{t*2}column Valor",
        f"{t*3}dataType: int64",
        f"{t*3}isHidden",
        f"{t*3}formatString: 0",
        f"{t*3}summarizeBy: none",
        f"{t*3}isNameInferred",
        f"{t*3}sourceColumn: [Valor]",
        "",
        f"{t*2}partition _Medidas = calculated",
        f"{t*3}mode: import",
        f'{t*3}source = ROW ( "Valor", 0 )',
        "",
    ]
    DESTINO.write_text("\n".join(salida), encoding="utf-8")
    print(f"{len(medidas)} medidas -> {DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
