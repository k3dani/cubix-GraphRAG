// 3. Melyek a legrövidebb dokumentumok, és vannak-e üres vagy szemét chunkok a betöltés után?
// Tartalmi hossz: a chunk szövege a címsorok és a „Szintetikus dokumentum” sablonsor nélkül.
// Gyanús az a chunk, amelyben ez $min_content karakternél kevesebb, vagy amelyet a szomszédja
// szó szerint tartalmaz (csak overlapből áll).
// params: {"min_content": 100, "limit": 5}
MATCH (d:Document)
RETURN 'legrövidebb dokumentum' AS lelet,
       d.doc_id AS elem,
       d.char_count AS hossz,
       toString(d.chunk_count) + ' chunk (' + d.doc_type + ')' AS `megjegyzés`
ORDER BY hossz
LIMIT $limit
UNION ALL
MATCH (c:Chunk)
WITH c,
     size(reduce(s = '', line IN split(c.text, '\n') |
       CASE WHEN line STARTS WITH '#' OR line STARTS WITH '*Szintetikus' THEN s ELSE s + trim(line) END
     )) AS content
WHERE content < $min_content OR EXISTS { (c)-[:NEXT_CHUNK]-(n:Chunk) WHERE n.text CONTAINS c.text }
RETURN 'gyanús chunk' AS lelet,
       c.chunk_id AS elem,
       c.char_count AS hossz,
       'tartalom ' + toString(content) + ' kar.: „' + left(replace(c.text, '\n', ' '), 90) + '…”' AS `megjegyzés`
