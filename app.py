from __future__ import annotations

import json

import gradio as gr


SCORE_ROWS = [
    ["Helpful content", 62, 181, 200, "People-first pages and practice-specific content improved; final theme-builder cleanup remains."],
    ["E-E-A-T and YMYL trust", 36, 187, 200, "Expert/practice identity is clearer; final office review and directory correction remain."],
    ["Canonical and crawling", 66, 188, 200, "Canonical, robots, llms.txt, and entity graph plugin layer is packaged; live activation remains."],
    ["Structured data", 32, 191, 200, "Person/practice/renter separation and medical schema are packaged; live validation remains."],
    ["AEO and AI features", 35, 180, 200, "Plain-language AI guidance and reproducible datasets are packaged; public DOI/Kaggle/ORCID links remain."],
    ["TOTAL", 231, 927, 1000, "Internal audit score only; not a Google certification."],
]

URL_ROWS = [
    ["URL001", "owned_site", "Positive Outcomes homepage", "https://positive-outcomes.com/", "live_needs_plugin", "Canonical practice URL."],
    ["URL002", "owned_site", "About Harvey L. Gayer", "https://positive-outcomes.com/about-us/", "live_rewritten", "Primary provider/entity page."],
    ["URL003", "owned_site", "Services", "https://positive-outcomes.com/services/", "live_rewritten", "Therapy/testing/evaluation scope page."],
    ["URL004", "owned_site", "Contact", "https://positive-outcomes.com/contact-us/", "live_rewritten", "Official appointment route."],
    ["URL005", "owned_site", "Location", "https://positive-outcomes.com/about-us/location-directions/", "live_rewritten", "Suite/location page; Maps/GBP verification pending."],
    ["URL006", "public_repo", "GitHub study repo", "https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint", "live_public_safe", "Redacted public-safe repo starter."],
    ["URL007", "hugging_face", "Hugging Face Space", "https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint", "live_public_safe", "Space created under the logged-in InspectorRoofing account."],
    ["URL008", "hugging_face", "Direct Gradio app", "https://inspectorroofing-doctor-ymyl-blueprint.hf.space/", "live_public_safe", "Direct app endpoint for score and URL tracking."],
]


def score_summary() -> dict:
    return {
        "before_total": 231,
        "after_package_total": 927,
        "final_target_total": 1000,
        "note": "Internal audit score only; not a Google certification.",
    }


def case_summary() -> str:
    return json.dumps(
        {
            "expert_person": "Harvey L. Gayer, Ph.D.",
            "practice": "Positive Outcomes Psychological Services, P.C.",
            "separate_entities": "Classic City Psychological Associates and other colocated/renting professionals",
            "entity_rule": "Renting office space does not make a provider part of Positive Outcomes Psychological Services, P.C.",
            "github": "https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint",
            "hugging_face_space": "https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint",
        },
        indent=2,
    )


with gr.Blocks(title="Doctor YMYL Blueprint") as demo:
    gr.Markdown("# Doctor YMYL Blueprint")
    gr.Markdown(
        "A public-safe research preview for YMYL entity clarity, AI search, schema, GEO, SEO, and AEO. "
        "This version excludes hold-only identifiers and internal evidence files."
    )

    with gr.Tab("Summary"):
        gr.Code(value=case_summary(), language="json", label="Entity Summary")
        gr.JSON(value=score_summary(), label="Score Summary")

    with gr.Tab("50-Standard Score"):
        gr.Dataframe(
            headers=["Group", "Before", "After Package", "Final Target", "Notes"],
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
            "require office approval before full release."
        )


if __name__ == "__main__":
    demo.launch()
