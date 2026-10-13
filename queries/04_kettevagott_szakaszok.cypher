// 4. Mely szakaszokat vágta ketté a chunkolás?
// Kettévágott az a szakasz, amelyet egyetlen chunk sem tartalmaz egészben. Az a szakasz nem számít,
// amely csak az overlap miatt lóg bele a következő chunkba (a 800/100-as vágásnál ez a gyakoribb).
MATCH (d:Document)-[:HAS_SECTION]->(s:Section)
WHERE s.char_count > 0
  AND NOT EXISTS {
    MATCH (c:Chunk)-[:IN_SECTION]->(s)
    WHERE c.char_start <= s.char_start AND c.char_end >= s.char_start + s.char_count
  }
MATCH (c:Chunk)-[:IN_SECTION]->(s)
WITH d, s, c ORDER BY c.index
RETURN d.doc_type AS `típus`,
       s.section_id AS szakasz,
       s.heading AS `cím`,
       s.char_count AS hossz,
       collect(c.chunk_id) AS chunkok
ORDER BY `típus`, szakasz
