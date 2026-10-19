# TÀI LIỆU 03 | Đặc tả CIS Controls v2.0.0 & Phân công triển khai

**Dự án:** Hệ thống đánh giá và tăng cường bảo mật GKE Standard / GKE Autopilot theo CIS Benchmark v2.0.0  
**Loại tài liệu:** Đặc tả kỹ thuật và tiêu chí nghiệm thu — **không phải báo cáo kết quả đã thực hiện**  
**Phiên bản trình bày:** v2.1 — giữ nguyên đặc tả v2, đã chèn 6 hình minh họa  
**Áp dụng cho:** Thành viên A (Cloud & Integration), B (Python Audit & Reporting), C (CIS Security, Labs & QA)  
**Nguồn chuẩn:** *CIS Google Kubernetes Engine (GKE) Benchmark v2.0.0* và *CIS Google Kubernetes Engine (GKE) Autopilot Benchmark v2.0.0*, cùng phát hành ngày 30/06/2026.  
**Đọc kèm:** [Tài liệu 01 — Tổng quan](01_CIS_GKE_TongQuan_CoHinh.md) và [Tài liệu 02 — Phân công](02_CIS_GKE_PhanCong_PhoiHop_CoHinh.md).  
**Nguyên tắc:** Mọi kết quả thử nghiệm, ảnh chụp, số lượng PASS/FAIL và log trong tài liệu này nếu xuất hiện dưới dạng ví dụ đều là **dữ liệu minh họa**, không được trình bày như đã đo từ GKE thật.

---

<a id="muc-luc"></a>

## Mục lục và bản đồ đọc nhanh

**Không cần đọc tuần tự toàn bộ tài liệu.** Chọn mục theo nhiệm vụ đang làm rồi mở đúng control. Phần chi tiết được giữ lại để dùng như tài liệu tra cứu khi code, test và nghiệm thu.

| Nếu đang cần… | Mở ngay |
|---|---|
| Hiểu phạm vi, kết quả phải đạt, ai chịu trách nhiệm | [§1 Cách dùng](#sec-01) · [§2 Ma trận CIS/A-B-C](#sec-02) |
| Viết collector, engine, JSON, kiểm thử chung | [§3 Quy chuẩn kỹ thuật](#sec-03) · [§11 Kiểm thử](#sec-11) · [§12 Contract](#sec-12) |
| Chuẩn bị demo/remediation và phân công phối hợp | [§10 Hai kịch bản](#sec-10) · [§13 Bàn giao](#sec-13) |
| Chốt nghiệm thu và kiểm nguồn | [§14 Checklist](#sec-14) · [§15 Nguồn CIS](#sec-15) |

### Tra cứu nhanh theo CIS Control

| Control | Mục tiêu kiểm tra | Mode | Người viết rule | Xem đặc tả |
|---|---|---|---|---|
| **4.1.4** | Workload dùng `default` ServiceAccount | Standard + Autopilot | **B** | [Mở §4](#cis-414) |
| **4.1.5** | Chỉ mount SA token khi cần API | Standard + Autopilot · Manual | **B** | [Mở §5](#cis-415) |
| **4.1.9** | RBAC gán `system:authenticated` | Standard + Autopilot | **B** | [Mở §6](#cis-419) |
| **4.2.1** | PSS enforce `baseline/restricted` | **Standard** · Manual | **C** | [Mở §7](#cis-421) |
| **4.3.1** | NetworkPolicy enforcement theo mode | Standard + Autopilot · Manual | **C** | [Mở §8](#cis-431) |
| **4.3.2** | Default-deny NetworkPolicy | **Standard** | **C** | [Mở §9](#cis-432) |

> **Quy tắc xuyên suốt:** A phụ trách Cloud/evidence; B phụ trách engine, các rule 4.1.x và reporting; C phụ trách diễn giải CIS, các rule 4.2–4.3, lab và QA. **Audit chỉ đọc; mọi thay đổi phải có phê duyệt riêng.**

---

<a id="sec-01"></a>

## 1. Bắt đầu tại đây — Tài liệu 03 dùng để làm gì?

### 1.1. Vai trò của ba tài liệu

| Tài liệu | Trả lời câu hỏi | Người dùng chính |
|---|---|---|
| **01 — Tổng quan và kế hoạch** | Dự án giải quyết bài toán gì, kiến trúc thế nào, làm những thành phần nào và nghiệm thu toàn hệ thống ra sao? | Cả nhóm |
| **02 — Phân công và phối hợp** | A/B/C chịu trách nhiệm gì, cần nhận gì, bàn giao gì và phối hợp ra sao? | Cả nhóm |
| **03 — Đặc tả CIS** | **Một control cụ thể phải kiểm tra chính xác cái gì, đọc dữ liệu ở đâu, phân loại kết quả thế nào, test ra sao, ai viết phần nào?** | C khi đặc tả và QA; B khi viết engine/rules; A khi cung cấp Cloud evidence và tích hợp |

Một **CIS control** không hoàn thành chỉ vì có hàm Python mang tên control đó. Control chỉ được xem là hoàn thiện ở phạm vi dự án khi: nguồn CIS đúng; có tập dữ liệu đầu vào rõ; rule xử lý đúng các tình huống đã đặc tả; có thử nghiệm PASS/FAIL/REVIEW/ERROR phù hợp; kết quả có bằng chứng truy xuất được; và người kiểm tra chéo xác nhận đúng kỳ vọng. Nếu control liên quan kịch bản khắc phục, còn phải có phê duyệt, backup, kiểm thử chức năng và re-audit.

### 1.2. Cách dùng khi bắt tay triển khai

1. **C** đối chiếu nội dung từng control với PDF và chốt *spec* (điều kiện, ngoại lệ, fixtures, bằng chứng mong đợi).
2. **B** chốt CLI, interface của collector/rule và JSON finding schema; trực tiếp viết nhóm rule `4.1.4`, `4.1.5`, `4.1.9`.
3. **C** trực tiếp viết nhóm rule `4.2.1`, `4.3.1`, `4.3.2` **trên interface chung do B thiết kế**, đồng thời sở hữu YAML lab và security QA.
4. **A** xây môi trường GKE, Google Cloud collector và chuẩn dữ liệu network/mode để các rule sử dụng, rồi cùng B/C kiểm chứng live.
5. Các bước phụ thuộc dữ liệu live chỉ thực hiện khi cluster đã sẵn sàng; **C có thể làm đặc tả/YAML/fixtures và B có thể viết engine/unit tests song song với A dựng hạ tầng**.

> **Phân biệt trách nhiệm:** C là người giữ độ chính xác nội dung CIS; B là người giữ tính nhất quán của Python Audit Engine; A là người giữ tính đúng và an toàn của hạ tầng cùng dữ liệu Google Cloud. **Người làm chính không có nghĩa tự phê duyệt thay đổi cloud hoặc Kubernetes.**

### 1.3. Các thuật ngữ dễ nhầm

| Thuật ngữ | Ý nghĩa trong dự án |
|---|---|
| **CIS Level 1 / Level 2** | Cấp độ khuyến nghị do CIS quy định. Không phải độ ưu tiên triển khai của nhóm. |
| **P0 / P1** | Độ ưu tiên **nội bộ dự án**. Sáu control ở tài liệu này là phạm vi P0 dù có control thuộc CIS Level 2. |
| **Automated / Manual** | Thuộc tính *Assessment Status* của CIS. `Manual` có phần cần người xác minh; không có nghĩa là không thể tự động thu thập bằng chứng. |
| **PASS / FAIL / REVIEW / N/A / ERROR** | Năm trạng thái **do phần mềm của dự án quy ước** để báo cáo. Không phải danh mục trạng thái gốc của CIS. |
| **Evidence** | Dữ liệu/đầu ra dùng làm căn cứ: đối tượng Kubernetes, cấu hình GKE, kết quả admission/traffic/HTTP, thao tác review; phải có nguồn và thời gian. |
| **Fixture** | Dữ liệu giả lập, được kiểm soát trước để chạy pytest; không phải bằng chứng hệ thống GKE thật. |
| **Remediation** | Thao tác thay đổi cấu hình nhằm khắc phục; hoàn toàn **tách** khỏi lệnh audit chỉ đọc. |
| **Mode-aware** | Cùng CIS ID có thể khác điều kiện/Level giữa Standard và Autopilot; phải dùng đúng benchmark của mode. |
| **Owner / Contributor / Reviewer / Approver** | Người chịu trách nhiệm đầu ra / người cùng làm / người review chất lượng / người có thẩm quyền cho phép thao tác có tác động. Reviewer không tự động là Approver. |

---

<a id="sec-02"></a>

## 2. Phạm vi CIS và ma trận phân công

### 2.1. Sáu control sẽ triển khai

| CIS ID | Nội dung cần đánh giá | GKE Standard v2.0.0 | GKE Autopilot v2.0.0 | Làm chính |
|---|---|---|---|---|
| **4.1.4** | Workload không sử dụng `default` ServiceAccount | **L1 — Automated** | **L1 — Automated** | **B** — Python rule; **C** — yêu cầu CIS/lab |
| **4.1.5** | Chỉ mount ServiceAccount token khi workload cần Kubernetes API | **L1 — Manual** | **L1 — Manual** | **B** — rule/REVIEW; **C** — đánh giá ngữ cảnh |
| **4.1.9** | Không gán RBAC tùy biến cho toàn bộ `system:authenticated` | **L1 — Automated** | **L1 — Automated** | **B** — Python rule; **C** — fixtures và QA |
| **4.2.1** | Workload namespace phải thực thi PSS `baseline` hoặc `restricted` | **L1 — Manual** | **Không có ID này** | **C** — rule/lab; **B** — review tích hợp |
| **4.3.1** | Xác minh NetworkPolicy enforcement theo mode | **L1 — Manual**, Dataplane V2/Calico | **L2 — Manual**, Dataplane V2 tích hợp | **C** — rule; **A** — cloud evidence |
| **4.3.2** | Đánh giá default-deny NetworkPolicy cho workload namespace | **L2 — Automated** | **Không có ID này** | **C** — rule/lab; **A** — enforcement/network |

**Không được tự sinh PASS của Autopilot cho `4.2.1` hoặc `4.3.2`**. Khi so sánh hai benchmark có thể ghi `N/A — không có control trong benchmark của mode`; trong một lần audit riêng từng mode nên mặc định chỉ phát sinh control tồn tại trong benchmark đó. `N/A` không tính vào PASS hay mẫu số kiểm tra tuân thủ. `NOT_IMPLEMENTED` và `OUT_OF_SCOPE` là **trạng thái coverage/metadata riêng**, không thay thế bằng `N/A`.

**Chú ý riêng về `4.3.2`:** Tên, *Description* và *Rationale* trong bản Standard v2.0.0 yêu cầu chính sách **default-deny**, nhưng phần *Audit* của control này trong PDF chủ yếu lặp lại phép kiểm tra **enforcement Dataplane V2/Calico**. Vì vậy tài liệu này **phân biệt**:

- **Kiểm tra được PDF mô tả trực tiếp:** xác minh NetworkPolicy thực sự có cơ chế enforcement.
- **Kiểm tra bổ sung của dự án, suy ra từ mục tiêu/tên control:** kiểm tra namespace workload có policy default-deny ingress/egress và phép thử traffic phù hợp. Đây là **đặc tả mở rộng của nhóm**, không được nói nguyên văn rằng PDF có sẵn thuật toán đầy đủ cho phần này.
- Một khi chưa có policy evidence hoặc coverage namespace đầy đủ, **không được kết luận toàn bộ ý nghĩa `4.3.2` đã đạt chỉ từ `ADVANCED_DATAPATH`**. C cần duyệt/ghi nhận quyết định mapping này trong CIS Matrix, B kiểm tra tính nhất quán của reporter, A xác nhận cloud evidence.

### 2.2. Ai làm phần nào trong toàn bộ quy trình?

| Hạng mục của một control | A — Cloud & Integration | B — Python Audit & Reporting | C — CIS Security & QA |
|---|---|---|---|
| Nguồn CIS/ID/Level/mode, điều kiện, ngoại lệ | Review điều kiện Cloud | Review tính có thể lập trình | **Chịu trách nhiệm và ký duyệt spec** |
| Thu thập Kubernetes API | Hỗ trợ quyền/context khi cần | **Sở hữu Kubernetes collector/contract** | Đề xuất resource/field cần đọc; kiểm bằng `kubectl` |
| Thu thập Google Cloud API | **Sở hữu Google Cloud collector/contract** | Tích hợp schema/đọc errors | Đối chiếu trường Cloud với audit procedure |
| Rule `4.1.4`, `4.1.5`, `4.1.9` | Hỗ trợ môi trường và live tests | **Viết code, pytest, xử lý lỗi** | Chuẩn hóa yêu cầu, fixtures, kịch bản/QA |
| Rule `4.2.1`, `4.3.1`, `4.3.2` | Hỗ trợ cloud/network evidence | **Thiết kế interface, review/merge, reporter** | **Viết code trên interface B, pytest/security tests** |
| YAML lab và baseline/after | Hỗ trợ cluster và connectivity | Kết nối audit, ghi kết quả | **Thiết kế và quản lý manifests/lab** |
| Remediation và functional tests | Hỗ trợ impact/rollback network/cloud | Audit, re-audit, before/after JSON/HTML | **Điều phối test và thay đổi có kiểm soát trong lab** |
| Báo cáo, CLI, trạng thái, evidence contract | Cung cấp cloud metadata/integration | **Sở hữu code đầu ra và chuẩn báo cáo** | Kiểm chứng diễn giải CIS/QA |
| PR review và quyền apply | Review thay đổi trong phần liên quan | Review rule/interface; không tự approve thay đổi của mình | Review nội dung CIS/policy; **Approver** là người được ủy quyền riêng |

### 2.3. Giao diện bàn giao dùng chung

| Nguồn → nơi nhận | Phải giao ít nhất | Người nhận dùng để |
|---|---|---|
| **C → B** | Control spec có dẫn chiếu PDF; field list; PASS/FAIL/REVIEW/ERROR cases; ngoại lệ; fixtures/test expectation | B viết 4.1.x, review/tích hợp 4.2.x–4.3.x |
| **A → B/C** | Định danh cluster/mode, trạng thái truy cập, cloud collector output và field `networkConfig.datapathProvider` + Calico fields khi Standard legacy; hướng xác minh read-only | Chọn rule đúng, chạy live và kiểm tra enforcement |
| **B → A/C** | CLI, data contract, fixtures runner, JSON/HTML schema, rule interface, hướng debug lỗi API | Triển khai/integration và QA end-to-end |
| **C → A/B** | YAML before/after, phạm vi namespace, expected functional/security evidence, backup/rollback, log test đã làm sạch | A hỗ trợ mạng/cloud, B báo cáo/re-audit |
| **B/C → cả nhóm** | PR, test logs, evidence có thời điểm, ghi chú khác biệt so với kỳ vọng, các vấn đề chưa giải quyết | Review, nghiệm thu, demo và tránh tuyên bố quá mức |

<a id="hinh-03-01"></a>

![Hình 03-01 — Ma trận 6 CIS Controls và phân công A/B/C](assets/images/09-cis-control-role-matrix.png)

*Hình 03-01. Ma trận 6 CIS Controls và phân công A/B/C.*
---

<a id="sec-03"></a>

## 3. Quy chuẩn kỹ thuật dùng chung

### 3.1. Luồng dữ liệu phải giữ nguyên nguyên tắc chỉ đọc

```text
Chọn cluster + xác thực mode
       ↓
Chọn đúng CIS Benchmark v2.0.0
       ↓
Kubernetes API collector (B) ←→ Google Cloud API collector (A)
       ↓                      [chỉ đọc]
Evidence Normalizer (B)
       ↓
Mode-aware Rule Registry + CIS Specs (B/C)
       ↓
Evaluator (B)
       ↓
PASS / FAIL / REVIEW / N/A / ERROR → JSON/HTML + evidence

TÁCH RIÊNG: phê duyệt → backup → remediation trong lab → functional test
          → re-audit → before/after → báo cáo.
```

Collector không được tự ý `patch`, `create`, `update`, `delete` tài nguyên Cloud/Kubernetes. Workflow `pytest`, `ruff`, `terraform fmt/validate` không tự `terraform apply` hoặc tự sửa cấu hình. Nếu muốn tự động hóa live audit qua GitHub Actions phải dùng identity đọc hạn chế; quyền thay đổi/remediation chỉ cấp cho bước có phê duyệt rõ.

### 3.2. Quy tắc tổng hợp kết quả

| Kết quả | Điều kiện sử dụng | Ví dụ đúng | Ví dụ sai |
|---|---|---|---|
| **PASS** | Tất cả điều kiện cần cho control/resource nằm trong phạm vi đã đánh giá có đủ evidence xác nhận đạt; với Manual phải có kết luận review hợp lệ | 4.1.9 quét đủ RBAC bindings, không có binding tùy biến tới `system:authenticated` | API không trả dữ liệu → suy ra không có vi phạm |
| **FAIL** | Có bằng chứng hiện hữu chỉ ra vi phạm rõ | Deployment trong lab khai báo `serviceAccountName: default` | Không có quyền list Pod → coi là FAIL |
| **REVIEW** | Cần thông tin nghiệp vụ, xác nhận vận hành, ngoại lệ hoặc đánh giá thủ công chưa hoàn thành | 4.1.5 token được mount nhưng chưa rõ ứng dụng có thực sự cần Kubernetes API | Lỗi 403 dùng REVIEW để che lỗi quyền |
| **N/A** | Chỉ dùng khi control thực sự không áp dụng cho mode/đối tượng; **không cộng PASS** | Bảng đối chiếu Autopilot với `4.2.1` Standard-only | Chưa viết rule nên ghi N/A |
| **ERROR** | Thiếu quyền, timeout, pagination lỗi, output sai schema, thiếu trường bắt buộc, thu thập thiếu khiến không thể kết luận | Cloud API `403` khi cần datapath để kiểm 4.3.1 | Dữ liệu thiếu nên mặc định PASS |

**Quy tắc ưu tiên an toàn:** thiếu bằng chứng bắt buộc → `ERROR`; có bằng chứng nhưng còn câu hỏi thuộc thẩm định Manual → `REVIEW`; có vi phạm xác minh được → `FAIL`; chỉ `PASS` khi đã hoàn tất tiêu chí. Đối với một control có nhiều đối tượng, hãy lưu **findings theo resource**, còn kết luận tổng hợp của control phải phản ánh sự không đầy đủ (không được có một FAIL bị nuốt bởi PASS khác, hoặc báo PASS toàn phần khi collection còn ERROR). Việc chọn mức tổng hợp cụ thể phải ghi thành test chung của evaluator.

### 3.3. Bảng trạng thái Manual: đề xuất quy trình duyệt

| Tình huống | Kết quả trước review | Người đánh giá cần làm | Kết quả sau review |
|---|---|---|---|
| Không xác định được Pod có cần Kubernetes API | REVIEW | Xác nhận nhu cầu API với owner workload, đối chiếu token mounting, RBAC và traffic/functionality | PASS/FAIL kèm người, thời điểm, bằng chứng |
| PSS namespace có nhãn hợp lệ, chưa chứng minh admission phù hợp | REVIEW | Kiểm tra scope workload, label và thử admission an toàn | PASS/FAIL kèm evidence |
| NetworkPolicy enforcement cấu hình có vẻ đúng | REVIEW | Kiểm tra đúng mode, dữ liệu GKE và test/rủi ro liên quan | PASS/FAIL kèm evidence |
| Manual chưa được duyệt hoặc ngoại lệ thiếu tài liệu | REVIEW | Ghi rõ đầu việc còn thiếu | Giữ REVIEW, không tự PASS |

Không để một ô `human_review: true` vô danh chuyển đổi REVIEW thành PASS. Kết luận thủ công phải có ít nhất **người đánh giá, thời gian, nhận định, đối tượng/phạm vi và evidence liên quan**. Phân biệt **người đánh giá security finding** với **người phê duyệt remediation**; đây là hai quyết định khác nhau.

### 3.4. Bộ dữ liệu chuẩn hóa bắt buộc

| Nhóm dữ liệu | Trường gợi ý | Phụ trách nguồn |
|---|---|---|
| Nhận diện cluster | `project_id`, `location`, `cluster_name`, `mode`, `benchmark_id`, `benchmark_version` | A cung cấp dữ liệu Cloud, B định nghĩa schema |
| Nhận diện đối tượng | `kind`, `namespace`, `name`, `uid`, `resource_version`, `workload_owner` (nếu có) | B collector Kubernetes; C chốt scope |
| Bằng chứng | `source_api`, `collected_at`, `raw_evidence_ref`, `normalized_evidence`, `redaction_applied` | B/A collectors; C kiểm độ phù hợp |
| Trạng thái thu thập | `complete`, `permission_denied`, `timeout`, `missing_fields`, `partial_pages` | A/B collectors |
| Định danh control | `control_id`, `mode`, `cis_level`, `assessment_type`, `rule_version`, `source_pdf_page` | C xác nhận CIS, B registry |
| Kết quả | `status`, `reason`, `affected_resources`, `review_questions`, `review_decision`, `remediation_hint` | B evaluator/reporter; C nghiệm thu |
| Truy xuất lần chạy | `run_id`, `timestamp_utc`, `tool_version`, `git_commit`, `evidence_hash` (nếu dùng) | B; A tích hợp |

Định dạng JSON ở đây là **đề xuất hợp đồng nội bộ**, không phải cấu trúc do CIS ban hành. Nếu schema thay đổi, B sửa `docs/contracts.md`, A xác nhận Cloud fields, C xác nhận rule/QA và cả ba review PR trước khi tích hợp.

### 3.5. Thu thập dữ liệu gì, tuyệt đối không thu thập gì?

**Kubernetes API collector (B)** cần list/get đủ những loại object được dùng cho rule: Namespace, ServiceAccount, Pod, các Pod templates của Deployment, StatefulSet, DaemonSet, Job/CronJob (khi thuộc phạm vi), RoleBinding, ClusterRoleBinding, Role/ClusterRole ở mức cần thiết để giải thích RBAC, NetworkPolicy và metadata cần kiểm tra. Hãy xử lý phân trang, trường vắng, `403`, object bị xóa giữa lúc audit và quyền đọc khác nhau theo namespace. Pod template và Pod đang chạy phải phân biệt vì template có thể chưa rollout.

**Google Cloud API collector (A)** cần đọc cấu hình cluster/mode qua Google Cloud Container API/SDK, bao gồm `networkConfig.datapathProvider`, các trường liên quan Calico `networkPolicy.enabled`, `networkPolicy.provider`, `addonsConfig.networkPolicyConfig.disabled` cho Standard. Không suy ra `ADVANCED_DATAPATH` chỉ từ tên cluster; tên field/kiểu dữ liệu cần đối chiếu output thực tế. Có thể ghi network/subnet để mô tả môi trường, nhưng không được lấy metadata không cần thiết hoặc giá trị credentials.

**Không đọc giá trị Kubernetes Secret, ServiceAccount bearer token, raw kubeconfig, GCP service account key, biến môi trường có mật khẩu.** Không gắn những nội dung đó vào test artifact hoặc báo cáo HTML. Dữ liệu phản hồi phải được redact và có thể dùng đường dẫn tham chiếu tới evidence đã làm sạch.

### 3.6. Đầu ra và tiêu chí hoàn thành chung một control

- [ ] CIS ID/mode/Level/Automated–Manual khớp **đúng PDF v2.0.0**; PDF reference có trang để kiểm lại.
- [ ] C mô tả điều kiện, ngoại lệ, data fields và manual questions, đồng thời đã review spec.
- [ ] Code chạy trên interface B thống nhất, không gắn cứng namespace hoặc mode theo tên.
- [ ] A/B xác thực collectors trả dữ liệu đủ hoặc `ERROR` rõ ràng khi không đủ.
- [ ] Có fixtures bao phủ expected status, negative cases, boundary/exception cases và lỗi thu thập.
- [ ] CI liên quan chạy thành công; không thay đổi kỳ vọng test chỉ để làm CI xanh.
- [ ] Có live test trên đúng mode/namespace được cấp quyền; evidence thật lưu riêng với fixtures.
- [ ] Report gắn đúng benchmark, mode, timestamp, scope, resource, reason và đường dẫn evidence; không lộ dữ liệu nhạy cảm.
- [ ] Với Manual, người đánh giá đã đưa kết luận hoặc giữ `REVIEW` trung thực.
- [ ] Với remediation demo, có approval, backup, rollback, functional test, re-audit và before/after.

<a id="hinh-03-02"></a>

![Hình 03-02 — Quy trình từ đặc tả CIS đến nghiệm thu, evidence và báo cáo](assets/images/10-rule-evidence-pipeline.png)

*Hình 03-02. Quy trình từ đặc tả CIS đến nghiệm thu, evidence và báo cáo.*
---
<a id="cis-414"></a>

## 4. CIS 4.1.4 — Workload không dùng `default` ServiceAccount

**Nguồn:** Standard Benchmark v2.0.0, trang PDF in **40–41**; Autopilot Benchmark v2.0.0, trang PDF in **26–27**.  
**Phạm vi:** Standard và Autopilot; **Level 1 — Automated** ở cả hai.  
**Owner control/rule:** **B**. **C** chịu trách nhiệm spec/lab/QA; **A** cung cấp cluster, context và môi trường live.

> **Điểm kiểm tra:** Pod/workload template sử dụng SA `default`, không phải SA `default` chỉ tồn tại.  
> **Trọng tâm bàn giao:** B — rule/pytest; C — YAML before/after và QA; A — GKE context.

### 4.1. Mục đích và tình huống thực tế

Kubernetes tạo một ServiceAccount tên `default` trong mỗi namespace. Khi một Pod không chỉ định `serviceAccountName`, Kubernetes sẽ sử dụng ServiceAccount mặc định của namespace đó. Điều này có thể khiến nhiều ứng dụng dùng chung một danh tính; khi danh tính ấy được cấp thêm quyền RBAC, các ứng dụng có thể nhận quyền ngoài dự kiến.

**Dự án không kiểm tra “ServiceAccount `default` có tồn tại hay không”.** Việc nó tồn tại là bình thường. Dự án kiểm tra **workload có chủ động sử dụng nó** và **có RoleBinding/ClusterRoleBinding gán quyền không phù hợp cho ServiceAccount mặc định** hay không; kèm theo bằng chứng token-mounting khi liên quan.

### 4.2. Những đối tượng và trường dữ liệu cần kiểm tra

| Đối tượng | Trường/thuộc tính cần đọc | Ý nghĩa |
|---|---|---|
| Pod | `metadata.namespace`, `metadata.name`, `spec.serviceAccountName`, `spec.automountServiceAccountToken` | Danh tính ServiceAccount thực tế và cấu hình token ở Pod |
| Deployment / StatefulSet / DaemonSet / Job / CronJob trong scope | Đường tới `spec.template.spec.serviceAccountName` (CronJob ở `spec.jobTemplate.spec.template.spec`) | Tìm nguyên nhân trong cấu hình **mong muốn** để tránh lỗi tái xuất hiện sau rollout |
| ServiceAccount | `metadata.namespace`, `metadata.name`, `automountServiceAccountToken` | Xác nhận ServiceAccount chuyên dụng và token default policy |
| RoleBinding / ClusterRoleBinding | `subjects[]`, `roleRef` | Tìm binding có subject `{kind: ServiceAccount, name: default, namespace: ...}` |
| Context đánh giá | Namespace có ứng dụng do người dùng quản lý, thông tin exception được duyệt | Tránh tùy tiện đánh giá/khắc phục namespace hệ thống |

**Ghi chú kỹ thuật:** trong Pod đã được admit, `spec.serviceAccountName` có thể được Kubernetes điền thành `default` ngay cả khi Pod template ban đầu bỏ trống. Khi thu thập, cần giữ **cả cấu hình template lẫn trạng thái Pod chạy** để kết luận đúng nguồn gây lỗi. `automountServiceAccountToken=false` giảm lộ token **không thay thế** yêu cầu dùng dedicated ServiceAccount của control này.

### 4.3. Logic đánh giá đề xuất

| Tình huống | Kết quả | Evidence bắt buộc |
|---|---|---|
| Workload trong scope chỉ định `serviceAccountName: default` | **FAIL** | Kind/namespace/name, field và giá trị tìm thấy |
| Pod template không chỉ định tên SA nên mặc định dùng `default` | **FAIL** | Template field missing + Pod/semantics mặc định; ghi rõ lý do |
| Binding cấp quyền tùy biến trực tiếp cho `default` SA trong workload namespace, không có ngoại lệ hợp lệ | **FAIL** hoặc finding vi phạm riêng | Binding, subject, roleRef, namespace và kết quả xác minh ngoại lệ |
| Workload sử dụng SA chuyên dụng; không có vi phạm binding được rà soát; dữ liệu đầy đủ | **PASS** | Tên SA, đối tượng, danh sách binding đã kiểm |
| Có exception đã ghi nhận nhưng cần quyết định của owner/security | **REVIEW** | Mã ngoại lệ, lý do và người cần đánh giá; không tự bỏ finding |
| Không list được workload, SA hoặc bindings cần kiểm | **ERROR** | API action, mã lỗi, scope bị ảnh hưởng |
| Chỉ thấy SA tên `default` tồn tại, không có workload/binding sử dụng sai | **Không được FAIL chỉ vì tồn tại** | Bằng chứng đã rà workload/bindings |

**Tổng hợp trên cluster:** nếu chỉ quét `lab-sa`, kết quả phải ghi `scope=lab-sa`, không tuyên bố toàn bộ cluster tuân thủ. Nếu phát hiện FAIL ở template và Pod thuộc cùng workload, deduplicate/nhóm chúng để báo cáo không tạo hai vi phạm trùng ý nghĩa.

### 4.4. Triển khai Python, fixtures và kiểm thử live

- **B** hiện thực `rule_4_1_4(evidence, context)` hoặc interface tương đương; đọc đối tượng chuẩn hóa, áp dụng bộ lọc namespace workload, phát finding theo resource và reason cụ thể. Unit tests phải chứng minh **không flag SA chỉ vì tồn tại**.
- **C** cung cấp `lab-sa/before` với một Deployment đơn giản **bỏ trống** `serviceAccountName` hoặc khai báo `default`; `lab-sa/after` chỉ định dedicated SA. Không cần cấp quyền nguy hiểm để tạo sai lệch mẫu. C ghi expected result cho cả template và Pod.
- **A** cung cấp cluster/context đúng mode; chỉ cấp quyền đọc cần thiết cho Audit Engine và quyền apply lab theo quy trình được phê duyệt.

| Test ID | Đầu vào | Kỳ vọng |
|---|---|---|
| `T414-01` | Namespace có SA `default`, **không** workload nào dùng | Không tạo FAIL chỉ vì SA tồn tại |
| `T414-02` | Deployment template không khai báo `serviceAccountName` | FAIL và ghi rõ nguồn template |
| `T414-03` | Workload chỉ định `serviceAccountName: default` | FAIL |
| `T414-04` | Workload dùng `sa-web` riêng và không có binding sai | PASS khi collection đầy đủ |
| `T414-05` | RoleBinding/ClusterRoleBinding tùy biến gán `default` SA | FAIL hoặc finding vi phạm RBAC riêng có evidence |
| `T414-06` | Thiếu quyền list workloads hoặc bindings | ERROR, không PASS |
| `T414-07` | Dữ liệu Pod và template cùng một workload | Báo cáo nhóm/khử trùng lặp đúng |

### 4.5. Remediation và nghiệm thu

**Trong namespace lab sau phê duyệt:** backup YAML; tạo dedicated ServiceAccount; cập nhật workload `serviceAccountName`; chỉ cấp RBAC tối thiểu nếu workload thật sự cần Kubernetes API; tắt token tự mount **khi không cần API** (liên hệ `4.1.5`); rollout và kiểm tra Pod Ready/HTTP. Không tự sửa/xóa ServiceAccount mặc định hoặc binding hệ thống ngoài scope. Chạy lại `4.1.4`, kiểm tra diff và diễn tập rollback nếu ứng dụng lỗi.

| Việc / trách nhiệm | Phụ trách chính | Bàn giao cho | Hoàn thành khi |
|---|---|---|---|
| Đối chiếu CIS, phạm vi, ngoại lệ | **C** | B | Spec + test expectations được review |
| Kubernetes collector, Python rule, pytest | **B** | C/A | Fixture tests xanh, finding có evidence |
| Hai bộ YAML before/after, HTTP functional | **C** | B/A | Deploy lại được, bản before và after khác biệt đúng mục tiêu |
| Môi trường Standard/Autopilot, cloud integration | **A** | B/C | Đúng context, collector chạy read-only |
| Audit → approval → fix → re-audit | **C** điều phối, **B** audit, **A** hỗ trợ | Cả nhóm | Có approval, backup, HTTP test, before/after thật |

**Nghiệm thu control:** không có false positive do SA `default` chỉ tồn tại; có FAIL thật từ workload dùng SA mặc định; sau sửa, workload có dedicated SA và vẫn hoạt động; báo cáo phân biệt rõ finding `4.1.4` với đánh giá token `4.1.5`.

[↑ Trở về mục lục](#muc-luc)

---

<a id="cis-415"></a>

## 5. CIS 4.1.5 — Chỉ mount ServiceAccount token khi cần Kubernetes API

**Nguồn:** Standard Benchmark v2.0.0, trang in **43–44**; Autopilot Benchmark v2.0.0, trang in **29–30**.  
**Phạm vi:** Standard và Autopilot; **Level 1 — Manual** ở cả hai.  
**Owner rule/contract REVIEW:** **B**. **Owner xác minh nhu cầu workload và test:** **C**. **A** hỗ trợ identity/RBAC/context khi cần.

> **Điểm kiểm tra:** Token chỉ mount khi nghiệp vụ thật sự cần gọi Kubernetes API; đây là **Manual**.  
> **Trọng tâm bàn giao:** B — token precedence và REVIEW; C — xác minh nhu cầu API; A — identity/context.

### 5.1. Bài toán bảo mật và giới hạn của automation

Kubernetes có thể tự gắn ServiceAccount token vào Pod để ứng dụng gọi Kubernetes API. Nếu ứng dụng không cần chức năng này, việc vẫn mang token làm tăng bề mặt rủi ro khi container bị xâm nhập. Ngược lại, controller/operator thực sự dùng Kubernetes API có thể bị hỏng nếu tắt token tùy tiện.

Điểm quan trọng nhất: **chỉ nhìn cấu hình `automountServiceAccountToken` không thể luôn biết một workload có cần Kubernetes API về mặt nghiệp vụ hay không.** Vì CIS đánh dấu **Manual**, engine phải hỗ trợ **REVIEW có câu hỏi cụ thể** chứ không tự động kết luận mọi Pod có token là FAIL.

### 5.2. Dữ liệu cần kiểm tra và cách xác định hiệu lực

| Nguồn | Field / evidence | Cần lưu ý |
|---|---|---|
| Pod hoặc Pod template | `spec.automountServiceAccountToken` | `false` tại Pod có ưu tiên hơn thiết lập của ServiceAccount |
| ServiceAccount gắn với Pod | `automountServiceAccountToken` | Dùng nếu trường tương ứng ở Pod không được đặt |
| Pod template / Pod | `serviceAccountName`, `volumes[*].projected.sources[*].serviceAccountToken` (nếu có), volumeMounts liên quan | Phân biệt auto-mount với token được cấu hình explicit; không đọc giá trị token |
| RBAC | Role/ClusterRole và RoleBinding/ClusterRoleBinding gán cho SA | Cung cấp ngữ cảnh quyền, **không chứng minh** ứng dụng đang dùng API |
| Hồ sơ workload / test | `requires_kubernetes_api: yes/no/unknown`, chủ ứng dụng xác nhận, test HTTP/functional | Đây là metadata/đánh giá do nhóm bổ sung, **không phải field Kubernetes mặc định** |

**Cách tính auto-mount theo Kubernetes:** nếu Pod khai báo `automountServiceAccountToken`, sử dụng giá trị của Pod; nếu Pod không khai báo, xem giá trị của ServiceAccount; nếu cả hai không khai báo thì mặc định là `true`. Tuy nhiên, **`false` không tự chứng minh rằng Pod tuyệt đối không có bất cứ token nào**, vì có thể có projected token được cấu hình riêng. Không đọc/ghi token thực tế để thực hiện kiểm tra này.

### 5.3. Ma trận quyết định

| Có cần Kubernetes API? | Auto-mount dự kiến / bằng chứng | Trạng thái đề xuất | Giải thích |
|---|---|---|---|
| **Không** (đã được owner xác minh) | `false`, không phát hiện token riêng trái chủ đích | **PASS sau manual review** | Cấu hình và nhu cầu nghiệp vụ khớp nhau |
| **Không** (đã được owner xác minh) | `true` hoặc không khai báo nên mặc định `true` | **FAIL sau manual review** | Token không cần thiết vẫn có nguy cơ được mount |
| **Có** (đã xác minh) | Token được mount, SA chuyên dụng và quyền RBAC tối thiểu phù hợp | **PASS sau manual review** | Có lý do sử dụng và giới hạn quyền; ghi evidence |
| **Có** (đã xác minh) | `false` khiến workload không gọi API như yêu cầu | **REVIEW/FAIL sau xác minh** | Có thể là lỗi chức năng/cấu hình; cần thấy triệu chứng thực |
| **Chưa biết** | `true`, `false` hoặc thiếu field | **REVIEW** | Cần hỏi owner workload; không mặc định FAIL hay PASS |
| Không list/get được Pod hoặc SA cần thiết | Bất kỳ | **ERROR** | Lỗi thu thập, khác REVIEW |

Trên fixture, B có thể kiểm **gợi ý trạng thái sơ bộ**; nhưng finding Manual chỉ nhận kết luận cuối khi có `review_decision` hợp lệ và evidence. Nếu `automount=false` song có projected token thủ công hoặc cơ chế cấp chứng thực khác, cần REVIEW rõ ràng thay vì suy diễn đã loại bỏ token.

### 5.4. Kiểm thử và remediation có kiểm soát

| Test ID | Trường hợp | Kết quả mong đợi |
|---|---|---|
| `T415-01` | Pod không cần API, `automount=false`, đã xác minh và test ứng dụng | PASS sau review |
| `T415-02` | Pod không cần API, không đặt flag ở Pod/SA | REVIEW trước xác nhận; FAIL sau khi xác minh không cần API |
| `T415-03` | Pod cần API, dùng dedicated SA với quyền tối thiểu, đã xác minh | PASS sau review |
| `T415-04` | Nhu cầu API chưa biết, token có thể mount | REVIEW + danh sách câu hỏi |
| `T415-05` | Pod false, SA true | Tính auto-mount dự kiến **false** do Pod ưu tiên |
| `T415-06` | Pod unset, SA false | Tính auto-mount dự kiến **false** |
| `T415-07` | Có projected serviceAccountToken riêng | REVIEW/giải thích riêng, không kết luận an toàn chỉ do auto-mount false |
| `T415-08` | Không truy cập được Pod/SA | ERROR |

**Kịch bản lab:** C chuẩn bị ứng dụng HTTP **không cần Kubernetes API** (có mô tả chứng minh). Baseline `before` cho token mặc định và `serviceAccountName` không phù hợp; `after` dùng SA chuyên dụng, `automountServiceAccountToken: false`. Sau approval, C triển khai và chạy HTTP/Ready, B audit + re-audit; nếu chức năng thay đổi, rollback trước khi chốt nghiệm thu. Đối với controller có nhu cầu API thật, minh họa bằng fixture và **không yêu cầu tắt token**.

| Việc / trách nhiệm | Phụ trách | Bàn giao |
|---|---|---|
| Control spec, định nghĩa câu hỏi manual, owner workload xác minh | **C** | Hồ sơ `requires_kubernetes_api` kèm lý do/evidence cho B |
| Token precedence logic, review workflow, pytest, finding/report | **B** | Module rule + test + status cho A/C |
| Kubernetes context, xác nhận quyền và kiểm thử hoạt động cluster | **A** | Điều kiện live và bằng chứng quyền/Cloud khi liên quan |
| YAML SA lab, backup/rollback, HTTP test | **C** | Manifests và logs đã làm sạch cho B |
| Kết luận sau review | **C** hoặc reviewer được phân quyền; B ghi nhận | Kết quả PASS/FAIL/REVIEW có người, thời gian, evidence |

**Nghiệm thu:** engine không biến `Manual` thành tự động PASS; tính đúng quyền ưu tiên Pod/SA; REVIEW hỏi được câu hỏi có thể hành động; tắt token chỉ sau khi xác nhận workload không cần API; ứng dụng sau sửa còn chạy.

<a id="hinh-03-05"></a>

![Hình 03-05 — ServiceAccount Hardening trước và sau thay đổi](assets/images/13-serviceaccount-hardening.png)

*Hình 03-05. ServiceAccount Hardening trước và sau thay đổi.*
[↑ Trở về mục lục](#muc-luc)

---

<a id="cis-419"></a>

## 6. CIS 4.1.9 — Hạn chế RBAC gán cho `system:authenticated`

**Nguồn:** Standard Benchmark v2.0.0, trang in **55–57**; Autopilot Benchmark v2.0.0, trang in **41–43**.  
**Phạm vi:** Standard và Autopilot; **Level 1 — Automated** ở cả hai.  
**Owner code:** **B**. **C** phụ trách xác minh ngoại lệ và fixtures; **A** hỗ trợ xác nhận quyền thực tế khi live.

> **Điểm kiểm tra:** RBAC bindings tùy biến đến `system:authenticated`; kiểm ngoại lệ hệ thống chính xác.  
> **Trọng tâm bàn giao:** B — rule/pytest; C — fixtures và kiểm tra ngoại lệ; A — môi trường/quyền đọc.

### 6.1. Chính xác kiểm tra điều gì?

`system:authenticated` là một Kubernetes Group rất rộng, đại diện cho các request đã xác thực. Gán Role/ClusterRole tùy biến cho group này có thể mở quyền truy cập ngoài ý muốn. Audit phải xem **cả `RoleBinding` theo namespace và `ClusterRoleBinding` toàn cluster**.

**Ba ClusterRoleBinding hệ thống dự kiến không tự động bị flag chỉ vì chúng có subject `system:authenticated`:**

- `system:basic-user`
- `system:discovery`
- `system:public-info-viewer`

Phải xác minh đây là **đúng các binding hệ thống mong đợi**, không chỉ bỏ qua mọi object có tên giống chúng một cách mù quáng. Nếu thông tin roleRef/subjects của bản ghi khác mẫu hợp lệ, cần đánh giá lại thay vì cho qua. **Không xóa các binding hệ thống** như một bài demo.

### 6.2. Evidence và logic

| Cần xem | Cách đọc | Điều kiện đáng chú ý |
|---|---|---|
| ClusterRoleBinding | Kubernetes RBAC API list tất cả | `subjects[]` có `{kind: Group, name: system:authenticated}` ngoài nhóm mặc định |
| RoleBinding | Kubernetes RBAC API list trên các namespace trong phạm vi, bảo đảm độ bao phủ | Bất kỳ RoleBinding tùy biến nào tham chiếu group trên |
| `roleRef` | Kind + name | Đưa vào báo cáo để giải thích quyền được gán |
| Role/ClusterRole tham chiếu | `rules` metadata (apiGroups, resources, verbs) | Đánh dấu mức rủi ro: wildcard, secrets, namespace-wide, workload access; không bắt buộc đọc nội dung Secret |
| Binding hệ thống được phép | Name, kind, roleRef, subjects và nguồn hệ thống | Không tạo false positive, không coi mọi `system:*` là miễn trừ |

| Tình huống | Kết quả |
|---|---|
| Chỉ có ba ClusterRoleBinding hệ thống mặc định đúng mẫu; kết quả collection đầy đủ | **PASS** |
| Tạo thêm `RoleBinding` custom đến Group `system:authenticated` | **FAIL** |
| Tạo thêm `ClusterRoleBinding` custom đến Group `system:authenticated` | **FAIL** |
| Object trông giống tên hệ thống nhưng vai trò/subjects khác kỳ vọng | **REVIEW hoặc FAIL** theo policy kiểm tra đã chốt; không whitelist theo tên đơn thuần |
| Không đủ quyền list bindings hoặc chỉ thấy một phần namespace | **ERROR**, không suy ra PASS |

**Lưu ý:** `system:unauthenticated` là control khác (`4.1.8`), không đánh tráo thành `4.1.9`. Ngoại lệ hệ thống trong `4.1.9` không có nghĩa mọi RoleBinding mặc định hoặc RoleBinding có chữ `system` đều an toàn.

### 6.3. Fixtures, kịch bản lab và remediation

| Test ID | Dữ liệu | Kỳ vọng |
|---|---|---|
| `T419-01` | Đúng ba default ClusterRoleBindings tới authenticated | PASS |
| `T419-02` | Một RoleBinding namespace tùy biến tới authenticated | FAIL |
| `T419-03` | Một ClusterRoleBinding tùy biến tới authenticated | FAIL |
| `T419-04` | Binding tùy biến chỉ gắn Group cụ thể `team-readonly` | Không FAIL vì `4.1.9` (vẫn phải kiểm quyền ở control khác nếu cần) |
| `T419-05` | Tên binding giống default nhưng roleRef/subject bị đổi | Không tự whitelist; xử lý theo spec bảo thủ |
| `T419-06` | List RBAC trả HTTP 403/mất trang | ERROR |
| `T419-07` | RBAC binding phân tán nhiều namespace | Collector quét đủ, không bỏ sót |

**Lab:** ưu tiên dùng fixture để tránh thay đổi quyền rộng trên cluster thật. Nếu cần live minh họa, tạo **RoleBinding giới hạn trong namespace lab**, chỉ cấp quyền quan sát ít tác động nhưng subject là `system:authenticated`; ghi phạm vi, tác động, phê duyệt và kế hoạch xóa. **Không tạo ClusterRoleBinding cấp rộng/cluster-admin để có FAIL đẹp.** Remediation gồm xác minh người dùng nào thật sự cần quyền, tạo Role/RoleBinding ít quyền cho subject cụ thể, kiểm tra truy cập hợp lệ rồi mới xóa binding custom. Không động vào các binding hệ thống.

| Việc | Owner | Bàn giao/đầu ra |
|---|---|---|
| Spec ngoại lệ và kiểm thử an toàn | **C** | Danh sách expected defaults; fixture RBAC cases; rủi ro lab |
| Rule RBAC, collector, pytest, evidence/report | **B** | Code + tests + danh sách finding theo binding |
| Context/quyền đọc RBAC ở hai cluster | **A** | Điều kiện live và lỗi quyền để kiểm thử |
| Kiểm chứng fix/báo cáo | **C** security QA, **B** re-audit | Before/After thật nếu có lab live; hoặc ghi rõ fixture-only |

**Nghiệm thu:** hai loại binding tùy biến đều bị phát hiện; không flag/xóa ba system defaults; không bỏ sót namespace; phân loại đúng `403 → ERROR`; không dùng thay đổi RBAC nguy hiểm để tạo tình huống thử nghiệm.

[↑ Trở về mục lục](#muc-luc)

---
<a id="cis-421"></a>

## 7. CIS 4.2.1 — Thực thi Pod Security Standards

**Nguồn:** **CIS GKE Standard Benchmark v2.0.0**, trang in **60–62**.  
**Phạm vi:** **chỉ Standard — Level 1 — Manual**. Autopilot Benchmark v2.0.0 **không có control ID `4.2.1`**.  
**Owner đặc tả, code rule và security lab:** **C**. **B** sở hữu interface/merge/reporter; **A** cung cấp cluster Standard và context phù hợp.

> **Điểm kiểm tra:** Standard workload namespaces có `enforce=baseline/restricted`, không đánh đồng `warn`/`audit`.  
> **Trọng tâm bàn giao:** C — rule, lab, admission QA; B — interface/reporter; A — Standard cluster.

### 7.1. Ý nghĩa và nguyên lý phải hiểu

*Pod Security Standards* (PSS) định nghĩa các profile bảo mật cho Pod. Với control này trên Standard, các namespace chứa **workload do người dùng quản lý** phải có cơ chế **thực thi** profile `baseline` hoặc `restricted` thông qua Pod Security Admission. `restricted` được chấp nhận vì chặt hơn `baseline`.

Đừng nhầm ba chế độ nhãn:

- `pod-security.kubernetes.io/enforce`: admission **chặn** request tạo/cập nhật Pod vi phạm theo chính sách có hiệu lực.
- `pod-security.kubernetes.io/warn`: chỉ cảnh báo, không phải bằng chứng đã chặn.
- `pod-security.kubernetes.io/audit`: ghi audit annotation/event phục vụ quan sát, không thay `enforce`.

Một namespace có `warn=baseline` hoặc `audit=restricted` nhưng **không có `enforce=baseline/restricted`** thì không được coi là đạt kiểm tra ở đây. Các Pod đã chạy trước khi thay đổi nhãn không tự bị đuổi khỏi node; vì vậy cần phân biệt **trạng thái namespace/admission hiện tại** với **độ an toàn của từng Pod đang chạy**.

### 7.2. Phạm vi và dữ liệu thu thập

| Kiểm tra | API/field cần đọc | Cách sử dụng |
|---|---|---|
| Danh sách namespace | Namespace API: `metadata.name`, `metadata.labels` | Xác định namespace trong scope; phân biệt namespace hệ thống |
| Nhãn PSS | `pod-security.kubernetes.io/enforce`, có thể xem `enforce-version` | `baseline`/`restricted` có giá trị; version pin nếu có phải được lưu/đánh giá tương thích |
| Namespace chứa user workloads | Pods/Controllers theo namespace, label sở hữu lab | Đảm bảo không bỏ namespace workload và không áp logic cho namespace chỉ chứa hệ thống mà không có kết luận scope |
| Admission thực nghiệm | Server-side dry-run tạo Pod có cấu hình chủ đích không hợp profile; phản hồi deny/admission error | Chỉ thực hiện theo kịch bản kiểm thử được cho phép; không deploy Pod đặc quyền thực sự |
| Exception và ngữ cảnh GKE | Danh sách namespace ngoại lệ hợp lệ, cluster mode, người xác minh | Manual review khi namespace có ngoại lệ/hệ thống đặc biệt |

**Phạm vi loại trừ:** không sửa `kube-system`, `kube-public`, `kube-node-lease` như một phần tự động của demo. Không coi việc loại trừ hệ thống là “toàn cluster đạt” khi phạm vi namespace chưa được ghi rõ.

### 7.3. Logic đánh giá và bước xác minh thủ công

| Điều kiện quan sát được | Kết quả đề xuất |
|---|---|
| User workload namespace có `enforce=baseline` hoặc `restricted` | **REVIEW trước manual validation**, sau xác minh scope và admission có thể PASS |
| Chỉ có `warn`/`audit`, thiếu `enforce` | **FAIL** với evidence nhãn namespace |
| `enforce=privileged` hoặc giá trị không đáp ứng baseline/restricted | **FAIL** |
| `enforce=baseline/restricted`, nhưng admission test cho thấy đối tượng vi phạm đáng lẽ phải bị chặn lại vẫn được admit | **FAIL/REVIEW điều tra**, ghi lại cấu hình và test; không tự PASS |
| Không rõ namespace nào thuộc user workload | **REVIEW** để xác định scope; không tuyên bố toàn bộ user namespaces đạt |
| Không thể list namespaces/labels hoặc lỗi API | **ERROR** |
| Mode Autopilot ở màn hình so sánh | **N/A — không tồn tại ID trong benchmark này**, không cộng PASS |

**Ví dụ để hình dung:** `lab-pss` chứa Deployment thử nghiệm. Ban đầu namespace chỉ có `warn=baseline`; công cụ phát hiện thiếu `enforce` và kết luận FAIL trong phạm vi lab. Sau phê duyệt, C sửa workload nếu cần, đặt `enforce=baseline`, thực hiện server-side dry-run một Pod vi phạm profile và xác minh admission từ chối. C là người xác nhận kết quả Manual; B đưa nhận định và bằng chứng vào report.

### 7.4. Bộ test cần có

| Test ID | Dữ liệu/kịch bản | Kỳ vọng |
|---|---|---|
| `T421-01` | Standard workload namespace có `enforce=baseline`, admission phù hợp, reviewer chấp nhận | PASS sau review |
| `T421-02` | `enforce=restricted`, admission phù hợp | PASS sau review |
| `T421-03` | Chỉ có `warn` và `audit`, thiếu `enforce` | FAIL |
| `T421-04` | `enforce=privileged` | FAIL |
| `T421-05` | Namespace có ngoại lệ cần xác minh | REVIEW và ghi nguyên nhân |
| `T421-06` | Autopilot ở **comparison** | N/A, không đánh tráo thành PASS |
| `T421-07` | Không đọc được Namespace API | ERROR |
| `T421-08` | Pod vi phạm bị deny trong server-side dry-run sau hardening | Có admission evidence và không deploy Pod không an toàn |

### 7.5. Remediation, tác động và phân công

**Tác động:** bật `enforce` có thể làm các lần rollout/job mới không được nhận nếu Pod không đáp ứng profile. Không áp nhãn ngay lập tức lên nhiều namespace; rà securityContext của workload và test trước bằng server-side dry-run; cân nhắc dùng warn/audit để quan sát trong quá trình chuẩn bị nhưng không dùng chúng thay bước enforce.

**Thực hiện trong lab:** C sao lưu labels/manifests; xin phê duyệt; chỉnh workload trước nếu vi phạm; áp `enforce=baseline/restricted`; kiểm tra admission/Pod Ready/HTTP; chạy re-audit; rollback nhãn/manifest khi test chức năng thất bại. A/B phối hợp đúng trách nhiệm.

| Việc / sản phẩm | Owner | Người phối hợp / người nhận |
|---|---|---|
| Chốt danh sách user workload namespaces và CIS mapping | **C** | A xác nhận cluster scope, B đọc dữ liệu |
| Viết rule `4.2.1`, fixtures/test cases | **C** | B review Python interface và merge |
| Kubernetes collector/normalizer đọc labels và lỗi | **B** | C kiểm evidence schema |
| Tạo YAML lab, test admission, before/after | **C** | A hỗ trợ cluster, B ghi report |
| Phân quyền/cluster và kiểm kết nối | **A** | C nhận môi trường test |
| Manual conclusion, functional QA, rollback | **C** hoặc reviewer được ủy quyền | B tổng hợp kết quả, A hỗ trợ khi liên quan cluster |

**Nghiệm thu:** chỉ `enforce=baseline/restricted` mới là bằng chứng cấu hình phù hợp; xác minh admission không được tạo workload không an toàn; kết luận cuối cho Manual có reviewer; Autopilot không nhận một PASS giả cho `4.2.1`.

<a id="hinh-03-06"></a>

![Hình 03-06 — CIS 4.2.1 trên Standard: PSS enforce, warn và audit](assets/images/14-pss-admission.png)

*Hình 03-06. CIS 4.2.1 trên Standard: PSS enforce, warn và audit.*
[↑ Trở về mục lục](#muc-luc)

---

<a id="cis-431"></a>

## 8. CIS 4.3.1 — Xác minh NetworkPolicy enforcement theo mode

**Nguồn:** Standard Benchmark v2.0.0, trang in **64–66**; Autopilot Benchmark v2.0.0, trang in **46–47**.  
**Phạm vi:** Standard **Level 1 — Manual**; Autopilot **Level 2 — Manual**.  
**Owner đặc tả/code rule:** **C**. **A** sở hữu Google Cloud network evidence; **B** sở hữu rule interface/manual review/reporting.

> **Điểm kiểm tra:** NetworkPolicy enforcement theo đúng mode; control **Manual**, không đồng nghĩa có default-deny.  
> **Trọng tâm bàn giao:** C — rule và manual evidence; A — Cloud dataplane; B — engine/reporter.

### 8.1. Control này kiểm tra điều gì và KHÔNG kiểm tra điều gì?

**Kiểm tra:** cụm GKE có cơ chế thực thi Kubernetes NetworkPolicy được hỗ trợ hay không. Chỉ tạo object `NetworkPolicy` **không có nghĩa** rule sẽ được thực thi, nếu dataplane/plugin không hỗ trợ hoặc không bật đúng.

**Không kiểm tra ở control này:** namespace đã tạo default-deny ingress/egress hay chưa. Trên Standard, đó là phần trọng tâm của `4.3.2` và kiểm tra mở rộng của nhóm. Trên Autopilot, có thể dùng NetworkPolicy để hardening nhưng không gán kết quả đó thành `4.3.2` vì benchmark Autopilot v2.0.0 không có control ID này.

### 8.2. Đúng cơ chế theo từng mode

| Chế độ | Trường Google Cloud / API evidence | Điều kiện kỳ vọng |
|---|---|---|
| **Standard — GKE Dataplane V2** | `networkConfig.datapathProvider` | `ADVANCED_DATAPATH` → enforcement tích hợp; không yêu cầu add-on Calico bật |
| **Standard — legacy datapath + Calico** | `networkConfig.datapathProvider`, `networkPolicy.enabled`, `networkPolicy.provider`, `addonsConfig.networkPolicyConfig.disabled` | `LEGACY_DATAPATH` + enabled=`true` + provider=`CALICO` + add-on disabled=`false` |
| **Standard — legacy thiếu một thành phần** | Các trường trên | Không đủ cấu hình enforcement; báo sai lệch/đề nghị review |
| **Autopilot** | `networkConfig.datapathProvider` và mode | `ADVANCED_DATAPATH` mặc định; **không bật Calico / NetworkPolicy add-on riêng** |
| **Bất kỳ mode** | API lỗi, trường bắt buộc thiếu hoặc quyền không đủ | `ERROR`, không PASS theo giả định mặc định của Google |

**Lưu ý trong PDF Standard:** ở nhánh `ADVANCED_DATAPATH`, `addonsConfig.networkPolicyConfig.disabled=True` có thể **hoàn toàn hợp lệ** vì Dataplane V2 đã tích hợp enforcement. Việc kiểm tra máy móc “add-on disabled thì FAIL” sẽ tạo false positive. Ở nhánh Calico, **cả node enforcement và add-on** phải đúng mới đủ.

### 8.3. Manual-review logic

| Tình huống | Trạng thái đề xuất và lý do |
|---|---|
| Standard `ADVANCED_DATAPATH`, API evidence đầy đủ | REVIEW chờ xác nhận Manual; reviewer kiểm mode, config và kịch bản thực tế → PASS |
| Standard legacy + Calico đủ ba thành phần | REVIEW chờ kiểm Manual → PASS khi xác minh được |
| Standard legacy không bật Calico hoặc thiếu add-on | FAIL khi chứng minh thiếu enforcement; ghi fields hiện hữu |
| Autopilot `ADVANCED_DATAPATH` xác nhận được | REVIEW chờ manual validation → PASS |
| Autopilot không trả `ADVANCED_DATAPATH` dù đúng mode | REVIEW/FAIL sau điều tra cấu hình và giới hạn API; tuyệt đối không cấu hình Calico trên Autopilot |
| Thiếu quyền đọc GKE Cluster API hoặc field bắt buộc | ERROR; không nói “Autopilot chắc chắn PASS vì là managed” |

**Điểm phân biệt Manual:** công cụ có thể tự so sánh giá trị Cloud rất rõ, nhưng quyết định công bố PASS cuối vẫn phải tuân theo quy trình Manual review mà nhóm đặt ra. Nếu triển khai một trạng thái sơ bộ như `candidate_pass`, nó phải ở **metadata**, không biến thành PASS khi chưa đủ bước review.

### 8.4. Các kịch bản kiểm thử

| Test ID | Chế độ/cấu hình | Kỳ vọng |
|---|---|---|
| `T431-01` | Standard `ADVANCED_DATAPATH`, add-on `disabled=true` | Không flag sai add-on; REVIEW → PASS sau review |
| `T431-02` | Standard `LEGACY_DATAPATH`, Calico enabled/provider/add-on đúng | REVIEW → PASS sau review |
| `T431-03` | Standard legacy, `networkPolicy.enabled=false` | FAIL |
| `T431-04` | Standard legacy, node enabled nhưng add-on disabled | FAIL hoặc REVIEW noncompliant/incomplete theo spec |
| `T431-05` | Autopilot `ADVANCED_DATAPATH` | REVIEW → PASS sau review, CIS **L2** |
| `T431-06` | Autopilot không có Calico config (bình thường) | Không flag thiếu Calico |
| `T431-07` | Không có quyền `clusters.get`/field cần thiết | ERROR |
| `T431-08` | Rule nhận dữ liệu Standard nhưng gắn benchmark Autopilot hoặc ngược lại | ERROR cấu hình/mode mismatch, không dùng nhầm rule |

**Tác động remediation:** Standard không thể bật Dataplane V2 trên cluster legacy hiện hữu chỉ bằng một lệnh chuyển đổi thông thường; cần tính tới tạo cluster mới nếu muốn thay sang V2. Với legacy, bật Calico có thể tạo lại node pools và gây gián đoạn; chỉ xử lý qua thiết kế hạ tầng/approval thích hợp. **Không tự chạy gcloud update trong audit hoặc CI thông thường.** Với Autopilot, enforcement đã tích hợp; remediation liên quan **NetworkPolicy objects**, không phải “bật Calico”.

| Công việc | Owner | Đầu ra / người nhận |
|---|---|---|
| Google Cloud collector và xác thực cluster mode | **A** | Cloud evidence có fields/errors cho B/C |
| CIS Standard/Autopilot mapping và code `4.3.1` | **C** | Rule + fixtures qua PR, B review |
| Registry, Manual-review workflow, reporter | **B** | Finding schema + JSON/HTML, C QA |
| Live verification dataplane / hỗ trợ debug | **A + C** | Bằng chứng config và traffic nếu cần cho B |
| Cloud change có tác động (nếu có) | **A** thực hiện sau phê duyệt | C xác minh QA; người có thẩm quyền approve độc lập |

**Nghiệm thu:** hai đường Standard (Dataplane V2/Calico) đều được xử lý đúng; Autopilot không bị kiểm add-on Calico; Level CIS đúng theo mode; thiếu quyền thành ERROR; kết quả Manual có evidence và review.

[↑ Trở về mục lục](#muc-luc)

---

<a id="cis-432"></a>

## 9. CIS 4.3.2 — Default-deny NetworkPolicy trong workload namespace

**Nguồn:** **CIS GKE Standard Benchmark v2.0.0**, trang in **67–69**.  
**Phạm vi:** **chỉ Standard — Level 2 — Automated**. Không có control `4.3.2` trong Autopilot Benchmark v2.0.0.  
**Owner nội dung, code rule và NetworkPolicy lab:** **C**. **A** xác minh enforcement/network; **B** tích hợp evaluator/report/re-audit.

> **Điểm kiểm tra:** Default-deny của Standard; tách kiểm tra enforcement trong PDF và policy coverage bổ sung của nhóm.  
> **Trọng tâm bàn giao:** C — rule, policy/traffic lab; A — network/cloud evidence; B — integration/report.

### 9.1. Mục đích bảo mật, khác biệt với `4.3.1`

Kubernetes mặc định không tự chia tách traffic của workload chỉ vì các Pod nằm trong namespace khác nhau. **NetworkPolicy** xác định luồng ingress/egress cho tập Pod được chọn. Mục tiêu default-deny là đặt trạng thái *không cho phép kết nối ngoài chủ đích*, sau đó thêm **allow rules tối thiểu** để workload vẫn hoạt động.

**Hai điều kiện khác nhau phải kiểm tra:**

1. **Enforcement hoạt động** qua Dataplane V2/Calico — đã được phân tích ở `4.3.1` và cũng được nêu trong phần Audit của PDF `4.3.2`.
2. **Các namespace workload thực sự có cấu hình default-deny cần thiết**, không chỉ sở hữu vài policy rời rạc — **đặc tả kiểm tra bổ sung của nhóm** nhằm đáp ứng ý nghĩa nêu ở tiêu đề/Description `4.3.2`. Có policy nhưng traffic vẫn thông vì allow rules quá rộng thì chưa chứng minh được hardening hữu hiệu.

**Bất nhất cần ghi trong báo cáo:** phần *Audit* chính thức của Standard `4.3.2` trình bày kiểm tra trạng thái Dataplane V2/Calico, khá giống `4.3.1`, thay vì đưa một thuật toán hoàn chỉnh để xác định namespace đã default-deny. Nhóm **không sửa lại PDF**, mà công khai cách mapping triển khai bổ sung. Nếu chưa được reviewer thông qua cách tính compliance cho tên control, giữ `REVIEW`/ghi rõ giới hạn thay vì tuyên bố hoàn toàn tuân thủ.

### 9.2. Cần thu thập những gì?

| Nguồn | Thông tin | Vai trò |
|---|---|---|
| Google Cloud API | GKE mode, `datapathProvider`, Calico fields nếu legacy | **A** cung cấp, bảo đảm enforcement thực sự được cấu hình |
| Kubernetes Namespace | Danh sách namespace chứa workload trong scope | **B** collector, **C** chốt namespace nào phải kiểm |
| NetworkPolicy API | `metadata.namespace/name`, `spec.podSelector`, `spec.policyTypes`, `spec.ingress`, `spec.egress` | **B** collector; **C** rule, phân tích isolation |
| Pods/labels/Services | Selector thực sự chọn Pod nào; dịch vụ nào cần liên lạc | **C** lab; **B** collector |
| Traffic test evidence | Kết quả HTTP, DNS, ingress, egress, allowed/blocked, thời điểm/context | **C** chủ trì; **A** hỗ trợ dataplane/troubleshooting |

**Lưu ý cấu trúc:** một policy với `podSelector: {}` chọn **tất cả Pod trong namespace đó**. Một policy có `policyTypes: [Ingress, Egress]` và không có ingress/egress allow rules là mẫu default-deny rõ ràng cho cả hai chiều; có thể dùng hai policy riêng để deny ingress và deny egress với coverage tương đương. Khi kết hợp cùng allow policies, NetworkPolicy dùng cơ chế **hợp các luồng được cho phép**, nên **có default-deny không tự bảo đảm cuối cùng mọi luồng ngoài ý muốn đều bị chặn**. Cần rà allow rules thực tế và đo traffic.

### 9.3. Ma trận đánh giá đề xuất cho dự án

| Quan sát được | Kết quả gợi ý | Vì sao |
|---|---|---|
| Standard, enforcement hợp lệ, **mọi namespace workload trong scope** có default-deny bao phủ toàn bộ Pod và hai chiều; không có allow quá rộng; test allowed/blocked đúng | **PASS**, chỉ sau khi coverage và độ tin cậy evidence được C xác nhận | Đạt cả điều kiện cấu hình do nhóm đặc tả và thực nghiệm trong lab |
| Thiếu default-deny cho một namespace workload | **FAIL** | Cần nêu namespace cụ thể |
| Chỉ deny ingress, không có egress isolation, hoặc ngược lại | **FAIL** theo đặc tả mặc định 2 chiều của dự án | Không đáp ứng mục tiêu ingress/egress trong lab |
| Policy default-deny chỉ chọn một subset Pod, bỏ sót workload khác trong namespace | **FAIL** hoặc REVIEW nếu selector/Pod inventory chưa đủ | Không bao phủ namespace workload |
| Enforcer không hoạt động | **FAIL** ở điều kiện nền `4.3.1`/`4.3.2`; không kết luận “policy đang bảo vệ” | Policy YAML không có hiệu lực cưỡng chế |
| Tìm thấy default-deny nhưng allow-all/allow quá rộng hoặc chưa có traffic evidence | **REVIEW** hoặc FAIL khi chứng minh vi phạm | Tránh tuyên bố an toàn chỉ bằng sự tồn tại của object |
| Chưa phân loại đủ namespace, lỗi list NetworkPolicy, Pod hoặc Cloud config | **ERROR** nếu lỗi thu thập; REVIEW nếu còn câu hỏi nghiệp vụ | Không được PASS khi scope/evidence không đầy đủ |
| Autopilot ở bảng đối chiếu | **N/A — không có ID `4.3.2`**, không coi là PASS | Vẫn có thể hardening với NetworkPolicy, nhưng ngoài control ID này |

**Phạm vi Level:** mặc dù `4.3.2` là **CIS Level 2** của Standard, nhóm chọn để demo P0 vì có khả năng chứng minh rõ before/after. Trên báo cáo cần giữ đồng thời `cis_level=2` và `project_priority=P0` (nếu có), không gọi nó là L1.

### 9.4. Thiết kế lab và traffic tests

**Lab tối thiểu:** namespace `lab-network`, một ứng dụng HTTP `server` với Service nội bộ, ít nhất một client hợp lệ và một client không được phép (có thể ở namespace khác); các namespace/labels được chọn sao cho xác minh selectors rõ. Tất cả traffic tests phải có giới hạn thời gian và tiêu chí thành công/thất bại minh bạch.

**Before:** chưa có baseline default-deny. Ghi danh sách policy thực tế, thử kết nối giữa các đối tượng, DNS và app HTTP. Không suy diễn “chắc chắn thông” — phải đo thực.

**After:** tạo default-deny ingress/egress bao phủ namespace, sau đó allow rule tối thiểu cho client đã duyệt, DNS khi workload cần phân giải tên và các luồng egress hợp lệ khác. Nếu workload dùng Workload Identity Federation for GKE, rà egress tới metadata server theo yêu cầu; **không mở egress toàn mạng** chỉ để test qua. Ghi lại cụ thể những flows được cho phép và bị chặn.

| Test ID | Tình huống | Kết quả mong đợi |
|---|---|---|
| `T432-01` | Namespace workload không có default-deny | FAIL, có namespace/Pod coverage evidence |
| `T432-02` | Có default deny ingress nhưng không có egress isolation | FAIL theo đặc tả 2 chiều của dự án |
| `T432-03` | Có default deny ingress + egress bao phủ tất cả Pods, enforcement hợp lệ | Candidate PASS; kiểm tiếp allow rules/traffic và review giới hạn PDF |
| `T432-04` | Policy chỉ chọn label một nhóm Pod, bỏ sót Pod khác | FAIL hoặc REVIEW nếu inventory incomplete |
| `T432-05` | Có default-deny nhưng một allow policy mở ingress/egress quá rộng | REVIEW/FAIL tùy mức có thể chứng minh, không tự PASS |
| `T432-06` | Allowed client vẫn gọi HTTP thành công; blocked client bị từ chối/timeout đúng kỳ vọng; DNS vẫn hoạt động nếu cần | Functional/security evidence đạt |
| `T432-07` | NetworkPolicy tồn tại nhưng enforcement cloud tắt | Không kết luận đạt; xuất finding thiếu enforcement |
| `T432-08` | API NetworkPolicy lỗi `403` hoặc mất dữ liệu namespace | ERROR |
| `T432-09` | Autopilot comparison | N/A cho ID 4.3.2, không thêm vào PASS |
| `T432-10` | Functional test hỏng sau khi áp policy | Rollback, lưu evidence và re-test; không xác nhận remediation thành công |

### 9.5. Quy trình sửa trong lab và trách nhiệm

1. **C** trình bày finding, tác động lên app/service, DNS, metadata và bảng traffic before.
2. **C/A** kiểm tra enforcer Standard đúng loại; nếu enforcer chưa đúng, **A** xử lý riêng qua Terraform/cloud change **sau phê duyệt**, không để C bật Calico tùy tiện.
3. **C** chuẩn bị YAML `default-deny` và `allow-*` tối thiểu, lưu bản policy/workload cũ.
4. **Người có thẩm quyền** phê duyệt chính xác phạm vi namespace/manifest và rollback plan. Nếu không được duyệt: **dừng, chỉ báo cáo**.
5. **C** áp policy **trong lab**, A hỗ trợ network debugging; chạy HTTP, DNS, ingress và egress allowed/blocked.
6. Nếu test chức năng **FAIL**, C rollback, thử lại và báo cáo trạng thái khôi phục. Không giấu thất bại.
7. Nếu test đạt, **B** chạy re-audit và before/after; **C** xác minh report khớp dữ liệu traffic/config thật.

| Việc / đầu ra | Owner | Bàn giao cho / reviewer |
|---|---|---|
| Spec default-deny, cách kiểm selector/coverage, trace nguồn CIS | **C** | B review interface; cả nhóm biết giới hạn PDF |
| Cloud enforcement, Dataplane V2/Calico, IAM/network troubleshooting | **A** | C kiểm thử, B dùng Cloud evidence |
| Code rule `4.3.2`, fixtures, NetworkPolicy manifests | **C** | B review/merge, A hỗ trợ live |
| Report schema, baseline/re-audit/compare | **B** | C QA, A tích hợp |
| Phê duyệt thay đổi | **Approver được ủy quyền**, độc lập với người tự tạo thay đổi | C/A chỉ thực hiện sau khi được duyệt |
| Functional allowed/blocked, DNS/HTTP, rollback/evidence | **C** | B đưa vào report, A cùng debug nếu lỗi |

**Nghiệm thu:** có bằng chứng cả enforcement và policy coverage; phát hiện được thiếu ingress/egress; luồng hợp lệ vẫn chạy, luồng không hợp lệ bị chặn; không gọi `ADVANCED_DATAPATH` là đủ để chứng minh có default-deny; không báo Autopilot PASS `4.3.2`; đã công bố giới hạn cách mapping PDF.

<a id="hinh-03-03"></a>

![Hình 03-03 — CIS 4.3.2 trên Standard: NetworkPolicy default-deny trước và sau](assets/images/11-networkpolicy-before-after.png)

*Hình 03-03. CIS 4.3.2 trên Standard: NetworkPolicy default-deny trước và sau.*
[↑ Trở về mục lục](#muc-luc)

---

<a id="sec-10"></a>

## 10. Hai kịch bản end-to-end và trách nhiệm A/B/C

### 10.1. Kịch bản SA Hardening — kết nối `4.1.4` và `4.1.5`

| Chặng | Việc phải làm | Người chịu trách nhiệm đầu ra | Bằng chứng/bàn giao |
|---|---|---|---|
| **Chuẩn bị** | Dựng namespace và workload HTTP `before`, có trạng thái dùng `default` SA, xác nhận không cần Kubernetes API | **C** | YAML before, HTTP baseline, xác nhận nhu cầu API → B |
| **Môi trường** | Chuẩn bị GKE context, quyền đọc và cấp phép áp dụng lab; đảm bảo không nhầm Standard/Autopilot | **A** | Cluster identity/mode/context, cloud/read access → B/C |
| **Audit ban đầu** | Chạy `4.1.4`, `4.1.5`, phân biệt Automated với Manual và lưu findings | **B** | Baseline JSON/HTML, evidence refs → C |
| **Kiểm chứng nội dung** | Xác minh `4.1.4` có FAIL thực, `4.1.5` có review question / kết luận đúng ngữ cảnh | **C** | Manual evidence, nhận xét QA → B |
| **Phê duyệt** | Trình impact, YAML diff, backup/rollback và phạm vi thay đổi cho approver | **C**, A hỗ trợ tác động cloud | Approval record; **không duyệt thì không apply** |
| **Khắc phục** | Tạo dedicated SA, cập nhật Pod template và tắt auto-mount khi không cần API | **C** | YAML after và command/log thay đổi → B |
| **Functional test** | Kiểm tra Pod Ready/HTTP; rollback nếu fail | **C**, A hỗ trợ môi trường | HTTP/rollout/rollback evidence → B |
| **Re-audit/report** | Chạy lại engine trên đúng resource/scope; so trước/sau | **B** | Before/After report → A/C |
| **Nghiệm thu** | Kiểm CIS, evidence, app activity và ghi giới hạn | **C** security QA; A tích hợp demo | QA conclusion chung |

**Không coi thành công chỉ vì đổi `serviceAccountName` trong Git.** Phải thấy trạng thái live sau rollout và ứng dụng hoạt động. Tương tự, `automountServiceAccountToken=false` chỉ đạt ý nghĩa của `4.1.5` khi đã có bằng chứng ứng dụng không cần Kubernetes API.

### 10.2. Kịch bản NetworkPolicy Hardening — kết nối `4.3.1` và `4.3.2`

| Chặng | Việc thực hiện | Người chịu trách nhiệm | Bàn giao |
|---|---|---|---|
| Xác minh trước | Chọn GKE **Standard**, xác nhận Dataplane V2 hoặc Calico đầy đủ, đọc network fields | **A**, C đối chiếu CIS | Cloud collector evidence → C/B |
| Chuẩn bị lab | Namespace, server, allowed client, blocked client, DNS/HTTP checks | **C** | YAML + traffic test plan → A/B |
| Baseline audit | Rule `4.3.1` + `4.3.2`, lưu kết quả và giới hạn data | **B** chạy engine; **C** xác minh rule | JSON/HTML + findings → C |
| Phân tích rủi ro | Thiết kế default-deny ingress/egress + allow rules tối thiểu | **C**, A review networking | Policy diff, allow-list, rollback plan |
| Approval | Xin phê duyệt trước apply | **C** đề xuất; Approver độc lập quyết định | Approval record |
| Apply trong lab | Áp chính sách trong namespace đã duyệt | **C**, A hỗ trợ debug | Applied manifests, Kubernetes evidence |
| Test network | Allowed/blocked, DNS, HTTP, metadata egress nếu cần | **C**; A hỗ trợ dataplane | Các phép đo/test kết quả thật → B |
| Re-audit | Chạy engine và compare đúng mode/cluster/resource | **B** | Before/After report → C/A |
| QA/rollback | Thử phục hồi khi test thất bại, xác nhận kết quả cuối | **C**, A hỗ trợ khi liên quan Cloud | QA + rollback/functional evidence |

**Cảnh báo:** dùng `4.3.1` để chứng minh enforcer tồn tại và `4.3.2` để kiểm chứng policy goal theo mapping đã được tài liệu này giải thích. Nếu cloud enforcement không hoạt động, không được tuyên bố policy có tác dụng.

<a id="hinh-03-04"></a>

![Hình 03-04 — Phối hợp A/B/C trong hai kịch bản ServiceAccount và NetworkPolicy](assets/images/12-owner-handoff-hardening.png)

*Hình 03-04. Phối hợp A/B/C trong hai kịch bản ServiceAccount và NetworkPolicy.*
---

<a id="sec-11"></a>

## 11. Bộ kiểm thử chung cho Audit Engine

### 11.1. Tách ba mức kiểm thử

| Loại kiểm thử | Dùng cho việc gì | Owner | Không được nhầm với |
|---|---|---|---|
| **Unit tests (`pytest`)** | Rule nhận input chuẩn/fixture và cho kết quả đúng kể cả dữ liệu biên, ngoại lệ, lỗi | **B** test framework; **B/C** theo rule phụ trách | Không chứng minh Cloud/Kubernetes thực tế đã tuân thủ |
| **Integration tests (read-only)** | Collector thực sự đọc được cluster/namespace, mode và resource; schema không đổi | **A** Cloud, **B** Engine, **C** đối chiếu | Không tự tạo policy/SA hoặc tự `apply` |
| **Functional/security tests trong lab** | App còn chạy, NetworkPolicy chặn/cho phép đúng, PSS admission như kỳ vọng, rollback hoạt động | **C** chủ trì, **A** hỗ trợ network, **B** report | Không thay thế đối chiếu CIS hoặc chứng minh tất cả mode đạt |

### 11.2. Những negative cases toàn hệ thống phải kiểm

| Tình huống | Kết quả bắt buộc | Phụ trách test |
|---|---|---|
| Mode xác định sai/mismatch benchmark | Chặn audit/ERROR rõ lý do; không đọc rule sai | A + B + C review |
| API `403`, timeout hoặc response thiếu bắt buộc | ERROR có nguồn và trường thiếu; không tự PASS/FAIL | A/B |
| Pagination thiếu một trang khi list nhiều namespaces/RBAC | ERROR/incomplete; không kết luận toàn cluster PASS | B |
| User workload không biết `requires_kubernetes_api` | REVIEW, nêu câu hỏi để xử lý | C/B |
| Chỉ tồn tại default SA, không có workload sử dụng | `4.1.4` không FAIL | B/C |
| Ba system defaults bind `system:authenticated` | `4.1.9` không FAIL chỉ vì tồn tại | B/C |
| Standard Dataplane V2 và network-policy add-on disabled | `4.3.1` không FAIL sai | A/C |
| Autopilot quét ID Standard-only | N/A trong so sánh hoặc không sinh finding trong audit mode-specific | B/C |
| Report chứa đường dẫn token/credential/secret | Dừng xuất/publish artifact; làm sạch bằng chứng | B/C, A xem CI/log |
| Không được phê duyệt remediation | **Không có thay đổi** trong cloud/namespace; report vẫn tạo được | C/A, B kiểm report |
| Functional test fail sau sửa | Rollback, chạy lại health/traffic test, ghi nhận failure | C/A |
| Re-audit trên cluster hoặc namespace khác baseline | Không so sánh như cùng một thực thể; báo scope mismatch | B |

### 11.3. Quy tắc coverage và tỷ lệ hiển thị trong báo cáo

Không nên công bố “tuân thủ CIS GKE 100%” khi dự án chỉ thực hiện một **tập 6 control chọn lọc** hoặc khi còn Manual REVIEW. Báo cáo tối thiểu phải thể hiện:

- Số control thuộc benchmark/mode trong **phạm vi đã chọn**, số control **đã triển khai**, số control **chưa triển khai**.
- PASS, FAIL, REVIEW, ERROR **tách riêng**; N/A nếu dùng trong bảng so sánh cũng tách riêng.
- Một tỷ lệ minh họa trên phần **đã có kết luận** (nếu muốn) phải chú thích công thức và mẫu số. Ví dụ `PASS / (PASS + FAIL)` chỉ phản ánh **các kết luận đã phân loại**, không phản ánh toàn bộ CIS compliance và không che REVIEW/ERROR.
- Level 1 và Level 2 không nên bị trộn như một profile tổng quát nếu người xem hiểu sai; Standard/Autopilot phải tách.
- Mọi số liệu, timestamp và kết quả live phải được lấy từ lần chạy thật; không chèn dữ liệu giả từ hình AI để trình bày là sản phẩm hoàn thành.

---

<a id="sec-12"></a>

## 12. Data contract và ví dụ output

### 12.1. JSON finding minh họa (không phải evidence thực tế)

```json
{
  "run_id": "example-run-id",
  "mode": "standard",
  "benchmark": "CIS Google Kubernetes Engine (GKE) Benchmark",
  "benchmark_version": "2.0.0",
  "cluster": {
    "project_id": "example-project",
    "location": "example-region",
    "name": "example-cluster"
  },
  "scope": {
    "namespaces": ["lab-sa"],
    "coverage": "selected-project-lab-only"
  },
  "control_id": "4.1.4",
  "cis_level": 1,
  "assessment_type": "Automated",
  "project_priority": "P0",
  "status": "FAIL",
  "resource": {
    "kind": "Deployment",
    "namespace": "lab-sa",
    "name": "example-web"
  },
  "reason": "Pod template uses the namespace default ServiceAccount",
  "evidence": {
    "source": "Kubernetes API",
    "field": "spec.template.spec.serviceAccountName",
    "observed": "default",
    "reference": "evidence/example-414-sanitized.json"
  },
  "collected_at": "EXAMPLE_TIMESTAMP_NOT_A_REAL_MEASUREMENT",
  "review_decision": null,
  "limitations": []
}
```

Đây **chỉ là schema ví dụ**, chưa phải contract cuối. Khi hiện thực cần thêm `run_status`, `collection_completeness`, `rule_version`, `git_commit`, `redaction`, `source_pdf_page` và các trường phục vụ finding Manual/ERROR. Tránh gộp nhiều cluster/mode hoặc nhiều resource vào một finding rồi mất dấu vi phạm.

### 12.2. Mẫu record Manual review

```yaml
control_id: "4.1.5"
mode: standard
resource: "Deployment/lab-sa/example-web"
review_status: pending  # pending | accepted | rejected
reviewer: null           # điền người thực sự đánh giá
reviewed_at: null        # timestamp thực tế, không ghi giả
requires_kubernetes_api: unknown  # yes | no | unknown
question: "Workload có cần gọi Kubernetes API bằng SA token không?"
source_evidence_refs:
  - "evidence/example-pod-spec.json"
conclusion: REVIEW
notes: "Chưa có xác nhận nhu cầu API từ owner workload."
```

Sau review, chỉ đổi `conclusion` khi có `reviewer`, `reviewed_at`, evidence và giải thích. Dữ liệu `requires_kubernetes_api` phải lấy từ xác nhận hoặc kiểm thử phù hợp; không giả định từ tên application.

### 12.3. Hợp đồng hàm ở mức khái niệm

```python
# Pseudocode interface đề xuất — không phải mã sản phẩm đã chạy.


def evaluate_control(control_spec, normalized_evidence, audit_context):
    """Return findings with status, evidence refs, and completeness metadata."""
    # B xác định schema, rule interface và cách tổng hợp.
    # B trực tiếp thực hiện 4.1.4 / 4.1.5 / 4.1.9.
    # C trực tiếp thực hiện 4.2.1 / 4.3.1 / 4.3.2 trên interface này.
    # A cung cấp Cloud collector evidence, không mutate trong audit.
    raise NotImplementedError
```

**Không được tự kết luận `N/A` khi Python chưa hiện thực rule**. Trường hợp đó phải nêu trong `coverage.not_implemented`, và nếu người dùng yêu cầu audit một control được đăng ký mà chưa có implementation thì báo lỗi/từ chối có giải thích, không tạo PASS/N/A giả.

---

<a id="sec-13"></a>

## 13. Bàn giao module và các phụ thuộc kỹ thuật

### 13.1. Việc có thể làm song song

| A có thể bắt đầu | B có thể bắt đầu | C có thể bắt đầu |
|---|---|---|
| Terraform VPC/subnets/GCS state, chuẩn bị GKE Standard/Autopilot, cloud collector mock schema | JSON models, Kubernetes collector mock clients, evaluator/status, CLI, pytest harness, 4.1.x rules trên fixtures | Đối chiếu CIS source, control matrix, fixtures specs, SA/PSS/NetworkPolicy manifests offline, test kế hoạch |

**Các điểm cần chốt chung trước khi tích hợp live:** mode/benchmark ID; `docs/contracts.md`; namespace scope; source evidence fields; Manual-review decision model; ownership file paths; expected rules/test cases.

### 13.2. Việc phụ thuộc thật

| Khi có đầu ra | Ai có thể làm tiếp? | Nếu chưa có thì làm gì thay thế? |
|---|---|---|
| **C** gửi CIS Matrix/spec/fixtures phiên bản thống nhất | **B/C** hiện thực và test rules trên input mock | B hoàn thiện engine framework, không đoán cách đánh giá |
| **B** gửi rule interface/schema | **C** viết 4.2/4.3 module đúng interface; **A** chuẩn hóa Cloud collector output | C tiếp tục test YAML/kịch bản thủ công, A dựng cloud |
| **A** giao live cluster + read-only APIs | **B** chạy live collector/audit, **C** deploy lab đúng scope | B/C chạy fixture/unit tests offline |
| **A** xác nhận Dataplane/Calico Standard | **C** kiểm tra default-deny có enforcement trong lab | C chưa tuyên bố traffic restriction thật từ YAML |
| **C** giao approval + YAML before/after + functional evidence | **B** tạo before/after report đáng tin cậy | B làm schema/compare bằng dữ liệu ví dụ và gắn rõ demo |
| **B** giao report/live findings | **C** làm security QA và chỉnh expected tests nếu spec có lỗi | C kiểm evidence `kubectl`/gcloud thủ công, không sửa số liệu bằng tay |

### 13.3. Danh mục bàn giao cuối theo người

| Thành viên | File/module tối thiểu cần bàn giao | Người nhận chính |
|---|---|---|
| **A** | Terraform cho hạ tầng/mạng/Standard/Autopilot, hướng dẫn GCS state và destroy, Google Cloud collector, cloud field mapping, context/permission guide, CI cloud auth safeguards | B và C |
| **B** | Python Audit Engine core, Kubernetes collector, mode-aware registry, 4.1.x rules, pytest/fixtures harness, JSON/HTML reporter, diff/re-audit runner, contract/CLI README | A và C |
| **C** | CIS Matrix có trang nguồn, đặc tả 6 controls, code rule 4.2.1/4.3.1/4.3.2 theo contract B, YAML SA/PSS/NP before/after, expected traffic/admission/HTTP tests, impact/approval/rollback plans, security QA report | A và B |
| **Cả nhóm** | PR reviews, source/evidence references, live demo tests trên hai mode đúng scope, approval records và cleanup confirmation | Người nghiệm thu/giảng viên |

**Điều kiện “đã bàn giao”:** người nhận chạy hoặc đọc thử được mà không phải đoán field/tên file; có commit và test evidence; có giới hạn rõ ràng; người review xác nhận interface phù hợp. Nếu chỉ gửi screenshot nhưng không có manifest/code/schema nguồn, chưa đủ bàn giao kỹ thuật.

---

<a id="sec-14"></a>

## 14. Checklist nghiệm thu

### 14.1. Checklist tổng thể

- [ ] Sáu control được mapping đúng mode, Level, Automated/Manual, version v2.0.0 và trang nguồn.
- [ ] A/B/C đã thống nhất `docs/contracts.md`, đặc tả scope workload và kiểu trả trạng thái.
- [ ] B triển khai/kiểm thử `4.1.4`, `4.1.5`, `4.1.9`; C triển khai/kiểm thử `4.2.1`, `4.3.1`, `4.3.2` trên interface chung.
- [ ] A cung cấp Google Cloud collector đúng mode, có cả trường hợp thiếu quyền/API error.
- [ ] Unit tests có positive/negative/exception/error cases, không chỉ test nhánh đẹp.
- [ ] Manual controls có reviewer, lý do, evidence; chưa xác minh giữ REVIEW.
- [ ] Không có false positive ở default SA chỉ tồn tại, ba system RBAC bindings, Dataplane V2 với add-on disabled.
- [ ] Không có PASS giả cho `4.2.1`/`4.3.2` Autopilot; N/A không cộng vào PASS.
- [ ] 4.3.2 có giải thích giới hạn/bất nhất phần Audit của PDF và mapping bổ sung của dự án; không coi enforcement là đủ để kết luận có default-deny.
- [ ] Live evidence có mode/cluster/namespace/timestamp, không lấy dữ liệu fixture gắn nhãn live.
- [ ] Hai kịch bản remediation có approval/backup/functional test/rollback/re-audit/Before–After.
- [ ] JSON/HTML không lộ Secret/token/credentials; CI không tự apply resource.
- [ ] README/runbook và các artefacts đủ để một thành viên khác chạy lại từng bước trong lab.

### 14.2. Những gì KHÔNG thuộc cam kết P0

Tài liệu này **không cam kết** quét toàn bộ CIS GKE Benchmark, không đưa ra chứng chỉ tuân thủ chính thức của CIS, không tự áp remediation lên production và không chứng minh năng lực bảo mật tổng thể của một GKE cluster chỉ từ sáu controls. Những việc đó nếu cần mở rộng phải thành scope riêng, có đánh giá rủi ro và nguồn CIS tương ứng.

**P1 tham khảo, chỉ triển khai nếu nhóm quyết định:** `4.1.2` (Secret access Manual, **không đọc secret values**); `5.6.1` (Standard VPC Flow Logs/Intranode Visibility); `5.4.1` (Autopilot control cùng chủ đề). Không tự nhập nhằng P1 với sáu control P0 hoặc sử dụng mã Standard cho Autopilot.

---

<a id="sec-15"></a>

## 15. Nguồn tham chiếu và nguyên tắc đối chiếu CIS

### 15.1. Nguồn chính (đã được đối chiếu khi biên soạn)

| Nguồn | Phiên bản | Các trang in trong PDF liên quan đến sáu control |
|---|---|---|
| *CIS Google Kubernetes Engine (GKE) Benchmark* | **v2.0.0 — 30/06/2026** | `4.1.4`: 40–41; `4.1.5`: 43–44; `4.1.9`: 55–57; `4.2.1`: 60–62; `4.3.1`: 64–66; `4.3.2`: 67–69 |
| *CIS Google Kubernetes Engine (GKE) Autopilot Benchmark* | **v2.0.0 — 30/06/2026** | `4.1.4`: 26–27; `4.1.5`: 29–30; `4.1.9`: 41–43; `4.3.1`: 46–47; **không có** `4.2.1` và `4.3.2` |
| Tài liệu 01 trong bộ dự án | Bản bảng Markdown hiện hành | Phạm vi, kiến trúc, kết quả audit, hai lab và nghiệm thu chung |
| Tài liệu 02 trong bộ dự án | Bản bảng Markdown hiện hành | Chủ sở hữu module, công việc trực tiếp A/B/C, bàn giao và review |

**Về cách ghi trang:** các số ở trên là **trang in trong nội dung CIS PDF**, không phải chỉ số trang 0-based của phần mềm đọc PDF. Khi trích dẫn trong báo cáo, ghi tên benchmark, phiên bản, CIS ID và số trang; không sao chép/phát tán toàn văn PDF benchmark lên repo public.

### 15.2. Ranh giới giữa yêu cầu nguồn CIS và quyết định thiết kế của dự án

| Thuộc về nguồn CIS v2.0.0 | Là quyết định/thành phần do nhóm thiết kế |
|---|---|
| Control ID, tên, Level, Automated/Manual, ý nghĩa bảo mật và Audit/Remediation/Impact được PDF mô tả | Chỉ chọn 6 control P0, xác định phạm vi namespace lab, ưu tiên giải pháp Python + Terraform |
| `4.3.1` có thể dùng Dataplane V2 hoặc Calico trên Standard; Autopilot có Dataplane V2 built-in | Manual `REVIEW` workflow, JSON/HTML schema, rule registry, reporter, phương án chọn test traffic |
| `4.1.9` nêu ba binding hệ thống mặc định và custom binding cần tránh | Thuật toán whitelist xác minh roleRef/subjects, tên file fixtures, bộ test IDs |
| `4.2.1` yêu cầu enforce baseline/restricted tại workload namespaces trên Standard | Lab admission/test case, người xác nhận review, nội dung demo |
| `4.3.2` mô tả default-deny nhưng Audit section chủ yếu xác minh enforcement | Phần kiểm tra bổ sung selector/policy ingress+egress/allowed-blocked traffic và cách giải thích giới hạn |

Trước khi nhóm công bố các kết quả hoặc sửa code theo thay đổi sản phẩm GKE, C đối chiếu lại nguồn CIS; A đối chiếu API và trạng thái GKE thực; B kiểm tra regression tests và báo cáo. **Nếu có khác biệt giữa dự kiến và dữ liệu thật, lưu sự khác biệt và điều tra; không thay evidence hoặc bỏ FAIL để đẹp báo cáo.**

---

## Kết luận — Sản phẩm cần hoàn thành

Tài liệu 03 là **đặc tả đưa dự án từ “có danh sách sáu CIS” sang “biết chính xác phải xây, kiểm thử và nghiệm thu mỗi CIS như thế nào”**:

- **A** đọc để biết cần dựng hạ tầng và giao trường Cloud nào cho rule, hỗ trợ network/permission gì và khi nào tuyệt đối không tự thay đổi hạ tầng.
- **B** đọc để biết input/evidence, logic đánh giá, cases pytest, điều kiện Manual/ERROR và cách tạo JSON/HTML/Before–After; đồng thời review code rule C theo interface chung.
- **C** đọc để biết cách diễn giải yêu cầu CIS v2.0.0, viết trực tiếp rule PSS/NetworkPolicy, chuẩn bị YAML/fixtures, chạy admission/traffic/HTTP tests, xin approval và kết luận QA.

**Quy tắc chốt:** đúng benchmark, đúng mode, đúng đối tượng, đủ evidence, có người làm chính, có người kiểm tra và **không nhận là đã đạt khi chưa thử nghiệm thật**.
