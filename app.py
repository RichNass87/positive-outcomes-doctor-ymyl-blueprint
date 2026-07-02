from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

import gradio as gr


SCORE_ROWS = [
    ["Trust-proof/AEO", 420, 877, 1000, "Provider/practice separation, restrained claims, schema, llms.txt, Search Console, and public-safe dataset are implemented."],
    ["High-risk/YMYL", 378, 846, 1000, "Public app remains informational and nonclinical; final score requires office review and external evidence capture."],
    ["Google/AEO/YMYL 50-standard", 231, 937, 1000, "Dataset creator/license cleanup added; final target requires GBP/directory/DOI/ORCID/Kaggle proof."],
]

URL_ROWS = [
    ["owned_site", "Positive Outcomes", "https://positive-outcomes.com/", "canonical practice source"],
    ["github", "Public study repo", "https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint", "public-safe source"],
    ["hugging_face", "Space", "https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint", "sync requires authenticated HF session"],
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.in_script = False
        self.in_style = False
        self.script_is_jsonld = False
        self.script_parts: list[str] = []
        self.title: list[str] = []
        self.text: list[str] = []
        self.jsonld: list[str] = []
        self.meta: dict[str, str] = {}
        self.canonical = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): v or "" for k, v in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "style":
            self.in_style = True
        elif tag == "script":
            self.in_script = True
            self.script_is_jsonld = "ld+json" in attr.get("type", "").lower()
            self.script_parts = []
        elif tag == "meta":
            key = attr.get("name") or attr.get("property")
            if key and attr.get("content"):
                self.meta[key.lower()] = attr["content"]
        elif tag == "link" and "canonical" in attr.get("rel", "").lower():
            self.canonical = attr.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "style":
            self.in_style = False
        elif tag == "script":
            if self.script_is_jsonld and self.script_parts:
                self.jsonld.append("".join(self.script_parts).strip())
            self.in_script = False
            self.script_is_jsonld = False
            self.script_parts = []

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self.in_script:
            if self.script_is_jsonld:
                self.script_parts.append(data)
            return
        if self.in_style:
            return
        if self.in_title:
            self.title.append(cleaned)
        else:
            self.text.append(cleaned)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def has_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms if term)


def normalize_url(url: str) -> str:
    candidate = (url or "").strip()
    if candidate and not re.match(r"^https?://", candidate, re.I):
        candidate = f"https://{candidate}"
    return candidate


def fetch_url(url: str) -> tuple[str, dict[str, str]]:
    normalized = normalize_url(url)
    parsed = urllib.parse.urlparse(normalized)
    if not parsed.scheme or not parsed.netloc:
        return "", {"status": "not_requested", "url": normalized}
    request = urllib.request.Request(
        normalized,
        headers={"User-Agent": "DoctorYMYLTrustProofBot/0.1", "Accept": "text/html,*/*;q=0.8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(900_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace"), {"status": str(getattr(response, "status", 200)), "url": normalized, "final_url": response.geturl()}
    except Exception as exc:
        return "", {"status": "fetch_error", "url": normalized, "error": str(exc)}


def parse_page(source: str) -> tuple[PageParser, list[dict], list[str]]:
    parser = PageParser()
    parser.feed(source or "")
    nodes: list[dict] = []
    errors: list[str] = []
    for block in parser.jsonld:
        try:
            data = json.loads(block)
        except Exception as exc:
            errors.append(str(exc))
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict):
                graph = item.get("@graph")
                if isinstance(graph, list):
                    nodes.extend(node for node in graph if isinstance(node, dict))
                nodes.append(item)
    return parser, nodes, errors


def schema_types(nodes: list[dict]) -> set[str]:
    found: set[str] = set()
    for node in nodes:
        raw = node.get("@type")
        if isinstance(raw, str):
            found.add(raw)
        elif isinstance(raw, list):
            found.update(item for item in raw if isinstance(item, str))
    return found


def grade(total: int) -> str:
    if total >= 930:
        return "Study-grade trust proof"
    if total >= 850:
        return "Strong YMYL readiness"
    if total >= 700:
        return "Useful, but public-safety gaps remain"
    if total >= 500:
        return "Material remediation needed"
    return "High-risk: do not treat as publication-ready"


def check(label: str, passed: bool, points: int, fix: str) -> list[str]:
    return [label, "PASS" if passed else "ACTION", str(points if passed else 0), fix if not passed else ""]


def audit_site(url: str, pasted_page: str, pasted_jsonld: str, provider: str, credential: str, practice: str, phone: str, address: str, conflicts: str, ai_decisions: bool, patient_data: bool, clinical_recs: bool) -> tuple[dict, list[list[str]], str]:
    fetched, meta = fetch_url(url) if url.strip() else ("", {"status": "not_requested", "url": ""})
    source = fetched or pasted_page or ""
    if pasted_jsonld.strip():
        source += f"<script type='application/ld+json'>{pasted_jsonld}</script>"
    parser, nodes, errors = parse_page(source)
    types = schema_types(nodes)
    visible = clean(" ".join(parser.title + [parser.meta.get("description", "")] + parser.text + [pasted_jsonld]))
    digits = re.sub(r"\D+", "", visible)
    phone_digits = re.sub(r"\D+", "", phone or "")
    schema_blob = json.dumps(nodes, default=str).lower()
    conflict_terms = [part.strip() for part in re.split(r"[,;\n]", conflicts or "") if part.strip()]
    conflict_attached = any(term.lower() in schema_blob for term in conflict_terms) and any(key in schema_blob for key in ["sameas", "employee", "member", "department"])
    address_hits = sum(1 for part in re.split(r"[, ]+", address or "") if len(part) > 3 and part.lower() in visible.lower())

    ymyl = has_any(visible, ["doctor", "psychologist", "therapy", "medical", "clinic", "patient", "testing", "evaluation", "health"])
    disclaimer = has_any(visible, ["not medical advice", "not legal advice", "emergency", "crisis", "911", "not a substitute"])
    proof = has_any(visible, ["source", "reviewed", "updated", "university", "license", "credential", "approved", "office"])
    restrained = not has_any(visible, ["guaranteed cure", "guaranteed result", "#1", "best doctor", "100% compliant", "certified by google"])
    separation = has_any(visible, ["separate", "not affiliated", "not associated", "rent", "renter", "colocated", "independent"])
    privacy = has_any(visible, ["privacy", "confidential", "hipaa", "patient information"])
    correction = has_any(visible, ["contact", "correction", "email", "phone", "appointment", "call"])
    local_schema = bool(types & {"LocalBusiness", "MedicalBusiness", "MedicalClinic", "Organization"})
    person_schema = "Person" in types

    rows = [
        check("YMYL scope", ymyl, 50, "State the health/high-trust service purpose clearly."),
        check("YMYL scope", disclaimer and not clinical_recs, 50, "Add non-advice/emergency boundaries and avoid diagnosis/treatment/legal decision support."),
        check("Identity", bool(provider and provider.lower() in visible.lower()), 40, "Name the responsible provider/person."),
        check("Identity", bool(credential and credential.lower() in visible.lower()) or has_any(visible, ["licensed", "ph.d", "credential"]), 30, "Show restrained credential/title wording."),
        check("Identity", bool(practice and practice.lower() in visible.lower()), 30, "Name the practice/business entity consistently."),
        check("Contact proof", bool(phone_digits and phone_digits in digits), 35, "Show the current patient phone/contact route."),
        check("Contact proof", address_hits >= 3, 35, "Show current address/suite/city/state/ZIP where appropriate."),
        check("Contact proof", correction, 30, "Add a clear contact/correction/appointment route."),
        check("Trust proof", proof, 40, "Add source, review, update, credential, or office-approval evidence."),
        check("Trust proof", restrained, 40, "Remove guarantees, superlatives, and unsupported certification claims."),
        check("Trust proof", privacy or not ymyl, 20, "Add privacy/confidentiality language for YMYL content."),
        check("Entity separation", not conflict_attached, 40, "Do not attach renters/separate businesses as employees, departments, sameAs, or members."),
        check("Entity separation", separation or not conflict_terms, 40, "Add visible wording when separate colocated entities exist."),
        check("Schema", bool(nodes), 25, "Add JSON-LD for the main person/practice entity."),
        check("Schema", not errors, 25, "Fix malformed JSON-LD."),
        check("Schema", local_schema or person_schema, 25, "Use Person plus MedicalClinic/MedicalBusiness/LocalBusiness where appropriate."),
        check("Schema", bool(parser.canonical) or not url.strip(), 25, "Add rel=canonical to public pages."),
        check("Governance", not ai_decisions, 35, "If AI affects consequential decisions, add notice, impact review, human oversight, correction, and appeal paths."),
        check("Governance", not patient_data, 35, "Do not upload patient or protected health data to public demos."),
        check("Governance", has_any(visible, ["google business", "maps", "directory", "github", "doi", "zenodo", "orcid", "kaggle", "source"]) or not has_any(visible, ["study", "research"]), 30, "For studies, add source registry, DOI/dataset/citation links, and directory monitoring."),
    ]
    total = sum(int(row[2]) for row in rows)
    actions = [row[3] for row in rows if row[1] == "ACTION"][:8]
    summary = {
        "score": total,
        "grade": grade(total),
        "url": meta.get("final_url") or meta.get("url") or "",
        "fetch": meta,
        "ymyl_detected": ymyl,
        "schema_types_found": sorted(types),
        "not_a_certification": "Readiness audit only; not legal, medical, Google, ranking, licensure, diagnosis, treatment, or patient-routing certification.",
        "top_actions": actions,
    }
    markdown = f"## YMYL Trust-Proof Readiness: {total}/1000\n\n**Grade:** {grade(total)}\n\nThis is a remediation screen, not a certification.\n\n### Highest Priority Fixes\n" + "\n".join(f"- {item}" for item in (actions or ["No priority fixes detected from this quick scan."]))
    return summary, rows, markdown


def score_summary() -> dict:
    return {
        "trust_proof_aeo": {"before": 420, "current": 877, "target": 1000},
        "high_risk_ymyl": {"before": 378, "current": 846, "target": 1000},
        "google_aeo_ymyl_50": {"before": 231, "current": 937, "target": 1000},
        "note": "Internal audit score only; not a Google score or certification.",
    }


def case_summary() -> str:
    return json.dumps(
        {
            "expert_person": "Harvey L. Gayer, Ph.D.",
            "practice": "Positive Outcomes Psychological Services, P.C.",
            "thesis": "YMYL trust proof: clear identity, restrained claims, source evidence, entity separation, uncertainty, and correction paths.",
            "public_safety": "Exact NPI/license identifiers are withheld pending Dr. Gayer approval.",
        },
        indent=2,
    )


with gr.Blocks(title="Doctor YMYL Blueprint") as demo:
    gr.Markdown("# Doctor YMYL Blueprint")
    gr.Markdown("A public-safe YMYL trust-proof checker for doctors and high-risk service websites. It tests whether public facts are clear, restrained, source-backed, and safe for humans and AI systems to interpret.")

    with gr.Tab("Site Audit"):
        gr.Markdown("## Check A Site For YMYL Trust Proof\nPaste a URL, page text/HTML, or JSON-LD. The score is a readiness audit, not a certification.")
        audit_url = gr.Textbox(label="Site or page URL", value="https://positive-outcomes.com/")
        page = gr.Textbox(label="Optional pasted HTML or page text", lines=6)
        jsonld = gr.Textbox(label="Optional pasted JSON-LD", lines=6)
        with gr.Row():
            provider = gr.Textbox(label="Expected provider/person", value="Harvey L. Gayer")
            credential = gr.Textbox(label="Expected credential/title", value="Ph.D., Licensed Psychologist")
        with gr.Row():
            practice = gr.Textbox(label="Expected practice/business", value="Positive Outcomes Psychological Services, P.C.")
            phone = gr.Textbox(label="Expected phone", value="706-543-3538")
        address = gr.Textbox(label="Expected address", value="485 Huntington Road, Suite 199, Athens, GA 30606")
        conflicts = gr.Textbox(label="Known separate/conflicting entities", value="Classic City Psychological Associates; other colocated providers")
        with gr.Row():
            ai_decisions = gr.Checkbox(label="Uses AI for consequential decisions")
            patient_data = gr.Checkbox(label="Handles patient/health data in this public app")
            clinical_recs = gr.Checkbox(label="Makes clinical/legal recommendations")
        button = gr.Button("Run YMYL Trust-Proof Audit", variant="primary")
        with gr.Row():
            summary = gr.JSON(label="Audit Summary")
            narrative = gr.Markdown()
        detail = gr.Dataframe(headers=["Dimension", "Status", "Points", "Fix"], label="Detailed Checks", interactive=False)
        button.click(audit_site, inputs=[audit_url, page, jsonld, provider, credential, practice, phone, address, conflicts, ai_decisions, patient_data, clinical_recs], outputs=[summary, detail, narrative])

    with gr.Tab("Summary"):
        gr.Code(value=case_summary(), language="json", label="Case Summary")
        gr.JSON(value=score_summary(), label="Score Summary")

    with gr.Tab("Scores"):
        gr.Dataframe(headers=["Track", "Before", "Current", "Target", "Notes"], value=SCORE_ROWS, interactive=False)

    with gr.Tab("URL Tracking"):
        gr.Dataframe(headers=["Type", "Title", "URL", "Notes"], value=URL_ROWS, interactive=False)

    with gr.Tab("Safety"):
        gr.Markdown("This public app is not medical advice, legal advice, psychological treatment, emergency support, or a compliance certification. It is a trust-proof readiness audit and public-safety study aid.")


if __name__ == "__main__":
    demo.launch()
