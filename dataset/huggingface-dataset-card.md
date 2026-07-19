---
license: cc-by-4.0
task_categories:
  - text-classification
  - feature-extraction
language:
  - en
tags:
  - ymyl
  - trust-proof
  - entity-resolution
  - schema-org
  - healthcare-seo
  - medical-schema
  - answer-engine-optimization
  - high-risk-ai
pretty_name: Positive Outcomes Entity-Clarity Case Study
size_categories:
  - n<1K
---

# Positive Outcomes Entity-Clarity Case Study

This dataset documents a public entity-clarity workflow for a local clinical psychology practice where public search and directory signals blended a solo practitioner practice with colocated but separate providers.

**Public record:** [Zenodo DOI 10.5281/zenodo.21171669](https://doi.org/10.5281/zenodo.21171669)

**Public record creators:** Richard Amir Nasser; Harvey L. Gayer, Ph.D.

**Repository:** https://github.com/RichNass87/positive-outcomes-doctor-ymyl-blueprint

**Research app:** https://huggingface.co/spaces/InspectorRoofing/doctor-ymyl-blueprint
**Paper distribution:** https://www.academia.edu/169828502/Trust_Proof_as_Cognitive_Alignment_A_Two_Voice_YMYL_Case_Study_in_Google_AI_Search_Source_Proof_Entity_Separation_and_Human_Trust_Psychology

The owned website for Positive Outcomes Psychological Services, P.C. is cited as the canonical medical-practice example for the study after live rewrite and office review. Third-party directories are included as evidence sources or conflict sources, not automatically treated as authority.

## Dataset Scope

Entities:

- Harvey L. Gayer, Ph.D.
- Positive Outcomes Psychological Services, P.C.
- Classic City Psychological Associates as a separate colocated entity

Trust-proof signals:

- clear provider and practice identity
- restrained credential wording
- source-backed claims
- current contact facts
- visible uncertainty when review is pending
- separation of renters/colocated professionals
- correction and publication-review gates

## Intended Use

- YMYL trust-proof research
- Structured-data quality scoring
- Answer-engine optimization testing
- Directory-conflict evidence workflows

## Not Intended For

- Medical advice
- Patient diagnosis or treatment recommendations
- Credential claims without current source verification
- Reidentification of private patient or office records
- Legal, medical, Google, regulatory, ranking, or licensure certification

## Scoring Boundary

The included scorecard is an internal gap-analysis tool. It does not certify medical quality, clinical appropriateness, licensure, legal compliance, Google ranking, answer-engine ranking, or the study's independent notability.

## Schema

The study uses Schema.org `Person`, `MedicalClinic`, `MedicalBusiness`, `LocalBusiness`, `PsychologicalTreatment`, `MedicalTest`, `Service`, `Organization`, and `CreativeWork` patterns. Medical schema is constrained to visible, office-approved claims and does not publish NPI/license values until approval.

The study also models Classic City Psychological Associates as a separate colocated organization and uses a visible/provider-facing clarification to avoid implying that renters are providers, employees, departments, or members of Positive Outcomes Psychological Services, P.C.

## Citation

Use the DOI record above. Cite the archive as a public working-paper and dataset package, not as peer-reviewed research.
