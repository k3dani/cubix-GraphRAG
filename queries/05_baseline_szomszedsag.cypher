// 5. Mit hozott volna a NEXT_CHUNK-szomszédság a naiv RAG-nek?
// Az 1. heti baseline top-4 találatai (baseline/answers.jsonl) mellé hozzávesszük a gráfból a
// találatok előző és következő chunkját, és megnézzük, így előkerül-e a válaszhoz szükséges chunk.
// params: {"hits": {"Q02": ["szerzodes_alvallalkozoi_kapos_gep#00", "jelentes_drava_invest_2024_kiegeszito#02", "szerzodes_alvallalkozoi_kapos_gep#02", "email_balokany_gepeszet_dontes#01"], "Q04": ["jelentes_drava_invest_2024_kiegeszito#02", "jelentes_mecsekko_holding_2024#03", "jelentes_mecsekko_holding_2024#01", "cegkivonat_drava_epito#00"], "Q07": ["level_hitelezoi_igenybejelentes_hegyhat#01", "cegkivonat_mecsekko_epitoanyag#01", "jelentes_drava_invest_2024_kiegeszito#02", "jelentes_mecsekko_holding_2024#03"]}}
// params: {"needed": {"Q02": ["szerzodes_alvallalkozoi_kapos_gep#01"], "Q04": ["cegkivonat_kapos_gep#01"], "Q07": ["level_hitelezoi_igenybejelentes_hegyhat#00", "cegkivonat_hegyhat#01"]}}
UNWIND keys($hits) AS question
MATCH (h:Chunk) WHERE h.chunk_id IN $hits[question]
OPTIONAL MATCH (h)-[:NEXT_CHUNK]-(n:Chunk) WHERE NOT n.chunk_id IN $hits[question]
WITH question, collect(DISTINCT n.chunk_id) AS neighbours
WITH question, neighbours, $needed[question] AS needed
RETURN question AS `kérdés`,
       needed AS `szükséges chunk (bármelyik)`,
       any(x IN needed WHERE x IN $hits[question]) AS `vektoros top-4-ben`,
       neighbours AS `szomszédként bekerülne`,
       any(x IN needed WHERE x IN neighbours) AS `szomszédsággal meglenne`
ORDER BY `kérdés`
