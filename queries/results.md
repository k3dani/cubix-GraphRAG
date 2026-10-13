# Cypher-lekérdezések és kimenetük

Futtatva: 2026-10-13T15:18:00+02:00, `uv run graph-queries`. A lekérdezések a `queries/*.cypher` fájlokban vannak; ez a fájl generált.

## 1. Korpusz-áttekintés dokumentumtípusonként (aggregáló)

`01_dokumentumtipusok.cypher` — Darabszám, chunkszám és hossz típusonként. A `lánc ép` oszlop betöltés-ellenőrzés: hány dokumentumnál fűzi fel a NEXT_CHUNK hiánytalanul, egyetlen láncba az összes chunkot.

```cypher
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
```

| típus | dokumentum | chunk | chunk/dok | átl. hossz | min. hossz | max. hossz | lánc ép |
|---|---|---|---|---|---|---|---|
| cégkivonat | 12 | 28 | 2.3 | 1396 | 1109 | 1925 | 12 |
| levél | 4 | 10 | 2.5 | 1280 | 913 | 1667 | 4 |
| szerződés | 4 | 11 | 2.8 | 1490 | 1081 | 1826 | 4 |
| jelentés | 2 | 7 | 3.5 | 1912 | 1591 | 2234 | 2 |
| számla | 2 | 4 | 2 | 1079 | 1071 | 1087 | 2 |
| e-mail | 1 | 2 | 2 | 1210 | 1210 | 1210 | 1 |

## 2. Hány chunk tartozik a leghosszabb dokumentumhoz?

`02_leghosszabb_dokumentum.cypher` — A karakterszám szerint leghosszabb dokumentum chunkjai sorrendben, a lefedett szakaszokkal.

```cypher
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
```

| dokumentum | hossz | chunkok | chunk | chunk hossza | lefedett szakaszok |
|---|---|---|---|---|---|
| jelentes_mecsekko_holding_2024 | 2234 | 4 | jelentes_mecsekko_holding_2024#00 | 225 | (bevezető) |
| jelentes_mecsekko_holding_2024 | 2234 | 4 | jelentes_mecsekko_holding_2024#01 | 673 | 1. A cégcsoport összetétele |
| jelentes_mecsekko_holding_2024 | 2234 | 4 | jelentes_mecsekko_holding_2024#02 | 793 | 2. Gazdálkodás, 3. Akvizíció |
| jelentes_mecsekko_holding_2024 | 2234 | 4 | jelentes_mecsekko_holding_2024#03 | 536 | 4. Kockázatok |

## 3. Melyek a legrövidebb dokumentumok, és vannak-e üres vagy szemét chunkok a betöltés után?

`03_legrovidebb_es_gyanus_chunkok.cypher` — Tartalmi hossz: a chunk szövege a címsorok és a „Szintetikus dokumentum” sablonsor nélkül. Gyanús az a chunk, amelyben ez $min_content karakternél kevesebb, vagy amelyet a szomszédja szó szerint tartalmaz (csak overlapből áll).

Paraméterek: `{"min_content": 100, "limit": 5}`

```cypher
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
```

| lelet | elem | hossz | megjegyzés |
|---|---|---|---|
| legrövidebb dokumentum | level_drava_gepeszet_ugyvezeto_valtas | 913 | 2 chunk (levél) |
| legrövidebb dokumentum | szamla_mecsekko_beton_MB-2025-0388 | 1071 | 2 chunk (számla) |
| legrövidebb dokumentum | szerzodes_konyveles_zselic_butor | 1081 | 2 chunk (szerződés) |
| legrövidebb dokumentum | szamla_kapos_gep_KG-2025-014 | 1087 | 2 chunk (számla) |
| legrövidebb dokumentum | cegkivonat_dunantuli_konyvelo | 1109 | 2 chunk (cégkivonat) |
| gyanús chunk | jelentes_mecsekko_holding_2024#00 | 225 | tartalom 67 kar.: „# Mecsekkő Holding Zrt. — Igazgatósági jelentés a 2024. üzleti évről  *Szintetikus dokumen…” |
| gyanús chunk | level_tolnaker_tulajdonosvaltas#02 | 87 | tartalom 87 kar.: „4. **Bankszámla:** pénzforgalmi számlaszámunk (99990282-06655234-15475586) változatlan.…” |

## 4. Mely szakaszokat vágta ketté a chunkolás?

`04_kettevagott_szakaszok.cypher` — Kettévágott az a szakasz, amelyet egyetlen chunk sem tartalmaz egészben. Az a szakasz nem számít, amely csak az overlap miatt lóg bele a következő chunkba (a 800/100-as vágásnál ez a gyakoribb).

```cypher
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
```

| típus | szakasz | cím | hossz | chunkok |
|---|---|---|---|---|
| e-mail | email_balokany_gepeszet_dontes/00 | (bevezető) | 1209 | email_balokany_gepeszet_dontes#00, email_balokany_gepeszet_dontes#01 |
| levél | level_drava_gepeszet_ugyvezeto_valtas/00 | (bevezető) | 912 | level_drava_gepeszet_ugyvezeto_valtas#00, level_drava_gepeszet_ugyvezeto_valtas#01 |
| levél | level_fizetesi_felszolitas_hegyhat/00 | (bevezető) | 1319 | level_fizetesi_felszolitas_hegyhat#00, level_fizetesi_felszolitas_hegyhat#01 |
| levél | level_tolnaker_tulajdonosvaltas/00 | (bevezető) | 1666 | level_tolnaker_tulajdonosvaltas#00, level_tolnaker_tulajdonosvaltas#01, level_tolnaker_tulajdonosvaltas#02, level_tolnaker_tulajdonosvaltas#03 |
| szerződés | szerzodes_konyveles_hegyhat_felmondas/01 | Tárgy: a 2019. február 1-jén kötött könyvelési megbízási szerződés felmondása | 948 | szerzodes_konyveles_hegyhat_felmondas#01, szerzodes_konyveles_hegyhat_felmondas#02 |
| számla | szamla_kapos_gep_KG-2025-014/00 | (bevezető) | 1086 | szamla_kapos_gep_KG-2025-014#00, szamla_kapos_gep_KG-2025-014#01 |
| számla | szamla_mecsekko_beton_MB-2025-0388/00 | (bevezető) | 1070 | szamla_mecsekko_beton_MB-2025-0388#00, szamla_mecsekko_beton_MB-2025-0388#01 |

## 5. Mit hozott volna a NEXT_CHUNK-szomszédság a naiv RAG-nek?

`05_baseline_szomszedsag.cypher` — Az 1. heti baseline top-4 találatai (baseline/answers.jsonl) mellé hozzávesszük a gráfból a találatok előző és következő chunkját, és megnézzük, így előkerül-e a válaszhoz szükséges chunk.

Paraméterek: `{"hits": {"Q02": ["szerzodes_alvallalkozoi_kapos_gep#00", "jelentes_drava_invest_2024_kiegeszito#02", "szerzodes_alvallalkozoi_kapos_gep#02", "email_balokany_gepeszet_dontes#01"], "Q04": ["jelentes_drava_invest_2024_kiegeszito#02", "jelentes_mecsekko_holding_2024#03", "jelentes_mecsekko_holding_2024#01", "cegkivonat_drava_epito#00"], "Q07": ["level_hitelezoi_igenybejelentes_hegyhat#01", "cegkivonat_mecsekko_epitoanyag#01", "jelentes_drava_invest_2024_kiegeszito#02", "jelentes_mecsekko_holding_2024#03"]}, "needed": {"Q02": ["szerzodes_alvallalkozoi_kapos_gep#01"], "Q04": ["cegkivonat_kapos_gep#01"], "Q07": ["level_hitelezoi_igenybejelentes_hegyhat#00", "cegkivonat_hegyhat#01"]}}`

```cypher
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
```

| kérdés | szükséges chunk (bármelyik) | vektoros top-4-ben | szomszédként bekerülne | szomszédsággal meglenne |
|---|---|---|---|---|
| Q02 | szerzodes_alvallalkozoi_kapos_gep#01 | nem | szerzodes_alvallalkozoi_kapos_gep#01, jelentes_drava_invest_2024_kiegeszito#01, email_balokany_gepeszet_dontes#00 | igen |
| Q04 | cegkivonat_kapos_gep#01 | nem | jelentes_drava_invest_2024_kiegeszito#01, jelentes_mecsekko_holding_2024#02, jelentes_mecsekko_holding_2024#00, cegkivonat_drava_epito#01 | nem |
| Q07 | level_hitelezoi_igenybejelentes_hegyhat#00, cegkivonat_hegyhat#01 | nem | level_hitelezoi_igenybejelentes_hegyhat#00, cegkivonat_mecsekko_epitoanyag#00, jelentes_drava_invest_2024_kiegeszito#01, jelentes_mecsekko_holding_2024#02 | igen |

## 6. Seed, 3 hop: kivel szerződnek egy személy érdekeltségei, és a partner a csoportjával is szerződik?

`06_seed_rejtett_erdekeltseg.cypher` — Személy -OWNS-> cég -PARTY_TO-> szerződés <-PARTY_TO- partner. Ez a Q04 seed-beli párja: a naiv RAG azért bukott, mert a híd-cég neve nincs a kérdésben; a gráfban ez egyetlen bejárás.

Paraméterek: `{"person_id": "varga-bela-1961-05-14"}`

```cypher
MATCH path = (p:Person {person_id: $person_id})-[o:OWNS]->(own:Company)
             -[r1:PARTY_TO]->(k:Contract)<-[r2:PARTY_TO]-(partner:Company)
WHERE o.valid_to IS NULL
RETURN p.name AS `személy`,
       toString(o.share_pct) + '% — ' + own.name + ' (' + r1.role + ')' AS `érdekeltség`,
       k.title AS `szerződés`,
       partner.name + ' (' + r2.role + ')' AS partner,
       length(path) AS hop,
       EXISTS {
         MATCH (p)-[os:OWNS*2..3]->(:Company)-[:PARTY_TO]->(:Contract)<-[:PARTY_TO]-(partner)
         WHERE all(x IN os WHERE x.valid_to IS NULL)
       } AS `a partner a holdingon át is szerződik vele`
```

| személy | érdekeltség | szerződés | partner | hop | a partner a holdingon át is szerződik vele |
|---|---|---|---|---|---|
| Varga Béla | 25% — Csongrád-Gép Kft. (alvállalkozó) | Alvállalkozói szerződés — Újszegedi Liget Lakópark, épületgépészet | Maros Építő Zrt. (fővállalkozó) | 3 | igen |

## 7. Seed, változó hosszú út: kik a cég (közvetett) tulajdonosai, és mekkora effektív hányaddal?

`07_seed_kozvetett_tulajdon.cypher` — A tulajdonosi lánc (OWNS*1..3) mentén a hányadok szorzata; csak a ma is hatályos élek számítanak. A Q10 seed-beli párja.

Paraméterek: `{"reg_no": "06-09-912305"}`

```cypher
MATCH path = (owner)-[os:OWNS*1..3]->(c:Company {reg_no: $reg_no})
WHERE all(o IN os WHERE o.valid_to IS NULL)
RETURN c.name AS `cég`,
       owner.name AS tulajdonos,
       owner:Person AS `természetes személy`,
       reduce(s = '', n IN nodes(path) | s + CASE WHEN s = '' THEN '' ELSE ' → ' END + n.name) AS `lánc`,
       length(path) AS hop,
       round(reduce(s = 1.0, o IN os | s * o.share_pct / 100.0) * 100, 1) AS `effektív %`
ORDER BY `effektív %` DESC, hop
```

| cég | tulajdonos | természetes személy | lánc | hop | effektív % |
|---|---|---|---|---|---|
| Tisza Beton Kft. | Tisza-Kő Holding Zrt. | nem | Tisza-Kő Holding Zrt. → Tisza Beton Kft. | 1 | 100 |
| Tisza Beton Kft. | Varga Béla | igen | Varga Béla → Tisza-Kő Holding Zrt. → Tisza Beton Kft. | 2 | 65 |
| Tisza Beton Kft. | Lakatos Éva | igen | Lakatos Éva → Tisza-Kő Holding Zrt. → Tisza Beton Kft. | 2 | 35 |

## 8. Seed, aggregáló: közös székhely — csoporton belüli kapcsolat, vagy csak székhelyszolgáltatás?

`08_seed_kozos_szekhely.cypher` — Címenként a bejegyzett cégek. Egy cégpár akkor függ össze, ha van közös gazdájuk tulajdonosi vagy vezetői szálon (vagy az egyik birtokolja a másikat). A Q09 seed-beli párja: a közös cím önmagában nem kapcsolat.

Paraméterek: `{"dataset": "seed"}`

```cypher
MATCH (a:Address {dataset: $dataset})<-[:REGISTERED_AT]-(c:Company)
WITH a, collect(c) AS companies
WHERE size(companies) > 1
UNWIND companies AS c1
UNWIND companies AS c2
WITH a, companies, c1, c2
WHERE c1.reg_no < c2.reg_no
WITH a, companies,
     collect(EXISTS { (c1)<-[:OWNS|OFFICER_OF*0..2]-(x)-[:OWNS|OFFICER_OF*0..2]->(c2) }) AS linked
OPTIONAL MATCH (provider:Company)-[:SEAT_PROVIDER_FOR]->(client:Company)
WHERE client IN companies
WITH a, companies, linked, collect(DISTINCT provider.name) AS providers
RETURN a.address AS `cím`,
       size(companies) AS `cégek`,
       [c IN companies | c.name] AS `bejegyzett cégek`,
       size([l IN linked WHERE l]) AS `összefüggő pár`,
       size([l IN linked WHERE NOT l]) AS `csak közös cím`,
       providers AS `székhelyszolgáltató`,
       CASE
         WHEN all(l IN linked WHERE l) THEN 'csoporton belüli kapcsolat'
         WHEN size(providers) > 0 THEN 'székhelyszolgáltatás, nem kapcsolat'
         ELSE 'vizsgálandó'
       END AS `értékelés`
ORDER BY `cégek` DESC
```

| cím | cégek | bejegyzett cégek | összefüggő pár | csak közös cím | székhelyszolgáltató | értékelés |
|---|---|---|---|---|---|---|
| 6720 Szeged, Kárász utca 11. | 3 | Alföldi Lakóépítő Kft. „f. a.”, Szék-Ház Kft., Csongrád-Gép Kft. | 0 | 3 | Szék-Ház Kft. | székhelyszolgáltatás, nem kapcsolat |
| 6728 Szeged, Budapesti út 30. | 2 | Tisza Beton Kft., Tisza-Kő Holding Zrt. | 1 | 0 | — | csoporton belüli kapcsolat |
