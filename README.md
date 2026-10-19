# CIS GKE Security Audit

Hệ thống đánh giá và kiểm tra tuân thủ an ninh theo chuẩn CIS Benchmark dành cho Google Kubernetes Engine (GKE).

## Cấu trúc thư mục dự án

```text
.github/
├── workflows/
│   └── ci.yml
├── ISSUE_TEMPLATE/
│   ├── task.yml
│   └── bug_report.yml
├── pull_request_template.md
└── CODEOWNERS

terraform/
├── bootstrap/       # A: GCS backend
├── shared/          # A: VPC, subnets
├── standard/        # A: GKE Standard
└── autopilot/       # A: GKE Autopilot

src/cis_gke_audit/
├── collectors/      # A: GCP | B: Kubernetes
├── normalizers/     # B
├── rules/           # B + C
├── evaluation/      # B
├── reporting/       # B
└── cli.py           # B

tests/
├── fixtures/        # B + C
├── unit/
└── integration/

labs/
├── service-account/ # C
├── network-policy/  # C
└── pod-security/     # C

docs/
├── contracts.md
├── cis-control-matrix.md
├── runbooks/
└── architecture/

pyproject.toml
.gitignore
README.md
LICENSE
```

## Phân chia trách nhiệm

- **A**: Hạ tầng Terraform (GCS Backend, VPC & Subnets, GKE Standard, GKE Autopilot) & GCP Collectors.
- **B**: Kubernetes Collector, Normalizers, Core Evaluation Engine, Reporting & CLI Interface.
- **C**: Labs kiểm thử thực hành (Service Account, Network Policy, Pod Security) & Rule definition/Fixtures.

## Bắt đầu nhanh (Quick Start)

```bash
# Cài đặt môi trường phát triển
pip install -e ".[dev]"

# Chạy kiểm thử
pytest

# Thực thi CLI
cis-gke-audit --help
```
