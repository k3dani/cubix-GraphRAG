# Naiv RAG baseline — válaszok

Beállítások: `run_at=2026-10-01T15:50:08+02:00`, `llm=qwen36`, `embedding=bge-m3`, `chunk_size=800`, `chunk_overlap=100`, `top_k=4`, `temperature=0`

## Q01 — tény

**Kérdés:** Ki a Mecsekkő Beton Kft. ügyvezetője?

A Mecsekkő Beton Kft. ügyvezetője Kocsis Tamás [cegkivonat_mecsekko_beton#01].

**Visszakeresett chunkok:**

- `cegkivonat_mecsekko_beton#01` (Jegyzett tőke … Beszámoló-adatok (2024)), score 0.7255
- `cegkivonat_mecsekko_epitoanyag#01` (Tevékenységi körök … Beszámoló-adatok (2024)), score 0.6789
- `cegkivonat_mecsekko_holding#01` (Jegyzett tőke … Pénzforgalmi számlaszám), score 0.6652
- `level_tolnaker_tulajdonosvaltas#03` ((bevezető)), score 0.6575

## Q02 — tény

**Kérdés:** Mekkora a Dráva Építő Zrt. és a Kapos-Gép Kft. közötti alvállalkozói szerződés nettó értéke, és mi a teljesítési véghatáridő?

A rendelkezésre álló dokumentumok alapján a Dráva Építő Zrt. és a Kapos-Gép Gépészeti Kft. közötti alvállalkozói szerződés nettó értéke **38 millió forint** [jelentes_drava_invest_2024_kiegeszito#02].

A teljesítési véghatáridőre vonatkozóan a szövegkörnyezet nem tartalmazza a pontos dátumot. A dokumentumok csak azt közlik, hogy a jótállás időtartama a sikeres műszaki átadás-átvételtől számított 36 hónap [szerzodes_alvallalkozoi_kapos_gep#02], valamint hogy az e-mailben említett ajánlattevő június 17-ével tudott volna kezdeni [email_balokany_gepeszet_dontes#01], de ez nem egyeztethető össze a beszámolóban szereplő 2024-es teljesítési összeggel és a szerződés aláírásának dátumával (2024. június 10.) egyértelműen, így a véghatáridő a megadott kontextusból nem állapítható meg.

**Visszakeresett chunkok:**

- `szerzodes_alvallalkozoi_kapos_gep#00` (Szerződő felek), score 0.651
- `jelentes_drava_invest_2024_kiegeszito#02` (3. Főbb beszállítók és alvállalkozók (Dráva Építő Zrt., 2024) … 4. Mérlegfordulónap utáni események), score 0.6434
- `szerzodes_alvallalkozoi_kapos_gep#02` (4. Jótállás … 5. Egyéb), score 0.6258
- `email_balokany_gepeszet_dontes#01` ((bevezető)), score 0.6125

## Q03 — tény

**Kérdés:** Hol vannak a Mecsekkő Beton Kft. telephelyei?

A rendelkezésre álló dokumentumok alapján a Mecsekkő Beton Kft. telephelyei a következők:

*   7630 Pécs, Megyeri út 120. (betonüzem) [cegkivonat_mecsekko_beton#00]
*   7700 Mohács, Vasút utca 9. (betonüzem, 2017-03-01-től) [cegkivonat_mecsekko_beton#00]

**Visszakeresett chunkok:**

- `cegkivonat_mecsekko_beton#01` (Jegyzett tőke … Beszámoló-adatok (2024)), score 0.6914
- `level_tolnaker_tulajdonosvaltas#03` ((bevezető)), score 0.6695
- `cegkivonat_mecsekko_beton#00` (Általános adatok … Tevékenységi körök), score 0.6607
- `jelentes_mecsekko_holding_2024#01` (1. A cégcsoport összetétele), score 0.6407

## Q04 — multi-hop

**Kérdés:** Van-e a Mecsekkő-csoport valamelyik tulajdonosának érdekeltsége a Dráva Építő Zrt. alvállalkozóiban?

A rendelkezésre álló dokumentumok alapján nem tudom megválaszolni a kérdést.

A [cegkivonat_drava_epito#00] szerint a Dráva Építő Zrt. egyedüli részvényese a Dráva Invest Kft. [cegkivonat_drava_epito#00]. A [jelentes_drava_invest_2024_kiegeszito#02] felsorolja a Dráva Építő Zrt. főbb alvállalkozóit (Mecsekkő Beton Kft., Kapos-Gép Gépészeti Kft., Dráva Gépészet Kft.), de nem tartalmaz információt ezek tulajdonosi szerkezetéről vagy a Mecsekkő-csoport tagjainak esetleges érdekeltségeiről.

A [jelentes_mecsekko_holding_2024#01] és [jelentes_mecsekko_holding_2024#03] a Mecsekkő-csoport tulajdonosait (Horváth Gábor, Szalai Erika) és leányvállalatait (Mecsekkő Beton Kft., Mecsekkő Építőanyag Kereskedelmi Kft., Tolnaker Kft.) ismerteti, de nem említi, hogy ezek a cégek vagy személyek érdekeltséggel bírnának a Dráva Építő Zrt. egyéb alvállalkozóiban (pl. Kapos-Gép Gépészeti Kft. vagy Dráva Gépészet Kft.). Bár a Mecsekkő Beton Kft. szerepel alvállalkozóként, a kérdés arra irányul, hogy a Mecsekkő-csoport *valamelyik tulajdonosának* van-e érdekeltsége az alvállalkozókban, amihez a szövegkörnyezet nem nyújt információt.

**Visszakeresett chunkok:**

- `jelentes_drava_invest_2024_kiegeszito#02` (3. Főbb beszállítók és alvállalkozók (Dráva Építő Zrt., 2024) … 4. Mérlegfordulónap utáni események), score 0.6881
- `jelentes_mecsekko_holding_2024#03` (4. Kockázatok), score 0.6282
- `jelentes_mecsekko_holding_2024#01` (1. A cégcsoport összetétele), score 0.6035
- `cegkivonat_drava_epito#00` (Általános adatok … Egyedüli részvényes), score 0.5966

## Q05 — multi-hop

**Kérdés:** Hová távozott a Dráva Gépészet Kft. korábbi ügyvezetője, és milyen üzleti kapcsolatban áll az új cége a Dráva-csoporttal?

A rendelkezésre álló dokumentumok alapján a Dráva Gépészet Kft. korábbi ügyvezetője, **Vincze Attila** távozásának pontos helye (hová távozott, azaz melyik új cégnél vagy szervezetnél helyezkedett el) nem derül ki. A tájékoztató levél és a cégkivonat csak azt rögzíti, hogy közös megegyezéssel távozott a cég éléről 2024. március 31-ével [level_drava_gepeszet_ugyvezeto_valtas#00], [cegkivonat_drava_gepeszet#01].

Az új ügyvezető, **Kun Judit** esetében a dokumentumok megadják az üzleti kapcsolatot: ő a **Dráva Invest Kft.** résztulajdonosa és ügyvezetője, amely társaság a Dráva-csoport tagja [level_drava_gepeszet_ugyvezeto_valtas#00], [jelentes_drava_invest_2024_kiegeszito#01]. A Dráva Invest Kft. beszámolójában szerepel, hogy a Dráva Gépészet Kft. a csoporton belül működik, és például a Kaposvári Logisztikai Csarnok épületgépészetét látta el [jelentes_drava_invest_2024_kiegeszito#02].

Összefoglalva:
*   Vincze Attila (korábbi ügyvezető) további sorsa a dokumentumokban nem szerepel.
*   Kun Judit (új ügyvezető) a Dráva-csoport tagja, a Dráva Invest Kft. ügyvezetője és tulajdonosa [level_drava_gepeszet_ugyvezeto_valtas#00], [jelentes_drava_invest_2024_kiegeszito#01].

**Visszakeresett chunkok:**

- `level_drava_gepeszet_ugyvezeto_valtas#00` ((bevezető)), score 0.6619
- `jelentes_drava_invest_2024_kiegeszito#01` (2. Jelentős események), score 0.6403
- `cegkivonat_drava_gepeszet#01` (Vezető tisztségviselő … Beszámoló-adatok), score 0.5998
- `jelentes_drava_invest_2024_kiegeszito#02` (3. Főbb beszállítók és alvállalkozók (Dráva Építő Zrt., 2024) … 4. Mérlegfordulónap utáni események), score 0.5936

## Q06 — multi-hop

**Kérdés:** Ugyanaz a Nagy László a felszámolás alatt álló cég tulajdonosa, aki a Zselic Bútor Kft. ügyvezetője?

Nem, a rendelkezésre álló dokumentumok alapján nem ugyanaz a személyről van szó, mivel a születési dátumaik és lakcímük eltérő.

A Zselic Bútor Kft. ügyvezetője Nagy László, aki 1985. december 1-jén született, és Kaposváron lakik [cegkivonat_zselic_butor#01].

A felszámolás alatt álló Hegyhát Építőipari Kft. 100%-os tulajdonosa szintén Nagy László, de ő 1971. március 8-án született, és Komlón lakik [cegkivonat_hegyhat#01].

**Visszakeresett chunkok:**

- `cegkivonat_zselic_butor#01` (Vezető tisztségviselő … Beszámoló-adatok (2024)), score 0.6375
- `cegkivonat_hegyhat#01` (Jegyzett tőke … Pénzforgalmi számlaszám), score 0.5374
- `cegkivonat_zselic_butor#00` (Általános adatok … Tagok), score 0.525
- `szerzodes_konyveles_zselic_butor#00` (Szerződő felek … 1. A megbízás tárgya), score 0.4806

## Q07 — multi-hop

**Kérdés:** Mekkora követelést jelentett be a Mecsekkő-csoport a felszámolás alatt álló cég ellen, és ki a felszámoló?

A rendelkezésre álló dokumentumok alapján a Mecsekkő-csoport (konkrétan a Mecsekkő Építőanyag Kft.) a Hegyhát Építőipari Kft. ellen **15 218 200 Ft** összegű követelést jelentett be [level_hitelezoi_igenybejelentes_hegyhat#01]. Ez az összeg a 14 605 800 Ft-os tőkekövetelést és a felszámolás kezdő időpontjáig járó 612 400 Ft-os késedelmi kamatot foglalja magában [level_hitelezoi_igenybejelentes_hegyhat#01].

A felszámoló nevét a megadott szövegrészletek **nem tartalmazzák**. A dokumentumok csak azt említik, hogy a nyilvántartási díjat a felszámoló számlájára utalták át, de a felszámoló személyére vonatkozó adat hiányzik [level_hitelezoi_igenybejelentes_hegyhat#01].

**Visszakeresett chunkok:**

- `level_hitelezoi_igenybejelentes_hegyhat#01` (A bejelentett követelés), score 0.656
- `cegkivonat_mecsekko_epitoanyag#01` (Tevékenységi körök … Beszámoló-adatok (2024)), score 0.588
- `jelentes_drava_invest_2024_kiegeszito#02` (3. Főbb beszállítók és alvállalkozók (Dráva Építő Zrt., 2024) … 4. Mérlegfordulónap utáni események), score 0.5789
- `jelentes_mecsekko_holding_2024#03` (4. Kockázatok), score 0.578

## Q08 — multi-hop

**Kérdés:** Ki a Mecsekkő Tolna Kft. jelenlegi ügyvezetője, és milyen más cégben tölt be vezető tisztséget?

A Mecsekkő Tolna Kft. jelenlegi ügyvezetője **Fodor Andrea** [cegkivonat_mecsekko_tolna#02]. Ő egyben a **Mecsekkő Építőanyag Kereskedelmi Kft.** ügyvezetője is [level_tolnaker_tulajdonosvaltas#01].

**Visszakeresett chunkok:**

- `cegkivonat_mecsekko_tolna#01` (Székhely … Tagok), score 0.7053
- `cegkivonat_mecsekko_tolna#02` (Vezető tisztségviselő … Beszámoló-adatok (2024)), score 0.6902
- `level_tolnaker_tulajdonosvaltas#01` ((bevezető)), score 0.6762
- `jelentes_mecsekko_holding_2024#01` (1. A cégcsoport összetétele), score 0.6435

## Q09 — multi-hop

**Kérdés:** Milyen kapcsolat van a Kapos-Gép Kft. és a Hegyhát Építőipari Kft. között?

A rendelkezésre álló dokumentumok alapján a Kapos-Gép Gépészeti Kft. és a Hegyhát Építőipari Kft. közötti kapcsolat az, hogy mindkét cég székhelye ugyanannál a cégnél, a Székhely-Pont Kft.-nél van bejegyezve [cegkivonat_kapos_gep#00].

A két vállalkozás között nincs közvetlen tulajdonosi vagy vezetői átfedés, mivel:
*   A Kapos-Gép Kft. tagjai Somogyi Lajos és Horváth Gábor, ügyvezetői Somogyi Lajos és Vincze Attila [cegkivonat_kapos_gep#01].
*   A Hegyhát Építőipari Kft. tagja és korábbi ügyvezetője Nagy László [cegkivonat_hegyhat#01].

További kapcsolatot (pl. közös tulajdonos, közös ügyvezető, jogutódlás) a megadott szövegrészletek nem tartalmaznak.

**Visszakeresett chunkok:**

- `cegkivonat_kapos_gep#01` (Jegyzett tőke … Pénzforgalmi számlaszám), score 0.5502
- `cegkivonat_hegyhat#01` (Jegyzett tőke … Pénzforgalmi számlaszám), score 0.5474
- `cegkivonat_kapos_gep#00` (Általános adatok … Jegyzett tőke), score 0.5465
- `cegkivonat_hegyhat#00` (Általános adatok … Jegyzett tőke), score 0.5386

## Q10 — multi-hop

**Kérdés:** Kik a Mecsekkő Beton Kft. végső (közvetett) tulajdonosai, és milyen arányban?

A rendelkezésre álló dokumentumok alapján a Mecsekkő Beton Kft. végső (közvetett) tulajdonosai a Mecsekkő Holding Zrt. részvényesei, akik a következő arányban rendelkeznek tulajdonrésszel:

*   **Horváth Gábor:** 60%
*   **Szalai Erika:** 40%

**Indoklás:**
1.  A Mecsekkő Beton Kft. 100%-os tulajdonosa a Mecsekkő Holding Zrt. [cegkivonat_mecsekko_beton#01].
2.  A Mecsekkő Holding Zrt. részvényesei Horváth Gábor (60%) és Szalai Erika (40%) [jelentes_mecsekko_holding_2024#01].

Mivel a Holding 100%-ban birtokolja a Beton Kft.-t, a végső tulajdonosi arányok megegyeznek a Holding részvényesi arányaival.

**Visszakeresett chunkok:**

- `cegkivonat_mecsekko_beton#01` (Jegyzett tőke … Beszámoló-adatok (2024)), score 0.6772
- `jelentes_mecsekko_holding_2024#01` (1. A cégcsoport összetétele), score 0.6649
- `cegkivonat_mecsekko_epitoanyag#01` (Tevékenységi körök … Beszámoló-adatok (2024)), score 0.6374
- `jelentes_mecsekko_holding_2024#02` (2. Gazdálkodás … 3. Akvizíció), score 0.637

## Q11 — globális

**Kérdés:** Milyen cégcsoportok szerepelnek a dokumentumokban, kik irányítják őket, és milyen tevékenységeket fednek le?

A rendelkezésre álló dokumentumok alapján a következő információk állapíthatók meg a cégcsoportokról, irányításról és tevékenységekről:

**1. Mecsekkő Holding Zrt. és kapcsolódó csoport**
*   **Cégcsoport:** A Mecsekkő Holding Zrt. áfacsoport-tag, amelynek csoportazonosító száma 99986045-5-02 [cegkivonat_mecsekko_holding#00]. A dokumentumok nem sorolják fel explicit a csoport többi tagját, de a holding jellegű főtevékenység utal egy alárendeltségi viszonyra [cegkivonat_mecsekko_holding#00].
*   **Irányítás:** A dokumentum kivonata nem tartalmazza a Mecsekkő Holding Zrt. igazgatóságának vagy tagjainak nevét, így az irányító személyek az adott szövegrész alapján nem azonosíthatók [jelentes_mecsekko_holding_200#00], [cegkivonat_mecsekko_holding#00].
*   **Tevékenységek:** A főtevékenység a vagyonkezelés (holding), kiegészítő tevékenységei az üzletvezetés, valamint saját tulajdonú és bérelt ingatlanok bérbeadása és üzemeltetése [cegkivonat_mecsekko_holding#00].

**2. Dunántúli Könyvelő Iroda Kft.**
*   **Cégcsoport:** A dokumentumok nem említenek csoporttagságot vagy csoportazonosító számot a Dunántúli Könyvelő Iroda Kft. esetében [cegkivonat_dunantuli_konyvelo#00].
*   **Irányítás:** A cég 100%-os tulajdonosa és tagja Bakos Mónika [cegkivonat_dunantuli_konyvelo#00]. Ő képviseli a céget a szerződésekben is [szerzodes_konyveles_zselic_butor#00].
*   **Tevékenységek:** A főtevékenység a számviteli, könyvvizsgálói és adószakértői tevékenység [cegkivonat_dunantuli_konyvelo#00]. A szerződés alapján konkrétan kettős könyvvitel vezetése, havi ÁFA- és járulékbevallások, bérszámfejtés (legfeljebb 25 fő), valamint éves beszámoló összeállítása és letétbe helyezése tartozik a szolgáltatásai közé [szerzodes_konyveles_zselic_butor#00].

**3. Zselic Bútor Kft.**
*   **Cégcsoport:** A dokumentumok nem említenek csoporttagságot a Zselic Bútor Kft. esetében [szerzodes_konyveles_zselic_butor#00].
*   **Irányítás:** A céget Nagy László ügyvezető képviseli [szerzodes_konyveles_zselic_butor#00].
*   **Tevékenységek:** A dokumentum nem tartalmazza a Zselic Bútor Kft. hivatalos tevékenységi körét, csak azt, hogy ő a megbízó a könyvelési szolgáltatásban [szerzodes_konyveles_zselic_butor#00].

Összefoglalva, a dokumentumok egy holding csoportot (Mecsekkő) és két egyedi céget (Dunántúli Könyvelő Iroda, Zselic Bútor) említenek, de a holding csoport tényleges tagjainak listája és a Mecsekkő Holding konkrét irányítói hiányoznak a szövegből.

**Visszakeresett chunkok:**

- `jelentes_mecsekko_holding_2024#00` ((bevezető)), score 0.514
- `cegkivonat_mecsekko_holding#00` (Általános adatok … Jegyzett tőke), score 0.4924
- `szerzodes_konyveles_zselic_butor#00` (Szerződő felek … 1. A megbízás tárgya), score 0.4884
- `cegkivonat_dunantuli_konyvelo#00` (Általános adatok … Tagok), score 0.4846

## Q12 — globális

**Kérdés:** Milyen tulajdonosi, vezetői és cégállapot-változások történtek 2024–2025-ben?

A rendelkezésre álló dokumentumok alapján a 2024–2025. időszakban a következő tulajdonosi, vezetői és cégállapot-változások történtek:

**Tulajdonosi változások:**
*   A Mecsekkő Holding Zrt. részvényesei Horváth Gábor (60%) és Szalai Erika (40%) maradtak [jelentes_mecsekko_holding_2024#01].
*   A Mecsekkő Holding Zrt. megvásárolta a Tolnaker Kft. 100%-os üzletrészét Bíró Pétertől és Bíró Petrától [jelentes_mecsekko_holding_2024#02].

**Vezetői változások:**
*   A dokumentumok nem tartalmaznak információt a Mecsekkő Holding Zrt. vagy a leányvállalatai (Mecsekkő Beton Kft., Mecsekkő Építőanyag Kft.) vezetői (ügyvezetői, igazgatósági) összetételének változásáról.
*   A Tolnaker Kft. ügyvezetőjeként a tájékoztatás szerint Bíró Péter maradt a helyén, aki köszönetet mondott a bizalomért a tulajdonosváltás kapcsán [level_tolnaker_tulajdonosvaltas#03].

**Cégállapot-változások:**
*   **Tulajdonosi szerkezet:** A Tolnaker Kft. 2024. november 1-jén került a Mecsekkő-csoportba, így a csoport 2024. december 31-én három, 100%-os tulajdonú leányvállalattal rendelkezett [jelentes_mecsekko_holding_2024#01].
*   **Cégnév:** A Tolnaker Kft. 2025. január 15-étől Mecsekkő Tolna Kft. néven folytatja tevékenységét [jelentes_mecsekko_holding_2024#01].
*   **Áfacsoport:** A Mecsekkő-csoport tagjai (a Tolnaker Kft. kivételével) 2023. január 1-je óta közös áfacsoportot alkotnak. A Tolnaker Kft. 2025. január 1-jétől csatlakozott ehhez az áfacsoportba [jelentes_mecsekko_holding_2024#01].
*   **Üzleti tevékenység:** 2025 második negyedévétől a szekszárdi telephely (korábban Tolnaker Kft., később Mecsekkő Tolna Kft.) kínálata a Mecsekkő Beton Kft. termékeivel bővült [level_tolnaker_tulajdonosvaltas#03].

**Visszakeresett chunkok:**

- `jelentes_mecsekko_holding_2024#00` ((bevezető)), score 0.5525
- `jelentes_mecsekko_holding_2024#02` (2. Gazdálkodás … 3. Akvizíció), score 0.5441
- `level_tolnaker_tulajdonosvaltas#03` ((bevezető)), score 0.5228
- `jelentes_mecsekko_holding_2024#01` (1. A cégcsoport összetétele), score 0.5134

## Q13 — globális

**Kérdés:** Melyek a dokumentumokból kirajzolódó legfontosabb üzleti kockázatok és összeférhetetlenségi jelek?

A rendelkezésre álló dokumentumok alapján a következő üzleti kockázatok és összeférhetetlenségi jelek kirajzolódódnak:

**1. Vevőkoncentráció kockázata**
A Mecsekkő Beton Zrt. árbevételének több mint 30%-a egyetlen vevőtől, a Dráva Építő Zrt.-től származik, ami jelentős függőséget és bevételkiesési kockázatot jelent [jelentes_mecsekko_holding_2024#03].

**2. Behajtási kockázat és értékvesztés**
A Mecsekkő Építőanyag Kft.-nek 14,6 millió Ft-os lejárt követelése van a Hegyhát Építőipari Kft.-vel szemben, amelyre 50%-os értékvesztést számoltak el, és a jelentés napján behajtási eljárás volt folyamatban [jelentes_mecsekko_holding_2024#03].

**3. Pénzügyi és adminisztratív mulasztások a Hegyhát Építőipari Kft.-nél**
A Hegyhát Építőipari Kft. nem fizette ki a könyvelési díjakat (762 000 Ft) a 2024. szeptember és 2025. január közötti időszakban, és nem adta át a beszámoló összeállításához szükséges bizonylatokat határidőre. Ez a mulasztás vezetett a könyvelési szerződés felmondásához [szerzodes_konyveles_hegyhat_felmondas#01].

**4. Cégfelszámolás és követelésállomány hiánya**
A Hegyhát Építőipari Kft.-vel szemben 2025. május 12-én indult felszámolási eljárás. Fontos megjegyezni, hogy a Dráva-csoportnak (Dráva Invest Kft. / Dráva Építő Zrt.) nincs nyitott követelése a Hegyhát Építőipari Kft.-vel szemben, ellentétben a Mecsekkő-csoporttal [jelentes_drava_invest_2024_kiegeszito#02].

**5. Piaci kockázat (keresletcsökkenés)**
A 2025. évi lakásépítési volumen várhatóan 5–10%-kal alacsonyabb lesz a 2024. évinél, ami az építőipari vállalkozások (így a Mecsekkő és a Dráva csoport tagjai) számára csökkenő piaci keresletet jelent [jelentes_mecsekko_holding_2024#03].

**6. Kapcsolati hálózat és csoporton belüli tranzakciók**
A Dráva-csoport jelentős volumenben (412 M Ft) bíz meg csoporton belüli céggel (Dráva Gépészet Kft.) épületgépészeti munkákban, míg a Mecsekkő Beton (884 M Ft) a Dráva Építő Zrt. fő beszállítója. Ez a szoros kapcsolati hálózat növeli a csoporton belüli függőségeket és az átláthatósági kockázatokat [jelentes_drava_invest_2024_kiegeszito#02].

**Visszakeresett chunkok:**

- `jelentes_mecsekko_holding_2024#03` (4. Kockázatok), score 0.4776
- `jelentes_mecsekko_holding_2024#00` ((bevezető)), score 0.4684
- `jelentes_drava_invest_2024_kiegeszito#02` (3. Főbb beszállítók és alvállalkozók (Dráva Építő Zrt., 2024) … 4. Mérlegfordulónap utáni események), score 0.4621
- `szerzodes_konyveles_hegyhat_felmondas#01` (Tárgy: a 2019. február 1-jén kötött könyvelési megbízási szerződés felmondása), score 0.4389

## Q14 — globális

**Kérdés:** Melyik cég áll üzleti kapcsolatban a legtöbb másik céggel a korpuszban?

A rendelkezésre álló dokumentumok alapján a **Mecsekkő Holding Zrt.** (és közvetve a Mecsekkő-csoport) áll üzleti kapcsolatban a legtöbb másik céggel.

Az alábbiakban részletezem a kapcsolatok számát a kontextus alapján:

1.  **Mecsekkő Holding Zrt. / Mecsekkő-csoport:**
    *   Tulajdonosi kapcsolat: Horváth Gábor és Szalai Erika [jelentes_mecsekko_holding_2024#01].
    *   Leányvállalati kapcsolat: Mecsekkő Beton Kft., Mecsekkő Építőanyag Kereskedelmi Kft., Tolnaker Kft. [jelentes_mecsekko_holding_2024#01].
    *   Áfacsoportos kapcsolat: A csoporttagok közös áfacsoportot alkotnak [jelentes_mecsekko_holding_2024#01].
    *   Beszállítói/vevői kapcsolat: A Mecsekkő Beton Kft. beszállítója a Dráva Építő Zrt.-nek (Dráva-csoport) [jelentes_drava_invest_2024_kiegeszito#02].
    *   Összesen: Legalább 5 másik jogi személyrel (tulajdonosok, leányvállalatok, Dráva-csoport) áll közvetlen üzleti vagy tulajdonosi kapcsolatban.

2.  **Dráva Invest Kft. / Dráva-csoport:**
    *   Beszállítói/vevői kapcsolat: Mecsekkő Beton Kft., Kapos-Gép Gépészeti Kft., Dráva Gépészet Kft. (csoporton belül), Hegyhát Építőipari Kft. (korábbi alvállalkozó) [jelentes_drava_invest_2024_kiegeszito#02].
    *   Összesen: Legalább 4 másik céggel áll kapcsolatban.

3.  **Kapos-Gép Gépészeti Kft.:**
    *   Üzleti kapcsolat: Dráva Építő Zrt. (alvállalkozó) [jelentes_drava_invest_2024_kiegeszito#02], valamint e-mailben említett ajánlattevőként [email_balokany_gepeszet_dontes#01].
    *   Összesen: 1-2 céggel áll kapcsolatban.

4.  **Zselic Bútor Kft.:**
    *   Üzleti kapcsolat: Dunántúli Könyvelő Iroda Kft. (könyvelési szolgáltatás) [szerzodes_konyveles_zselic_butor#00].
    *   Összesen: 1 céggel áll kapcsolatban.

5.  **Dunántúli Könyvelő Iroda Kft.:**
    *   Üzleti kapcsolat: Zselic Bútor Kft. (megbízó) [szerzodes_konyveles_zselic_butor#00].
    *   Összesen: 1 céggel áll kapcsolatban.

A Mecsekkő-csoport tehát a legtöbb más céggel (tulajdonosi, leányvállalati, áfacsoportos és beszállítói/vevői viszonyban) áll fennálló kapcsolattal a megadott korpuszban.

**Visszakeresett chunkok:**

- `jelentes_mecsekko_holding_2024#01` (1. A cégcsoport összetétele), score 0.4099
- `jelentes_drava_invest_2024_kiegeszito#02` (3. Főbb beszállítók és alvállalkozók (Dráva Építő Zrt., 2024) … 4. Mérlegfordulónap utáni események), score 0.4045
- `email_balokany_gepeszet_dontes#01` ((bevezető)), score 0.3914
- `szerzodes_konyveles_zselic_butor#00` (Szerződő felek … 1. A megbízás tárgya), score 0.3908
