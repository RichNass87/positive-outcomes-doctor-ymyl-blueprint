---
title: Positive Outcomes Doctor YMYL Blueprint
sdk: gradio
app_file: app.py
license: mit
---

# Positive Outcomes YMYL Entity Separation Study

Local deliverable package for showing how YMYL trust proof works for Dr. Harvey L. Gayer and Positive Outcomes Psychological Services, P.C.: clear identity, restrained claims, source evidence, correction paths, and separation from Classic City Psychological Associates and other colocated providers.

## What This Contains

- `plugin/positive-outcomes-entity-separator/`: WordPress plugin draft.
- `app/`: Static YMYL/AEO scoring app with 0-100 category scores and 0-1000 totals.
- `schema/`: Public entity graph JSON-LD, review-only credential graph, capability model, and scoring rubrics.
- `ai-files/`: Draft `robots.txt` and `llms.txt`.
- `dataset/`: Hugging Face, Kaggle, Zenodo, ORCID, and publication link templates.
- `dataset/url-tracking.*`: Canonical and tracked URLs for GitHub, Hugging Face, DOI, directory, and owned-site references.
- `study/`: Whitepaper outline, academia notes, and site rewrite plan.
- `study/academic-paper-draft.md`: Academic working paper for Richard Nasser and Harvey L. Gayer, Ph.D.
- `study/kdp-manuscript-draft.md`: KDP-style manuscript draft for Dr. Gayer to edit.
- `study/kdp-50-source-working-bibliography.md`: 50-source bibliography bank.
- `study/independent-practices-page.md`: patient-facing clarification page for independent practices at the same address.
- `documents/`: Editable DOCX versions of the academic paper and KDP manuscript.
- `evidence/`: Source-grounded entity notes and conflict map.
- `app.py`: Gradio Doctor YMYL Blueprint scorecard, high-risk publication gate, and site-level YMYL readiness checker.
- `deploy/`: GitHub, Hugging Face, and Zenodo deployment notes.
- `dataset/dr-gayer-google-source-registry.*`: Google-discoverable source registry including UGA, the owned site, NPI Registry, Healthgrades, WebMD monitoring, Maps/GBP, and schema anchors.

## Source Of Truth

The governing business instruction is Dr. Harvey Gayer's June 30, 2026 email:

- Positive Outcomes Psychological Services, P.C. is Dr. Harvey Gayer's solo practice.
- Dr. Gayer is the provider to show for Positive Outcomes.
- Classic City Psychological Associates is separate and rents office space.
- Other providers are not associated with Positive Outcomes.
- The final Positive Outcomes suite should be Suite 199.
- Appointment route should use `706-543-3538` and `PositiveOutcomesOffice@gmail.com`.

## Key Research Findings

- Eight core Positive Outcomes pages were rewritten live to identify Dr. Gayer and Positive Outcomes clearly. The later plugin pass also neutralizes legacy homepage theme-builder residue on the public output.
- UGA verifies Harvey Louis Gayer as Part-time Clinical Assistant Professor, Clinical Program, and describes him as a licensed psychologist and Director of Positive Outcomes Psychological Services, P.C.
- Healthgrades currently blends multiple providers and Suite 201 into the Positive Outcomes group listing, which is a third-party entity-conflict source.
- The office-supplied Google Maps embed identifies Positive Outcomes Psychological Services as the mapped place; the live Google Business Profile details still need office review against Suite 199, `706-543-3538`, and the owned website.
- Dr. Gayer is modeled as a professional person entity through the owned About page, UGA profile, Positive Outcomes practice relationship, source registry, and future approved ORCID/DOI/research metadata. Nonclinical identities are not needed on the public clinical site.
- Official NPI Registry evidence is retained as review-gated credential support. Exact NPI/license identifiers are withheld from the public package until Dr. Gayer approves public wording.
- Harvey's primary owned-site image is `https://positive-outcomes.com/wp-content/uploads/2014/09/gayer.jpg`; schema now uses it as the primary `image`/`primaryImageOfPage` signal.
- The plugin creates `/independent-practices-at-this-address/` to identify Classic City Psychological Associates and other independent providers as separate from Positive Outcomes without attaching them to Dr. Gayer or the Positive Outcomes practice.

## Scoring System

The score system has two 0-1000 tracks:

- Trust-proof/AEO score: 10 categories, each 0-100.
- High-risk/YMYL publication gate: 10 categories, each 0-100.

Baseline and target scores are included as working estimates, not certification:

- Entity baseline: 420/1000
- Entity after live rewrite/plugin/schema/app package: 877/1000
- Entity target after directory/publication/review completion: 1000/1000
- High-risk baseline: 378/1000
- High-risk after live rewrite/plugin/schema/app package: 846/1000
- High-risk target before final publication: 1000/1000
- Combined working score: 399/1000 before, 862/1000 after live rewrite/plugin/schema/app package, 1000/1000 target.
- Google/AEO/YMYL 50-standard score: 231/1000 before, 953/1000 after package implementation, 1000/1000 final target.
- Gemini-derived AEO gap benchmark from user-supplied screenshots: 685/1000 before the v0.3.7 polish pass, 952/1000 after central schema/Q&A/source-proof improvements, 1000/1000 final target after directories, Dr. Gayer approval, DOI/ORCID/Kaggle, and evidence captures.

Final "after" scoring should be rerun after directory corrections, Dr. Gayer approval of public credential language, screenshots/URL Inspection captures, and publication of the DOI/Kaggle/ORCID study assets.

## Gradio App

Install and run locally:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/validate_blueprint.py
python app.py
```

The app is a pre-publication audit tool. It now includes a site-level YMYL readiness checker that accepts a URL, pasted page HTML/text, or pasted JSON-LD and returns a 0-1000 remediation score. It does not diagnose, treat, make patient decisions, provide legal advice, or certify compliance.

On this workstation, the tested local app is running at `http://127.0.0.1:8060`.

## Publication Gate

Do not publish as final until:

- The WordPress plugin/schema is live. Public-safe package source is at plugin version `0.2.6`.
- `/llms.txt` and `/entity-graph.jsonld` are reachable.
- `/independent-practices-at-this-address/` is reachable and indexable.
- Homepage theme-builder residue is corrected or neutralized in public output.
- Google Search Console domain ownership is verified through the DNS provider.
- Google Business Profile and Maps details are office-reviewed.
- Healthgrades and major directories are corrected or logged.
- NPI/license publication decision is office-approved.
- Public-safe GitHub is live; Hugging Face update is staged until the account is authenticated for upload.
- Zenodo DOI, Kaggle, and ORCID links are created.

## Research And KDP Assets

The package includes two editorial deliverables:

- Academic paper draft: `documents/trust-proof-cognitive-alignment-academic-paper.docx`
- KDP manuscript draft: `documents/when-search-learns-like-people-kdp-manuscript.docx`

Dr. Gayer is treated as a Ph.D. licensed psychologist and senior clinical/forensic authority. The manuscript does not describe him as Psy.D. because the verified credential supplied for the case is Ph.D.

## Medical Schema Strategy

The schema strategy intentionally separates authority and conflict:

- The owned Positive Outcomes website is the canonical medical-practice example.
- UGA is an independent authority source for Dr. Gayer's academic/professional role.
- Healthgrades is included as conflict evidence until corrected.
- WebMD is tracked as a monitored directory source; no verified Dr. Gayer WebMD URL is added as `sameAs` unless found and reviewed.
- Medical schema uses `MedicalClinic`, `MedicalBusiness`, `LocalBusiness`, `PsychologicalTreatment`, `MedicalTest`, `Service`, `Person`, and `CreativeWork` patterns, constrained to visible and approved claims.

## Credential Review Graph

The package now includes `schema/harvey-gayer-credential-review-graph.jsonld`. It records Dr. Gayer's review-gated NPI/license evidence, UGA-sourced education/experience facts, and the stale NPI contact-field warning. Exact NPI/license values are intentionally not copied into the public WordPress schema unless Dr. Gayer approves final public wording.

## WordPress Plugin

The local package source has been advanced to `0.3.7` with the expanded credential-safe schema model, AI Summary blocks, footer map/contact proof, Dataset Rich Results cleanup, removal of stale service-availability wording from visible body copy and SEO metadata, a more human-facing About page source section, and a Gemini-derived 685-to-952 AEO gap benchmark. It does these things:

1. Outputs a grounded JSON-LD graph for Dr. Gayer and Positive Outcomes.
2. Keeps Dr. Gayer's professional person entity separate from, but connected to, the clinical practice entity.
3. Adds public `llms.txt` and `entity-graph.jsonld` endpoints.
4. Adds noindex protection for hard conflict pages while allowing official "not Classic City" clarification pages to stay indexable.
5. Adds Google Search Console URL-prefix verification meta and supports DNS-domain verification documentation.
6. Keeps `robots.txt` focused on the real XML sitemap while linking the entity graph as a comment.
7. Models Dr. Gayer's public-safe credentials, UGA affiliation, and person/practice/entity separation without exposing review-gated identifier numbers.
8. Adds Dataset `creator`, `publisher`, `license`, `usageInfo`, `dateModified`, and `inLanguage` fields to clear Google optional structured-data notices without inventing an open clinical-content license.
9. Adds a plain-language trust-proof block, more conversational FAQ answers, and source-priority language so public readers and AI systems see the same restrained proof structure.

Install path:

`wp-content/plugins/positive-outcomes-entity-separator/positive-outcomes-entity-separator.php`

The live plugin does not publish NPI/license values by default. Publish those only after office approval of the exact public language.

## Publication Links

`dataset/publication-links.json` contains placeholders for:

- GitHub repository
- Hugging Face dataset
- Zenodo DOI
- Kaggle dataset
- ORCID work record

Those should be filled after the public artifacts exist.

Current public-safe GitHub repository:

`https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint`

Current Hugging Face Space:

`https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint`

Current live Gradio score app:

`https://inspectorroofing-doctor-ymyl-blueprint.hf.space/`
