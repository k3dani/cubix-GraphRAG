// 2. Hány chunk tartozik a leghosszabb dokumentumhoz?
// A karakterszám szerint leghosszabb dokumentum chunkjai sorrendben, a lefedett szakaszokkal.
MATCH (d:Document)
WITH d ORDER BY d.char_count DESC LIMIT 1
MATCH (d)-[:CONTAINS]->(c:Chunk)-[:IN_SECTION]->(s:Section)
WITH d, c, s ORDER BY c.index, s.order
WITH d, c, collect(s.heading) AS sections
RETURN d.doc_id AS dokumentum,
       d.char_count AS hossz,
       d.chunk_count AS chunkok,
       c.chunk_id AS chunk,
       c.char_count AS `chunk hossza`,
       sections AS `lefedett szakaszok`
ORDER BY c.index
