// TABLA: cotizaciones internacionales mensuales de metales (API del BCRP).
// Nombre de la consulta: fact_precios_metales
//
// IMPORTANTE: revisa los códigos en https://estadisticas.bcrp.gob.pe
// (buscar "Cotizaciones internacionales"). La columna "serie_bcrp" muestra el
// nombre oficial que devuelve la API, así puedes comprobar que cada código
// corresponde al metal correcto. Si alguno no coincide, cambia el código aquí.
let
    Series = #table(
        type table [codigo = text, metal = text, unidad = text, factor_usd = number],
        {
            {"PN01652XM", "Cobre", "US$/lb",     0.01},   // la API lo da en ¢US$/lb
            {"PN01654XM", "Oro",   "US$/oz troy", 1},
            {"PN01655XM", "Plata", "US$/oz troy", 1},
            {"PN01657XM", "Zinc",  "US$/lb",     0.01}
        }
    ),
    Inicio = "2015-1",
    Fin = Text.From(Date.Year(DateTime.LocalNow())) & "-12",
    ConDatos = Table.AddColumn(Series, "datos", each fnBCRP([codigo], Inicio, Fin)),
    Expandido = Table.ExpandTableColumn(ConDatos, "datos", {"fecha", "valor", "serie_bcrp"}),
    ConPrecio = Table.AddColumn(Expandido, "precio_usd", each [valor] * [factor_usd], type number),
    Limpio = Table.SelectRows(ConPrecio, each [precio_usd] <> null),
    Final = Table.SelectColumns(Limpio, {"fecha", "metal", "unidad", "precio_usd", "serie_bcrp", "codigo"})
in
    Final
