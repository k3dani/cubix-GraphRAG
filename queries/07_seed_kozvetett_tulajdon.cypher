// 7. Seed, változó hosszú út: kik a cég (közvetett) tulajdonosai, és mekkora effektív hányaddal?
// A tulajdonosi lánc (OWNS*1..3) mentén a hányadok szorzata; csak a ma is hatályos élek számítanak.
// A Q10 seed-beli párja.
// params: {"reg_no": "06-09-912305"}
MATCH path = (owner)-[os:OWNS*1..3]->(c:Company {reg_no: $reg_no})
WHERE all(o IN os WHERE o.valid_to IS NULL)
RETURN c.name AS `cég`,
       owner.name AS tulajdonos,
       owner:Person AS `természetes személy`,
       reduce(s = '', n IN nodes(path) | s + CASE WHEN s = '' THEN '' ELSE ' → ' END + n.name) AS `lánc`,
       length(path) AS hop,
       round(reduce(s = 1.0, o IN os | s * o.share_pct / 100.0) * 100, 1) AS `effektív %`
ORDER BY `effektív %` DESC, hop
