from __future__ import annotations

import json

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
    ["URL007", "hugging_face", "Hugging Face Space", "https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint", "live_public_safe", "Space under the InspectorRoofing account."],
    ["URL008", "hugging_face", "Direct Gradio app", "https://inspectorroofing-doctor-ymyl-blueprint.hf.space/", "live_public_safe", "Direct app endpoint for score and URL tracking."],
]


def score_summary() -> dict:
    return {
        "entity_aeo": {"before": 420, "current": 877, "target": 1000},
        "high_risk_ymyl": {"before": 378, "current": 846, "target": 1000},
        "google_aeo_ymyl_50": {"before": 231, "current": 937, "target": 1000},
        "note": "Internal audit score only; not a Google score, legal certification, compliance certification, diagnosis, treatment recommendation, or patient-routing tool.",
    }


def case_summary() -> str:
    return json.dumps(
        {
            "expert_person": "Harvey L. Gayer, Ph.D.",
            "practice": "Positive Outcomes Psychological Services, P.C.",
            "separate_entities": "Classic City Psychological Associates and other colocated/renting professionals",
            "entity_rule": "Renting office space does not make a provider part of Positive Outcomes Psychological Services, P.C.",
            "public_safety": "Exact NPI/license identifiers are withheld pending Dr. Gayer approval.",
            "dataset_schema_cleanup": "Dataset creator, publisher, license, usageInfo, dateModified, and inLanguage fields were added for public structured-data hygiene.",
            "github": "https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint",
            "hugging_face_space": "https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint",
        },
        indent=2,
    )


with gr.Blocks(title="Doctor YMYL Blueprint") as demo:
    gr.Markdown("# Doctor YMYL Blueprint")
    gr.Markdown(
        "A public-safe research preview for YMYL entity clarity, AI search, schema, GEO, SEO, and AEO. "
        "This version excludes exact hold-only credential identifiers and internal evidence files."
    )

    with gr.Tab("Summary"):
        gr.Code(value=case_summary(), language="json", label="Entity Summary")
        gr.JSON(value=score_summary(), label="Score Summary")

    with gr.Tab("Scores"):
        gr.Dataframe(
            headers=["Track", "Before", "Current", "Target", "Notes"],
            value=SCORE_ROWS,
            interactive=False,
        )

    with gr.Tab("URL Tracking"):
        gr.Dataframe(
            headers=["Asset", "Type", "Title", "URL", "Status", "Notes"],
            value=URL_ROWS,
            interactive=False,
        )

    with gr.Tab("Safety"):
        gr.Markdown(
            "This public app is not medical advice, legal advice, psychological treatment, emergency support, "
            "or a compliance certification. Clinical wording, NPI/license display, and final publication metadata "
            "require Dr. Gayer or authorized office approval before full release."
        )


if __name__ == "__main__":
    demo.launch()
