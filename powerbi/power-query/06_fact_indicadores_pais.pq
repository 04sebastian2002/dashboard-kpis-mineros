// TABLA: indicadores mineros por país (API del Banco Mundial).
// Nombre de la consulta: fact_indicadores_pais
let
    Indicadores = #table(
        type table [codigo = text, nombre_corto = text],
        {
            {"NY.GDP.MINR.RT.ZS",  "Rentas minerales (% del PIB)"},
            {"TX.VAL.MMTL.ZS.UN",  "Exportación de minerales y metales (% de exportaciones)"},
            {"NY.GDP.MKTP.CD",     "PIB (US$ corrientes)"},
            {"BX.KLT.DINV.CD.WD",  "Inversión extranjera directa (US$)"}
        }
    ),
    ConDatos = Table.AddColumn(Indicadores, "datos", each fnBancoMundial([codigo])),
    Expandido = Table.ExpandTableColumn(ConDatos, "datos", {"pais_iso3", "pais", "anio", "valor"}),
    // Al expandir se pierden los tipos: se vuelven a asignar
    Tipado = Table.TransformColumnTypes(Expandido, {{"pais_iso3", type text}, {"pais", type text}, {"anio", Int64.Type}, {"valor", type number}}),
    Final = Table.RemoveColumns(Tipado, {"codigo"})
in
    Final
