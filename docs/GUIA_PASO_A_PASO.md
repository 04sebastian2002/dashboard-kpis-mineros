# Guía paso a paso: armar el dashboard en Power BI Desktop

Tiempo estimado: 2 a 3 horas. Haz una parte por sesión si prefieres.
Guarda seguido con **Ctrl + G** como `dashboard-kpis-mineros.pbix`.

---

## Parte 1. Configuración inicial (5 min)

1. Abre Power BI Desktop > **Informe en blanco**.
2. **Archivo > Opciones y configuración > Opciones**:
   - *Configuración regional* (en **Archivo actual**): Español (Perú).
   - *Carga de datos* (en **Archivo actual**): desmarca **Inteligencia de tiempo automática**
     (usaremos nuestra propia tabla Calendario).
3. **Diseño > Importar tema** (o **Temas ⌄ > Examinar temas** en otras versiones) > elige `powerbi/tema-minero.json`
   (en versiones antiguas está en **Vista > Temas**). Para tener el archivo en tu PC:
   en GitHub, botón verde **Code > Download ZIP** y luego **Extraer todo**.

---

## Parte 2. Cargar los datos de la mina (20 min)

Todo se hace en el **Editor de Power Query**: **Inicio > Transformar datos**.

### 2.1 Parámetro con la ruta de los datos
1. **Inicio > Administrar parámetros > Nuevo parámetro**.
2. Nombre `RutaDatos`, Tipo **Texto**, Valor actual:
   `https://raw.githubusercontent.com/04sebastian2002/dashboard-kpis-mineros/main/data/`
3. Aceptar.

> El repositorio debe ser **público** para que esta URL funcione.

### 2.2 Función para leer los CSV
1. **Inicio > Nuevo origen > Consulta en blanco**.
2. **Inicio > Editor avanzado** > borra todo > pega el contenido de
   `powerbi/power-query/01_fnLeerCSV.pq` > **Listo**.
3. En el panel derecho, cambia el nombre de la consulta a `fnLeerCSV`.

### 2.3 Las 8 tablas
Por cada tabla de `02_tablas_mina.pq`:
1. **Nuevo origen > Consulta en blanco** > **Editor avanzado**.
2. Pega (cambiando el nombre del archivo):
   ```
   let
       Origen = fnLeerCSV("fact_produccion_diaria")
   in
       Origen
   ```
3. Renombra la consulta con el mismo nombre (`fact_produccion_diaria`).

Si Power BI pregunta por la privacidad o la autenticación: elige **Anónimo** y nivel **Público**.

---

## Parte 3. Conectar las APIs (20 min)

Igual que antes, una consulta en blanco por archivo, con estos nombres:

| Archivo | Nombre de la consulta |
|---|---|
| `03_fnBCRP.pq` | `fnBCRP` |
| `04_fact_precios_metales.pq` | `fact_precios_metales` |
| `05_fnBancoMundial.pq` | `fnBancoMundial` |
| `06_fact_indicadores_pais.pq` | `fact_indicadores_pais` |

**Verifica los precios:** abre `fact_precios_metales` y mira la columna `serie_bcrp`.
Debe decir el nombre de cada metal (cobre, oro, plata, zinc). Si algún código trae
otra serie, búscalo en https://estadisticas.bcrp.gob.pe ("Cotizaciones internacionales")
y corrígelo en la tabla `Series` de esa consulta.

Si aparece *"Formula.Firewall"*: **Archivo > Opciones > Privacidad** (Archivo actual) >
**Ignorar los niveles de privacidad**.

Al terminar: **Inicio > Cerrar y aplicar**.

---

## Parte 4. Modelo de datos (15 min)

1. **Modelado > Nueva tabla** > pega `powerbi/dax/01_calendario.dax`.
2. Renombra la columna `Date` a `Fecha`. Clic derecho en la tabla **Calendario** >
   **Marcar como tabla de fechas** > `Fecha`.
3. Ve a la **Vista de modelo** (tercer ícono a la izquierda) y arrastra para crear
   estas relaciones (todas *de uno a varios*, dirección **única**):

```
Calendario[Fecha]   1 ──── *  fact_produccion_diaria[fecha]
Calendario[Fecha]   1 ──── *  fact_equipos_diario[fecha]
Calendario[Fecha]   1 ──── *  fact_costos_mensual[mes]
Calendario[Fecha]   1 ──── *  fact_plan_mensual[mes]
Calendario[Fecha]   1 ──── *  fact_seguridad_mensual[mes]
Calendario[Fecha]   1 ──── *  fact_ambiental_mensual[mes]
Calendario[Fecha]   1 ──── *  fact_precios_metales[fecha]
dim_zonas[zona_id]  1 ──── *  fact_produccion_diaria[zona_id]
dim_equipos[equipo_id] 1 ── * fact_equipos_diario[equipo_id]
```

`fact_indicadores_pais` queda **sin relación** (es anual y por país).

Es un **modelo estrella**: una buena palabra para mencionar en entrevistas.

---

## Parte 5. Medidas DAX (30 min)

1. **Inicio > Especificar datos** > nombre `_Medidas` > **Cargar**.
2. Selecciona `_Medidas` > **Inicio > Nueva medida** > pega una medida de
   `powerbi/dax/02_medidas.dax` > Enter. Repite con cada una.
3. Formatos (Herramientas de medición):
   - Las que terminan en `(%)` → **Porcentaje**, 1 decimal.
   - `(t)`, `(US$)`, `(m3)` → **Número entero** con separador de miles.
   - `US$/lb` → 2 decimales.
4. Elimina la columna vacía de `_Medidas`: la tabla pasa a tener el ícono de calculadora.

---

## Parte 6. Las páginas del dashboard (1 a 1,5 h)

Lienzo: **Vista > Configuración de página > 16:9**. Arriba de cada página pon un
título y los filtros (segmentaciones) de **Año** y **Mes**.

### Página 1 · Resumen ejecutivo
- **Tarjetas** (fila superior): `Cu Fino (t)`, `Cumplimiento Cu (%)`, `Costo C1 (US$/lb)`,
  `Precio Cu (US$/lb)`, `OEE (%)`, `TRIFR`.
- **Gráfico de líneas y columnas**: eje `Año-Mes`, columnas `Cu Fino (t)`, línea `Cu Fino Plan (t)`.
- **Medidor**: `Cumplimiento Cu (%)` con destino 1.
- **Gráfico de líneas**: `Precio Cu (US$/lb)` y `Costo C1 (US$/lb)` por mes
  (el espacio entre las dos líneas es el margen).

### Página 2 · Mercado de metales (API BCRP)
- Segmentación de `fact_precios_metales[metal]` (selección única).
- Tarjetas: `Precio Metal Seleccionado`, `Variación Mensual (%)`, `Variación Anual (%)`.
- **Gráfico de líneas**: eje `Fecha` (jerarquía Año > Mes), valor `Precio Metal Seleccionado`.
- **Matriz**: filas `Año`, columnas `metal`, valores `Precio Metal Seleccionado`.
- Cuadro de texto con la medida `Última Actualización Precios`.

### Página 3 · Producción y planta
- Tarjetas: `Mineral Procesado (t)`, `Ley Cu (%)`, `Recuperación Cu (%)`, `Ratio Desmonte/Mineral`.
- **Columnas apiladas**: `Año-Mes` × `Cu Fino (t)` con leyenda `dim_zonas[zona]`.
- **Gráfico de dispersión**: eje X `Ley Cu (%)`, eje Y `Recuperación Cu (%)`, detalles `Fecha`.
- **Columnas agrupadas**: `Temporada` × `Procesamiento Diario Promedio (t/d)`
  (muestra el efecto de la temporada de lluvias).

### Página 4 · Equipos y mantenimiento
- Segmentación de `dim_equipos[tipo]`.
- Tarjetas: `Disponibilidad Mecánica (%)`, `Utilización (%)`, `Rendimiento (%)`, `OEE (%)`.
- **Tabla**: `equipo_id`, `modelo`, `OEE (%)`, `MTBF (h)`, `MTTR (h)`, `N° Fallas`.
  Activa **formato condicional > escala de colores** en `OEE (%)`.
- **Líneas**: `OEE (%)` por `Año-Mes`.
- **Barras**: los 10 equipos con más `N° Fallas` (filtro *N superior*).

### Página 5 · Costos
- Tarjetas: `Costo Cash (US$)`, `Costo C1 (US$/lb)`, `Ingreso Estimado Cu (US$)`, `Margen Cash (%)`.
- **Gráfico de cascada**: categoría `categoria_costo`, valor `Costo Cash (US$)`.
- **Anillo**: `categoria_costo` × `Costo Cash (US$)`.
- **Líneas**: `Costo por t Procesada (US$/t)` por mes.

### Página 6 · Seguridad y ESG
- Tarjetas: `TRIFR`, `LTIFR`, `Índice de Severidad`, `Recirculación de Agua (%)`,
  `Intensidad de Carbono (tCO2e/t Cu)`, `Energía Renovable (%)`.
- **Columnas + línea**: `Incidentes Registrables` (columnas) y `TRIFR` (línea) por mes.
- **Área apilada**: `Agua Fresca (m3)` y `Agua Recirculada (m3)` por mes.
- **Líneas**: `Intensidad Energética (kWh/t)` por mes.

### Página 7 · Perú en el mundo (API Banco Mundial)
- Segmentaciones: `nombre_corto` (selección única) y `anio`.
- **Barras horizontales**: `pais` × `Valor Indicador` (ordenado de mayor a menor).
- **Líneas**: eje `anio`, valor `Valor Indicador`, leyenda `pais`.
- Tarjetas: `Valor Indicador Perú` y `Ranking Perú`.
- **Mapa** (opcional): ubicación `pais`, tamaño `Valor Indicador`.

### Toques finales
- **Botones de navegación**: Insertar > Botones > Navegador > **Navegador de páginas**.
- **Información sobre herramientas** con las unidades de cada KPI.
- Pie de página en todas: *"Datos operativos simulados con fines demostrativos.
  Precios: BCRP. Indicadores país: Banco Mundial."*

---

## Parte 7. Publicar (opcional, 15 min)

1. **Inicio > Publicar** > inicia sesión con una cuenta de trabajo o estudiante.
2. En app.powerbi.com: **Configuración del conjunto de datos > Actualización programada**
   (diaria) → los precios se actualizan solos.
3. Captura de pantalla de cada página (**Win + Shift + S**) y guárdala en `docs/img/`
   para el README.

> Si no tienes cuenta de trabajo, no pasa nada: sube el `.pbix` y las capturas al repositorio.

---

## Problemas comunes

| Problema | Solución |
|---|---|
| Los decimales salen como 054 en vez de 0,54 | La función `fnLeerCSV` ya usa `"en-US"`; revisa que la copiaste completa. |
| `Formula.Firewall` | Opciones > Privacidad > Ignorar niveles de privacidad. |
| Error 404 al leer los CSV | El repo no es público o el valor de `RutaDatos` está mal escrito (debe terminar en `/`). |
| La API del BCRP no responde | Prueba la URL en el navegador: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01652XM/json/2024-1/2024-6/esp` |
| Las medidas de tiempo dan en blanco | Falta marcar Calendario como tabla de fechas, o falta la relación con la tabla. |
