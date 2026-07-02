---
license: cc-by-4.0
task_categories:
  - text-classification
  - feature-extraction
language:
  - en
tags:
  - ymyl
  - entity-resolution
  - schema-org
  - healthcare-seo
  - medical-schema
  - answer-engine-optimization
  - high-risk-ai
pretty_name: Positive Outcomes YMYL Entity Separation Study
size_categories:
  - n<1K
---

# Positive Outcomes YMYL Entity Separation Study

This dataset documents a before-and-after entity separation workflow for a local clinical psychology practice where public search and directory signals blended a solo practitioner practice with colocated but separate providers.

The owned website for Positive Outcomes Psychological Services, P.C. is cited as the canonical medical-practice example for the study after live rewrite and office review. Third-party directories are included as evidence sources or conflict sources, not automatically treated as authority.

## Dataset Scope

Entities:

- Harvey L. Gayer, Ph.D.
- Positive Outcomes Psychological Services, P.C.
- Classic City Psychological Associates as a separate colocated entity
- Separate athletics/coaching identity for Harvey Gayer

Key source registry:

- Positive Outcomes owned website: canonical medical-practice example
- University of Georgia profile: independent academic/professional authority source
- NPI Registry: official internal verification source, held from public schema pending office approval
- Healthgrades: conflict source showing Suite 201 and multiple providers
- WebMD: monitored medical directory source; no verified Harvey Gayer profile URL found during current search
- Google Business Profile / Maps: user-supplied embed captured as a high-priority map signal; live profile details still require verification
- Schema.org MedicalBusiness, MedicalClinic, and PsychologicalTreatment: technical schema anchors

## Intended Use

- YMYL entity-resolution research
- Structured-data quality scoring
- Answer-engine optimization testing
- Directory-conflict remediation workflows

## Not Intended For

- Medical advice
- Patient diagnosis or treatment recommendations
- Credential claims without current source verification
- Reidentification of private patient or office records

## Scoring

Scores use 10 dimensions from 0-100 each, with total score from 0-1000.

Entity/AEO baseline estimate: 420/1000.

Entity/AEO after live rewrite/plugin/schema/app package: 877/1000.

Entity/AEO target after remediation: 1000/1000.

High-risk/YMYL baseline estimate: 378/1000.

High-risk/YMYL after live rewrite/plugin/schema/app package: 846/1000.

High-risk/YMYL target before final publication: 1000/1000.

Google/AEO/YMYL 50-standard baseline estimate: 231/1000.

Google/AEO/YMYL 50-standard after package implementation: 937/1000.

Google/AEO/YMYL 50-standard final target: 1000/1000.

## Schema

The study uses Schema.org `Person`, `MedicalClinic`, `MedicalBusiness`, `LocalBusiness`, `PsychologicalTreatment`, `MedicalTest`, `Service`, `Organization`, and `CreativeWork` patterns. Medical schema is constrained to visible, office-approved claims and does not publish NPI/license values until approval.

The study also models Classic City Psychological Associates as a separate colocated organization and uses a visible/provider-facing clarification to avoid implying that renters are providers, employees, departments, or members of Positive Outcomes Psychological Services, P.C.

## Citation

Add Zenodo DOI after publication.
