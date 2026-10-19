# Data Contracts & Schemas

Tài liệu định nghĩa chuẩn giao tiếp dữ liệu giữa các module:

## 1. Flow kiến trúc dữ liệu

```
[ Collectors (A/B) ] 
       │ (Raw JSON / API Objects)
       ▼
[ Normalizers (B) ] 
       │ (Normalized Resource Models)
       ▼
[ Rules & Evaluation Engine (B/C) ] 
       │ (Evaluation Result / Findings)
       ▼
[ Reporting (B) ] 
       │ (CLI Table / JSON / Markdown)
```

## 2. Models quy chuẩn

### 2.1. Normalized Cluster Config
- `cluster_name`: string
- `location`: string
- `mode`: enum ("STANDARD", "AUTOPILOT")
- `master_authorized_networks_enabled`: bool
- `private_cluster_config`: object
- `workload_identity_config`: object
- `shielded_nodes_enabled`: bool
- `network_policy_enabled`: bool

### 2.2. Finding Model
- `rule_id`: string (e.g., `CIS-GKE-5.1.1`)
- `title`: string
- `section`: string
- `severity`: enum ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL")
- `status`: enum ("PASS", "FAIL", "NOT_APPLICABLE", "ERROR")
- `resource_id`: string
- `remediation`: string
