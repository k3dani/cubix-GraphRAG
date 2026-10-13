# GraphRAG kurzusprojekt — magyar cégháló

Egyetlen rendszer, amely hétről hétre épül a Cubix GraphRAG-kurzus alatt. A kiindulópont egy naiv RAG baseline, a cél
egy mért GraphRAG-rendszer. A modellek saját infrastruktúrán futnak, fizetős API nélkül. Bármilyen
OpenAI-kompatibilis végponttal futtatható (vLLM, Ollama, LM Studio, OpenAI).

## Korpusz

**25 magyar nyelvű, szintetikus üzleti dokumentum** (`corpus/`, Markdown) két kitalált dél-dunántúli cégcsoportról
és környezetükről. A dokumentumtípusok:

| Típus | Db | Példa |
|---|---|---|
| Cégkivonat (a cégjegyzék mintájára, előzményekkel) | 12 | `cegkivonat_kapos_gep.md` |
| Szerződés / felmondás | 4 | `szerzodes_alvallalkozoi_kapos_gep.md` |
| Levél / e-mail | 5 | `email_balokany_gepeszet_dontes.md` |
| Számla | 2 | `szamla_mecsekko_beton_MB-2025-0388.md` |
| Éves jelentés / kiegészítő melléklet | 2 | `jelentes_mecsekko_holding_2024.md` |

**Honnan van?** Kézzel írtuk, egy dokumentumkezelő rendszer (DocAI) valós iratainak mintájára: cégkivonat,
partnerlevelezés, számla. A cégek, személyek és azonosítók kitaláltak. Az adószámok és bankszámlaszámok formailag
érvényesek, de a `999…` / `998…` prefix jelzi, hogy nem valósak. **Miért nem valós cégadat?** A valós cégadat
egyenként nyilvános, de egy céghalmaz együtt egy vállalkozás partnerhálóját tükrözi, és magánszemélyek adatait
is tartalmazza. Ezt publikus repóba nem tesszük.

**Miért alkalmas GraphRAG-ra?** A korpuszt az összekötöttségre terveztük: ugyanazok a cégek és személyek
3–8 dokumentumban is előfordulnak. Beépített helyzetek:

- **Rejtett érdekeltség:** az egyik csoport tulajdonosa 30%-os tag egy olyan cégben, amely a másik csoport
  alvállalkozója. Egyetlen dokumentum sem mondja ki.
- **Vezető átigazolása:** a volt ügyvezető a konkurenshez megy, és a konkurens megkapja a korábbi munkáltató
  csoportjának megbízását.
- **Akvizíció, névváltozás, áfacsoport-csatlakozás:** ugyanaz a cég két néven és két adószámmal szerepel.
- **Névrokonok:** két különböző Nagy László, a felszámolt cég tulajdonosa és egy bútorgyár ügyvezetője.
- **Hamis kapcsolat:** két független cég székhelye egy székhelyszolgáltató címén van.
- **Felszámolás** követelés-bejelentéssel.

**A próbákon kiderült:**
- A dokumentumok rövidek: a medián 1 300 karakter, a `##` szakaszoké mindössze ~150.
- A cégkivonat szakaszai (Tagok, Vezető tisztségviselők) önmagukban nem mondják meg, melyik cégről szólnak.
  Ez a chunkolásnál fontos lett.

## Kérdések

A [`questions.md`](questions.md) 14 kérdést tartalmaz, mindegyikhez elvárt választ és forrásokat. A típusok:
3 **tény** (kontroll), 7 **multi-hop** (2–4 dokumentum összekötése), 4 **globális** (a korpusz egészére vonatkozó
kérdés).

## Mit építettünk — 1. hét: naiv RAG

```
corpus/*.md ─▶ DirectoryLoader ─▶ RecursiveCharacterTextSplitter ─▶ bge-m3 embedding ─▶ Qdrant
                (forrás-metaadat)    (800 / 100, címmel prefixelve)

kérdés ─▶ bge-m3 ─▶ Qdrant top-4 (koszinusz) ─▶ prompt [chunk-id]-kel ─▶ Qwen3.6 ─▶ válasz + források
```

| Komponens | Választás | Indoklás |
|---|---|---|
| Betöltés | LangChain `DirectoryLoader` + `TextLoader` | A korpusz Markdown. Metaadat: `source`, `doc_id`, `title`, `section`, `chunk_id`, `start_index` |
| Chunkolás | 800 karakter, 100 overlap, szeparátorok: `\n## ` → bekezdés → sor → mondat | Lásd lent |
| Embedding | `BAAI/bge-m3` (1024 dim, koszinusz) | Többnyelvű modell, jó magyar teljesítménnyel. Saját vLLM-en fut |
| Vektor-DB | Qdrant (Docker) | A kurzus referencia-stackje. A pontazonosító a `chunk_id` UUID5-je, így az újraindexelés determinisztikus |
| LLM | `Qwen3.6-35B-A3B` (vLLM), `temperature=0`, thinking kikapcsolva | Saját infrastruktúra, ingyenes. Thinking nélkül a válasz rövidebb és reprodukálhatóbb |
| Top-k | 4 | 4 × ~700 karakter ≈ 2–3 dokumentumnyi kontextus. Ez szándékosan „naiv”: nem tömjük tele a kontextust |
| Forrásmegjelölés | A prompt `[chunk_id]` hivatkozást kér minden állítás után, a kimenet a chunkokat score-ral és szakasszal is listázza | DoD |

**Miért 800/100?**
- A szakaszok túl kicsik (~150 karakter) ahhoz, hogy önálló chunkok legyenek. Egy „Tagok” szakasz egymagában
  zajos találat lenne.
- A teljes dokumentum (~1 300 karakter) viszont több témát kever.
- 800 karakternél egy dokumentum 2–3 chunkra esik szét, és a chunk több egymás utáni cégkivonat-rovatot fog át.
  Az eredmény: 62 chunk, medián 673 karakter.
- A 100 karakteres (~12%-os) overlap csak akkor számít, ha a vágás szakaszon belül történik. Ilyenkor a következő
  chunk magával viszi az előző sorokat, a szakaszcímmel együtt.
- **Minden chunk elejére bekerül a dokumentum címe** („Dokumentum: Cégkivonat — Kapos-Gép Gépészeti Kft.”).
  Enélkül egy „Vezető tisztségviselők” chunkból nem derülne ki, melyik cégről szól.

## Futtatás

Előfeltétel: [uv](https://docs.astral.sh/uv/), Docker, valamint egy OpenAI-kompatibilis chat- és embedding-végpont.
A 2. heti gráf-lépésekhez modell-végpont nem kell, csak Docker.

```bash
cp .env.example .env          # végpontok, modellnevek, Neo4j-jelszó
docker compose up -d --wait   # Qdrant: localhost:6333 · Neo4j: localhost:7474 (Browser), :7687 (Bolt)
uv sync

# 1. hét — naiv RAG
uv run ingest                 # korpusz → chunkok → Qdrant (a kollekciót újraépíti)
uv run ask "Ki a Mecsekkő Beton Kft. ügyvezetője?"
uv run baseline               # mind a 14 kérdés → baseline/answers.md + answers.jsonl

# 2. hét — gráf
uv run load-docs              # korpusz → Document / Section / Chunk a Neo4j-ben
uv run load-seed              # kitalált seed-cégháló a séma szerint
uv run graph-queries          # queries/*.cypher → queries/results.md
```

Az `.env.example` alapértelmezésként `bge-m3`-at (1024 dim) vár. Ha más embedding-modellt használsz, állítsd be az
`EMBEDDING_DIMENSION`-t. Nem Qwen3 LLM-nél pedig a `LLM_DISABLE_THINKING=false` kell.

A Neo4j Browser a <http://localhost:7474> címen érhető el. A felhasználó `neo4j`, a jelszó a `.env`
`NEO4J_PASSWORD` értéke. Egy `queries/*.cypher` fájl ott is lefuttatható: előtte a fájl `// params:` sorait
`:params {...}` formában kell megadni. Ha tiszta lappal szeretnél indulni: `docker compose down -v`, ez a
Neo4j-kötetet is törli. A `NEO4J_PASSWORD` csak az első indításkor érvényesül, későbbi módosítás után
ugyanez a `down -v` kell.

## Baseline eredmény

A válaszok javítás nélkül a [`baseline/answers.md`](baseline/answers.md) fájlban vannak; gépi formában a
`baseline/answers.jsonl`-ben, a futás beállításaival együtt. Az értékelés kézi, az elvárt válaszokkal összevetve.

| # | Típus | Eredmény | Mi történt |
|---|---|---|---|
| Q01 | tény | ✅ | |
| Q02 | tény | ❌ | 38 M Ft-ot mondott 96,5 helyett: a csoport mellékletéből a *2024. évi teljesítést* vette. A szerződés `#01` chunkja, amelyben a díj és a határidő is benne van, nem került a top-4 közé (a `#00` és a `#02` igen) |
| Q03 | tény | ✅ | |
| Q04 | multi-hop | ❌ | „Nem tudom.” A Kapos-Gép cégkivonata, amelyből kiderül Horváth Gábor 30%-a, nem került elő, mert a kérdésben nem szerepel a Kapos-Gép neve |
| Q05 | multi-hop | ❌ | „Nem derül ki, hová távozott.” A Kapos-Gép cégkivonata itt sem került elő |
| Q06 | multi-hop | ✅ | Mindkét cégkivonat előkerült, a születési adatok alapján jól szétválasztotta a két személyt |
| Q07 | multi-hop | ◐ | Az összeg jó, de „a felszámoló neve nem szerepel”. Ugyanannak a levélnek a fejléce (`#00`) tartalmazza, de az nem jött vissza |
| Q08 | multi-hop | ✅ | |
| Q09 | multi-hop | ✅ | A közös székhelyet megtalálta, és nem állított tulajdonosi kapcsolatot |
| Q10 | multi-hop | ✅ | |
| Q11 | globális | ❌ | A Dráva-csoport kimaradt, és szerinte „a holding irányítói nem ismertek” |
| Q12 | globális | ❌ | Csak a Mecsekkő-eseményeket sorolta fel. Kimaradt a vezetőváltás, az átigazolás és a felszámolás, és tévesen azt állította, hogy Bíró Péter marad az ügyvezető |
| Q13 | globális | ◐ | A vevőkoncentrációt és a Hegyhát-kockázatot megtalálta. Az érdekeltségi összefonódás kimaradt, helyette egy nem létező „összeférhetetlenséget” konstruált |
| Q14 | globális | ❌ | A Mecsekkő-csoportot nevezte meg a Dráva Építő helyett, mert csak abból a 4 chunkból számolt, amit látott |

**Összesítés:** tény 2/3 · multi-hop 4/7 (+1 részben) · globális 0/4 (+1 részben).

**Hol bukott a baseline?**
- **Globális kérdések.** Mind a négy elbukott, ami várható: a top-4 chunk a 62-ből a korpusz ~6%-a, a modell pedig
  ebből a szeletből általánosít. Ennél rosszabb, hogy *magabiztosan* teszi („a Mecsekkő-csoport áll a legtöbb
  kapcsolatban”), és nem jelzi, hogy csak részleges képet lát.
- **Multi-hop kérdések.** Pontosan ott buktak el, ahol a *híd-entitás nem szerepel a kérdésben*. A Q04-ben és a
  Q05-ben a kérdés a Dráva-csoportról és a Mecsekkő tulajdonosáról szól, a választ viszont egy harmadik cég
  (Kapos-Gép) cégkivonata hordozza. A hasonlósági keresés ezt nem találja meg, mert szemantikailag nem hasonlít a
  kérdésre. Ahol mindkét entitás neve szerepelt a kérdésben (Q06, Q08–Q10), ott a naiv RAG is boldogult.
- **Tényes kérdés is elbukott a chunkolás miatt.** A Q02-ben és a Q07-ben ugyanannak a dokumentumnak egy másik
  chunkja hordozta a hiányzó tényt. A Q02-ben ráadásul egy versengő szám (a 2024. évi teljesítés) helyes válasznak
  tűnt.

Ezt a hiányt célozza a következő hetekben a gráf: az entitás–kapcsolat bejárás az első problémára, a
közösség-összefoglalók a másodikra.

## 2. hét: gráf és séma

```
corpus/*.md ─▶ split_documents() ─▶ (:Document)─[:CONTAINS]─▶(:Chunk)─[:NEXT_CHUNK]─▶(:Chunk) …
               (ugyanaz, mint a      └─[:HAS_SECTION]─▶(:Section)◀─[:IN_SECTION]─┘
                Qdrant-indexé)

seed.py ─▶ sémaellenőrzés ─▶ MERGE ─▶ (:Person)─[:OWNS]─▶(:Company)─[:PARTY_TO]─▶(:Contract) …

queries/*.cypher ─▶ uv run graph-queries ─▶ queries/results.md
```

| Komponens | Választás | Indoklás |
|---|---|---|
| Gráf-DB | Neo4j 2026.09 Community, Docker | Ingyenes, és a kurzus referencia-stackje. A 4. héten a GDS Community plugin hozza a Leident. Csak `127.0.0.1`-en hallgat. Named volume-ba ír, mert a bind mount a konténer uid-jára állítaná át a host-könyvtár tulajdonosát |
| Driver | hivatalos `neo4j` Python-driver | Minden érték paraméterként megy (`$rows`, `$person_id`, `$reg_no`). Címke és éltípus csak a séma fix szótárából kerül a lekérdezés szövegébe, adatból soha |
| Séma | [`docs/schema.md`](docs/schema.md) | 11 szakterületi és 3 dokumentum-címke, 18 szakterületi éltípus. Lent röviden |
| Seed | [`seed.py`](src/graphrag_course/seed.py): 19 csomópont, 33 él | Kitalált, de a korpusz csapdáit hordozza. Lent részletesen |
| Dokumentumgráf | 25 `Document`, 163 `Section`, 62 `Chunk` | Extrakció nélkül, a korpusz szerkezetéből. A `chunk_id` megegyezik a Qdrant-pontokéval |
| Lekérdezések | [`queries/*.cypher`](queries/) → [`queries/results.md`](queries/results.md) | 8 lekérdezés, kimenettel. Egyenként a Neo4j Browserbe is bemásolhatók |

### A séma röviden

A teljes leírás, irányokkal és indoklással: [`docs/schema.md`](docs/schema.md). A fő döntések:

- **Szakterületi fogalmak, nem PERSON/ORG/GEO.** Csomópont a cég, a személy, a cím, a szerződés, a projekt, a
  számla, a felszámolási eljárás, az áfacsoport, a tevékenység (TEÁOR), a bankszámla és az éves beszámoló-adat.
  Az élek a cégjegyzék és az üzleti iratok nyelvét követik: `OWNS`, `OFFICER_OF`, `REGISTERED_AT`,
  `SEAT_PROVIDER_FOR`, `PARTY_TO {role}`, `FILED_CLAIM` és így tovább.
- **A cég kulcsa a cégjegyzékszám, nem a név és nem az adószám.** A Tolnaker → Mecsekkő Tolna esetben két név és két
  adószám tartozik ugyanahhoz a céghez. A **személy kulcsa név + születési dátum**, mert a korpuszban két Nagy
  László van.
- **Az idő az élen van** (`valid_from`/`valid_to`). Ha ugyanaz a tag két időszakban más hányaddal szerepel, az két
  él. Somogyi Lajos 100%-a és 70%-a ilyen.
- **A szerződés csomópont, nem él.** Felek, projekt és számlák kapcsolódnak hozzá, és saját életciklusa van. A
  projekt is csomópont, mert a Q04 lényege, hogy ugyanazon a projekten két érintett cég is dolgozik.
- **Nem lesz csomópont a cégcsoport,** mert az `OWNS`-fából levezethető, és a 4. heti közösségdetekciónak kell
  kiadnia. **Nem kerül a gráfba a lakcím** (adatminimalizálás).

### Seed: a Tisza-csoport

Szegedi mini-cégháló: 4 személy, 6 cég, 3 cím, 2 szerződés, 1 projekt, 1 számla, 1 felszámolási eljárás és 1
áfacsoport. Szándékosan független a korpusztól, mert a 3. heti kinyerés a korpusz cégeit tölti majd a gráfba:
- más a megye (cégjegyzékszám `06-…`);
- mások a nevek;
- mások az azonosítók. Formailag érvényesek, és a `999…` prefix itt is a kitalált adatot jelzi.

A szerkezete viszont a korpusz csapdáit ismétli, így a lekérdezéseket már most ki lehet próbálni rajta:

| Seed | A korpuszbeli párja | Mit tesztel |
|---|---|---|
| Varga Béla a Tisza-Kő Holding 65%-os tulajdonosa, és 25%-os tag a Csongrád-Gépben. A Csongrád-Gép a Maros Építő alvállalkozója, a holding betongyára ugyanannak a projektnek a beszállítója | Horváth Gábor – Kapos-Gép – Dráva Építő (Q04) | rejtett érdekeltség |
| Pap Kristóf a Tisza Beton ügyvezetője volt, majd saját céget alapított | Vincze Attila (Q05) | átigazolt vezető |
| Kárász utca 11.: a Csongrád-Gép, az Alföldi Lakóépítő és a szolgáltató Szék-Ház székhelye | Széchenyi tér 4. (Q09) | hamis kapcsolat |
| Budapesti út 30.: a holding és a betongyára | — | valódi közös cím (kontroll) |
| Tisza-Kő Holding → Tisza Beton, 100% | Mecsekkő Holding → Mecsekkő Beton (Q10) | közvetett tulajdon |
| Pap Kristóf a Csongrád-Gépben 2022-ig 100%, azóta 75% | Somogyi Lajos (Kapos-Gép) | időben változó tulajdon |
| Az Alföldi Lakóépítő felszámolás alatt áll, a Tisza Beton hitelezőként jelentkezik | Hegyhát (Q07) | felszámolás |

**Idempotencia.** A seed és a dokumentumgráf is MERGE-dzsel töltődik, minden kulcson uniqueness constraint van.

- **Újrafuttatás:** a mért második futás után a gráf 269 → 269 csomópont és 611 → 611 él maradt.
- **Szinkron:** ami a forrásból kikerül, az a gráfból is törlődik. Próba: 400-as chunkmérettel 126 chunk lett,
  800-zal visszatöltve 62, maradvány nélkül. Egy seed-csomópontot kivéve az élei is törlődtek.
- **Sémaellenőrzés:** a betöltő elutasítja a sémasértő élet, például `(:Project)-[:OWNS]->(:Company)`.

### Cypher a saját adaton

A 8 lekérdezés teljes szövege és kimenete: [`queries/results.md`](queries/results.md).

| # | Kérdés | Eredmény |
|---|---|---|
| 1 | Dokumentumtípusonkénti áttekintés (aggregáló) | 12 cégkivonat, 4 szerződés, 4 levél, 2 jelentés, 2 számla, 1 e-mail. Átlagosan 2–3,5 chunk/dokumentum. A `NEXT_CHUNK`-lánc mind a 25 dokumentumban ép |
| 2 | Hány chunk tartozik a leghosszabb dokumentumhoz? | 4: a Mecsekkő Holding igazgatósági jelentése (2 234 karakter) |
| 3 | Legrövidebb dokumentumok, üres vagy szemét chunkok | Üres chunk nincs. Két gyanús chunk van, lásd lent |
| 4 | Mely szakaszokat vágta ketté a chunkolás? | 7 szakasz. Hatból a fejléces dokumentumok (levél, számla, e-mail) `##` nélküli törzse, egy pedig a felmondólevél 948 karakteres indoklása, amely egymaga hosszabb a chunkméretnél. A többi 137 `##`-szakasz egyben maradt |
| 5 | Mit hozott volna a `NEXT_CHUNK`-szomszédság a baseline-nak? | A Q02-t és a Q07-et megmentené, a Q04-et nem |
| 6 | Seed, 3 hop: Varga Béla érdekeltségei kivel szerződnek? | A Csongrád-Gépen át a Maros Építővel, amellyel a holding betongyára is szerződik |
| 7 | Seed, változó hosszú út: a Tisza Beton közvetett tulajdonosai | Holding 100%, Varga Béla 65%, Lakatos Éva 35% (a lánc mentén szorzott hányad) |
| 8 | Seed, aggregáló: közös székhely, kapcsolat vagy csapda? | Kárász utca: 3 cég, 0 összefüggő pár, székhelyszolgáltató → nem kapcsolat. Budapesti út: csoporton belüli |

**Amit a dokumentumgráf megmutatott:**

- **Egy szemét chunk három globális kérdésnél is elvette a négy hely egyikét.** A
  `jelentes_mecsekko_holding_2024#00` tartalma a cím és a sablonsor nélkül 67 karakter: egyetlen mondat arról,
  hogy ez a jelentés kivonata. A baseline mégis a Q11, a Q12 és a Q13 top-4-ébe is behozta. Az oka valószínűleg
  a chunk elé tett címelőtag („Dokumentum: Mecsekkő Holding Zrt. — Igazgatósági jelentés a 2024. üzleti évről”),
  ami általánosan hasonlít a globális kérdésekre. A másik gyanús chunk
  (`level_tolnaker_tulajdonosvaltas#02`, 87 karakter) egyetlen bankszámla-sor, amelyből a kontextus nélkül nem derül
  ki, kinek a számlája.
- **A struktúra-szomszédság olcsó javítás lenne, de csak egy hibatípusra.** A Q02-ben a baseline a szerződés `#00` és
  `#02` chunkját hozta vissza, a díjat és a határidőt tartalmazó `#01` éppen közöttük van. A Q07-ben a levél
  törzsét (`#01`) megtalálta, a felszámoló nevét hordozó fejlécet (`#00`) nem. Mindkettőt egyetlen
  `NEXT_CHUNK`-lépés hozná be. A Q04-nél viszont a híd-cég (Kapos-Gép) dokumentuma egyáltalán nem került elő, és
  ezen semmilyen szomszédság nem segít. Ehhez entitásgráf kell: ez a 3. hét.
- **A `##`-mentén vágás működik.** A 163 szakaszból 7 esik több chunkba úgy, hogy egyik chunk sem tartalmazza
  egészben. Hat ezek közül a `##` nélküli levelek, számlák és az e-mail törzse, ahol nincs mi mentén vágni. A
  hetedik egy 948 karakteres szakasz, amely nem fér el egy 800-as chunkban. Cégkivonat-szakaszt egyet sem vágott
  ketté a chunkolás. A több chunkban is megjelenő többi szakasz csak az overlap miatt lóg át, ezért a 4.
  lekérdezés azt nézi, van-e chunk, amely a szakaszt egészben tartalmazza.

A baseline-t és a chunkolást nem javítjuk utólag. A fenti leletek a későbbi hetek mért összevetésének
kiindulópontjai.
