// 1. Korpusz-áttekintés dokumentumtípusonként (aggregáló)
// Darabszám, chunkszám és hossz típusonként. A `lánc ép` oszlop betöltés-ellenőrzés: hány
// dokumentumnál fűzi fel a NEXT_CHUNK hiánytalanul, egyetlen láncba az összes chunkot.
MATCH (d:Document)
WITH d,
     COUNT { (d)-[:CONTAINS]->(:Chunk) } AS chunks,
     COUNT { (d)-[:CONTAINS]->(c:Chunk) WHERE NOT EXISTS { ()-[:NEXT_CHUNK]->(c) } } AS heads,
     COUNT { (d)-[:CONTAINS]->(:Chunk)-[:NEXT_CHUNK]->(:Chunk)<-[:CONTAINS]-(d) } AS links
RETURN d.doc_type AS `típus`,
       count(d) AS dokumentum,
       sum(chunks) AS chunk,
       round(avg(chunks), 1) AS `chunk/dok`,
       toInteger(avg(d.char_count)) AS `átl. hossz`,
       min(d.char_count) AS `min. hossz`,
       max(d.char_count) AS `max. hossz`,
       sum(CASE WHEN heads = 1 AND links = chunks - 1 THEN 1 ELSE 0 END) AS `lánc ép`
ORDER BY dokumentum DESC, `típus`
