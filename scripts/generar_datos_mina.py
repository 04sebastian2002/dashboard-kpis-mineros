"""
Genera un dataset simulado (pero realista) de una mina de cobre a tajo abierto
en Perú: "Mina Ficticia Cerro Andino".

Los datos operativos de las minas reales no son públicos, así que se simulan
con rangos típicos de la gran minería peruana. Los precios de metales y los
datos país vienen de APIs reales (ver powerbi/power-query).

Uso:
    python scripts/generar_datos_mina.py

Salida: archivos CSV en la carpeta data/
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 42
FECHA_INICIO = "2023-01-01"
FECHA_FIN = "2026-10-31"
CARPETA = Path(__file__).resolve().parent.parent / "data"

rng = np.random.default_rng(SEMILLA)
fechas = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="D")
n_dias = len(fechas)
t = np.arange(n_dias)

# Estacionalidad: temporada de lluvias en la sierra peruana (diciembre a marzo)
mes = fechas.month.to_numpy()
lluvias = np.isin(mes, [12, 1, 2, 3])


# ---------------------------------------------------------------- dimensiones
def dim_zonas() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "zona_id": ["F1", "F2", "F3", "F4"],
            "zona": ["Fase 1 - Norte", "Fase 2 - Centro", "Fase 3 - Sur", "Fase 4 - Expansión"],
            "ley_cu_base_pct": [0.62, 0.55, 0.48, 0.58],
            "participacion": [0.30, 0.30, 0.25, 0.15],
        }
    )


def dim_equipos() -> pd.DataFrame:
    filas = []
    for i in range(1, 25):
        filas.append(("CAM-%02d" % i, "Camión", "Komatsu 930E", "Acarreo", 290))
    for i in range(1, 5):
        filas.append(("PAL-%02d" % i, "Pala", "P&H 4100XPC", "Carguío", 4200))
    for i in range(1, 4):
        filas.append(("PER-%02d" % i, "Perforadora", "Epiroc Pit Viper 271", "Perforación", 180))
    return pd.DataFrame(
        filas, columns=["equipo_id", "tipo", "modelo", "flota", "capacidad_nominal_tph"]
    )


# ------------------------------------------------------------- producción
def fact_produccion(zonas: pd.DataFrame) -> pd.DataFrame:
    # Concentradora de ~90 000 t/día con mejora gradual y caídas en lluvias
    tendencia = 1 + 0.04 * t / n_dias
    procesado_total = 90_000 * tendencia * np.where(lluvias, 0.94, 1.0)
    procesado_total *= rng.normal(1, 0.035, n_dias)

    # Paradas de planta programadas (2 días cada ~6 meses)
    for inicio in pd.date_range(FECHA_INICIO, FECHA_FIN, freq="6MS") + pd.Timedelta(days=14):
        mask = (fechas >= inicio) & (fechas < inicio + pd.Timedelta(days=2))
        procesado_total[mask] *= 0.25

    filas = []
    for _, z in zonas.iterrows():
        mineral_proc = procesado_total * z.participacion * rng.normal(1, 0.05, n_dias)
        # La ley baja lentamente con la profundidad del tajo
        ley = z.ley_cu_base_pct * (1 - 0.06 * t / n_dias) * rng.normal(1, 0.06, n_dias)
        # Recuperación: sube con la ley de cabeza (relación típica en flotación de cobre)
        # más una variación mensual de la planta (dureza del mineral, reactivos, etc.)
        efecto_mes = rng.normal(0, 0.8, 12 * 5)[(fechas.year.to_numpy() - 2023) * 12 + mes - 1]
        recuperacion = np.clip(
            87.5 + 25 * (ley - 0.54) + efecto_mes + rng.normal(0, 1.0, n_dias), 80, 93
        )
        ley_mo = np.clip(rng.normal(0.018, 0.003, n_dias), 0.008, 0.03)
        ratio_desmonte = rng.normal(2.3, 0.2, n_dias)  # t desmonte / t mineral
        mineral_extraido = mineral_proc * rng.normal(1.02, 0.03, n_dias)
        desmonte = mineral_extraido * ratio_desmonte
        cu_fino = mineral_proc * ley / 100 * recuperacion / 100

        filas.append(
            pd.DataFrame(
                {
                    "fecha": fechas.date,
                    "zona_id": z.zona_id,
                    "mineral_extraido_t": mineral_extraido.round(0),
                    "desmonte_t": desmonte.round(0),
                    "mineral_procesado_t": mineral_proc.round(0),
                    "ley_cu_pct": ley.round(4),
                    "ley_mo_pct": ley_mo.round(4),
                    "recuperacion_cu_pct": recuperacion.round(2),
                    "cu_fino_t": cu_fino.round(2),
                }
            )
        )
    df = pd.concat(filas, ignore_index=True)
    df["material_movido_t"] = df.mineral_extraido_t + df.desmonte_t
    return df


# ---------------------------------------------------------------- equipos
def fact_equipos(equipos: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for _, e in equipos.iterrows():
        edad = rng.uniform(0, 1)  # equipos más antiguos fallan más
        mant_prog = np.where(rng.random(n_dias) < 0.09, rng.uniform(8, 16, n_dias), 0)
        mant_no_prog = np.where(
            rng.random(n_dias) < 0.07 + 0.07 * edad, rng.uniform(3, 16, n_dias), 0
        )
        disponibles = np.clip(24 - mant_prog - mant_no_prog, 0, 24)
        # Demoras operativas: cambios de turno, voladuras, clima (más en lluvias)
        demoras = np.clip(
            rng.normal(np.where(lluvias, 4.0, 2.8), 0.8, n_dias), 0, disponibles
        )
        operativas = disponibles - demoras
        rendimiento = np.clip(rng.normal(0.88, 0.05, n_dias), 0.6, 1.0)
        # Camiones y palas: toneladas. Perforadoras: metros perforados.
        toneladas = operativas * e.capacidad_nominal_tph * rendimiento

        filas.append(
            pd.DataFrame(
                {
                    "fecha": fechas.date,
                    "equipo_id": e.equipo_id,
                    "horas_calendario": 24.0,
                    "horas_mant_programada": mant_prog.round(2),
                    "horas_mant_no_programada": mant_no_prog.round(2),
                    "horas_demora": demoras.round(2),
                    "horas_operativas": operativas.round(2),
                    "produccion_real": toneladas.round(0),
                    "produccion_nominal": (operativas * e.capacidad_nominal_tph).round(0),
                    "fallas": (mant_no_prog > 0).astype(int),
                }
            )
        )
    return pd.concat(filas, ignore_index=True)


# ---------------------------------------------------------------- mensuales
meses = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="MS")
n_meses = len(meses)


def fact_costos(prod: pd.DataFrame) -> pd.DataFrame:
    prod_mes = (
        prod.assign(mes=pd.to_datetime(prod.fecha).dt.to_period("M").dt.to_timestamp())
        .groupby("mes")[["material_movido_t", "mineral_procesado_t"]]
        .sum()
    )
    # US$ por tonelada, con inflación de costos ~3 % anual
    unitarios = {
        "Mina (perforación, voladura, carguío, acarreo)": ("material_movido_t", 1.65),
        "Planta concentradora": ("mineral_procesado_t", 5.40),
        "Energía": ("mineral_procesado_t", 2.10),
        "Mantenimiento": ("material_movido_t", 0.55),
        "Servicios y G&A": (None, 6_500_000),
        "Transporte y puerto (concentrado)": ("mineral_procesado_t", 0.95),
    }
    filas = []
    for i, m in enumerate(meses):
        inflacion = 1.03 ** (i / 12)
        for categoria, (base, valor) in unitarios.items():
            if base is None:
                costo = valor
            else:
                costo = prod_mes.loc[m, base] * valor
            costo *= inflacion * rng.normal(1, 0.04)
            filas.append((m.date(), categoria, round(costo, 2)))
    return pd.DataFrame(filas, columns=["mes", "categoria_costo", "costo_usd"])


def fact_plan(prod: pd.DataFrame) -> pd.DataFrame:
    """Presupuesto mensual (plan) para comparar Real vs Plan."""
    prod_mes = (
        prod.assign(mes=pd.to_datetime(prod.fecha).dt.to_period("M").dt.to_timestamp())
        .groupby("mes")[["mineral_procesado_t", "cu_fino_t", "material_movido_t"]]
        .sum()
    )
    plan = prod_mes.rolling(3, min_periods=1).mean() * rng.normal(1.03, 0.02, (n_meses, 3))
    plan = plan.round(0).reset_index()
    plan.columns = ["mes", "mineral_procesado_plan_t", "cu_fino_plan_t", "material_movido_plan_t"]
    plan["mes"] = plan.mes.dt.date
    plan["costo_plan_usd"] = (plan.cu_fino_plan_t * 2204.62 * 1.75).round(0)
    return plan


def fact_seguridad() -> pd.DataFrame:
    trabajadores = rng.normal(4200, 150, n_meses).round(0)
    horas_hombre = trabajadores * 26 * 11  # 26 días x 11 h promedio
    # La tasa de incidentes mejora con el tiempo (programa de seguridad)
    tasa = np.linspace(1.6, 0.9, n_meses)  # por millón de HH
    registrables = rng.poisson(tasa * horas_hombre / 1e6)
    ltis = rng.binomial(registrables, 0.35)
    return pd.DataFrame(
        {
            "mes": meses.date,
            "trabajadores": trabajadores.astype(int),
            "horas_hombre": horas_hombre.round(0),
            "incidentes_registrables": registrables,
            "lesiones_tiempo_perdido": ltis,
            "cuasi_accidentes": rng.poisson(28, n_meses),
            "dias_perdidos": ltis * rng.integers(5, 40, n_meses),
        }
    )


def fact_ambiental(prod: pd.DataFrame) -> pd.DataFrame:
    proc_mes = (
        prod.assign(mes=pd.to_datetime(prod.fecha).dt.to_period("M").dt.to_timestamp())
        .groupby("mes")["mineral_procesado_t"]
        .sum()
        .to_numpy()
    )
    agua_total = proc_mes * rng.normal(0.65, 0.03, n_meses)  # m3 por t procesada
    recirculacion = np.clip(np.linspace(0.72, 0.82, n_meses) + rng.normal(0, 0.01, n_meses), 0, 0.95)
    energia = proc_mes * rng.normal(0.024, 0.001, n_meses)  # MWh por t
    renovable = np.clip(np.linspace(0.35, 0.55, n_meses), 0, 1)
    emisiones = energia * (1 - renovable) * 0.42 + proc_mes * 0.0035  # tCO2e (red + diésel)
    return pd.DataFrame(
        {
            "mes": meses.date,
            "agua_fresca_m3": (agua_total * (1 - recirculacion)).round(0),
            "agua_recirculada_m3": (agua_total * recirculacion).round(0),
            "energia_mwh": energia.round(0),
            "energia_renovable_pct": (renovable * 100).round(1),
            "emisiones_tco2e": emisiones.round(0),
        }
    )


def main() -> None:
    CARPETA.mkdir(exist_ok=True)
    zonas = dim_zonas()
    equipos = dim_equipos()
    prod = fact_produccion(zonas)

    tablas = {
        "dim_zonas": zonas.drop(columns=["ley_cu_base_pct", "participacion"]),
        "dim_equipos": equipos,
        "fact_produccion_diaria": prod,
        "fact_equipos_diario": fact_equipos(equipos),
        "fact_costos_mensual": fact_costos(prod),
        "fact_plan_mensual": fact_plan(prod),
        "fact_seguridad_mensual": fact_seguridad(),
        "fact_ambiental_mensual": fact_ambiental(prod),
    }
    for nombre, df in tablas.items():
        ruta = CARPETA / f"{nombre}.csv"
        df.to_csv(ruta, index=False, encoding="utf-8")
        print(f"{ruta.name:32s} {len(df):>8,} filas")


if __name__ == "__main__":
    main()
