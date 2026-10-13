"""Seed: 19 csomópontnyi kitalált, a sémát követő mini-cégháló (Tisza-csoport, Szeged).

A korpusz cégeitől szándékosan független (más megye, más nevek), de ugyanazokat a csapdákat
hordozza: rejtett érdekeltség egy alvállalkozóban, átigazolt vezető, székhelyszolgáltatói közös
cím, áfacsoport, felszámolás. Az adószámok formailag érvényesek, de a 999… prefix jelzi,
hogy kitaláltak.
"""

from graphrag_course.graph import (
    Node,
    Rel,
    count_graph,
    ensure_constraints,
    get_driver,
    merge_graph,
)

DATASET = "seed"

# kulcsok (a relációkban ezekkel hivatkozunk a csomópontokra)
VARGA = "varga-bela-1961-05-14"
LAKATOS = "lakatos-eva-1968-09-02"
FEKETE = "fekete-otto-1970-02-11"
PAP = "pap-kristof-1979-11-23"
HOLDING = "06-10-904417"
BETON = "06-09-912305"
MAROS = "06-10-903318"
GEP = "06-09-928841"
ALFOLDI = "06-09-917762"
SZEKHAZ = "06-09-921150"
ADDR_SZEKHAZ = "6720 Szeged, Kárász utca 11."
ADDR_BETON = "6728 Szeged, Budapesti út 30."
ADDR_MAROS = "6724 Szeged, Kossuth Lajos sugárút 80."
VAT_GROUP = "99986980-5-06"
FRAME = "keret-tisza-beton-maros-epito-2024-01-08"
SUBCONTRACT = "alv-maros-epito-csongrad-gep-2025-03-10"
PROJECT = "ujszegedi-liget-lakopark"
INVOICE = f"{GEP}/CSG-2025/031"
PROCEEDING = "Fpk.06-25-000412"


def person(person_id: str, name: str, birth_date: str, mother_name: str) -> Node:
    return (
        "Person",
        {
            "person_id": person_id,
            "name": name,
            "birth_date": birth_date,
            "mother_name": mother_name,
        },
    )


def company(reg_no: str, name: str, full_name: str, legal_form: str, tax: str, **props) -> Node:
    return (
        "Company",
        {
            "reg_no": reg_no,
            "name": name,
            "full_name": full_name,
            "aliases": [name, full_name],
            "legal_form": legal_form,
            "tax_number": tax,
            "status": "aktív",
            **props,
        },
    )


NODES: list[Node] = [
    person(VARGA, "Varga Béla", "1961-05-14", "Tóth Ilona"),
    person(LAKATOS, "Lakatos Éva", "1968-09-02", "Kis Mária"),
    person(FEKETE, "Fekete Ottó", "1970-02-11", "Nagy Erzsébet"),
    person(PAP, "Pap Kristóf", "1979-11-23", "Szabó Anna"),
    company(
        HOLDING,
        "Tisza-Kő Holding Zrt.",
        "Tisza-Kő Holding Zártkörűen Működő Részvénytársaság",
        "Zrt.",
        "99915883-4-06",
        founded_on="2011-03-01",
    ),
    company(
        BETON,
        "Tisza Beton Kft.",
        "Tisza Beton Gyártó Korlátolt Felelősségű Társaság",
        "Kft.",
        "99913991-4-06",
        founded_on="2012-05-10",
    ),
    company(
        MAROS,
        "Maros Építő Zrt.",
        "Maros Építő Zártkörűen Működő Részvénytársaság",
        "Zrt.",
        "99979733-2-06",
        founded_on="2006-09-18",
    ),
    company(
        GEP,
        "Csongrád-Gép Kft.",
        "Csongrád-Gép Épületgépészeti Korlátolt Felelősségű Társaság",
        "Kft.",
        "99909118-2-06",
        founded_on="2018-02-01",
    ),
    company(
        ALFOLDI,
        "Alföldi Lakóépítő Kft. „f. a.”",
        "Alföldi Lakóépítő Korlátolt Felelősségű Társaság „felszámolás alatt”",
        "Kft.",
        "99941707-2-06",
        founded_on="2015-06-22",
        status="felszámolás alatt",
        status_since="2025-09-01",
    ),
    company(
        SZEKHAZ,
        "Szék-Ház Kft.",
        "Szék-Ház Szolgáltató Korlátolt Felelősségű Társaság",
        "Kft.",
        "99975368-2-06",
        founded_on="2014-11-03",
    ),
    ("Address", {"address": ADDR_SZEKHAZ, "postal_code": "6720", "city": "Szeged"}),
    ("Address", {"address": ADDR_BETON, "postal_code": "6728", "city": "Szeged"}),
    ("Address", {"address": ADDR_MAROS, "postal_code": "6724", "city": "Szeged"}),
    ("VatGroup", {"group_tax_id": VAT_GROUP, "name": "Tisza-Kő áfacsoport"}),
    (
        "Contract",
        {
            "contract_id": FRAME,
            "contract_type": "keretszerződés",
            "title": "Keretszerződés transzportbeton szállítására",
            "signed_on": "2024-01-08",
            "valid_from": "2024-01-15",
            "valid_to": "2026-12-31",
            "annual_cap_huf": 600_000_000,
        },
    ),
    (
        "Contract",
        {
            "contract_id": SUBCONTRACT,
            "contract_type": "alvállalkozói szerződés",
            "title": "Alvállalkozói szerződés — Újszegedi Liget Lakópark, épületgépészet",
            "signed_on": "2025-03-10",
            "net_value_huf": 74_500_000,
            "deadline": "2026-05-31",
        },
    ),
    ("Project", {"project_id": PROJECT, "name": "Újszegedi Liget Lakópark", "city": "Szeged"}),
    (
        "Invoice",
        {
            "invoice_id": INVOICE,
            "number": "CSG-2025/031",
            "invoice_type": "részszámla",
            "issued_on": "2025-09-30",
            "net_amount_huf": 24_800_000,
            "vat": "fordított adózás",
        },
    ),
    (
        "InsolvencyProceeding",
        {
            "case_no": PROCEEDING,
            "kind": "felszámolás",
            "court": "Szegedi Törvényszék",
            "started_on": "2025-09-01",
        },
    ),
]

RELS: list[Rel] = [
    # tulajdon: a holdingot ketten birtokolják, a holding a betongyárat
    (VARGA, "OWNS", HOLDING, {"share_pct": 65, "valid_from": "2011-03-01"}),
    (LAKATOS, "OWNS", HOLDING, {"share_pct": 35, "valid_from": "2011-03-01"}),
    (HOLDING, "OWNS", BETON, {"share_pct": 100, "valid_from": "2012-05-10"}),
    # Pap Kristóf alapította a Csongrád-Gépet; 2022-ben Varga Béla 25%-ot vett benne —
    # ugyanaz a tag két időszakban két él (a valid_from az él azonosítója)
    (PAP, "OWNS", GEP, {"share_pct": 100, "valid_from": "2018-02-01", "valid_to": "2022-02-28"}),
    (PAP, "OWNS", GEP, {"share_pct": 75, "valid_from": "2022-03-01"}),
    (VARGA, "OWNS", GEP, {"share_pct": 25, "valid_from": "2022-03-01"}),
    # vezető tisztségviselők; Pap Kristóf a betongyárból ment át a saját cégébe
    (VARGA, "OFFICER_OF", HOLDING, {"role": "az igazgatóság elnöke", "valid_from": "2011-03-01"}),
    (LAKATOS, "OFFICER_OF", HOLDING, {"role": "igazgatósági tag", "valid_from": "2011-03-01"}),
    (
        PAP,
        "OFFICER_OF",
        BETON,
        {"role": "ügyvezető", "valid_from": "2012-05-10", "valid_to": "2017-12-31"},
    ),
    (LAKATOS, "OFFICER_OF", BETON, {"role": "ügyvezető", "valid_from": "2018-01-01"}),
    (PAP, "OFFICER_OF", GEP, {"role": "ügyvezető", "valid_from": "2018-02-01"}),
    (FEKETE, "OFFICER_OF", MAROS, {"role": "vezérigazgató", "valid_from": "2006-09-18"}),
    # székhelyek: a holding és a betongyár közös címe valódi (csoporton belüli) kapcsolat,
    # a Kárász utcai cím csak székhelyszolgáltatás — hamis kapcsolat
    (HOLDING, "REGISTERED_AT", ADDR_BETON, {}),
    (BETON, "REGISTERED_AT", ADDR_BETON, {}),
    (MAROS, "REGISTERED_AT", ADDR_MAROS, {}),
    (GEP, "REGISTERED_AT", ADDR_SZEKHAZ, {}),
    (ALFOLDI, "REGISTERED_AT", ADDR_SZEKHAZ, {}),
    (SZEKHAZ, "REGISTERED_AT", ADDR_SZEKHAZ, {}),
    (SZEKHAZ, "SEAT_PROVIDER_FOR", GEP, {}),
    (SZEKHAZ, "SEAT_PROVIDER_FOR", ALFOLDI, {}),
    # áfacsoport: a tagok csoporttag-adószámot kapnak (-4-)
    (HOLDING, "MEMBER_OF", VAT_GROUP, {"valid_from": "2020-01-01"}),
    (BETON, "MEMBER_OF", VAT_GROUP, {"valid_from": "2020-01-01"}),
    # ugyanazon a projekten a Varga-érdekeltség két cége is a Maros Építőnek dolgozik
    (BETON, "PARTY_TO", FRAME, {"role": "szállító"}),
    (MAROS, "PARTY_TO", FRAME, {"role": "megrendelő"}),
    (MAROS, "PARTY_TO", SUBCONTRACT, {"role": "fővállalkozó"}),
    (GEP, "PARTY_TO", SUBCONTRACT, {"role": "alvállalkozó"}),
    (FRAME, "FOR_PROJECT", PROJECT, {}),
    (SUBCONTRACT, "FOR_PROJECT", PROJECT, {}),
    (GEP, "ISSUED", INVOICE, {}),
    (INVOICE, "BILLED_TO", MAROS, {}),
    (INVOICE, "UNDER_CONTRACT", SUBCONTRACT, {}),
    # felszámolás: az adós a Kárász utcai címen ül, a betongyár hitelező
    (PROCEEDING, "AGAINST", ALFOLDI, {}),
    (
        BETON,
        "FILED_CLAIM",
        PROCEEDING,
        {
            "amount_huf": 8_940_600,
            "principal_huf": 8_612_000,
            "interest_huf": 328_600,
            "filed_on": "2025-10-20",
        },
    ),
]


def main() -> None:
    with get_driver() as driver:
        ensure_constraints(driver)
        before = count_graph(driver)
        stats = merge_graph(driver, NODES, RELS, dataset=DATASET)
        after = count_graph(driver)
    print(
        f"seed: {stats['nodes']} csomópont, {stats['rels']} él MERGE-ölve "
        f"(törölt elavult: {stats['removed_nodes']} csomópont, {stats['removed_rels']} él)"
    )
    print(
        f"a gráf: {before['nodes']} → {after['nodes']} csomópont, "
        f"{before['rels']} → {after['rels']} él"
    )
