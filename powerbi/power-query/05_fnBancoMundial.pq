// FUNCIÓN: descarga un indicador anual de la API del Banco Mundial. No necesita clave.
// Documentación: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
// Nombre de la consulta: fnBancoMundial
// Ejemplo: fnBancoMundial("NY.GDP.MINR.RT.ZS")
(indicador as text) as table =>
let
    Paises = "PER;CHL;COD;CHN;AUS;USA;MEX;CAN",
    Respuesta = Web.Contents(
        "https://api.worldbank.org",
        [
            RelativePath = "v2/country/" & Paises & "/indicator/" & indicador,
            Query = [format = "json", date = "2000:2030", per_page = "5000"]
        ]
    ),
    Json = Json.Document(Respuesta),
    // La respuesta es una lista: {0} = información de páginas, {1} = datos
    Registros = Json{1},
    Tabla = Table.FromList(Registros, Splitter.SplitByNothing(), {"r"}),
    Columnas = Table.ExpandRecordColumn(Tabla, "r", {"countryiso3code", "country", "indicator", "date", "value"}),
    ConPais = Table.TransformColumns(Columnas, {{"country", each _[value], type text}, {"indicator", each _[value], type text}}),
    Renombrado = Table.RenameColumns(ConPais, {
        {"countryiso3code", "pais_iso3"}, {"country", "pais"},
        {"indicator", "indicador"}, {"date", "anio"}, {"value", "valor"}
    }),
    Tipado = Table.TransformColumnTypes(Renombrado, {{"anio", Int64.Type}, {"valor", type number}}),
    SinVacios = Table.SelectRows(Tipado, each [valor] <> null),
    ConCodigo = Table.AddColumn(SinVacios, "codigo_indicador", each indicador, type text)
in
    ConCodigo
