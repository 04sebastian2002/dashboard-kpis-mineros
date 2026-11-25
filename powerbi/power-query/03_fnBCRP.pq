// FUNCIÓN: descarga una serie mensual de la API del Banco Central de Reserva
// del Perú (BCRP). No necesita clave.
// Documentación: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
// Nombre de la consulta: fnBCRP
// Ejemplo: fnBCRP("PN01652XM", "2023-1", "2026-12")
(codigo as text, inicio as text, fin as text) as table =>
let
    // Se usa RelativePath para que la actualización programada funcione
    // también en el servicio de Power BI (web).
    Respuesta = Web.Contents(
        "https://estadisticas.bcrp.gob.pe",
        [RelativePath = "estadisticas/series/api/" & codigo & "/json/" & inicio & "/" & fin & "/esp"]
    ),
    Json = Json.Document(Respuesta),
    NombreSerie = Json[config][series]{0}[name],
    Periodos = Table.FromRecords(Json[periods]),
    // "Ene.2023" -> 1/01/2023. El BCRP usa "Set" para septiembre.
    Meses = {"Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"},
    ConFecha = Table.AddColumn(
        Periodos, "fecha",
        each
            let
                abrev = Text.Replace(Text.BeforeDelimiter([name], "."), "Sep", "Set"),
                anio = Number.FromText(Text.AfterDelimiter([name], ".")),
                numMes = List.PositionOf(Meses, abrev) + 1
            in
                #date(anio, numMes, 1),
        type date
    ),
    // Los meses sin dato vienen como "n.d." y quedan en blanco.
    ConValor = Table.AddColumn(
        ConFecha, "valor",
        each try Number.FromText([values]{0}, "en-US") otherwise null,
        type number
    ),
    Resultado = Table.AddColumn(
        Table.SelectColumns(ConValor, {"fecha", "valor"}),
        "serie_bcrp", each NombreSerie, type text
    )
in
    Resultado
