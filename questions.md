# Kérdések

A kérdéseket a GraphRAG-alkalmasság eldöntésére állítottuk össze. Három típusuk van:

- **tény**: a válasz egyetlen dokumentum egyetlen helyén megvan. Ez a kontrollcsoport, ezen a naiv RAG-nek is jól kell teljesítenie.
- **multi-hop**: legalább két dokumentum tényeit kell összekötni. Az irányt mondó entitás gyakran nem szerepel a kérdésben.
- **globális**: a választ a korpusz egésze vagy nagy része adja, sehol nincs egyben leírva.

Az „elvárt válasz” a korpuszból kézzel levezetett helyes válasz. A „források” a válaszhoz szükséges dokumentumok.

| # | Típus | Kérdés |
|---|---|---|
| Q01 | tény | Ki a Mecsekkő Beton Kft. ügyvezetője? |
| Q02 | tény | Mekkora a Dráva Építő Zrt. és a Kapos-Gép Kft. közötti alvállalkozói szerződés nettó értéke, és mi a teljesítési véghatáridő? |
| Q03 | tény | Hol vannak a Mecsekkő Beton Kft. telephelyei? |
| Q04 | multi-hop | Van-e a Mecsekkő-csoport valamelyik tulajdonosának érdekeltsége a Dráva Építő Zrt. alvállalkozóiban? |
| Q05 | multi-hop | Hová távozott a Dráva Gépészet Kft. korábbi ügyvezetője, és milyen üzleti kapcsolatban áll az új cége a Dráva-csoporttal? |
| Q06 | multi-hop | Ugyanaz a Nagy László a felszámolás alatt álló cég tulajdonosa, aki a Zselic Bútor Kft. ügyvezetője? |
| Q07 | multi-hop | Mekkora követelést jelentett be a Mecsekkő-csoport a felszámolás alatt álló cég ellen, és ki a felszámoló? |
| Q08 | multi-hop | Ki a Mecsekkő Tolna Kft. jelenlegi ügyvezetője, és milyen más cégben tölt be vezető tisztséget? |
| Q09 | multi-hop | Milyen kapcsolat van a Kapos-Gép Kft. és a Hegyhát Építőipari Kft. között? |
| Q10 | multi-hop | Kik a Mecsekkő Beton Kft. végső (közvetett) tulajdonosai, és milyen arányban? |
| Q11 | globális | Milyen cégcsoportok szerepelnek a dokumentumokban, kik irányítják őket, és milyen tevékenységeket fednek le? |
| Q12 | globális | Milyen tulajdonosi, vezetői és cégállapot-változások történtek 2024–2025-ben? |
| Q13 | globális | Melyek a dokumentumokból kirajzolódó legfontosabb üzleti kockázatok és összeférhetetlenségi jelek? |
| Q14 | globális | Melyik cég áll üzleti kapcsolatban a legtöbb másik céggel a korpuszban? |

## Elvárt válaszok

**Q01 — tény.** Kocsis Tamás, 2016-09-01 óta.
Forrás: `cegkivonat_mecsekko_beton`.

**Q02 — tény.** Nettó 96 500 000 Ft (átalányár, fordított ÁFA), a véghatáridő 2025-06-30.
Forrás: `szerzodes_alvallalkozoi_kapos_gep`.

**Q03 — tény.** 7630 Pécs, Megyeri út 120. és 7700 Mohács, Vasút utca 9. (mindkettő betonüzem).
Forrás: `cegkivonat_mecsekko_beton`.

**Q04 — multi-hop.** Igen. Horváth Gábor a Mecsekkő Holding 60%-os részvényese, és 2021-06-15 óta 30%-os tagja a
Kapos-Gép Kft.-nek. A Kapos-Gép 2024-06-10 óta a Dráva Építő alvállalkozója a Balokány B–C épületgépészetében
(96,5 M Ft). Ráadásul a Mecsekkő Beton legnagyobb vevője maga a Dráva Építő.
Források: `jelentes_mecsekko_holding_2024` / `cegkivonat_mecsekko_holding`, `cegkivonat_kapos_gep`,
`szerzodes_alvallalkozoi_kapos_gep`.

**Q05 — multi-hop.** Vincze Attila 2024-03-31-én távozott. 2024-04-15-től a Kapos-Gép Kft. ügyvezetője. A
Kapos-Gép 2024-06-10-én alvállalkozói szerződést kötött a Dráva Építővel (Balokány B–C gépészet, 96,5 M Ft). A
munkát azért kapta meg, mert a Dráva Gépészetnél Vincze távozása után kapacitáshiány lett: a szerelők egy része vele
ment.
Források: `cegkivonat_drava_gepeszet`, `cegkivonat_kapos_gep`, `email_balokany_gepeszet_dontes`,
`szerzodes_alvallalkozoi_kapos_gep`.

**Q06 — multi-hop.** Nem, két különböző személyről van szó.
- A Hegyhát Építőipari Kft. „f. a.” tulajdonosa Nagy László (szül. 1971-03-08, anyja neve Kiss Margit, Komló).
- A Zselic Bútor ügyvezetője Nagy László (szül. 1985-12-01, anyja neve Molnár Judit, Kaposvár).

Források: `cegkivonat_hegyhat`, `cegkivonat_zselic_butor`.

**Q07 — multi-hop.** A Mecsekkő Építőanyag Kft. jelentette be a követelést. Összege 15 218 200 Ft: 14 605 800 Ft
tőke és 612 400 Ft késedelmi kamat. A felszámoló a Pannon-Lex Felszámoló Kft., ügyszám Fpk.02-25-000318.
Források: `level_hitelezoi_igenybejelentes_hegyhat`, `cegkivonat_mecsekko_epitoanyag` vagy
`jelentes_mecsekko_holding_2024` (csoporttagság).

**Q08 — multi-hop.** Fodor Andrea, 2025-02-01 óta. 2018-01-01 óta a Mecsekkő Építőanyag Kereskedelmi Kft.
ügyvezetője is.
Források: `cegkivonat_mecsekko_tolna`, `cegkivonat_mecsekko_epitoanyag`.

**Q09 — multi-hop.** Csak a székhelyük azonos: 7621 Pécs, Széchenyi tér 4. Ez a Székhely-Pont Kft.
székhelyszolgáltatási címe, ahol 41 cég székhelye van. Közös tulajdonos vagy vezető nincs, tehát érdemi kapcsolat
sincs. Ez csapda: a közös cím hamis kapcsolatot sugall.
Források: `cegkivonat_kapos_gep`, `cegkivonat_hegyhat`, `cegkivonat_szekhely_pont`.

**Q10 — multi-hop.** Horváth Gábor 60% és Szalai Erika 40%, a Mecsekkő Holding Zrt.-n keresztül, amely 100%-os tag.
Források: `cegkivonat_mecsekko_beton`, `jelentes_mecsekko_holding_2024`.

**Q11 — globális.**
- **Mecsekkő-csoport** (Horváth Gábor, Szalai Erika): betongyártás, építőanyag-kereskedelem; Pécs, Mohács, Komló,
  Szigetvár, Szekszárd.
- **Dráva-csoport** (Németh Zoltán, Kun Judit): építőipari fővállalkozás és épületgépészet.
- **Független cégek:** Kapos-Gép (gépészet), Hegyhát (építőipar, felszámolás alatt), Zselic Bútor (bútorgyártás),
  valamint két szolgáltató: Dunántúli Könyvelő Iroda és Székhely-Pont.

**Q12 — globális.**
- 2024-03-31: Vincze Attila távozik a Dráva Gépészettől.
- 2024-04-01: Kun Judit lesz a Dráva Gépészet ügyvezetője.
- 2024-04-15: Vincze Attila a Kapos-Gép ügyvezetője lesz.
- 2024-11-01: a Mecsekkő Holding megveszi a Tolnakert (a Bíró Pétertől és Bíró Petrától vásárolt üzletrész).
- 2025-01-01: a Tolnaker belép az áfacsoportba.
- 2025-01-15: névváltozás Mecsekkő Tolna Kft.-re, tőkeemelés 20 M Ft-ra.
- 2025-02-01: Fodor Andrea váltja Bíró Pétert az ügyvezetésben.
- 2025-04-30: megszűnik a Dunántúli Könyvelő és a Hegyhát könyvelési szerződése.
- 2025-05-12: a Hegyhát felszámolása, Nagy László ügyvezetői jogköre megszűnik.

**Q13 — globális.**
- A Hegyhát fizetésképtelensége (15,2 M Ft bejelentett követelés, 50%-os értékvesztés).
- Összeférhetetlenség: Horváth Gábor a Mecsekkő-tulajdonosa és a Kapos-Gép résztulajdonosa is; a Kapos-Gép a
  Mecsekkő Beton legnagyobb vevőjének alvállalkozója.
- A Mecsekkő Beton vevőkoncentrációja: a Dráva Építő adja az árbevétel 31%-át.
- A Dráva Gépészet kapacitás- és árbevétel-vesztése (−35%, veszteséges év).
- A székhelyszolgáltatói cím hamis kapcsolatot sugall.

**Q14 — globális.** A Dráva Építő Zrt. A szerződéses és tulajdonosi kapcsolatai: Dráva Invest (tulajdonos), Mecsekkő
Beton (beszállító), Kapos-Gép (alvállalkozó), Dráva Gépészet (csoporton belüli alvállalkozó), Hegyhát (korábbi
alvállalkozó).
