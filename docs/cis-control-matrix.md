# CIS GKE Benchmark Control Matrix

Bảng đối chiếu các tiêu chí đánh giá theo chuẩn CIS Google Kubernetes Engine Benchmark v1.4.0+:

| CIS ID | Section | Tiêu đề kiểm tra | Phân loại | Mức độ | Phụ trách |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **5.1.1** | Control Plane | Ensure Master Authorized Networks is Enabled | Automated | High | A + B |
| **5.1.2** | Control Plane | Ensure Private Clusters Are Enabled | Automated | Critical | A + B |
| **5.1.3** | Control Plane | Ensure Shielded GKE Nodes Are Enabled | Automated | High | A + B |
| **5.2.1** | Node Security | Ensure default Service Account is not used | Automated | Critical | A + C |
| **5.2.2** | Node Security | Ensure Workload Identity is Enabled | Automated | High | A + C |
| **5.3.1** | Network | Ensure Network Policy is Enabled & Enforced | Automated | High | B + C |
| **5.4.1** | Pod Security | Ensure Pod Security Admission (PSA) is Enforced | Automated | Medium | B + C |

*Ghi chú:*
- **A**: Infrastructure & GCP API Collector
- **B**: K8s Collector, Evaluation, Reporter
- **C**: Rule Logic & Lab Validations
