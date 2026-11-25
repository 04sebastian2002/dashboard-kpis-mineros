// TABLAS DE LA MINA SIMULADA. Crea una consulta en blanco por cada línea,
// con el nombre de la izquierda y el código de la derecha
// (Inicio > Nuevo origen > Consulta en blanco > Editor avanzado).
//
//   dim_zonas               =  fnLeerCSV("dim_zonas")
//   dim_equipos             =  fnLeerCSV("dim_equipos")
//   fact_produccion_diaria  =  fnLeerCSV("fact_produccion_diaria")
//   fact_equipos_diario     =  fnLeerCSV("fact_equipos_diario")
//   fact_costos_mensual     =  fnLeerCSV("fact_costos_mensual")
//   fact_plan_mensual       =  fnLeerCSV("fact_plan_mensual")
//   fact_seguridad_mensual  =  fnLeerCSV("fact_seguridad_mensual")
//   fact_ambiental_mensual  =  fnLeerCSV("fact_ambiental_mensual")
//
// Ejemplo del Editor avanzado para dim_zonas:
let
    Origen = fnLeerCSV("dim_zonas")
in
    Origen
