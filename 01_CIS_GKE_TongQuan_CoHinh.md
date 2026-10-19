# TÀI LIỆU 01 — TỔNG QUAN VÀ KẾ HOẠCH TRIỂN KHAI DỰ ÁN CIS GKE

**Tên dự án:** Xây dựng hệ thống tự động đánh giá và tăng cường bảo mật Google Kubernetes Engine theo CIS Benchmark v2.0.0  
**Phạm vi:** GKE Standard và GKE Autopilot · Terraform · Python · Kubernetes Security · GitHub Actions  
**Tính chất tài liệu:** Tài liệu nền tảng để hiểu, thiết kế, triển khai và nghiệm thu dự án; **không phải lịch tiến độ**.  
**Tài liệu đi kèm:** [Tài liệu 02 — Phân công và phối hợp ba thành viên](02_CIS_GKE_PhanCong_PhoiHop_TrinhBayBang.md).

> **Đọc nhanh:** Nhóm dựng hai môi trường GKE bằng Terraform, xây một công cụ Python đọc cấu hình Kubernetes/Google Cloud để kiểm tra các CIS controls đã chọn, lưu bằng chứng và xuất báo cáo JSON/HTML. Trên môi trường lab, nhóm chủ động tạo hai tình huống cấu hình chưa an toàn, kiểm tra phát hiện, khắc phục **sau phê duyệt**, kiểm tra ứng dụng còn hoạt động và chạy lại audit để chứng minh thay đổi. Mọi đánh giá phải dùng đúng benchmark cho **Standard** hoặc **Autopilot**; không tự nhận đã kiểm tra toàn bộ CIS v2.0.0.

---

## 1. ĐỌC PHẦN NÀY TRƯỚC: DỰ ÁN ĐANG LÀM GÌ?

### 1.1. Bài toán thực tế

Một cụm Kubernetes có thể chạy ứng dụng bình thường nhưng vẫn tồn tại cấu hình rủi ro: workload dùng `default` Service Account, token được tự động mount không cần thiết, RBAC cấp quyền cho nhóm người dùng quá rộng, namespace không có Pod Security enforcement hoặc thiếu NetworkPolicy. Người quản trị phải đối chiếu cấu hình đang chạy với các khuyến nghị CIS, kiểm tra từng bằng chứng và quyết định cách xử lý. Việc thực hiện thủ công dễ mất thời gian, khó lặp lại và khó chứng minh cấu hình đã cải thiện.

Dự án giải quyết **một phần có chủ đích** của bài toán đó: tạo quy trình đánh giá có thể chạy lại, kết quả có thể giải thích và hai ví dụ hardening được kiểm chứng thực tế. **CIS Benchmark là chuẩn tham chiếu; công cụ do nhóm tự xây không phải CIS-CAT, không được giới thiệu là công cụ đã được CIS chứng nhận.**

### 1.2. Câu chuyện dự án trong một luồng

Quy trình triển khai và cách kiểm chứng được nhìn rõ theo từng chặng:

| Chặng | Nội dung thực hiện và kết quả cần thấy |
|---|---|
| **01. Môi trường** | Terraform dựng tài nguyên Google Cloud, gồm mạng, GKE Standard và GKE Autopilot. Hạ tầng được lưu bằng mã nguồn và state riêng để có thể tái tạo, kiểm soát thay đổi và dọn dẹp. |
| **02. Workload thí nghiệm** | đưa ứng dụng thử nghiệm lên các namespace lab, có bản cấu hình ban đầu và bản cấu hình đã tăng cường bảo mật; không sửa tài nguyên hệ thống của GKE. |
| **03. Baseline audit** | Python thu thập dữ liệu qua Kubernetes API và Google Cloud API bằng quyền đọc phù hợp, xác định mode của cluster rồi chọn đúng rule của benchmark tương ứng. |
| **04. Đánh giá & báo cáo** | mỗi kiểm tra cho biết CIS ID, tên kiểm tra, mode, đối tượng bị ảnh hưởng, bằng chứng, lý do và một trong năm trạng thái `PASS`, `FAIL`, `REVIEW`, `N/A`, `ERROR`. |
| **05. Phê duyệt thay đổi** | chỉ với tình huống đã chọn, nhóm đánh giá tác động, xác nhận quyền phê duyệt, sao lưu manifest cũ và nêu cách khôi phục. **Không được duyệt thì dừng tại báo cáo; không tự động sửa.** |
| **06. Khắc phục trong lab** | thay cấu hình Service Account hoặc áp dụng NetworkPolicy phù hợp; kiểm tra Pod, HTTP, DNS và luồng mạng theo từng tình huống. |
| **07. Kiểm chứng & dọn dẹp** | chạy cùng bộ audit, so sánh trước/sau và xuất báo cáo JSON/HTML cùng bằng chứng thật. Cuối cùng lưu artifact cần thiết rồi dọn tài nguyên cloud có phát sinh chi phí. |

**Đích đến:** không chỉ có một bảng báo `PASS`, mà có thể chỉ ra **vì sao** cấu hình ban đầu đáng lo ngại, **đã sửa gì**, **có được phép sửa không**, **ứng dụng có bị ảnh hưởng không** và **bằng chứng nào xác nhận trạng thái mới**.

### 1.3. Đầu ra cuối cùng phải nhìn thấy được

Một người khác mở repository phải tìm được: mã Terraform để dựng hạ tầng; manifests cho lab; công cụ Python chạy qua CLI; các rule CIS có đối chiếu benchmark; bộ kiểm thử `pytest`; GitHub Actions CI; báo cáo JSON/HTML thật; bằng chứng thử nghiệm Service Account và NetworkPolicy trước/sau; tài liệu cách chạy, rollback, đánh giá thủ công, chi phí và cleanup.

![Toàn cảnh dự án CIS GKE](assets/images/01-overview.png)

*Hình 1. Quy trình tổng thể của hệ thống đánh giá và tăng cường bảo mật GKE.*

---

## 2. MỤC TIÊU, PHẠM VI VÀ NHỮNG GÌ KHÔNG LÀM

### 2.1. Mục tiêu cụ thể

| Mục tiêu | Nội dung dự án cần đạt |
|---|---|
| **Hạ tầng có thể tái tạo** | dựng được hai cụm GKE theo mã Terraform, xác minh kết nối đúng cluster, quản lý được state và chi phí. |
| **Đánh giá có cơ sở** | mỗi rule được liên kết đúng CIS ID, tên, `Level`, `Automated/Manual`, cách thu thập evidence và phạm vi áp dụng Standard/Autopilot. |
| **Tự động hóa phần có thể tự động** | collector và evaluator chạy lại được, có kiểm thử dữ liệu giả lập lẫn kiểm thử live; không tự kết luận `PASS` khi thiếu điều kiện cần đánh giá thủ công. |
| **Báo cáo dễ hiểu** | xuất JSON để xử lý bằng chương trình và HTML để người xem lần theo finding, nguồn dữ liệu, vấn đề và kết quả trước/sau. |
| **Khắc phục an toàn** | minh họa hai quy trình được kiểm soát: Service Account hardening và default-deny NetworkPolicy trên Standard. |
| **Khả năng nghiệm thu** | có bằng chứng triển khai thật, kiểm thử chức năng, rollback, kiểm soát quyền/phê duyệt và hướng dẫn để người khác chạy lại. |

### 2.2. Phạm vi cốt lõi và mở rộng

| Nhóm phạm vi | Nội dung và giới hạn |
|---|---|
| **Bắt buộc (P0)** | hai cluster, nền tảng IaC/CI, hai API collectors, bộ đánh giá theo mode, **sáu CIS ID trong danh mục ở mục 4**, JSON/HTML, unit/integration tests, hai tình huống remediation được duyệt và re-audit. Sáu ID này **không đồng nghĩa cả sáu đều tồn tại trong từng benchmark**; Standard có sáu mục trong danh sách, Autopilot có bốn mục cùng số ID hoặc khác mô tả như bảng ở mục 4. |
| **Mở rộng có điều kiện (P1)** | đánh giá quyền truy cập Secrets theo `4.1.2`; VPC Flow Logs và Intranode Visibility theo `5.6.1` (Standard) / `5.4.1` (Autopilot); tăng số fixtures hoặc trường so sánh. Chỉ triển khai P1 khi P0 đã ổn định và đã kiểm tra chính xác các trường cloud liên quan. |
| **Ngoài phạm vi** | tự động sửa mọi lỗi phát hiện; thay đổi cluster sản xuất; bao phủ toàn bộ CIS Benchmark v2.0.0; dashboard thời gian thực hoặc hệ thống SIEM; tích hợp đa cloud; tự khẳng định cluster ‘đạt chứng nhận CIS’. Một control chưa triển khai phải được ghi là **ngoài phạm vi kiểm thử**, không được giấu trong `PASS` hay `N/A`. |

### 2.3. Các khái niệm cần hiểu thống nhất

| Khái niệm | Cách hiểu đúng trong dự án |
|---|---|
| **GKE Standard** | người triển khai kiểm soát nhiều cấu hình cluster/node/network hơn; phải kiểm tra các setting do khách hàng chịu trách nhiệm. |
| **GKE Autopilot** | Google quản lý và thiết lập sẵn nhiều thành phần hơn; vẫn cần kiểm tra phần cấu hình workload, RBAC và các mục thực sự xuất hiện trong *CIS GKE Autopilot Benchmark*. |
| **CIS control/recommendation** | một khuyến nghị cấu hình, có mã riêng, `Level`, cách audit và thông tin rủi ro. **Level 1/Level 2** là profile CIS; **P0/P1** chỉ là mức ưu tiên của dự án. |
| **Evidence** | dữ liệu hoặc quan sát có nguồn, thời điểm, đối tượng và cách thu thập; ví dụ tên workload, `serviceAccountName`, thông tin RoleBinding, cấu hình dataplane, nhãn namespace hoặc log thử kết nối. |
| **Audit / remediation / re-audit** | lần lượt là đánh giá hiện trạng (không sửa), thực hiện thay đổi có kiểm soát, và đánh giá lại sau thay đổi. |
| **Fixture** | dữ liệu đầu vào được dựng trước để kiểm thử rule; fixture chỉ chứng minh logic unit test, **không thay thế bằng chứng live**. |

---

## 3. KIẾN TRÚC HỆ THỐNG: CÁC KHỐI VÀ CÁCH CHÚNG KẾT NỐI

### 3.1. Bức tranh tổng thể

Hệ thống chia thành năm khối. Mỗi khối có nhiệm vụ riêng và ranh giới rõ ràng:

| Khối kiến trúc | Chức năng và yêu cầu triển khai |
|---|---|
| **Khối 1 — Repository và làm việc nhóm** | * GitHub chứa Terraform, Python, YAML, tests, tài liệu, schema kết quả và workflow. Pull request cần reviewer, tránh thay đổi trực tiếp nhánh chính. |
| **Khối 2 — Kiểm thử tự động (GitHub Actions CI)** | * Mỗi pull request chạy kiểm tra không tác động cloud như `terraform fmt`, `terraform validate` trong điều kiện phù hợp, Ruff và `pytest`. Nếu có workflow chạy audit trên cloud, nó sử dụng quyền đọc cần thiết qua OpenID Connect/Workload Identity Federation hoặc cơ chế ngắn hạn an toàn. **CI kiểm tra mã không đồng nghĩa được quyền `terraform apply` hoặc sửa tài nguyên**; bước có tác động phải có phê duyệt riêng. |
| **Khối 3 — Google Cloud infrastructure** | * Terraform quản lý VPC, hai subnet phù hợp, cluster Standard và cluster Autopilot, quyền và cấu hình tối thiểu cho lab. GCS bucket backend lưu Terraform state có versioning, phân quyền và **state tách `shared`, `standard`, `autopilot`** (tên chính xác do nhóm chốt). State chỉ lưu trong backend, không commit lên Git. |
| **Khối 4 — Python CIS Audit Engine** | * Công cụ chạy **bên ngoài cluster**, không phải cài scanner có quyền sửa vào workload. Kubernetes API collector đọc namespace, Pod/workload, Service Account, RBAC, NetworkPolicy; Google Cloud API collector đọc thông tin cluster/mode/dataplane/subnet khi rule cần. Module chuẩn hóa evidence cung cấp dữ liệu nhất quán cho rule registry và evaluator. Mỗi mode có danh mục rule đúng CIS v2.0.0. |
| **Khối 5 — Reporting và controlled remediation** | * Reporter tạo `JSON` và `HTML`. Workflow sửa cấu hình là **làn riêng**, chỉ hoạt động sau review/approval; sử dụng YAML/manifest do nhóm kiểm soát và kiểm tra sau thay đổi. Không để hàm `audit` tự gọi `kubectl apply`, `terraform apply` hoặc thay đổi IAM. |

![Kiến trúc chi tiết hệ thống CIS GKE](assets/images/02-architecture.png)

*Hình 2. Kiến trúc hệ thống và các luồng tương tác giữa các thành phần.*

### 3.2. Dữ liệu đi qua hệ thống như thế nào?

Một lần audit nhận `project`, `cluster`, `location`, `mode` và phạm vi namespace. Trước tiên công cụ **xác nhận** identity cluster/mode bằng nguồn cloud khi có thể; nếu dữ liệu không thống nhất, phải dừng hoặc trả `ERROR`, không suy luận theo tên cluster. Collector đọc thông tin cấu hình và trả evidence chuẩn hóa. Registry chỉ lấy rule có trong benchmark của mode được chọn. Evaluator thực hiện kiểm tra và gắn lý do cho từng finding. Cuối cùng reporter xuất cùng một nội dung nhất quán ở hai định dạng JSON/HTML.

Điểm quan trọng là **độc lập giữa logic và môi trường**: unit tests có thể cấp dữ liệu fixture vào evaluator mà không cần tạo cluster; live tests xác thực rằng collector thực sự đọc được dữ liệu và kết luận có ý nghĩa trong GKE.

### 3.3. Quy tắc thiết kế để tránh lỗi tích hợp

- Thống nhất **hợp đồng dữ liệu** (schema): mã CIS, benchmark/mode, đối tượng, trạng thái, evidence, thời điểm, cách kiểm tra, độ tin cậy, chi tiết đánh giá thủ công, nguồn lỗi và khuyến nghị.
- Các API operations phục vụ audit luôn **read-only**; cấp quyền ít nhất có thể và xử lý thông báo bị từ chối quyền rõ ràng.
- Tránh phụ thuộc tên namespace, node hoặc region cố định trong logic. Chỉ truy cập namespace lab được khai báo nếu đó là phạm vi demo.
- Không đặt Secrets, access token, credential, thông tin thanh toán hoặc raw kubeconfig trong logs/report/PR.
- Cấu hình có nguồn quản lý riêng: Terraform quản lý hạ tầng; Kubernetes YAML quản lý lab resources. Đổi setting hạ tầng theo đúng nguồn IaC để tránh drift ngoài ý muốn.

---

## 4. CHÍNH XÁC SẼ KIỂM TRA CIS NÀO?

Hai tài liệu nguồn cùng phiên bản **v2.0.0 ngày 30/06/2026** nhưng không có tập control giống nhau: *CIS Google Kubernetes Engine (GKE) Benchmark* áp dụng cho Standard trong phạm vi dự án; *CIS GKE Autopilot Benchmark* cho Autopilot. Danh mục P0 dưới đây được đối chiếu từ **từng tài liệu riêng**. Cột “Cách CIS đánh giá” là nhãn `Automated`/`Manual` của benchmark, không phải mức tự động hóa mà nhóm đã hoàn thành.

| CIS ID | Ý nghĩa cần kiểm tra | GKE Standard | GKE Autopilot |
|---|---|---|---|
| **4.1.4** | Workload không dùng `default` Service Account một cách chủ động | Level 1 · Automated | Level 1 · Automated |
| **4.1.5** | Token Service Account chỉ mount khi Pod thực sự cần Kubernetes API | Level 1 · Manual | Level 1 · Manual |
| **4.1.9** | Không cấp RBAC tùy biến cho nhóm `system:authenticated` | Level 1 · Automated | Level 1 · Automated |
| **4.2.1** | Namespace chứa workload áp dụng PSS `baseline` hoặc `restricted` với chế độ `enforce` | Level 1 · Manual | **Không có ID này trong Autopilot v2.0.0** |
| **4.3.1** | Đánh giá cơ chế NetworkPolicy enforcement | Level 1 · Manual: Dataplane V2 **hoặc** Calico | Level 2 · Manual: Dataplane V2 tích hợp |
| **4.3.2** | Default-deny NetworkPolicy trên các namespace workload | Level 2 · Automated | **Không có ID này trong Autopilot v2.0.0** |

**Lưu ý bắt buộc khi lập trình và viết báo cáo:**

1. `4.1.4`: **sự tồn tại** của Service Account tên `default` là hành vi Kubernetes bình thường, **không tự nó là FAIL**. Phải xem workload đang dùng tài khoản nào và RBAC được gán ra sao.
2. `4.1.5`: một Pod có token không đủ để kết luận luôn sai; trước tiên phải xác định workload có thực sự cần Kubernetes API hay không. Khi chưa có dữ kiện nghiệp vụ, đưa `REVIEW` với câu hỏi/evidence cần người kiểm tra.
3. `4.1.9`: các ClusterRoleBinding hệ thống `system:basic-user`, `system:discovery`, `system:public-info-viewer` là ngoại lệ mặc định được benchmark mô tả; **không xóa/không flag chỉ vì chúng tồn tại**. Tìm binding tùy biến gán cho `system:authenticated`.
4. `4.2.1`: trong Standard phải kiểm tra `enforce`, không chấp nhận chỉ `warn` hoặc `audit` như đã chặn vi phạm. Tập trung namespace chứa workload do nhóm quản lý; không tùy tiện chỉnh `kube-system`.
5. `4.3.1`: trên Standard, `ADVANCED_DATAPATH` chứng minh Dataplane V2; nếu dùng legacy datapath thì cần kiểm tra cả Calico node enforcement **và** network-policy add-on. Trên Autopilot, Dataplane V2 được tích hợp; **không hướng dẫn bật Calico**.
6. `4.3.2`: dùng default-deny đủ **ingress và egress** trên namespace mục tiêu, sau đó allow luồng thật sự cần. Kiểm tra **cả cấu hình policy lẫn lưu lượng thực**. Nhóm đang chọn control này làm demo P0 dù CIS xếp **Level 2**. Không suy diễn rằng Autopilot đạt `4.3.2` chỉ vì Dataplane V2 có sẵn.

**Cách thể hiện control không có trong một benchmark:** nếu dùng bảng so sánh hợp nhất, có thể hiển thị `N/A – control không tồn tại trong benchmark của mode này` để giúp người đọc so sánh; không cộng mục đó vào `PASS` hoặc mẫu số tỷ lệ tuân thủ. Khi đánh giá riêng từng mode, **không cần phát sinh finding** cho mã không thuộc benchmark đó. “Chưa code”/“ngoài scope” phải ghi là `NOT_IMPLEMENTED/OUT_OF_SCOPE` ở **metadata coverage**, không đánh tráo thành `N/A`.

**P1 nếu được bổ sung:** `4.1.2` quyền Secrets (Manual, Level 1 ở cả hai mode); `5.6.1` VPC Flow Logs + Intranode Visibility (Standard, Automated, **Level 2**); `5.4.1` cùng chủ đề trong Autopilot (Automated, **Level 1**). Đọc `Impact` và `Audit` tương ứng vì những cài đặt network/cluster này có thể gây gián đoạn và tốn chi phí. **Không lấy giá trị nội dung Secrets** để thu thập bằng chứng; chỉ kiểm tra metadata/quyền.

![Bản đồ CIS theo mode GKE](assets/images/03-cis-mode-matrix.png)

*Hình 3. Đối chiếu các CIS controls được chọn giữa GKE Standard và Autopilot.*

---

## 5. CÔNG CỤ PYTHON PHẢI HOẠT ĐỘNG RA SAO?

### 5.1. Các thành phần phải có

| Thành phần | Nhiệm vụ chính và giới hạn |
|---|---|
| **Kubernetes API collector** | Đọc Pod, workloads (Deployment/DaemonSet/StatefulSet/Job khi cần), namespace, ServiceAccount, RBAC bindings và NetworkPolicy; chỉ thu thập evidence, không tự kết luận CIS. |
| **Google Cloud API collector** | Đọc mode/cluster, subnet, network/dataplane và các trường Google Cloud cần thiết cho từng rule; chỉ sử dụng API/SDK với quyền đọc. |
| **Evidence normalizer** | Chuẩn hóa đối tượng, nguồn dữ liệu, thời điểm, trường thiếu và lỗi từng phần để đầu vào rule nhất quán. |
| **Mode-aware rule registry** | Đăng ký từng control theo đúng benchmark v2.0.0, ID, Level, Manual/Automated, điều kiện áp dụng Standard/Autopilot và hàm đánh giá. |
| **Evaluator** | Sinh finding kèm bằng chứng, giải thích và một trong năm trạng thái; không suy diễn PASS khi thiếu dữ liệu hoặc cần người xác minh. |
| **Reporter & Test suite** | Xuất JSON/HTML; pytest chạy fixtures PASS/FAIL/REVIEW/N/A/ERROR và trường hợp lỗi; live integration test xác nhận bằng chứng thật trên cả hai mode. |

**Nguyên tắc thực hiện:** Audit dùng API/SDK phù hợp thay vì phân tích chuỗi `kubectl` dễ sai; `kubectl` vẫn dùng để đối chứng thủ công. Fixture kiểm thử logic không thay thế evidence từ cluster thật.

### 5.2. Ý nghĩa chính xác của năm kết quả

| Trạng thái | Khi dùng | Điều không được làm |
|---|---|---|
| **PASS** | Có đủ bằng chứng để kết luận control đã được đáp ứng trong phạm vi kiểm tra | Không tự PASS nếu còn điều kiện Manual chưa xác minh |
| **FAIL** | Có bằng chứng cụ thể chứng minh vi phạm điều kiện đánh giá | Không biến API lỗi hoặc thiếu quyền thành FAIL |
| **REVIEW** | Cần người đánh giá xác nhận ngữ cảnh nghiệp vụ, ngoại lệ hoặc một bước thủ công | Không dùng REVIEW để che lỗi lập trình/thu thập dữ liệu |
| **N/A** | Control thực sự không áp dụng theo mode/đối tượng được xác định | Không tính N/A là PASS, không dùng N/A cho code chưa triển khai |
| **ERROR** | Không thể hoàn tất việc đánh giá: thiếu quyền, timeout, lỗi SDK/API, input không hợp lệ… | Không bỏ finding lỗi khỏi báo cáo mà không giải thích |

**Kết luận Manual:** nguồn CIS gắn `Manual` có nghĩa là cần xem xét phần không thể xác nhận hoàn toàn bằng chương trình. Công cụ có thể đọc dữ liệu, nêu nhận định sơ bộ và đính evidence, nhưng quyết định `PASS/FAIL` cuối cùng cần dựa trên quy trình xác minh đã ghi lại. Nếu chưa hoàn tất, trả `REVIEW` với câu hỏi cụ thể và chỗ ghi nhận reviewer, thời điểm, quyết định.

![Luồng Python CIS Audit Engine](assets/images/04-audit-flow.png)

*Hình 4. Luồng hoạt động của Python CIS Audit Engine.*

### 5.3. Giao diện và định dạng kết quả cần thống nhất

Nhóm cần chốt sớm **contract CLI** (tham số, mode, cluster, output directory, exit code) và **schema báo cáo**. Chẳng hạn, CLI về mặt ý tưởng cung cấp các hành động `audit` và `compare`; phần remediation tách riêng, không được kích hoạt ngầm từ `audit`. Thư mục kết quả phải chứa metadata của lần chạy (mode, benchmark, cluster, thời điểm, phiên bản Git, tool version), danh sách findings và vị trí evidence tương ứng.

Ví dụ **cấu trúc đề xuất**, không phải kết quả audit thật và không phải một định dạng do CIS quy định:

```json
{
  "run_id": "example-run",
  "benchmark": "CIS GKE Benchmark v2.0.0",
  "mode": "standard",
  "cluster": "example-standard",
  "scope": {"namespaces": ["lab-sa", "lab-network"]},
  "findings": [
    {
      "control_id": "4.1.4",
      "cis_level": 1,
      "assessment_type": "Automated",
      "status": "FAIL",
      "resource": "Deployment/lab-sa/web",
      "reason": "Workload uses default Kubernetes ServiceAccount",
      "evidence_ref": "evidence/example-414.json"
    }
  ]
}
```

Đây là **mẫu tích hợp** để các phần của dự án giao tiếp, không phải khẳng định dữ liệu thật tồn tại. Khi triển khai, schema chính thức cần mô tả thêm lỗi thu thập, thời gian, cách kiểm tra, benchmark source, manual review, trạng thái approval, đường dẫn trước/sau và điều kiện để so sánh. Cần thống nhất `status` là kết luận của **một control/đối tượng cụ thể**, tránh gom nhiều resource khiến một `FAIL` bị lẫn trong một `PASS` tổng thể.

---

## 6. HAI KỊCH BẢN LAB CHỨNG MINH GIÁ TRỊ DỰ ÁN

### 6.1. Kịch bản A — Service Account Hardening

**Rủi ro muốn chứng minh:** một ứng dụng sử dụng `default` Service Account vì workload không chỉ định `serviceAccountName`; token có thể được tự mount dù ứng dụng không gọi Kubernetes API. Cách cấu hình này làm khó quản lý quyền riêng cho từng workload và tăng rủi ro lộ credential.

**Thiết lập lab:** dựng namespace chuyên dụng và ứng dụng HTTP đơn giản. Bản `before` chủ đích dùng `default` Service Account, có bằng chứng workload thực sự hoạt động. **Không** cần cấp các quyền nguy hiểm hoặc gán `cluster-admin` để tạo bằng chứng. Dùng `4.1.4` làm kiểm tra cốt lõi; `4.1.5` cần nhận định ứng dụng có cần Kubernetes API hay không; `4.1.9` có thể kiểm tra độc lập các RBAC binding liên quan.

**Quy trình:** audit baseline → hiển thị `FAIL`/`REVIEW` tương ứng kèm evidence → giải thích tác động → nhận phê duyệt → lưu bản YAML cũ → tạo **dedicated ServiceAccount**, cập nhật workload `serviceAccountName`, đặt `automountServiceAccountToken: false` **nếu xác nhận không cần Kubernetes API** → triển khai trong lab → kiểm tra rollout/HTTP → re-audit → before/after → kiểm tra và diễn tập rollback nếu kết quả chức năng không đạt.

**Đủ điều kiện nghiệm thu khi:** bản `after` không còn workload chủ động dùng `default` SA, trường token phù hợp nhu cầu API, Pod Ready/HTTP đạt, audit phản ánh sự thay đổi bằng evidence, có bản sao cấu hình trước và thủ tục phục hồi. Không hứa tất cả rule đều `PASS` nếu còn bước Manual chưa được người đánh giá hoàn tất.

### 6.2. Kịch bản B — NetworkPolicy Hardening trên GKE Standard

**Rủi ro muốn chứng minh:** namespace workload chưa có chính sách `default-deny`; các Pod có thể trao đổi lưu lượng không cần thiết nếu enforcement hỗ trợ và không có policy nào hạn chế.

**Điều kiện tiên quyết:** kiểm tra `4.3.1` để chắc chắn cụm Standard thực sự hỗ trợ enforcement qua **GKE Dataplane V2 hoặc Calico được cấu hình đúng**. Nếu enforcement không hoạt động, chỉ tạo YAML NetworkPolicy không chứng minh đã cô lập được traffic.

**Thiết lập lab:** tạo namespace `lab-network`, một server/service và ít nhất hai client hoặc hướng traffic đủ để chứng minh luồng hợp lệ/không hợp lệ. Đo thử trước thay đổi: kết nối ứng dụng, DNS cần thiết và luồng giữa Pod/namespace. Bản `after` phải có default-deny cho cả **Ingress** và **Egress**, sau đó là các allow rules **tối thiểu** để ứng dụng hoạt động, bao gồm DNS nếu có nhu cầu; xem thêm đường đến metadata server nếu lab dùng Workload Identity Federation.

**Quy trình:** audit baseline `4.3.2` → lưu manifest/traffic evidence trước → phân tích luồng được phép → approval → backup policy cũ → áp dụng default-deny và allow phù hợp trên namespace lab → đo lại traffic **allowed/blocked**, DNS và HTTP → re-audit → so trước/sau → diễn tập rollback khi functional test thất bại.

**Đủ điều kiện nghiệm thu khi:** policy chọn đúng workload, có isolation ingress/egress, luồng không được phép bị chặn, luồng cần thiết vẫn chạy, chứng cứ có timestamp/context, rule/report phản ánh thay đổi. Kịch bản này **chỉ claim compliance với CIS `4.3.2` trên Standard**; có thể áp dụng chính sách tương tự ở Autopilot để minh họa hardening nhưng **không gắn nhãn là `4.3.2` của Autopilot**.

### 6.3. Quy trình sửa chung bắt buộc

Mọi bản sửa đi qua chuỗi: **Phát hiện → kiểm tra evidence → phân tích tác động → người có thẩm quyền phê duyệt → backup cấu hình cũ → áp dụng chỉ trên lab → functional test → re-audit → compare before/after → báo cáo**.

- **Không được phê duyệt:** dừng nhánh sửa, xuất báo cáo hiện trạng, **không thay đổi cấu hình**.
- **Đã áp dụng nhưng kiểm tra chức năng không đạt:** kích hoạt thủ tục rollback, kiểm tra chức năng lại, ghi lý do thất bại và kết quả audit sau rollback; không sửa report để tạo PASS giả.
- **Đã áp dụng và chức năng đạt:** đánh giá lại bằng cùng benchmark/mode/scope, lưu thay đổi có bằng chứng và ghi người phê duyệt.

![Quy trình kiểm tra phê duyệt khắc phục và kiểm chứng](assets/images/05-remediation-flow.png)

*Hình 5. Quy trình kiểm tra, phê duyệt, khắc phục và kiểm chứng lại.*

---

## 7. CỤ THỂ TỪNG HẠNG MỤC CẦN LÀM VÀ SẢN PHẨM BÀN GIAO

Bảng dưới đây cho phép kiểm tra nhanh toàn bộ công việc. Các mục 7.1–7.7 giải thích chi tiết phương pháp và yêu cầu bàn giao tương ứng.

| Hạng mục | Đầu ra cốt lõi | Kiểm tra hoàn thành |
|---|---|---|
| **Repository & CI** | Repo, workflow, PR template, quy tắc bảo vệ dữ liệu | CI phát hiện lỗi và không tự sửa cloud |
| **Terraform & GKE** | VPC/GCS state, 2 cluster, runbook provision/destroy | Hai mode hoạt động, tái tạo được, context đúng |
| **CIS Control Matrix** | Mapping Standard/Autopilot, Level, Manual/Automated, evidence | Không nhầm control, mode hoặc ngoại lệ |
| **Python Audit Engine** | Collectors, evaluator, registry, CLI, rules, pytest | Tạo findings 5 trạng thái với evidence thật |
| **Security labs** | YAML before/after cho SA, NP, PSS, traffic/admission tests | Có kết quả chức năng và khả năng rollback |
| **Reporting & approval** | JSON/HTML, diff, hồ sơ phê duyệt và rollback | N/A không bị tính là PASS; không sửa khi chưa duyệt |
| **QA & handover** | README/runbooks, live logs, demo, cost/cleanup | Người khác có thể tái chạy và kiểm chứng |

### 7.1. Repository, quy tắc làm việc và CI

**Thực hiện:** tạo GitHub repository, cấu trúc thư mục thống nhất, template PR, `.gitignore`/quy tắc bảo vệ thông tin nhạy cảm; cấu hình CI tối thiểu để validate Terraform, chạy Ruff và `pytest`. Chỉ bật job có quyền truy cập cloud khi có nhu cầu rõ ràng, danh tính/điều kiện kích hoạt phù hợp và kiểm soát quyền; không dùng access key dài hạn lưu trong Git.

**Bàn giao:** `.github/workflows/`, mẫu PR, README cấu trúc repo, kết quả CI trên PR thật. **Nghiệm thu:** commit sai định dạng/test lỗi bị phát hiện, PR hợp lệ chạy sạch, thao tác read-only không có side effect.

### 7.2. Hạ tầng Terraform và quản lý tài nguyên GKE

**Thực hiện:** xác định project, billing/quota, region, cấu hình mạng không chồng CIDR, VPC/subnet, thông số GKE Standard và Autopilot, ranh giới IAM, các đầu ra cần thiết cho collector. Khởi tạo backend GCS theo phương án quản lý riêng; chuẩn bị `plan` để review trước khi apply. Lựa chọn networking, endpoint, NAT/private nodes và chi phí phải phù hợp khả năng test; không mặc định một cấu hình cụ thể luôn có thể dùng ở mọi project/quota.

**Bàn giao:** Terraform modules/config/variables/outputs, file hướng dẫn bootstrap backend, ba state tách biệt, hướng dẫn provision/check/destroy, thông số kết nối không chứa secret. **Nghiệm thu:** hai cluster đúng mode và healthy; chọn đúng context khi chạy `kubectl`; có chạy smoke deployment; hạ tầng tái tạo được và có checklist cleanup/billing.

### 7.3. CIS Control Matrix và phạm vi đánh giá

**Thực hiện:** đối chiếu hai PDF v2.0.0 ở mức từng control P0/P1: ID, tên chính xác, Level, Automated/Manual, áp dụng theo mode, cần dữ liệu Kubernetes hay Google Cloud, điều kiện PASS/FAIL, ngoại lệ, dữ liệu cần review, rủi ro khi sửa. Không copy nội dung benchmark dài dòng vào tài liệu xuất bản; giữ tham chiếu PDF/trang và diễn giải ngắn bằng lời của nhóm.

**Bàn giao:** `docs/cis-control-matrix.md` hoặc CSV/JSON tương ứng, fixtures và expected outcomes đã review. **Nghiệm thu:** không đánh dấu sai mode/Level, đặc biệt `4.2.1`, `4.3.1`, `4.3.2` và các mục Flow Logs; không biến control Manual thành tự PASS.

### 7.4. Python Audit Engine, rule tests và kết quả có thể giải thích

**Thực hiện:** viết collectors; chuẩn hóa evidence; định nghĩa registry theo mode; viết rule `4.1.4`, `4.1.5`, `4.1.9`, `4.2.1`, `4.3.1`, `4.3.2` với điều kiện áp dụng tương ứng. Mỗi rule tối thiểu có fixture sạch/vi phạm, dữ liệu thiếu hoặc API lỗi khi phù hợp. Cần phân biệt lỗi do **không đủ quyền đọc** và cấu hình thực sự vi phạm.

**Bàn giao:** source Python, CLI, schema mẫu, unit tests, log kiểm tra thật trên Standard/Autopilot. **Nghiệm thu:** kết quả ổn định với cùng evidence, xử lý mode đúng, sinh năm trạng thái nhất quán, không lộ secret và không tự động sửa.

### 7.5. Lab YAML, thực nghiệm PSS và NetworkPolicy

**Thực hiện:** viết YAML namespace/app/Service Account bản `before` và `after`; dựng tình huống PSS `4.2.1` **trên Standard** và đo admission bằng thao tác thử nghiệm phù hợp (ví dụ server-side dry-run hoặc tạo workload test trong lab), không tạo cấu hình nguy hiểm ở namespace hệ thống. Với NetworkPolicy, chuẩn bị script đo traffic ứng dụng/DNS/blocked và kịch bản rollback có thể áp dụng được.

**Bàn giao:** `labs/sa/`, `labs/network-policy/`, `labs/pod-security/` hoặc cấu trúc tương đương, test commands, expected outcomes, bản policy/manifest được review, evidence thật. **Nghiệm thu:** tái hiện được trạng thái trước/sau; ứng dụng lab có health check; chính sách không gây gián đoạn ngoài namespace mục tiêu.

### 7.6. Báo cáo, before/after và quy trình phê duyệt

**Thực hiện:** hiển thị finding rõ tên, nguồn, đối tượng, thời điểm, kết quả, giải thích và khuyến nghị; tổng hợp coverage theo mode, số `PASS/FAIL/REVIEW/N/A/ERROR` minh bạch. Module `compare` phải đối chiếu **cùng mode, cluster, CIS ID, resource và phạm vi namespace**, chỉ ghi cải thiện khi evidence hậu kiểm chứng minh. Approval gồm người duyệt, scope, tác động dự kiến, manifest/hash, cách rollback; không chỉ ghi “approved” chung chung.

**Bàn giao:** report mẫu bằng fixture, report live JSON/HTML, before/after diff, hồ sơ approval/rollback, ảnh chụp màn hình thật nếu dùng trong báo cáo học thuật. **Nghiệm thu:** HTML đọc hiểu được, JSON validate theo schema, không có token/Secret, thống kê không gộp N/A thành PASS.

### 7.7. Kiểm thử, tài liệu triển khai, demo và cleanup

**Thực hiện:** test logic với `pytest`; live tests cho hai mode; thử xử lý lỗi; kiểm thử chức năng hai tình huống; kiểm tra khả năng rollback; viết runbook khởi tạo cloud, chạy audit, triển khai lab, sửa cấu hình được duyệt, xuất báo cáo và destroy. Có thể quay bản demo dự phòng nhưng **không dùng ảnh AI làm bằng chứng live**.

**Bàn giao:** test suite + kết quả chạy có thời gian/Git SHA, README, runbook, tài liệu so sánh hai mode theo evidence thật, hồ sơ chi phí và cleanup. **Nghiệm thu:** một thành viên khác đọc hướng dẫn có thể chạy lại, hiểu kết quả và dọn tài nguyên không còn nhu cầu.

---

## 8. KIỂM THỬ VÀ TIÊU CHÍ NGHIỆM THU CUỐI

**Các lớp kiểm thử không thay thế cho nhau:**

| Lớp kiểm thử | Nội dung cần chứng minh |
|---|---|
| **Static/CI** | Terraform format/validate, Ruff, kiểm tra tests ở PR; chỉ xác nhận mã nguồn và test offline. |
| **Unit tests bằng fixtures** | từng rule trả kết quả đúng với case đúng/sai/manual/missing/exception; ví dụ API `403` phải là `ERROR`, binding hệ thống mặc định không bị flag `4.1.9`. |
| **Integration tests live** | collector thực sự lấy dữ liệu hai GKE modes, xác định mode đúng, report có nguồn bằng chứng và đúng phạm vi. |
| **Security/functional tests** | PodSecurity admission, ứng dụng HTTP Ready, DNS khi cần, traffic cho phép/bị chặn, khả năng khôi phục trước khi coi remediation thành công. |
| **Reproducibility và cleanup** | tái chạy từ runbook; thu thập evidence, xác nhận đã phá hủy lab cloud ngoài phần giữ lại có chủ đích. |

**Checklist nghiệm thu tối thiểu:**

- [ ] GKE Standard và Autopilot được dựng từ Terraform; thông tin cluster/mode và state tách rõ.
- [ ] Các control P0 đều có mapping đúng **theo từng benchmark**, có ghi rõ control chỉ có ở một mode.
- [ ] Collectors chạy read-only; evaluator phân biệt năm trạng thái và không nhầm `N/A` với `PASS`.
- [ ] Có unit tests cho happy path, negative path và lỗi; có live evidence trên cả hai mode.
- [ ] Có JSON/HTML report dễ đối chiếu finding/evidence, không chứa credential.
- [ ] Có tình huống SA với before, approval, backup, after, functional test, re-audit và rollback plan.
- [ ] Có tình huống NetworkPolicy trên Standard với enforcement, default-deny ingress/egress, allow tối thiểu, allowed/blocked/DNS tests, before/after và rollback plan.
- [ ] Khi không phê duyệt không có thao tác thay đổi nào; khi functional test lỗi phải rollback và ghi evidence.
- [ ] README/runbooks/tài liệu mô tả giới hạn, ngoài phạm vi và các kiểm tra Manual chưa kết luận; có cleanup/chi phí.

**Không đặt mục tiêu “100% PASS” bằng mọi giá.** Một `FAIL` có evidence thật, một `REVIEW` cần con người và một `ERROR` được phân tích đúng còn có giá trị học thuật hơn việc đổi nhãn để kết quả trông đẹp.

---

## 9. CÁC RỦI RO VÀ ĐIỂM DỄ HIỂU SAI

| Rủi ro / hiểu nhầm | Hệ quả có thể xảy ra | Cách phòng tránh |
|---|---|---|
| **Nhầm benchmark** | cùng ID chưa chắc cùng mô tả/Level, ví dụ `4.3.1`; có ID ở Standard nhưng không có ở Autopilot. | mapping hai PDF độc lập và có tests kiểm tra khả năng áp dụng. |
| **Nhầm `Automated/Manual`** | đó là phân loại của CIS; việc viết Python đọc dữ liệu không tự động chuyển một khuyến nghị Manual thành Automated. | ghi rõ phần công cụ làm, phần reviewer xác nhận. |
| **Nhầm NetworkPolicy YAML với traffic đã bị chặn** | cấu hình policy mà không có dataplane enforcement phù hợp có thể không bảo vệ được ứng dụng. | vừa đọc cluster configuration vừa đo traffic. |
| **Sai do thiếu quyền thu thập** | API `403`, timeout hoặc trường cloud thiếu không chứng minh vi phạm. | trả `ERROR` hoặc `REVIEW` khi đúng ngữ cảnh, ghi chi tiết và không bịa evidence. |
| **Remediation gây gián đoạn** | bỏ token có thể ảnh hưởng workload cần API; default-deny có thể chặn DNS, metadata hoặc ứng dụng. | impact review, backup, allow rules tối thiểu, approval, functional tests và rollback. |
| **Chi phí, quota, truy cập cluster** | GKE có chi phí chạy thật, giới hạn quota, các tùy chọn networking cần thiết có thể phát sinh hạ tầng hỗ trợ. | chốt budget/region trước apply, chọn cấu hình lab phù hợp, theo dõi Billing và dọn sau khi lưu bằng chứng. |
| **Rò thông tin** | Terraform state, kubeconfig, token và Kubernetes Secrets có thể nhạy cảm. | remote backend có IAM/versioning, làm sạch report, secret scanning phù hợp và không commit key. |

---

## 10. TRIỂN KHAI THEO PHỤ THUỘC, KHÔNG THEO NGÀY

Đây là **thứ tự phụ thuộc kỹ thuật**, không phải lịch cứng:

| Điểm triển khai | Việc thực hiện và điều kiện phụ thuộc |
|---|---|
| **Có thể bắt đầu song song** | hạ tầng Terraform; thiết kế Python schema/collectors dùng fixtures; đối chiếu CIS Matrix và chuẩn bị YAML lab. Ba nhánh này cần thống nhất sớm mode names, namespace names, evidence schema và expected outcomes. |
| **Khi hạ tầng dùng được** | triển khai smoke app, kiểm tra context, thay fixture bằng live evidence, chạy integration tests trên Standard/Autopilot. |
| **Khi audit baseline đáng tin cậy** | hoàn thiện JSON/HTML; thực hiện hai remediation **sau khi được duyệt**; chạy functional test, re-audit và compare. |
| **Khi kết nối toàn hệ thống ổn định** | bổ sung P1 có chọn lọc, viết báo cáo đối chiếu, luyện demo, khóa bằng chứng và cleanup tài nguyên. |

**Không cần đợi xong Terraform mới viết Python rules, cũng không cần đợi Python mới viết YAML lab.** Cần đợi ở các **điểm giao nhau**: chốt contract trước tích hợp, có cluster trước live tests, có baseline trước before/after, có approval trước apply và có functional test trước kết luận remediation thành công.

Chi tiết **ai thực hiện, ai hỗ trợ, ai bàn giao và ai kiểm tra** nằm trong [Tài liệu 02](02_CIS_GKE_PhanCong_PhoiHop_TrinhBayBang.md).

---

## 11. DANH MỤC HỒ SƠ/TÀI LIỆU CẦN GIỮ LẠI

Về tổ chức repository, nhóm có thể dùng cấu trúc sau làm **gợi ý**, không xem là thư mục đã tồn tại:

```text
repo/
├── terraform/
│   ├── bootstrap/            # Khởi tạo backend GCS
│   ├── shared/               # Network/shared state
│   ├── standard/             # GKE Standard state
│   └── autopilot/            # GKE Autopilot state
├── src/cis_gke_audit/
│   ├── collectors/           # Kubernetes, Google Cloud
│   ├── normalizers/
│   ├── rules/                 # Rule modules + mode registry
│   ├── evaluation/
│   ├── reporting/
│   └── cli.py
├── tests/
│   ├── fixtures/
│   ├── unit/
│   └── integration/
├── labs/
│   ├── service-account/
│   ├── network-policy/
│   └── pod-security/
├── docs/
│   ├── contracts.md
│   ├── cis-control-matrix.md
│   ├── runbooks/
│   └── images/
├── .github/workflows/
└── README.md
```

Bằng chứng chạy thật có thể nằm trong vùng artifact riêng, được phân quyền và làm sạch. Nếu repo public, **không đẩy raw cloud output nhạy cảm**, Terraform state, kubeconfig, credentials hoặc Secrets. Một bộ evidence tối thiểu nên có run ID, thời điểm, mode, cluster/scope đã ẩn thông tin nhạy cảm nếu cần, Git SHA, control ID, test ID, nguồn và kết quả.

### Nguồn tham chiếu và nguyên tắc kiểm tra độ chính xác

1. **CIS Google Kubernetes Engine (GKE) Benchmark v2.0.0**, 30/06/2026 — tài liệu đối chiếu Standard; đặc biệt Recommendations `4.1.4`, `4.1.5`, `4.1.9`, `4.2.1`, `4.3.1`, `4.3.2`, `5.6.1`.
2. **CIS Google Kubernetes Engine (GKE) Autopilot Benchmark v2.0.0**, 30/06/2026 — tài liệu đối chiếu Autopilot; đặc biệt `4.1.4`, `4.1.5`, `4.1.9`, `4.3.1`, `5.4.1`.
3. **Báo cáo nhóm 20 (2025)** — tham khảo cách diễn giải và xây dựng thực nghiệm, **không dùng làm nguồn chuẩn cho mapping v2.0.0** vì báo cáo tham chiếu Autopilot Benchmark v1.2.0.
4. Tài liệu chính thức Google Cloud/GKE, Kubernetes và GitHub Actions để đối chiếu API, IAM, NetworkPolicy và tính năng theo phiên bản cluster khi triển khai thật.

> **Lưu ý bản biên soạn:** Tài liệu này mô tả **công việc sẽ triển khai và tiêu chí kiểm chứng**, không xác nhận dự án đã triển khai thành công. Danh mục rule và thuộc tính Level/Manual/Automated được đối chiếu với hai PDF CIS v2.0.0 cung cấp cho dự án. Trước khi chạy thật, nhóm vẫn cần xác nhận phiên bản GKE, quyền, quota và hành vi API trong môi trường thực tế.


