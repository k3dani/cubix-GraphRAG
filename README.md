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

```bash
cp .env.example .env          # végpontok és modellnevek megadása
docker compose up -d          # Qdrant a localhost:6333-on
uv sync
uv run ingest                 # korpusz → chunkok → Qdrant (a kollekciót újraépíti)
uv run ask "Ki a Mecsekkő Beton Kft. ügyvezetője?"
uv run baseline               # mind a 14 kérdés → baseline/answers.md + answers.jsonl
```

Az `.env.example` alapértelmezésként `bge-m3`-at (1024 dim) vár. Ha más embedding-modellt használsz, állítsd be az
`EMBEDDING_DIMENSION`-t. Nem Qwen3 LLM-nél pedig a `LLM_DISABLE_THINKING=false` kell.

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
