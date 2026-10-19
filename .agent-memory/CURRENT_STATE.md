# Project Current State: cis-gke-security-audit

## Overview
Hệ thống đánh giá và tăng cường bảo mật tự động dành cho Google Kubernetes Engine (GKE) theo hai chuẩn CIS Benchmark v2.0.0 (30/06/2026) cho Standard và Autopilot.

## Project Status: Initial Setup / Draft (Chưa triển khai)
- Chưa chạy `terraform apply` hoặc `kubectl apply`; chưa tạo tài nguyên thật trên Google Cloud.
- Chưa thực thi audit trên cluster thật; các fixtures chỉ phục vụ kiểm thử logic offline.
- Dự án không chứa file binary PDF của CIS; chỉ dẫn chiếu mã control và diễn giải kỹ thuật.

## Core Scope (P0 - 6 CIS Controls)
- `4.1.4` (Level 1 · Automated): Workload không dùng default ServiceAccount (Standard & Autopilot) - Owner: B, Review: C
- `4.1.5` (Level 1 · Manual / `REVIEW`): Không mount token SA nếu không cần K8s API (Standard & Autopilot) - Owner: B, Review: C
- `4.1.9` (Level 1 · Automated): Không cấp custom RBAC cho system:authenticated (Standard & Autopilot) - Owner: B, Review: C
- `4.2.1` (Level 1 · Manual): Enforce PSS baseline/restricted trên namespace (CHỈ CÓ TRÊN STANDARD) - Owner: C, Review: B
- `4.3.1` (Manual): Đánh giá cơ chế NetworkPolicy enforcement (Standard L1: Dataplane V2 / Calico; Autopilot L2: Dataplane V2) - Owner: C, Review: A, B
- `4.3.2` (Level 2 · Automated): Default-deny NetworkPolicy ingress/egress (CHỈ CÓ TRÊN STANDARD) - Owner: C, Review: A, B

## Team Roles & Ownership
- **Role A (Cloud & Integration Lead):** Terraform (bootstrap, shared VPC, standard, autopilot), Cloud Collector (GCP API), CI/WIF authentication, integration demo, cleanup.
- **Role B (Python Audit & Reporting Lead):** Core Python engine, CLI Typer, K8s Collector, Normalizers, Evaluator, Rules 4.1.x, Data Contracts, Reporter (JSON/HTML), Pytest.
- **Role C (CIS Security, Labs & QA Lead):** CIS Matrix v2.0.0, Rules 4.2.x & 4.3.x, Labs & Manifests (SA, PSS, NetworkPolicy), Remediation & Rollback workflow, Security QA.

## Governance & Collaboration Assets Initialized
- `README.md`: Mục tiêu, trạng thái chưa triển khai, phạm vi P0, kiến trúc 5 khối, ownership A/B/C, quick start.
- `docs/contributing.md`: Quy ước nhánh `feat/a-*`, `feat/b-*`, `feat/c-*`, `fix/*`, `docs/*`; quy trình 6 bước Issue -> Branch -> PR -> Cross-Review -> CI -> Merge.
- `.github/pull_request_template.md`: Mục tiêu, linked issue, changes, test evidence, CIS mapping/mode, rủi ro, rollback/approval plan.
- `.github/ISSUE_TEMPLATE/`: `task.yml` và `bug_report.yml` dạng GitHub Issue Forms hợp lệ.
- `docs/contracts.md`: DRAFT khung schema dữ liệu (cần B xác nhận types, A review Cloud fields, C review security semantics).
- `.github/CODEOWNERS`: Phân quyền với placeholder usernames, tối thiểu 2 reviewers/vùng, ghi chú thay thế và giới hạn GitHub private Free.
- `.github/workflows/ci.yml`: Pipeline CI cấu hình 2 jobs `terraform-checks` và `python-checks`, trigger trên push/PR vào `main`, quyền `contents: read`.
- `.gitkeep`: Được bảo lưu trong tất cả các thư mục chưa có code (`terraform/*`, `tests/fixtures`, `tests/integration`, `docs/architecture`, `docs/runbooks`).

## Next Actions / Open Decisions for A, B, C
- **Role B:** Xác nhận schema trong `docs/contracts.md` và hiện thực hóa thành Pydantic models trong `src/cis_gke_audit/normalizers/`.
- **Role A:** Review các trường Google Cloud API trong `docs/contracts.md` và thiết kế skeleton cho GCP collector.
- **Role C:** Cập nhật `docs/cis-control-matrix.md` từ format cũ sang CIS Benchmark v2.0.0 chuẩn, đồng thời chuẩn bị manifest cho lab.

