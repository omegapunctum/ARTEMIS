# ARTEMIS product context

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The owner initially contributes source-aware records personally; later contributors and editorial reviewers use explicit server permissions.

## Product Purpose

ARTEMIS represents source-aware knowledge about the world through one spatial-temporal semantic core. The authorized editor pilot lets a person save a new architecture-object proposal, attach one Source and atomic Claim, review exact submitted content, explicitly publish a candidate card, and correct it without erasing accepted history.

## Operating Context

Canonical authority and current capability remain in [Project Truth](docs/PROJECT_TRUTH.md), [Product Scope](docs/ARTEMIS_PRODUCT_SCOPE.md), [Data Contract](docs/DATA_CONTRACT.md), [Epistemic Contract](docs/EPISTEMIC_CONTRACT.md) and the [bounded editor specification](docs/work/2026-10-07_KNOWLEDGE_EDITOR_v1.md). This design context is not another lifecycle or domain owner.

## Capabilities and Constraints

Reuse the existing web/FastAPI/auth stack. The pilot uses separate SQLite-backed editorial records and URL/bibliographic Sources. Unknown dates, locations, confidence and rights remain unknown. Editorial acceptance and explicit publication are separate; owner self-review is labeled. There is no automatic AI content generation, historical acceptance, legacy Airtable write, frozen-package migration or Globe corpus intake. Backend hosting and later PostgreSQL/PostGIS/file-storage provisioning remain open deployment work.

## Brand Commitments

Preserve the established ARTEMIS interface identity and factual product terminology. The user approved a Russian-first working form; direct code implementation was selected over a preliminary visual mockup.

## Evidence on Hand

Existing runtime CSS and browser captures establish incumbent visual authority. New editor test data must be explicitly synthetic; technical review does not validate historical content or user value.

## Product Principles

- Preserve source provenance and independent epistemic dimensions.
- Save incomplete work and disclose which fields are needed for submission.
- Keep accepted revisions and publication history immutable.
- Record the actual actor and review mode without invented independence.
- Reuse existing visual conventions and verify keyboard and narrow-screen operation.
