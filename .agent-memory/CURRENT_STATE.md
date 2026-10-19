# Project Current State: cis-gke-security-audit

## Overview
CIS Benchmark Security Audit tool for Google Kubernetes Engine (GKE).

## Directory Structure Initialized
- `.github/`: CI workflows, issue templates (task & bug report), PR template, CODEOWNERS.
- `terraform/`: Infrastructure modules for GCS backend (`bootstrap`), VPC & Subnets (`shared`), GKE Standard (`standard`), GKE Autopilot (`autopilot`).
- `src/cis_gke_audit/`: Core Python audit package including `collectors`, `normalizers`, `rules`, `evaluation`, `reporting`, and `cli.py`.
- `tests/`: `fixtures`, `unit`, `integration`.
- `labs/`: Test environments for `service-account`, `network-policy`, and `pod-security`.
- `docs/`: `contracts.md`, `cis-control-matrix.md`, `runbooks/`, `architecture/`.
- Root configs: `pyproject.toml`, `.gitignore`, `README.md`, `LICENSE`.

## Next Steps / Active Tasks
- Implement GCP and Kubernetes data collectors.
- Define rule specifications in `rules/` aligned with CIS Benchmark GKE v1.4.0.
- Setup test harness with fixtures in `tests/fixtures/`.
