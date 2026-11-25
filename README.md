# ⛏️ Dashboard de KPIs Mineros · Perú

Dashboard en **Power BI** para analizar una operación de cobre a tajo abierto en Perú,
conectado a **APIs públicas** de precios de metales y de indicadores mineros por país.

> **Nota:** la mina "Cerro Andino" es **ficticia**. Sus datos operativos son simulados
> con rangos típicos de la gran minería peruana, porque los datos reales de las minas no
> son públicos. Los precios de los metales y los indicadores por país son **datos reales**.

<!-- Agrega aquí las capturas: ![Resumen](docs/img/01-resumen.png) -->

## 📊 Qué muestra

| Página | KPIs principales | Fuente |
|---|---|---|
| Resumen ejecutivo | Cu fino, cumplimiento del plan, costo C1, OEE, TRIFR | Mina simulada + BCRP |
| Mercado de metales | Precio de cobre, oro, plata y zinc; variación mensual y anual | **API BCRP** |
| Producción y planta | Tonelaje, ley de cabeza, recuperación, ratio desmonte/mineral | Mina simulada |
| Equipos y mantenimiento | Disponibilidad, utilización, rendimiento, OEE, MTBF, MTTR | Mina simulada |
| Costos | Costo cash por categoría, C1 (US$/lb), margen | Mina simulada + BCRP |
| Seguridad y ESG | TRIFR, LTIFR, severidad, agua, energía, CO₂ | Mina simulada |
| Perú en el mundo | Rentas minerales, exportaciones mineras, IED vs. otros países | **API Banco Mundial** |

## 🏗️ Arquitectura

```
 API BCRP (precios) ───────┐
 API Banco Mundial ────────┤
                           ├──> Power Query (M) ──> Modelo estrella ──> Medidas DAX ──> Dashboard
 GitHub /data (CSV) ───────┘                          + Calendario
        ▲
        └── scripts/generar_datos_mina.py (Python + pandas)
```

**Modelo estrella:** una tabla `Calendario` y dos dimensiones (`dim_zonas`, `dim_equipos`)
conectadas a 7 tablas de hechos (producción diaria, equipos, costos, plan, seguridad,
ambiental y precios).

## 🧮 KPIs y fórmulas

| KPI | Fórmula |
|---|---|
| Cobre fino | Mineral procesado × ley Cu × recuperación |
| Ley Cu (ponderada) | Σ(t × ley) / Σ t |
| Disponibilidad mecánica | (Horas calendario − mantenimiento) / horas calendario |
| Utilización | Horas operativas / horas disponibles |
| OEE | Disponibilidad × utilización × rendimiento |
| MTBF / MTTR | Horas operativas / fallas · horas de reparación / fallas |
| Costo C1 | Costo cash / libras de Cu fino |
| TRIFR / LTIFR | Incidentes registrables (o con tiempo perdido) × 10⁶ / horas-hombre |
| Intensidad hídrica | m³ de agua fresca / t procesada |

Todas las medidas están en [`powerbi/dax/02_medidas.dax`](powerbi/dax/02_medidas.dax).

## 📁 Estructura

```
├── data/                     CSV de la mina simulada (2023 a 2026)
├── scripts/
│   └── generar_datos_mina.py genera los CSV
├── powerbi/
│   ├── power-query/          conexiones a las APIs y a los CSV (lenguaje M)
│   ├── dax/                  tabla Calendario y medidas
│   └── tema-minero.json      tema de colores (tonos cobre)
└── docs/
    └── GUIA_PASO_A_PASO.md   cómo armar el dashboard desde cero
```

## 🚀 Cómo usarlo

1. **Regenerar los datos** (opcional):
   ```bash
   pip install -r requirements.txt
   python scripts/generar_datos_mina.py
   ```
2. **Armar el dashboard**: sigue la [guía paso a paso](docs/GUIA_PASO_A_PASO.md).

## 🔌 APIs utilizadas

- **BCRP · Banco Central de Reserva del Perú**: cotizaciones internacionales mensuales.
  Sin clave. [Documentación](https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api)
- **Banco Mundial · World Development Indicators**: indicadores anuales por país.
  Sin clave. [Documentación](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)

## 🛠️ Tecnologías

Power BI Desktop · Power Query (M) · DAX · Python · pandas · NumPy · APIs REST · Git

---

Proyecto del portafolio de [04sebastian2002](https://github.com/04sebastian2002).
