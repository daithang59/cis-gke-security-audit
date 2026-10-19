## 1. Mục tiêu (Goal / Objective)
<!-- Tóm tắt ngắn gọn mục tiêu của Pull Request này: giải quyết vấn đề gì, tính năng nào được bổ sung hoặc lỗi nào được khắc phục -->


## 2. Issue liên kết (Linked Issue)
<!-- Dẫn chiếu issue tương ứng, ví dụ: Fixes #12 hoặc Relates to #34 -->
Fixes #

---

## 3. Vai trò phụ trách & Phạm vi thay đổi (Role & Scope)

### Vai trò chính (Owner):
- [ ] **Role A (Cloud & Integration Lead):** Terraform (Bootstrap, Shared, GKE Standard, Autopilot) / GCP Collectors / CI & WIF
- [ ] **Role B (Python Audit & Reporting Lead):** Core Engine / K8s Collector / Normalizers / Rules 4.1.x / Reporter / CLI
- [ ] **Role C (CIS Security, Labs & QA Lead):** CIS Matrix / Rules 4.2.x & 4.3.x / Labs & Manifests / Remediation & QA

### Loại thay đổi (Type of Change):
- [ ] Tính năng mới (New feature)
- [ ] Sửa lỗi (Bug fix)
- [ ] Thay đổi hợp đồng dữ liệu / Breaking change (Contracts update)
- [ ] Cập nhật tài liệu / Runbooks (Documentation)
- [ ] Cập nhật Labs / Test Fixtures (Testing assets)

---

## 4. Đối chiếu CIS Benchmark v2.0.0 (CIS Mapping & Mode)

### GKE Mode áp dụng:
- [ ] **GKE Standard** (*CIS Google Kubernetes Engine Benchmark v2.0.0*)
- [ ] **GKE Autopilot** (*CIS Google Kubernetes Engine Autopilot Benchmark v2.0.0*)
- [ ] Không áp dụng (Thay đổi hạ tầng chung, CI, hoặc tài liệu)

### CIS Control ID liên quan:
- [ ] **4.1.4** - Ensure default ServiceAccount is not used by workloads (Level 1 · Automated)
- [ ] **4.1.5** - Ensure SA token is only mounted when workload requires API (Level 1 · Manual / `REVIEW`)
- [ ] **4.1.9** - Ensure custom RBAC is not granted to `system:authenticated` (Level 1 · Automated)
- [ ] **4.2.1** - Ensure PSS `baseline`/`restricted` is enforced on namespaces (Level 1 · Manual) *(Standard only)*
- [ ] **4.3.1** - Evaluate NetworkPolicy enforcement mechanism (Standard: Level 1 · Manual; Autopilot: Level 2 · Manual)
- [ ] **4.3.2** - Ensure default-deny NetworkPolicy is enforced on namespaces (Level 2 · Automated) *(Standard only)*
- [ ] Không liên quan trực tiếp đến 6 P0 controls

---

## 5. Kết quả kiểm thử & Bằng chứng (Test Results & Evidence)

> **LƯU Ý:** Fixtures offline chỉ phục vụ kiểm thử logic của unit tests, **tuyệt đối không mô tả fixtures là live evidence**. Nếu có kết quả chạy trên cụm GKE thật, ghi rõ context, timestamp và git commit.

### Đã chạy kiểm thử:
- [ ] `ruff check .` đạt chuẩn không có lỗi.
- [ ] `pytest tests/unit/` đạt 100% PASS.
- [ ] `pytest tests/fixtures/` bao phủ cả case PASS, FAIL, và Edge cases.
- [ ] (Tùy chọn) Live audit test trên cụm GKE lab (đính kèm bằng chứng bên dưới nếu có).

### Bằng chứng kiểm thử (Evidence output / logs):
```text
<!-- Dán kết quả chạy pytest hoặc output CLI tại đây -->
```

---

## 6. Đánh giá rủi ro (Risk Assessment)
<!-- Đánh giá các rủi ro có thể phát sinh:
- Có làm vỡ schema hợp đồng dữ liệu trong `docs/contracts.md` không?
- Có làm tăng chi phí Cloud ngoài dự kiến không?
- Có nguy cơ chặn nhầm lưu lượng mạng của workload trong lab không?
-->
- **Mức độ rủi ro:** [ ] Thấp | [ ] Trung bình | [ ] Cao
- **Chi tiết:** 

---

## 7. Kế hoạch Phê duyệt & Rollback (Approval & Rollback Plan)
<!-- Bắt buộc điền nếu PR có liên quan đến thay đổi cấu hình hạ tầng Terraform hoặc thay đổi cấu hình Lab Kubernetes -->
- **Người phê duyệt (Approver):** `@...`
- **Tài nguyên bị ảnh hưởng (Target resources/namespaces):** 
- **Quy trình Rollback chi tiết (Step-by-step rollback):**
  1. 
  2. 
- **Kiểm tra chức năng sau rollback (Functional test):**

---

## 8. Checklist trước khi Merge
- [ ] Mã nguồn đã được tự review cục bộ trước khi mở PR.
- [ ] Không chứa credential, API key, token, private key, raw kubeconfig hoặc tfstate.
- [ ] Không commit file binary PDF của CIS Benchmark vào repository.
- [ ] Đã tag đủ ít nhất 2 reviewers phù hợp theo `.github/CODEOWNERS`.
- [ ] Đã cập nhật tài liệu liên quan trong thư mục `docs/` (nếu có thay đổi schema hoặc matrix).
