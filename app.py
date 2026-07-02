from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

import gradio as gr


SCORE_ROWS = [
    ["Entity/AEO", 420, 877, 1000, "Provider/practice separation, schema, llms.txt, Search Console, and public-safe dataset are implemented."],
    ["High-risk/YMYL", 378, 846, 1000, "Public app remains informational and nonclinical; final score requires office review and external evidence capture."],
    ["Google/AEO/YMYL 50-standard", 231, 937, 1000, "Dataset creator/license cleanup added; final target requires GBP/directory/DOI/ORCID/Kaggle proof."],
]

URL_ROWS = [
    ["URL001", "owned_site", "Positive Outcomes homepage", "https://positive-outcomes.com/", "live_cleaned", "Canonical practice URL."],
    ["URL002", "owned_site", "About Harvey L. Gayer", "https://positive-outcomes.com/about-us/", "live_rewritten", "Primary provider/entity page."],
    ["URL003", "owned_site", "Services", "https://positive-outcomes.com/services/", "live_rewritten", "Therapy/testing/evaluation scope page."],
    ["URL004", "owned_site", "Contact", "https://positive-outcomes.com/contact-us/", "live_rewritten", "Official appointment route."],
    ["URL005", "owned_site", "Location", "https://positive-outcomes.com/about-us/location-directions/", "live_rewritten", "Suite/location page; Maps/GBP verification pending."],
    ["URL006", "public_repo", "GitHub study repo", "https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint", "live_public_safe", "Redacted public-safe repo."],
    ["URL007", "hugging_face", "Hugging Face Space", "https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint", "staged", "Space update requires Hugging Face authentication."],
    ["URL008", "hugging_face", "Direct Gradio app", "https://inspectorroofing-doctor-ymyl-blueprint.hf.space/", "staged", "Direct app endpoint after Space sync."],
]


class PageSignalsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.in_script = False
        self.in_style = False
        self.in_heading = False
        self.current_script_is_jsonld = False
        self.current_script: list[str] = []
        self.title: list[str] = []
        self.body: list[str] = []
        self.headings: list[str] = []
        self.jsonld_scripts: list[str] = []
        self.meta: dict[str, str] = {}
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "style":
            self.in_style = True
        elif tag == "script":
            self.in_script = True
            self.current_script_is_jsonld = "ld+json" in attr.get("type", "").lower()
            self.current_script = []
        elif tag in {"h1", "h2", "h3"}:
            self.in_heading = True
        elif tag == "meta":
            key = attr.get("name") or attr.get("property")
            if key and attr.get("content"):
                self.meta[key.lower()] = attr["content"]
        elif tag == "link":
            self.links.append(attr)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "style":
            self.in_style = False
        elif tag == "script":
            if self.current_script_is_jsonld and self.current_script:
                self.jsonld_scripts.append("".join(self.current_script).strip())
            self.in_script = False
            self.current_script_is_jsonld = False
            self.current_script = []
        elif tag in {"h1", "h2", "h3"}:
            self.in_heading = False

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self.in_script:
            if self.current_script_is_jsonld:
                self.current_script.append(data)
            return
        if self.in_style:
            return
        if self.in_title:
            self.title.append(text)
        elif self.in_heading:
            self.headings.append(text)
            self.body.append(text)
        else:
            self.body.append(text)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def normalize_url(url: str) -> str:
    candidate = (url or "").strip()
    if candidate and not re.match(r"^https?://", candidate, flags=re.I):
        candidate = f"https://{candidate}"
    return candidate


def fetch_url_text(url: str, timeout: int = 12) -> tuple[str, dict[str, str]]:
    normalized = normalize_url(url)
    parsed = urllib.parse.urlparse(normalized)
    if not parsed.scheme or not parsed.netloc:
        return "", {"status": "not_requested", "url": normalized}
    request = urllib.request.Request(
        normalized,
        headers={
            "User-Agent": "DoctorYMYLBlueprintBot/0.1 (+https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(900_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace"), {
                "status": str(getattr(response, "status", 200)),
                "url": normalized,
                "final_url": response.geturl(),
                "content_type": response.headers.get("content-type", ""),
            }
    except Exception as exc:
        return "", {"status": "fetch_error", "url": normalized, "error": str(exc)}


def fetch_support_file(base_url: str, filename: str) -> dict[str, str]:
    parsed = urllib.parse.urlparse(normalize_url(base_url))
    if not parsed.scheme or not parsed.netloc:
        return {"file": filename, "status": "not_checked", "url": ""}
    support_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, f"/{filename}", "", "", ""))
    text, meta = fetch_url_text(support_url, timeout=6)
    return {
        "file": filename,
        "status": "found" if meta.get("status", "").startswith("2") and text else "missing_or_blocked",
        "url": support_url,
        "bytes": str(len(text)),
    }


def parse_page(raw_html: str) -> dict:
    parser = PageSignalsParser()
    parser.feed(raw_html or "")
    return {
        "title": clean_text(" ".join(parser.title)),
        "description": clean_text(parser.meta.get("description", "")),
        "robots": clean_text(parser.meta.get("robots", "")),
        "headings": [clean_text(item) for item in parser.headings if clean_text(item)],
        "text": clean_text(" ".join(parser.body)),
        "jsonld_scripts": parser.jsonld_scripts,
        "canonical": next((link.get("href", "") for link in parser.links if "canonical" in link.get("rel", "").lower()), ""),
    }


def parse_jsonld_blocks(blocks: list[str]) -> tuple[list[dict], list[str]]:
    nodes: list[dict] = []
    errors: list[str] = []
    for block in blocks:
        if not block.strip():
            continue
        try:
            parsed = json.loads(block)
        except Exception as exc:
            errors.append(f"JSON-LD parse error: {exc}")
            continue
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            if not isinstance(item, dict):
                continue
            graph = item.get("@graph")
            if isinstance(graph, list):
                nodes.extend(node for node in graph if isinstance(node, dict))
            nodes.append(item)
    return nodes, errors


def type_values(node: dict) -> list[str]:
    raw_type = node.get("@type")
    if isinstance(raw_type, str):
        return [raw_type]
    if isinstance(raw_type, list):
        return [item for item in raw_type if isinstance(item, str)]
    return []


def has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms if term)


def has_regex(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.I | re.S) is not None


def grade(total: int) -> str:
    if total >= 930:
        return "Study-grade YMYL readiness"
    if total >= 850:
        return "Strong YMYL readiness"
    if total >= 700:
        return "Useful, but public-safety gaps remain"
    if total >= 500:
        return "Material remediation needed"
    return "High-risk: do not treat as publication-ready"


def score_dimension(label: str, checks: list[tuple[bool, int, str, str]]) -> tuple[int, list[list[str]]]:
    score = 0
    rows: list[list[str]] = []
    for passed, points, check, fix in checks:
        if passed:
            score += points
        rows.append([label, check, "PASS" if passed else "ACTION", str(points if passed else 0), "" if passed else fix])
    return min(score, 100), rows


def entity_conflict_found(text: str, schema_text: str, expected_practice: str, conflict_entities: str) -> bool:
    conflicts = [item.strip() for item in re.split(r"[,;\n]", conflict_entities or "") if item.strip()]
    if not conflicts:
        return False
    for conflict in conflicts:
        conflict_seen = conflict.lower() in text.lower()
        practice_seen = bool(expected_practice and expected_practice.lower() in text.lower())
        conflict_attached_in_schema = conflict.lower() in schema_text.lower() and any(
            relation in schema_text.lower() for relation in ["sameas", "employee", "member", "department", "worksfor"]
        )
        if conflict_seen and practice_seen and conflict_attached_in_schema:
            return True
    return False


def audit_site(
    url: str,
    pasted_html_or_text: str,
    pasted_jsonld: str,
    expected_provider: str,
    expected_credential: str,
    expected_practice: str,
    expected_phone: str,
    expected_address: str,
    conflict_entities: str,
    fetch_public_files: bool,
    uses_ai_for_decisions: bool,
    handles_patient_data: bool,
    makes_clinical_or_legal_recommendations: bool,
) -> tuple[dict, list[list[str]], str]:
    fetched_html, fetch_meta = fetch_url_text(url) if url.strip() else ("", {"status": "not_requested", "url": ""})
    source_html = fetched_html or pasted_html_or_text or ""
    page = parse_page(source_html)
    visible_text = clean_text(" ".join([page["title"], page["description"], " ".join(page["headings"]), page["text"]]))
    all_text = clean_text(" ".join([visible_text, pasted_jsonld]))
    jsonld_blocks = list(page["jsonld_scripts"])
    if pasted_jsonld.strip():
        jsonld_blocks.append(pasted_jsonld.strip())
    schema_nodes, schema_errors = parse_jsonld_blocks(jsonld_blocks)
    schema_text = json.dumps(schema_nodes, default=str)
    schema_types = sorted({schema_type for node in schema_nodes for schema_type in type_values(node)})
    support_files = []
    if fetch_public_files and url.strip():
        support_files = [
            fetch_support_file(url, "robots.txt"),
            fetch_support_file(url, "sitemap.xml"),
            fetch_support_file(url, "sitemap_index.xml"),
            fetch_support_file(url, "llms.txt"),
        ]
    support_found = {item["file"]: item["status"] for item in support_files}

    ymyl_terms = [
        "psychologist",
        "psychological",
        "therapy",
        "mental health",
        "doctor",
        "medical",
        "clinic",
        "health",
        "forensic",
        "evaluation",
        "testing",
        "diagnosis",
        "treatment",
        "patient",
    ]
    ymyly = has_any(all_text, ymyl_terms)
    has_disclaimer = has_any(all_text, ["not medical advice", "not legal advice", "emergency", "911", "crisis", "not a substitute"])
    has_privacy = has_any(all_text, ["privacy", "hipaa", "confidential", "protected health", "patient information"])
    has_correction_route = has_any(all_text, ["correction", "contact", "email", "phone", "appointment", "call"])
    has_human_review = has_any(all_text, ["human review", "licensed", "doctor", "psychologist", "office approval", "reviewed by"])
    has_schema = bool(schema_nodes)
    local_schema = any({"LocalBusiness", "MedicalClinic", "MedicalBusiness", "Organization"} & set(type_values(node)) for node in schema_nodes)
    person_schema = any("Person" in type_values(node) for node in schema_nodes)
    dataset_schema = any("Dataset" in type_values(node) for node in schema_nodes)
    phone_digits = re.sub(r"\D+", "", expected_phone or "")
    text_digits = re.sub(r"\D+", "", all_text)
    expected_phone_found = bool(phone_digits and phone_digits in text_digits)
    address_parts = [part.strip() for part in re.split(r"[, ]+", expected_address or "") if len(part.strip()) >= 3]
    expected_address_found = bool(expected_address and sum(1 for part in address_parts if part.lower() in all_text.lower()) >= 3)
    provider_found = has_any(all_text, [expected_provider]) if expected_provider else has_any(all_text, ["doctor", "dr.", "provider", "psychologist"])
    credential_found = has_any(all_text, [expected_credential, "licensed", "ph.d", "psyd", "md", "npi", "credential"]) if expected_credential else has_any(all_text, ["licensed", "credential"])
    practice_found = has_any(all_text, [expected_practice]) if expected_practice else has_any(all_text, ["practice", "clinic", "organization"])
    conflict_attached = entity_conflict_found(all_text, schema_text, expected_practice, conflict_entities)
    conflict_visible = has_any(all_text, ["separate", "not associated", "not affiliated", "rent", "renter", "colocated", "independent"])
    sameas_conflict = has_any(schema_text, ["healthgrades", "webmd", "doctor.webmd"]) and not has_any(all_text, ["conflict source", "monitor"])
    npi_public_warning = has_regex(all_text, r"\bNPI\b.{0,40}\b\d{10}\b") or has_regex(all_text, r"\blicen[cs]e\b.{0,40}\b[A-Z]{2,}\d{4,}\b")

    dimension_specs = [
        ("YMYL Scope And Intended Use", [(ymyly, 25, "Health/clinical/YMYL or high-trust service topic is recognized.", "State the site purpose, audience, and public-safety boundaries clearly."), (not makes_clinical_or_legal_recommendations, 25, "The app/page is not positioned as diagnosis, treatment, or legal decision support.", "Remove diagnosis, treatment, legal, eligibility, or emergency decision claims."), (has_disclaimer, 25, "Non-advice or emergency boundary language is visible.", "Add plain-language non-advice and emergency/crisis boundaries."), (has_human_review, 25, "Human expert or office-review signal is visible.", "Add named human review ownership for YMYL content.")]),
        ("Provider And Practice Identity", [(provider_found, 25, "Provider/person entity is named.", "Name the responsible provider/person entity."), (credential_found, 25, "Credential or professional role is visible.", "Show credential/title in office-approved wording."), (practice_found, 25, "Practice/business entity is named.", "Name the practice entity consistently."), (person_schema or "Person" in all_text, 25, "Person schema or equivalent person signal exists.", "Add Person JSON-LD or visible person-entity facts.")]),
        ("Contact, NAP, And Appointment Route", [(expected_phone_found or has_regex(all_text, r"\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}"), 25, "Phone/contact route is visible.", "Add the current patient phone/contact route."), (expected_address_found or has_any(all_text, ["address", "suite", "road", "street", "avenue"]), 25, "Address/location signal is visible.", "Add current address, suite, city, state, and ZIP where appropriate."), (has_any(all_text, ["hours", "monday", "appointment", "schedule", "call", "email"]), 25, "Hours or appointment process is visible.", "Add office hours and appointment process."), (local_schema, 25, "Local/medical business schema supports contact facts.", "Add LocalBusiness/MedicalBusiness/MedicalClinic schema.")]),
        ("Entity Separation And Conflict Control", [(not conflict_attached, 30, "Known separate entities are not attached to the practice in schema.", "Do not connect renters/separate businesses as employees, departments, or members."), (conflict_visible or not conflict_entities.strip(), 25, "Visible separation language exists when conflicts are known.", "Add public copy explaining separate colocated/renting entities."), (not sameas_conflict, 25, "Conflict directories are not used as canonical sameAs truth.", "Move conflict directories into source registry/monitoring, not sameAs."), (not npi_public_warning, 20, "Exact credential identifiers are not exposed without context.", "If publishing exact identifiers, add approval and source context.")]),
        ("Helpful Content And E-E-A-T", [(bool(page["title"]) and bool(page["description"]), 20, "Title and meta description are present.", "Add a specific title and meta description."), (len(visible_text) >= 600, 20, "Visible text gives enough context for people and AI systems.", "Add substantial original public-facing content."), (has_any(all_text, ["about", "profile", "bio", "experience", "education", "university", "source", "reviewed"]), 20, "Expertise/source signals are visible.", "Add bio, education, affiliations, source links, and review ownership."), (has_any(all_text, ["updated", "reviewed", "date", "current", "office"]), 20, "Freshness/current-status language exists.", "Add reviewed/updated date or office confirmation wording."), (not has_any(all_text, ["lorem ipsum", "guaranteed cure", "#1 doctor"]), 20, "No obvious placeholder or exaggerated clinical claim found.", "Remove placeholder copy and unsupported claims.")]),
        ("Structured Data And Schema Safety", [(has_schema, 20, "JSON-LD or structured data is present.", "Add JSON-LD for the main entity."), (not schema_errors, 20, "JSON-LD parses cleanly.", "Fix malformed JSON-LD."), (local_schema or person_schema, 20, "Schema includes relevant person/local/medical entity.", "Use Person plus MedicalClinic/MedicalBusiness/LocalBusiness where appropriate."), (not has_any(schema_text, ["hidden claim", "fake review"]), 20, "No obvious misleading schema-only claim found.", "Keep schema aligned with visible content."), (dataset_schema or has_any(schema_text, ["publisher", "creator", "license", "dateModified"]) or not has_schema, 20, "Research dataset/publisher/license signals are handled when relevant.", "For research data, include creator, publisher, license, usageInfo, dateModified, and language.")]),
        ("Crawl, Indexing, And AI Files", [(bool(page["canonical"]) or not url.strip(), 20, "Canonical URL is present or URL was not fetched.", "Add rel=canonical to public pages."), ("noindex" not in page["robots"].lower(), 20, "Page is not accidentally noindexed.", "Remove noindex from canonical public pages."), (support_found.get("robots.txt") == "found" or not fetch_public_files, 20, "robots.txt found or check skipped.", "Publish robots.txt and avoid blocking pages that need noindex."), (support_found.get("sitemap.xml") == "found" or support_found.get("sitemap_index.xml") == "found" or not fetch_public_files, 20, "Sitemap found or check skipped.", "Publish and submit sitemap/index."), (support_found.get("llms.txt") == "found" or has_any(all_text, ["llms.txt", "entity graph"]) or not fetch_public_files, 20, "AI-readable llms/entity summary exists or check skipped.", "Add llms.txt or a public entity summary.")]),
        ("Privacy, Data Governance, And Human Oversight", [(has_privacy or not ymyly, 25, "Privacy/confidentiality language is visible for YMYL content.", "Add privacy/confidentiality/HIPAA-safe language where appropriate."), (not handles_patient_data, 25, "No public patient-data handling declared.", "Do not upload patient or protected health data to public demos."), (not uses_ai_for_decisions, 25, "AI is not used for consequential decisions.", "If AI affects decisions, add impact assessment, notice, correction, appeal, and human oversight."), (has_correction_route, 25, "Correction/contact route exists.", "Add a route to correct public profile or practice facts.")]),
        ("Monitoring And Publication Governance", [(has_any(all_text, ["google business", "maps", "directory", "source registry", "source"]), 25, "External source/directory monitoring is mentioned.", "Track Google Business Profile, maps, and major directories."), (has_any(all_text, ["doi", "zenodo", "github", "hugging face", "orcid", "kaggle", "citation"]) or not has_any(all_text, ["study", "research"]), 25, "Research publication metadata is handled when relevant.", "For studies, add GitHub, DOI, dataset, ORCID, and citation metadata after review."), (has_any(all_text, ["approved", "review", "sign off", "office", "correction"]), 25, "Human approval or correction workflow is visible.", "Add approval/sign-off workflow for YMYL claims."), (not has_any(all_text, ["100% compliant", "guaranteed compliance", "certified by google"]), 25, "No false compliance guarantee detected.", "Avoid claiming Google, medical, legal, or regulatory certification unless formally obtained.")]),
    ]
    dimensions: list[tuple[str, int, list[list[str]]]] = []
    for label, checks in dimension_specs:
        dimension_score, rows = score_dimension(label, checks)
        dimensions.append((label, dimension_score, rows))

    audit_rows = [row for _, _, rows in dimensions for row in rows]
    total = sum(score for _, score, _ in dimensions)
    actions = [row for row in audit_rows if row[2] == "ACTION"]
    top_actions = [row[4] for row in actions[:8]]
    summary = {"url": fetch_meta.get("final_url") or fetch_meta.get("url") or "", "fetch": fetch_meta, "score": total, "grade": grade(total), "ymyl_detected": ymyly, "not_a_certification": "Public-readiness audit only; not legal, medical, Google, or regulatory certification.", "schema_types_found": schema_types, "support_files": support_files, "schema_parse_errors": schema_errors, "dimension_scores": {label: score for label, score, _ in dimensions}, "top_actions": top_actions}
    markdown = f"## YMYL Readiness: {total}/1000\n\n**Grade:** {grade(total)}\n\nThis is a screening and remediation tool. It does not certify legal compliance, medical accuracy, Google ranking, professional licensure, diagnosis, treatment, or patient routing.\n\n### Highest Priority Fixes\n" + "\n".join(f"- {item}" for item in (top_actions or ["No priority fixes detected from this quick scan."]))
    return summary, audit_rows, markdown


def score_summary() -> dict:
    return {"entity_aeo": {"before": 420, "current": 877, "target": 1000}, "high_risk_ymyl": {"before": 378, "current": 846, "target": 1000}, "google_aeo_ymyl_50": {"before": 231, "current": 937, "target": 1000}, "note": "Internal audit score only; not a Google score, legal certification, compliance certification, diagnosis, treatment recommendation, or patient-routing tool."}


def case_summary() -> str:
    return json.dumps({"expert_person": "Harvey L. Gayer, Ph.D.", "practice": "Positive Outcomes Psychological Services, P.C.", "separate_entities": "Classic City Psychological Associates and other colocated/renting professionals", "entity_rule": "Renting office space does not make a provider part of Positive Outcomes Psychological Services, P.C.", "public_safety": "Exact NPI/license identifiers are withheld pending Dr. Gayer approval.", "dataset_schema_cleanup": "Dataset creator, publisher, license, usageInfo, dateModified, and inLanguage fields were added for public structured-data hygiene.", "github": "https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint", "hugging_face_space": "https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint"}, indent=2)


with gr.Blocks(title="Doctor YMYL Blueprint") as demo:
    gr.Markdown("# Doctor YMYL Blueprint")
    gr.Markdown("A public-safe research preview and site-audit tool for YMYL entity clarity, AI search, schema, GEO, SEO, and AEO. This version excludes exact hold-only credential identifiers and internal evidence files.")

    with gr.Tab("Site Audit"):
        gr.Markdown("## Check A Site For YMYL Readiness\n\nPaste a URL, page HTML/text, or JSON-LD. The app gives a 0-1000 public-readiness score and remediation list. It is not a legal, medical, Google, or regulatory certification.")
        audit_url = gr.Textbox(label="Site or page URL", value="https://positive-outcomes.com/")
        with gr.Accordion("Optional page/source inputs", open=False):
            audit_html = gr.Textbox(label="Paste page HTML or visible page text if URL fetch is blocked", lines=8)
            audit_jsonld = gr.Textbox(label="Paste JSON-LD schema if you want to test schema separately", lines=8)
        with gr.Accordion("Expected entity facts", open=True):
            with gr.Row():
                audit_provider = gr.Textbox(label="Expected provider/person", value="Harvey L. Gayer")
                audit_credential = gr.Textbox(label="Expected credential/title", value="Ph.D., Licensed Psychologist")
            with gr.Row():
                audit_practice = gr.Textbox(label="Expected practice/business", value="Positive Outcomes Psychological Services, P.C.")
                audit_phone = gr.Textbox(label="Expected phone", value="706-543-3538")
            audit_address = gr.Textbox(label="Expected address", value="485 Huntington Road, Suite 199, Athens, GA 30606")
            audit_conflicts = gr.Textbox(label="Known separate/conflicting entities", value="Classic City Psychological Associates; other colocated providers")
        with gr.Accordion("Risk controls", open=True):
            with gr.Row():
                audit_fetch_support = gr.Checkbox(label="Also check robots/sitemap/llms files", value=False)
                audit_ai_decisions = gr.Checkbox(label="Uses AI for consequential decisions", value=False)
            with gr.Row():
                audit_patient_data = gr.Checkbox(label="Handles patient/health data in this public app", value=False)
                audit_recommendations = gr.Checkbox(label="Makes clinical/legal recommendations", value=False)
        run_site_audit = gr.Button("Run YMYL Readiness Audit", variant="primary")
        with gr.Row():
            audit_summary = gr.JSON(label="Audit Summary")
            audit_markdown = gr.Markdown()
        audit_table = gr.Dataframe(headers=["Dimension", "Check", "Status", "Points", "Fix"], label="Detailed Checks", interactive=False, wrap=True)
        run_site_audit.click(audit_site, inputs=[audit_url, audit_html, audit_jsonld, audit_provider, audit_credential, audit_practice, audit_phone, audit_address, audit_conflicts, audit_fetch_support, audit_ai_decisions, audit_patient_data, audit_recommendations], outputs=[audit_summary, audit_table, audit_markdown])

    with gr.Tab("Summary"):
        gr.Code(value=case_summary(), language="json", label="Entity Summary")
        gr.JSON(value=score_summary(), label="Score Summary")

    with gr.Tab("Scores"):
        gr.Dataframe(headers=["Track", "Before", "Current", "Target", "Notes"], value=SCORE_ROWS, interactive=False)

    with gr.Tab("URL Tracking"):
        gr.Dataframe(headers=["Asset", "Type", "Title", "URL", "Status", "Notes"], value=URL_ROWS, interactive=False)

    with gr.Tab("Safety"):
        gr.Markdown("This public app is not medical advice, legal advice, psychological treatment, emergency support, or a compliance certification. Clinical wording, NPI/license display, and final publication metadata require Dr. Gayer or authorized office approval before full release.")


if __name__ == "__main__":
    demo.launch()
