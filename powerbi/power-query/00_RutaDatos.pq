// PARÁMETRO: carpeta "raw" del repositorio en GitHub donde están los CSV.
// Power BI descarga los CSV desde internet, así el dashboard se actualiza solo.
// Cómo crearlo: Inicio > Administrar parámetros > Nuevo parámetro
//   Nombre: RutaDatos   Tipo: Texto   Valor actual: (la URL de abajo)
"https://raw.githubusercontent.com/04sebastian2002/dashboard-kpis-mineros/main/data/" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
