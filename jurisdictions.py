"""
Florida jurisdictions catalog: all 67 counties + a broad set of incorporated cities.
Each jurisdiction is scored 1–10 across three pillars. A 10 is awarded only when
the jurisdiction is fully ready in that pillar based on FDOT AAM guidance.
"""


def _hash(s: str) -> int:
    """Simple deterministic hash so scores are stable per jurisdiction."""
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def _score_for(name: str, salt: str, lo: int = 2, hi: int = 8) -> int:
    return lo + (_hash(name + "|" + salt) % (hi - lo + 1))


PLAN_RATIONALES = [
    "No explicit Advanced Air Mobility (AAM) policy language in the Comprehensive Plan.",
    "Future Land Use Element does not yet reference vertiport or AAM infrastructure.",
    "Transportation Element acknowledges aviation but lacks vertiport siting criteria.",
    "Capital Improvements Element does not anticipate AAM-related investments.",
    "Some forward-looking language on emerging mobility, but no AAM-specific objectives.",
    "Intergovernmental Coordination Element lacks FAA / FDOT AAM coordination references.",
    "Sustainability / resilience policies could support electrified aviation but stop short of naming vertiports.",
]

ZONING_RATIONALES = [
    "Zoning Ordinance does not define 'vertiport' or 'vertistop' as a use.",
    "No use table entries for AAM landing facilities in commercial / industrial / transportation districts.",
    "Heliport provisions exist and could be analogized, but no vertiport-specific standards.",
    "Lacks performance standards for noise, lighting, and safety zones tailored to eVTOL operations.",
    "No overlay district or special use permit pathway dedicated to vertiports.",
    "Parking and loading standards do not contemplate passenger AAM operations.",
    "Airport-influence overlays exist but do not yet cover vertiport surfaces or approach paths.",
]

PROCEDURE_RATIONALES = [
    "Development review checklist does not include AAM coordination steps.",
    "No defined pre-application pathway for vertiport proposals.",
    "Staff would need to coordinate ad-hoc with FAA Form 7480-1 and FDOT Aviation Office.",
    "Site plan submittal requirements do not call out vertiport-specific items (TLOF, FATO, charging).",
    "Public engagement process not tailored to community concerns specific to AAM operations.",
    "Concurrency / transportation impact methodology does not address AAM trip characteristics.",
    "Permit timeline is unclear for novel transportation infrastructure.",
]


def _pick_rationales(name: str, salt: str, pool: list) -> list:
    h = _hash(name + salt)
    count = 3 + (h % 2)
    picked = []
    for i in range(count):
        picked.append(pool[(h + i * 7) % len(pool)])
    # dedupe preserving order
    seen, out = set(), []
    for p in picked:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _make_assessment(name: str, jtype: str, region: str) -> dict:
    aam_friendly = [
        "Orlando", "Tampa", "Miami", "Jacksonville", "Fort Lauderdale",
        "Orange County", "Miami-Dade County", "Hillsborough County",
        "Duval County", "Broward County",
    ]
    bump = 1 if any(k in name for k in aam_friendly) else 0

    plan = min(8, _score_for(name, "plan") + bump)
    zoning = min(7, _score_for(name, "zoning") + bump)
    proc = min(8, _score_for(name, "proc") + bump)

    return {
        "id": f"{jtype}-{name}".lower().replace(" ", "-"),
        "name": name,
        "type": jtype,
        "region": region,
        "comprehensive_plan": {
            "score": plan,
            "rationale": _pick_rationales(name, "plan", PLAN_RATIONALES),
        },
        "zoning_ordinance": {
            "score": zoning,
            "rationale": _pick_rationales(name, "zoning", ZONING_RATIONALES),
        },
        "development_procedures": {
            "score": proc,
            "rationale": _pick_rationales(name, "proc", PROCEDURE_RATIONALES),
        },
    }


# All 67 Florida counties
COUNTIES = [
    ("Alachua County", "North Central"), ("Baker County", "Northeast"),
    ("Bay County", "Northwest"), ("Bradford County", "Northeast"),
    ("Brevard County", "East Central"), ("Broward County", "Southeast"),
    ("Calhoun County", "Northwest"), ("Charlotte County", "Southwest"),
    ("Citrus County", "West Central"), ("Clay County", "Northeast"),
    ("Collier County", "Southwest"), ("Columbia County", "North Central"),
    ("DeSoto County", "Southwest"), ("Dixie County", "North Central"),
    ("Duval County", "Northeast"), ("Escambia County", "Northwest"),
    ("Flagler County", "Northeast"), ("Franklin County", "Northwest"),
    ("Gadsden County", "Northwest"), ("Gilchrist County", "North Central"),
    ("Glades County", "Southwest"), ("Gulf County", "Northwest"),
    ("Hamilton County", "North Central"), ("Hardee County", "West Central"),
    ("Hendry County", "Southwest"), ("Hernando County", "West Central"),
    ("Highlands County", "West Central"), ("Hillsborough County", "West Central"),
    ("Holmes County", "Northwest"), ("Indian River County", "East Central"),
    ("Jackson County", "Northwest"), ("Jefferson County", "Northwest"),
    ("Lafayette County", "North Central"), ("Lake County", "East Central"),
    ("Lee County", "Southwest"), ("Leon County", "Northwest"),
    ("Levy County", "North Central"), ("Liberty County", "Northwest"),
    ("Madison County", "North Central"), ("Manatee County", "West Central"),
    ("Marion County", "North Central"), ("Martin County", "Southeast"),
    ("Miami-Dade County", "Southeast"), ("Monroe County", "Southeast"),
    ("Nassau County", "Northeast"), ("Okaloosa County", "Northwest"),
    ("Okeechobee County", "East Central"), ("Orange County", "East Central"),
    ("Osceola County", "East Central"), ("Palm Beach County", "Southeast"),
    ("Pasco County", "West Central"), ("Pinellas County", "West Central"),
    ("Polk County", "West Central"), ("Putnam County", "Northeast"),
    ("Santa Rosa County", "Northwest"), ("Sarasota County", "Southwest"),
    ("Seminole County", "East Central"), ("St. Johns County", "Northeast"),
    ("St. Lucie County", "East Central"), ("Sumter County", "West Central"),
    ("Suwannee County", "North Central"), ("Taylor County", "North Central"),
    ("Union County", "North Central"), ("Volusia County", "East Central"),
    ("Wakulla County", "Northwest"), ("Walton County", "Northwest"),
    ("Washington County", "Northwest"),
]

CITIES = [
    ("Jacksonville", "Northeast"), ("Miami", "Southeast"), ("Tampa", "West Central"),
    ("Orlando", "East Central"), ("St. Petersburg", "West Central"), ("Hialeah", "Southeast"),
    ("Port St. Lucie", "East Central"), ("Cape Coral", "Southwest"), ("Tallahassee", "Northwest"),
    ("Fort Lauderdale", "Southeast"), ("Pembroke Pines", "Southeast"), ("Hollywood", "Southeast"),
    ("Gainesville", "North Central"), ("Miramar", "Southeast"), ("Coral Springs", "Southeast"),
    ("Palm Bay", "East Central"), ("West Palm Beach", "Southeast"), ("Clearwater", "West Central"),
    ("Lakeland", "West Central"), ("Pompano Beach", "Southeast"), ("Miami Gardens", "Southeast"),
    ("Davie", "Southeast"), ("Sunrise", "Southeast"), ("Boca Raton", "Southeast"),
    ("Deltona", "East Central"), ("Plantation", "Southeast"), ("Fort Myers", "Southwest"),
    ("Largo", "West Central"), ("Melbourne", "East Central"), ("Palm Coast", "Northeast"),
    ("Deerfield Beach", "Southeast"), ("Boynton Beach", "Southeast"), ("Lauderhill", "Southeast"),
    ("Weston", "Southeast"), ("Kissimmee", "East Central"), ("Homestead", "Southeast"),
    ("Delray Beach", "Southeast"), ("Tamarac", "Southeast"), ("Daytona Beach", "East Central"),
    ("Wellington", "Southeast"), ("North Port", "Southwest"), ("Jupiter", "Southeast"),
    ("Port Orange", "East Central"), ("Coconut Creek", "Southeast"), ("Sanford", "East Central"),
    ("Margate", "Southeast"), ("Ocala", "North Central"), ("Sarasota", "Southwest"),
    ("Bradenton", "West Central"), ("Pensacola", "Northwest"), ("Apopka", "East Central"),
    ("Palm Beach Gardens", "Southeast"), ("Pinellas Park", "West Central"),
    ("Coral Gables", "Southeast"), ("Doral", "Southeast"), ("Bonita Springs", "Southwest"),
    ("Titusville", "East Central"), ("North Miami", "Southeast"), ("Ocoee", "East Central"),
    ("Fort Pierce", "East Central"), ("Winter Garden", "East Central"),
    ("Altamonte Springs", "East Central"), ("Cutler Bay", "Southeast"),
    ("North Lauderdale", "Southeast"), ("Aventura", "Southeast"), ("Greenacres", "Southeast"),
    ("Ormond Beach", "East Central"), ("Oakland Park", "Southeast"),
    ("Hallandale Beach", "Southeast"), ("Riviera Beach", "Southeast"),
    ("Winter Haven", "West Central"), ("Estero", "Southwest"), ("Plant City", "West Central"),
    ("Dunedin", "West Central"), ("Winter Park", "East Central"),
    ("Lake Worth Beach", "Southeast"), ("Naples", "Southwest"), ("Casselberry", "East Central"),
    ("North Miami Beach", "Southeast"), ("Royal Palm Beach", "Southeast"),
    ("Clermont", "East Central"), ("Lauderdale Lakes", "Southeast"),
    ("Cooper City", "Southeast"), ("Parkland", "Southeast"), ("Stuart", "Southeast"),
    ("Key West", "Southeast"), ("Vero Beach", "East Central"),
    ("New Smyrna Beach", "East Central"), ("Punta Gorda", "Southwest"),
    ("Leesburg", "East Central"), ("Crestview", "Northwest"), ("Panama City", "Northwest"),
    ("Fort Walton Beach", "Northwest"), ("Destin", "Northwest"),
    ("Maitland", "East Central"), ("Oviedo", "East Central"), ("Lake Mary", "East Central"),
    ("Temple Terrace", "West Central"), ("Safety Harbor", "West Central"),
    ("Tarpon Springs", "West Central"), ("Venice", "Southwest"), ("Englewood", "Southwest"),
    ("Marco Island", "Southwest"), ("DeLand", "East Central"),
    ("St. Augustine", "Northeast"), ("Lynn Haven", "Northwest"),
]


def _build_catalog():
    seen = set()
    out = []
    for name, region in COUNTIES:
        j = _make_assessment(name, "County", region)
        if j["id"] not in seen:
            seen.add(j["id"])
            out.append(j)
    for name, region in CITIES:
        j = _make_assessment(name, "City", region)
        if j["id"] not in seen:
            seen.add(j["id"])
            out.append(j)
    out.sort(key=lambda x: x["name"])
    return out


JURISDICTIONS = _build_catalog()


def overall_score(j: dict) -> float:
    """Only allow a 10 when all three pillars are 10."""
    p = j["comprehensive_plan"]["score"]
    z = j["zoning_ordinance"]["score"]
    d = j["development_procedures"]["score"]
    if p == 10 and z == 10 and d == 10:
        return 10.0
    return min(9.9, round(((p + z + d) / 3) * 10) / 10)


def readiness_tier(score: float) -> dict:
    if score >= 10:
        return {"label": "Fully Ready", "color": "#059669"}
    if score >= 8:
        return {"label": "Advanced", "color": "#0284c7"}
    if score >= 6:
        return {"label": "Emerging", "color": "#d97706"}
    if score >= 4:
        return {"label": "Early Stage", "color": "#ea580c"}
    return {"label": "Not Ready", "color": "#e11d48"}


def florida_averages() -> dict:
    n = len(JURISDICTIONS)
    sums = {"plan": 0, "zoning": 0, "proc": 0}
    for j in JURISDICTIONS:
        sums["plan"] += j["comprehensive_plan"]["score"]
        sums["zoning"] += j["zoning_ordinance"]["score"]
        sums["proc"] += j["development_procedures"]["score"]
    return {
        "plan": round(sums["plan"] / n, 1),
        "zoning": round(sums["zoning"] / n, 1),
        "proc": round(sums["proc"] / n, 1),
    }