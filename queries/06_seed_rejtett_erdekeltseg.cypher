// 6. Seed, 3 hop: kivel szerződnek egy személy érdekeltségei, és a partner a csoportjával is szerződik?
// Személy -OWNS-> cég -PARTY_TO-> szerződés <-PARTY_TO- partner. Ez a Q04 seed-beli párja: a naiv RAG
// azért bukott, mert a híd-cég neve nincs a kérdésben; a gráfban ez egyetlen bejárás.
// params: {"person_id": "varga-bela-1961-05-14"}
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
