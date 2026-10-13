// 8. Seed, aggregáló: közös székhely — csoporton belüli kapcsolat, vagy csak székhelyszolgáltatás?
// Címenként a bejegyzett cégek. Egy cégpár akkor függ össze, ha van közös gazdájuk tulajdonosi vagy
// vezetői szálon (vagy az egyik birtokolja a másikat). A Q09 seed-beli párja: a közös cím önmagában
// nem kapcsolat.
// params: {"dataset": "seed"}
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
