// FUNCIÓN: lee un CSV del repositorio y detecta los tipos de columna.
// Nombre de la consulta: fnLeerCSV
(nombreArchivo as text) as table =>
let
    Fuente = Csv.Document(
        Web.Contents(RutaDatos & nombreArchivo & ".csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Encabezados = Table.PromoteHeaders(Fuente, [PromoteAllScalars = true]),
    // Los CSV usan punto decimal: se fija la cultura "en-US" para que
    // Power BI en español no confunda 0.54 con 54.
    Columnas = Table.ColumnNames(Encabezados),
    Tipos = List.Transform(
        Columnas,
        each {
            _,
            if _ = "fecha" or _ = "mes" then type date
            else if List.Contains({"zona_id", "zona", "equipo_id", "tipo", "modelo", "flota", "categoria_costo"}, _) then type text
            else type number
        }
    ),
    Tipado = Table.TransformColumnTypes(Encabezados, Tipos, "en-US")
in
    Tipado
