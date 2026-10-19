# CIS GKE Security Audit

Hệ thống đánh giá và tăng cường bảo mật tự động dành cho Google Kubernetes Engine (GKE) dựa trên hai bộ chuẩn CIS Benchmark v2.0.0 (phát hành ngày 30/06/2026):
- **CIS Google Kubernetes Engine (GKE) Benchmark v2.0.0** (áp dụng cho GKE Standard)
- **CIS Google Kubernetes Engine (GKE) Autopilot Benchmark v2.0.0** (áp dụng cho GKE Autopilot)

> **Thông báo quan trọng về bản quyền & tính pháp lý:**  
> Dự án này là công cụ độc lập do đội ngũ kỹ sư xây dựng nhằm tham chiếu và đối soát theo các khuyến nghị an ninh mở của Center for Internet Security (CIS). Dự án **không phải là CIS-CAT**, không được CIS tài trợ hay chứng nhận chính thức, và không tuyên bố một cụm GKE đạt "chứng nhận CIS". Các tài liệu PDF gốc của CIS Benchmark **không được lưu trữ trong repository** này; dự án chỉ dẫn chiếu theo mã Control ID, tiêu đề, và diễn giải kỹ thuật của nhóm.

---

## 1. Trạng thái dự án (Project Status)

- **Giai đoạn hiện tại:** `KHỞI TẠO NỀN TẢNG (INITIAL SETUP / DRAFT / CHƯA TRIỂN KHAI)`.
- **Hạ tầng Cloud:** Mã nguồn Terraform đã được phân vùng nhưng **chưa chạy `terraform apply`**; chưa có tài nguyên thật trên Google Cloud.
- **Audit Engine:** Đang xây dựng khung code (skeleton), CLI, và các hợp đồng dữ liệu (data contracts). **Chưa chạy audit trên cluster thật**.
- **Dữ liệu kiểm thử:** Tất cả các kết quả mẫu hoặc test fixtures trong repo hiện tại chỉ phục vụ unit tests offline, **tuyệt đối không phải là bằng chứng (evidence) thu thập từ môi trường thật**.

---

## 2. Mục tiêu dự án

1. **Đánh giá tự động theo đúng chế độ cụm (Mode-aware Audit):** Tự động phát hiện cluster chạy GKE Standard hay GKE Autopilot để áp dụng đúng tập rule từ benchmark tương ứng.
2. **Minh bạch bằng chứng (Evidence-based Findings):** Mỗi kết luận (`PASS`, `FAIL`, `REVIEW`, `N/A`, `ERROR`) đều phải đính kèm bằng chứng cấu hình thực tế, thời điểm quét, và lý do kỹ thuật rõ ràng.
3. **Tách biệt đánh giá và khắc phục (Read-only by Default):** Engine audit chỉ đọc (read-only), không bao giờ tự ý sửa đổi cụm. Thao tác khắc phục (Remediation) phải qua phê duyệt và kiểm soát nghiêm ngặt.
4. **Minh họa Hardening có kiểm soát:** Thực nghiệm 2 kịch bản tăng cường an ninh mẫu trong môi trường lab (Service Account Hardening & NetworkPolicy Default-Deny), có đo lường trước/sau (before/after), kiểm thử chức năng ứng dụng, và sẵn sàng kế hoạch rollback.

---

## 3. Phạm vi P0 (Core CIS Scope)

Đội ngũ tập trung tối đa nguồn lực vào 6 CIS Controls cốt lõi thuộc nhóm `P0`:

| CIS ID | Tiêu đề kiểm tra | GKE Standard | GKE Autopilot | Người phụ trách chính |
| :---: | :--- | :---: | :---: | :---: |
| **4.1.4** | Ensure default Service Account is not actively used by workloads | Level 1 · Automated | Level 1 · Automated | **B** (Review: C) |
| **4.1.5** | Ensure Service Account token is only mounted when workload requires K8s API | Level 1 · Manual (`REVIEW`) | Level 1 · Manual (`REVIEW`) | **B** (Review: C) |
| **4.1.9** | Ensure custom RBAC is not granted to `system:authenticated` group | Level 1 · Automated | Level 1 · Automated | **B** (Review: C) |
| **4.2.1** | Ensure Pod Security Admission (PSS `baseline`/`restricted`) is enforced on workload namespaces | Level 1 · Manual | **Không có trong Autopilot v2.0.0** | **C** (Review: B) |
| **4.3.1** | Evaluate NetworkPolicy enforcement mechanism | Level 1 · Manual (Dataplane V2 / Calico) | Level 2 · Manual (Dataplane V2 built-in) | **C** (Review: A, B) |
| **4.3.2** | Ensure default-deny NetworkPolicy (ingress & egress) is enforced on workload namespaces | Level 2 · Automated | **Không có trong Autopilot v2.0.0** | **C** (Review: A, B) |

### Ghi chú quan trọng về ngữ nghĩa đánh giá:
- **Khác biệt Benchmark:** Control `4.2.1` và `4.3.2` **chỉ tồn tại trong Standard Benchmark v2.0.0**, không áp dụng cho Autopilot.
- **Khác biệt Level:** Control `4.3.1` xếp hạng **Level 1** trên Standard (yêu cầu kiểm tra Dataplane V2 hoặc Calico), nhưng xếp hạng **Level 2** trên Autopilot (chỉ ghi nhận Dataplane V2 tích hợp sẵn).
- **Phân định rõ trạng thái:** Các rule chưa được lập trình phải được đánh dấu rõ ràng trong metadata là `NOT_IMPLEMENTED` hoặc `OUT_OF_SCOPE`, **tuyệt đối không được đánh tráo thành `N/A` hay `PASS`**. Trạng thái `N/A` chỉ dùng khi control không tồn tại trong benchmark của mode tương ứng.

---

## 4. Kiến trúc hệ thống (System Architecture)

Hệ thống được thiết kế theo mô hình 5 khối chức năng độc lập với ranh giới trách nhiệm rõ ràng:

```text
[ Khối 1: Git & Collaboration ]  ──>  [ Khối 2: CI / Quality Gate ]
  • Git branch, PR review               • Ruff, Pytest, Terraform fmt/validate
  • CODEOWNERS, Issue templates         • Không cấp quyền mutate Cloud

[ Khối 3: GCP Infrastructure (IaC) ]
  • Terraform: VPC & Subnets (shared), GKE Standard, GKE Autopilot
  • GCS Backend với state độc lập (shared, standard, autopilot)

[ Khối 4: Python CIS Audit Engine (Out-of-cluster, Read-only) ]
  • Collectors: Google Cloud API Collector (A) + K8s API Collector (B)
  • Normalizers & Evaluator: Chuẩn hóa dữ liệu & đối soát theo mode (B)
  • Rule Registry: Quản lý rules 4.1.x (B) và 4.2.x/4.3.x (C)

[ Khối 5: Reporting & Controlled Remediation ]
  • Reporter: Xuất kết quả JSON & HTML kèm bằng chứng (B)
  • Labs & Hardening: Service Account & NetworkPolicy manifests (C)
  • Controlled Rollback & Post-audit Re-evaluation (A + B + C)
```

---

## 5. Phân công trách nhiệm (A / B / C Ownership)

| Thành viên | Vai trò | Khu vực sở hữu chính | Trách nhiệm cốt lõi |
| :--- | :--- | :--- | :--- |
| **A** | **Cloud & Integration Lead** | `/terraform/`<br>`/src/cis_gke_audit/collectors/gcp/`<br>`.github/workflows/` (IaC & WIF) | • Quản lý Google Cloud project, IAM, chi phí và hạn mức (quota).<br>• Xây dựng Terraform cho VPC, Subnets, GKE Standard, GKE Autopilot.<br>• Viết Google Cloud API collector (read-only) thu thập cấu hình cluster/network.<br>• Quản trị CI/WIF authentication, điều phối tích hợp end-to-end và cleanup. |
| **B** | **Python Audit & Reporting Lead** | `/src/cis_gke_audit/`<br>`/tests/`<br>`docs/contracts.md` | • Kiến trúc phần mềm Python Audit Engine, thiết kế Typer CLI.<br>• Viết Kubernetes API collector (read-only) và normalizers.<br>• Quản trị data contracts, rule registry, evaluator và bộ rule `4.1.4`, `4.1.5`, `4.1.9`.<br>• Xây dựng reporter xuất JSON/HTML và cơ chế so sánh Before/After. |
| **C** | **CIS Security, Labs & QA Lead** | `/labs/`<br>`/src/cis_gke_audit/rules/` (4.2.x, 4.3.x)<br>`docs/cis-control-matrix.md` | • Chuẩn hóa ma trận CIS Benchmark v2.0.0 theo Standard và Autopilot.<br>• Lập trình security rules `4.2.1`, `4.3.1`, `4.3.2` theo interface chung của B.<br>• Xây dựng Kubernetes manifests và môi trường lab (SA, PSS, NetworkPolicy).<br>• Chủ trì kịch bản Remediation (phê duyệt, backup, thực thi, functional test, rollback). |

---

## 6. Cấu trúc thư mục

```text
cis-gke-security-audit/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml       # Form báo cáo lỗi chuẩn GitHub
│   │   └── task.yml             # Form tạo task công việc phân vai A/B/C
│   ├── workflows/
│   │   └── ci.yml               # Pipeline kiểm tra linting và unit tests
│   ├── CODEOWNERS               # Quy định reviewers tối thiểu cho từng vùng
│   └── pull_request_template.md # Template PR chuẩn cho dự án
├── docs/
│   ├── architecture/            # Sơ đồ và tài liệu kiến trúc
│   ├── runbooks/                # Hướng dẫn vận hành, triển khai và dọn dẹp
│   ├── cis-control-matrix.md    # Ma trận đối chiếu chi tiết CIS Controls v2.0.0
│   ├── contracts.md             # DRAFT khung schema trao đổi dữ liệu nội bộ
│   └── contributing.md          # Hướng dẫn quy trình đóng góp và Git workflow
├── labs/                        # Kịch bản thực nghiệm an ninh (Role C)
│   ├── network-policy/          # Lab NetworkPolicy default-deny & allow rules
│   ├── pod-security/            # Lab Pod Security Admission baseline/restricted
│   └── service-account/         # Lab Service Account hardening & token mount
├── src/cis_gke_audit/           # Mã nguồn Python Audit Engine (Role B)
│   ├── collectors/              # API Collectors (Cloud API: A, K8s API: B)
│   ├── evaluation/              # Engine đối soát rule và đánh giá kết quả
│   ├── normalizers/             # Chuẩn hóa tài nguyên thành models thống nhất
│   ├── reporting/               # Xuất báo cáo JSON / HTML
│   ├── rules/                   # Định nghĩa logic các rule CIS (B & C)
│   └── cli.py                   # Điểm vào dòng lệnh (CLI Interface)
├── terraform/                   # Mã nguồn hạ tầng Google Cloud (Role A)
│   ├── bootstrap/               # GCS Bucket backend cho Terraform state
│   ├── shared/                  # Mạng dùng chung (VPC, Subnets, Firewall)
│   ├── standard/                # Cụm GKE Standard
│   └── autopilot/               # Cụm GKE Autopilot
├── tests/                       # Bộ kiểm thử tự động
│   ├── fixtures/                # Dữ liệu giả lập phục vụ unit tests
│   ├── integration/             # Kiểm thử tích hợp
│   └── unit/                    # Kiểm thử đơn vị các module
├── .gitignore                   # Loại trừ secrets, credentials, tfstate, v.v.
├── pyproject.toml               # Cấu hình dự án Python, dependencies, ruff, pytest
└── README.md                    # Tài liệu tổng quan dự án
```

---

## 7. Quy trình đóng góp (Contributing)

Mọi thành viên tuân thủ quy trình cộng tác chặt chẽ để đảm bảo an toàn và tính toàn vẹn:
1. **Tạo Issue:** Mô tả rõ mục tiêu, phân vai (A / B / C) và acceptance criteria.
2. **Tạo Branch:** Tuân thủ tiền tố: `feat/a-*`, `feat/b-*`, `feat/c-*`, `fix/*`, hoặc `docs/*`.
3. **Mở Pull Request:** Sử dụng `.github/pull_request_template.md`, ghi rõ CIS mapping, mode, rủi ro, và bằng chứng kiểm thử.
4. **Kiểm tra chéo & CI:** Tối thiểu 1-2 reviewers phê duyệt; CI phải PASS. Người tạo PR không được tự duyệt.
5. **Merge:** Hợp nhất qua `Squash and merge`.

> Xem chi tiết tại [Tài liệu hướng dẫn đóng góp](docs/contributing.md).

---

## 8. Hướng dẫn phát triển cục bộ (Local Development)

```bash
# 1. Khởi tạo môi trường ảo Python
python -m venv .venv
source .venv/bin/activate  # Trên Linux/macOS
# hoặc: .venv\Scripts\Activate.ps1 trên Windows

# 2. Cài đặt package ở chế độ editable cùng dev dependencies
pip install -e ".[dev]"

# 3. Kiểm tra mã nguồn với Ruff
ruff check .

# 4. Chạy toàn bộ kiểm thử đơn vị
pytest
```
