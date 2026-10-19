# Data Contracts & Schemas (DRAFT)

> [!WARNING]
> **TÀI LIỆU NÀY LÀ BẢN THẢO (DRAFT KHUNG SCHEMA) — CHƯA PHẢI BẢN CHỐT CHÍNH THỨC**  
> Tài liệu này phác thảo khung hợp đồng dữ liệu giữa các module thu thập (Collectors), chuẩn hóa (Normalizers), đánh giá (Evaluator) và báo cáo (Reporting).
> 
> **Các hành động rà soát bắt buộc trước khi cố định API (Action Items):**
> 1. **Role B (Python Audit Lead):** Xác nhận và chuẩn hóa các kiểu dữ liệu bằng Python Pydantic (hoặc dataclasses), cơ chế serialization JSON và error handling.
> 2. **Role A (Cloud & Integration Lead):** Review và xác nhận các trường dữ liệu trích xuất từ Google Cloud API (Container Engine v1 API response, `networkConfig.datapathProvider`, `privateClusterConfig`, `masterAuthorizedNetworksConfig`, `ipAllocationPolicy`, các mã lỗi IAM/API).
> 3. **Role C (CIS Security, Labs & QA Lead):** Review và chuẩn hóa ngữ nghĩa an ninh (Security Semantics: định nghĩa các trạng thái `PASS`, `FAIL`, `REVIEW`, `N/A`, `ERROR`, cách mô tả bằng chứng evidence, và câu hỏi thẩm định cho các rule `Manual`).

---

## 1. Kiến trúc luồng dữ liệu (Data Pipeline Flow)

```text
  ┌─────────────────────────────────────────────────────────────┐
  │                    COLLECTORS (Read-Only)                   │
  │  [A: Google Cloud API Collector]   [B: K8s API Collector]   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Raw Dictionaries / API Models
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                      NORMALIZERS (B)                        │
  │  • Làm sạch dữ liệu, loại bỏ thông tin nhạy cảm             │
  │  • Chuẩn hóa thành NormalizedResource & NormalizedCluster   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Clean Normalized Models
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 RULES & EVALUATION ENGINE                   │
  │  • Role Registry: Chọn rule theo Mode (STANDARD/AUTOPILOT)  │
  │  • Rules 4.1.x (B) & Rules 4.2.x/4.3.x (C)                  │
  │  • Đánh giá và sinh FindingResult                           │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Evaluation Findings
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                        REPORTING (B)                        │
  │  • JSON Reporter (Machine-readable)                         │
  │  • HTML Reporter (Auditor-friendly with Evidence & Diff)    │
  └─────────────────────────────────────────────────────────────┘
```

---

## 2. Khung Schema Chi Tiết (Draft Data Models)

### 2.1. Cloud Cluster Metadata (`RawCloudClusterData`) — *Role A review*
Dữ liệu do Google Cloud Collector (Role A) thu thập từ Google Cloud API (`projects.locations.clusters.get`):

```python
# Draft Pydantic Model
class ClusterMode(str, Enum):
    STANDARD = "STANDARD"
    AUTOPILOT = "AUTOPILOT"


class RawCloudClusterData:
    project_id: str
    location: str
    cluster_name: str
    mode: ClusterMode  # Tự động xác định từ cluster.autopilot.enabled
    cluster_version: str  # GKE control plane version
    status: str  # RUNNING, PROVISIONING, etc.

    # Network & Datapath fields (phục vụ Rule 4.3.1)
    datapath_provider: (
        str  # "ADVANCED_DATAPATH" (Dataplane V2) hoặc "DATAPATH_PROVIDER_UNSPECIFIED"
    )
    network_policy_enabled: bool  # addon networkPolicyConfig.disabled == False (Standard)
    network_policy_provider: str  # "CALICO" hoặc "PROVIDER_UNSPECIFIED"

    # Control Plane Security fields
    master_authorized_networks_enabled: bool
    private_cluster_enabled: bool  # privateClusterConfig.enablePrivateNodes
    private_endpoint_enabled: bool  # privateClusterConfig.enablePrivateEndpoint

    # Node Security fields
    workload_identity_pool: Optional[str]  # workloadIdentityConfig.workloadPool
    shielded_nodes_enabled: bool  # shieldedNodes.enabled

    # Metadata thu thập
    collected_at: str  # ISO 8601 UTC timestamp
    collector_error: Optional[str]  # Ghi nhận lỗi nếu thiếu quyền IAM (e.g. 403 Forbidden)
```

### 2.2. Kubernetes Workload & RBAC Metadata (`RawK8sResourceData`) — *Role B review*
Dữ liệu do Kubernetes Collector (Role B) thu thập qua K8s API:

```python
class RawK8sWorkloadData:
    namespace: str
    kind: str  # Pod, Deployment, DaemonSet, StatefulSet, Job
    name: str
    service_account_name: str  # Phục vụ Rule 4.1.4 (xác định xem có dùng default SA)
    automount_service_account_token: Optional[
        bool
    ]  # Phục vụ Rule 4.1.5 (mount token ở Pod/SA spec)
    labels: Dict[str, str]
    pod_security_labels: Dict[str, str]  # Labels PSS trên namespace (phục vụ Rule 4.2.1)


class RawK8sRBACData:
    kind: str  # RoleBinding hoặc ClusterRoleBinding
    name: str
    namespace: Optional[str]  # None đối với ClusterRoleBinding
    role_ref: Dict[str, str]  # kind, name
    subjects: List[Dict[str, str]]  # kind, name, namespace (tìm system:authenticated - Rule 4.1.9)
    is_system_binding: bool  # True nếu thuộc whitelist mặc định của K8s/GKE


class RawK8sNetworkPolicyData:
    namespace: str
    name: str
    pod_selector: Dict[str, Any]
    policy_types: List[str]  # ["Ingress"], ["Egress"], hoặc ["Ingress", "Egress"]
    has_ingress_rules: bool
    has_egress_rules: bool
    is_default_deny_all: (
        bool  # True nếu podSelector: {} và policyTypes có Ingress + Egress không rules
    )
```

### 2.3. Hợp đồng Kết quả Đánh giá (`FindingResult`) — *Role C review ngữ nghĩa*
Mỗi kết quả kiểm tra của một control trên một tài nguyên mục tiêu:

```python
class EvaluationStatus(str, Enum):
    PASS = "PASS"  # Thỏa mãn khuyến nghị của CIS Benchmark
    FAIL = "FAIL"  # Vi phạm khuyến nghị của CIS Benchmark
    REVIEW = "REVIEW"  # Control Manual - cần người thẩm định xác nhận ngữ cảnh nghiệp vụ
    NOT_APPLICABLE = "N/A"  # Control không tồn tại trong benchmark của mode này
    ERROR = "ERROR"  # Lỗi thu thập dữ liệu (thiếu quyền, timeout, API hỏng)


class CISBenchmarkType(str, Enum):
    GKE_STANDARD_V2_0_0 = "CIS Google Kubernetes Engine (GKE) Benchmark v2.0.0"
    GKE_AUTOPILOT_V2_0_0 = "CIS Google Kubernetes Engine (GKE) Autopilot Benchmark v2.0.0"


class FindingResult:
    rule_id: str  # "4.1.4", "4.1.5", "4.1.9", "4.2.1", "4.3.1", "4.3.2"
    benchmark: CISBenchmarkType  # Bộ benchmark được áp dụng
    cluster_mode: ClusterMode  # STANDARD hoặc AUTOPILOT
    cis_level: str  # "Level 1" hoặc "Level 2"
    assessment_type: str  # "Automated" hoặc "Manual"

    status: EvaluationStatus  # PASS | FAIL | REVIEW | N/A | ERROR
    target_resource: str  # e.g., "k8s/namespace/default/Pod/web-app"

    title: str  # Tên tiêu chuẩn của CIS Control
    evidence: Dict[str, Any]  # Bằng chứng cấu hình thu được (observed data vs expected)
    rationale: str  # Giải thích vì sao đạt / không đạt / câu hỏi Manual cần thẩm định
    remediation_guidance: str  # Tóm lược hướng dẫn khắc phục tham chiếu từ benchmark

    timestamp: str  # Thời điểm thực hiện đánh giá (ISO 8601 UTC)
    evaluated_by: str  # Version của audit engine
```

### 2.4. Khung Báo cáo Tổng thể (`AuditReport`) & Metadata Coverage
Tách biệt rõ giữa **mức độ hỗ trợ của công cụ (Tool Coverage)** và **kết quả đánh giá thực tế (Cluster Findings)**:

```python
class RuleCoverageStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"  # Đã code xong rule logic
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"  # Nằm trong scope dự án nhưng chưa hoàn thiện code
    OUT_OF_SCOPE = "OUT_OF_SCOPE"  # Nằm ngoài phạm vi P0 của dự án


class ControlCoverageMeta:
    rule_id: str
    standard_support: RuleCoverageStatus
    autopilot_support: RuleCoverageStatus
    owner: str  # "Role B" hoặc "Role C"


class AuditReport:
    report_id: str
    generated_at: str
    target_cluster: Dict[str, str]  # project, location, cluster_name, mode
    is_live_audit: bool  # True nếu chạy trên GKE thật; False nếu chạy từ test fixtures

    summary: Dict[str, int]  # {"PASS": 0, "FAIL": 0, "REVIEW": 0, "N/A": 0, "ERROR": 0}
    findings: List[FindingResult]
    coverage_metadata: List[ControlCoverageMeta]
```

---

## 3. Quy tắc Ngữ nghĩa An ninh (Security Semantics Guidelines)

1. **Nguyên tắc đối với trạng thái `REVIEW`:**
   - Áp dụng cho các control `Manual` (ví dụ `4.1.5` token mount hoặc `4.3.1` network enforcement).
   - Bắt buộc phải trả kèm danh sách câu hỏi nghiệp vụ và vị trí tài nguyên cần thẩm định. Không được phép tự động trả `PASS`.
2. **Nguyên tắc đối với trạng thái `N/A`:**
   - Chỉ được áp dụng khi Control ID đó **hoàn toàn không tồn tại** trong phiên bản CIS Benchmark của cluster mode đang quét (ví dụ: `4.2.1` và `4.3.2` trên GKE Autopilot).
   - Không được dùng `N/A` để che giấu các rule chưa được viết code (`NOT_IMPLEMENTED`).
3. **Nguyên tắc đối với trạng thái `ERROR`:**
   - Trả `ERROR` khi API trả về mã lỗi (`401`, `403`, `500`), timeout, hoặc response không thể parse.
   - Không được suy diễn thiếu quyền thành `FAIL`.
4. **Bảo vệ dữ liệu nhạy cảm (Sanitization):**
   - Tuyệt đối không lưu trữ Secret data, private keys, authorization tokens hoặc raw environment variables trong trường `evidence` của `FindingResult`.

