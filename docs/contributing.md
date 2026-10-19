# Hướng dẫn đóng góp (Contributing Guide)

Tài liệu này quy định tiêu chuẩn làm việc, quy ước phân nhánh Git, quy trình kiểm thử và nguyên tắc phối hợp dành cho cả 3 thành viên (**A**, **B**, **C**) trong dự án `cis-gke-security-audit`.

---

## 1. Nguyên tắc làm việc cốt lõi

1. **Minh bạch trách nhiệm:** Mỗi thay đổi phải gắn liền với một vai trò chịu trách nhiệm chính (**A**, **B**, hoặc **C**), nhưng các khu vực giao thoa bắt buộc phải được review chéo.
2. **Không tự phê duyệt:** Người tạo Pull Request (PR) **tuyệt đối không tự phê duyệt hoặc tự merge** mã nguồn của chính mình.
3. **Audit chỉ đọc (Read-only):** Mã nguồn của Python Audit Engine chỉ thực hiện các lệnh đọc dữ liệu (`get`, `list`, `describe`). Không tích hợp logic mutate (`create`, `update`, `delete`, `apply`) vào luồng audit.
4. **Phê duyệt tách biệt (Approval Gate):** Thao tác `terraform apply`, `kubectl apply` hoặc thay đổi cấu hình hạ tầng/lab là một quy trình tách biệt, bắt buộc có người phê duyệt trước khi thực thi trên môi trường thật. **Merge PR vào nhánh `main` không đồng nghĩa với tự động áp dụng lên Cloud.**
5. **Bảo mật thông tin:** Tuyệt đối không commit credentials, GCP service account keys, tokens, secret values, raw kubeconfig hoặc Terraform state lên repository. Mọi dữ liệu nhạy cảm phải được đưa vào `.gitignore`.
6. **Không đưa file PDF CIS Benchmark vào repo:** Chỉ dẫn chiếu theo tên chuẩn (*CIS GKE Benchmark v2.0.0* / *CIS GKE Autopilot Benchmark v2.0.0* ngày 30/06/2026), mã Control ID, tiêu đề và phân tích kỹ thuật của nhóm.

---

## 2. Quy ước đặt tên nhánh (Branching Strategy)

Tất cả các nhánh phải được tạo từ nhánh `main` mới nhất và tuân thủ định dạng tiền tố sau:

| Tiền tố nhánh | Vai trò chính | Phạm vi áp dụng | Ví dụ |
| :--- | :---: | :--- | :--- |
| `feat/a-*` | **Role A** | Hạ tầng Terraform, GCP Cloud Collector, CI/WIF authentication, mạng VPC/Subnet. | `feat/a-gcs-backend`<br>`feat/a-gcp-collector-cluster-mode`<br>`feat/a-wif-github-actions` |
| `feat/b-*` | **Role B** | Khung Python Audit Engine, CLI Typer, K8s Collector, Normalizers, Evaluator, Rules `4.1.x`, Reporter JSON/HTML. | `feat/b-cli-skeleton`<br>`feat/b-k8s-collector-sa`<br>`feat/b-rule-4-1-4-default-sa`<br>`feat/b-html-reporter` |
| `feat/c-*` | **Role C** | Đặc tả CIS Matrix, Rules `4.2.x` & `4.3.x`, Kubernetes Manifests cho Labs, kịch bản Remediation & Rollback, QA. | `feat/c-cis-matrix-v2`<br>`feat/c-rule-4-2-1-pss`<br>`feat/c-rule-4-3-2-network-policy`<br>`feat/c-lab-service-account` |
| `fix/*` | Chung | Sửa lỗi logic, sửa bug trong collectors, rules, tests hoặc scripts. | `fix/collector-timeout-handling`<br>`fix/rule-4-1-9-system-binding-whitelist` |
| `docs/*` | Chung | Cập nhật tài liệu kỹ thuật, runbooks, diagrams, contracts hoặc ma trận CIS. | `docs/update-contracts-schema`<br>`docs/cis-control-matrix-review` |

---

## 3. Quy trình cộng tác 6 bước (Standard Workflow)

```text
  [ 1. Issue ] ──> [ 2. Branch ] ──> [ 3. Pull Request ]
                                            │
  [ 6. Merge ] <── [ 5. CI Pass ] <── [ 4. Cross-Review ]
```

### Bước 1: Tạo Issue
- Mọi công việc phải bắt đầu bằng một GitHub Issue được tạo từ template:
  - **Task Issue (`task.yml`):** Dành cho việc phát triển tính năng, viết rule, dựng hạ tầng, làm lab. Phải điền rõ Role chịu trách nhiệm, Acceptance Criteria và rủi ro.
  - **Bug Report (`bug_report.yml`):** Dành cho việc báo cáo lỗi sai lệch kết quả, lỗi collector, lỗi cú pháp hoặc sai lệch mapping CIS.

### Bước 2: Tạo Branch
- Checkout nhánh mới từ nhánh `main` đã cập nhật:
  ```bash
  git checkout main
  git pull origin main
  git checkout -b feat/b-rule-4-1-4-default-sa
  ```

### Bước 3: Phát triển & Kiểm thử cục bộ
- Viết mã nguồn kèm theo unit test hoặc fixtures tương ứng.
- Đảm bảo tuân thủ tiêu chuẩn mã nguồn trước khi tạo commit:
  ```bash
  # Định dạng và kiểm tra linter
  ruff check .
  
  # Chạy bộ test cục bộ
  pytest
  ```

### Bước 4: Mở Pull Request (PR)
- Tạo PR trỏ vào nhánh `main`.
- Bắt buộc sử dụng nội dung mẫu tại `.github/pull_request_template.md`.
- Điền đầy đủ:
  - Mục tiêu và Issue liên kết (`Fixes #...`).
  - Tóm tắt thay đổi và Role phụ trách.
  - CIS Mapping & GKE Mode áp dụng (Standard, Autopilot, hoặc cả hai).
  - Bằng chứng kiểm thử (Unit test log, fixture pass). **Tuyệt đối không giả mạo fixture thành live evidence.**
  - Đánh giá rủi ro và kế hoạch Rollback nếu PR có liên quan đến cấu hình lab hoặc hạ tầng.

### Bước 5: Kiểm tra chéo (Cross-Review) & CI
- Tối thiểu 1-2 reviewers phù hợp theo phân quyền tại `.github/CODEOWNERS`:
  - Thay đổi liên quan đến **Data Contracts** (`docs/contracts.md`): B xác nhận schema, A kiểm tra Cloud fields, C kiểm tra ngữ nghĩa bảo mật.
  - Thay đổi liên quan đến **CIS Matrix** (`docs/cis-control-matrix.md`): C phụ trách nội dung, B đối chiếu evaluator, A xác nhận nguồn dữ liệu Cloud.
  - Thay đổi liên quan đến **Terraform**: A làm chính, B/C review tác động mạng và chi phí.
- Toàn bộ pipeline kiểm tra tự động trên GitHub Actions (`.github/workflows/ci.yml`) phải đạt trạng thái **PASS** (xanh).

### Bước 6: Merge vào nhánh chính
- Sau khi có đủ số lượng Approve và CI PASS, PR được merge vào `main` bằng phương thức **Squash and merge**.
- Xóa nhánh tính năng sau khi merge thành công.

---

## 4. Quy chuẩn kỹ thuật khi viết Rule và Fixtures

1. **Không giả định mode:** Mọi rule phải kiểm tra điều kiện áp dụng cho `STANDARD` hay `AUTOPILOT`. Ví dụ: Rule `4.2.1` và `4.3.2` không được kích hoạt khi cluster ở chế độ Autopilot.
2. **Xử lý Manual Controls:** Đối với các control Manual (như `4.1.5` token mount hoặc `4.3.1` enforcement mechanism), engine chỉ thu thập evidence và trả trạng thái `REVIEW` kèm câu hỏi nghiệp vụ cần thẩm định, không tự ý kết luận `PASS` hoặc `FAIL` khi chưa đủ thông tin.
3. **Phân biệt `NOT_IMPLEMENTED` và `N/A`:**
   - `NOT_IMPLEMENTED` / `OUT_OF_SCOPE`: Control nằm trong benchmark nhưng engine chưa viết mã kiểm tra.
   - `N/A`: Control hoàn toàn không tồn tại trong benchmark của mode đang quét (ví dụ `4.2.1` trên Autopilot).
4. **Cấu trúc Fixtures:** Đặt fixtures trong `tests/fixtures/<mode>/<control_id>/` dưới dạng file JSON hoặc YAML mô phỏng raw API response, bao gồm cả các trường hợp: happy path (`PASS`), violation (`FAIL`), edge cases (rỗng, thiếu quyền, timeout).

---

## 5. Kênh hỗ trợ & Trao đổi

- Thảo luận kiến trúc: Trao đổi trực tiếp trên GitHub Issue hoặc PR liên quan.
- Bất đồng về CIS mapping: Căn cứ vào văn bản gốc *CIS GKE Benchmark v2.0.0* và ghi nhận tại `docs/cis-control-matrix.md`.
- Bất đồng về cấu trúc dữ liệu: Căn cứ vào `docs/contracts.md`.
