# TÀI LIỆU 02 — PHÂN CÔNG CÔNG VIỆC VÀ CÁCH PHỐI HỢP NHÓM 3 NGƯỜI

**Dự án:** Đánh giá và tăng cường bảo mật GKE Standard/Autopilot theo CIS Benchmark v2.0.0  
**Thành viên:** A · B · C  
**Mục đích:** Đọc vào biết **mỗi người làm gì, làm đến đâu là đủ, phải bàn giao gì, phụ thuộc ai và làm song song thế nào**. Không phân chia theo ngày, không áp tỷ lệ giờ công cứng.  
**Tài liệu gốc để hiểu toàn hệ thống:** [Tài liệu 01 — Tổng quan và kế hoạch triển khai](01_CIS_GKE_TongQuan_TrinhBayBang.md).

> **Tóm tắt 30 giây:** **A** chịu trách nhiệm nền tảng Google Cloud, Terraform, GKE, CI/cloud access và ghép hệ thống chạy thực tế. **B** chịu trách nhiệm phần mềm Python Audit Engine, collectors Kubernetes, các rule Service Account/RBAC, test và báo cáo. **C** chịu trách nhiệm độ chính xác CIS, security labs, các rule Pod Security/NetworkPolicy, remediation và kiểm thử bảo mật/chức năng. Cả ba cùng review những phần giao nhau; người viết chính một thay đổi không tự phê duyệt thay đổi đó.

---

## 1. BỨC TRANH PHÂN CÔNG: AI LÀM CHÍNH PHẦN NÀO?

| Thành viên | Phần sở hữu chính | Kết quả cuối cần bàn giao | Vai trò ngoài chuyên môn chính |
|---|---|---|---|
| **A — Cloud & Integration Lead** | Google Cloud project/IAM/cost, Terraform, VPC, hai GKE clusters, GCS state, Google Cloud collector, hạ tầng CI/WIF, tích hợp end-to-end | Cluster Standard/Autopilot dùng được; IaC tái tạo được; Cloud collector và luồng tích hợp chạy đúng | Hỗ trợ B test collector/rules, hỗ trợ C dataplane/traffic, review thay đổi quan trọng |
| **B — Python Audit & Reporting Lead** | Python architecture, CLI, Kubernetes collector, evidence schema, registry/evaluator, rule `4.1.4/4.1.5/4.1.9`, pytest, JSON/HTML, compare | Audit Engine chạy được trên fixture và cloud thật, báo cáo có evidence và before/after | Pair kiểm tra Terraform/CI, hỗ trợ C viết/kiểm tra rule và re-audit |
| **C — CIS Security, Labs & QA Lead** | CIS Matrix v2.0.0 theo hai mode, security rule spec và code `4.2.1/4.3.1/4.3.2`, manifests, SA/NP/PSS labs, remediation, functional/security QA | Matrix chính xác; labs trước/sau; hai kịch bản khắc phục có approval/rollback/test/re-audit | Pair dùng GKE/kubectl, viết fixture/test Python, nghiệm thu reporter và demo |

**Nguyên tắc quan trọng:** A, B, C là **người phụ trách đầu ra**, không phải ba nhóm độc lập. Một người có thể code phần của người khác để hỗ trợ, nhưng không được có hai người cùng âm thầm sửa một interface mà không thống nhất. Phần nào thay đổi hợp đồng dữ liệu thì người cung cấp **và** người sử dụng đều phải review.

### 1.1. Tách ba khái niệm để làm việc không chồng chéo

| Vai trò | Phạm vi trách nhiệm và cách phối hợp |
|---|---|
| **Người làm chính (Owner)** | trực tiếp tổ chức, triển khai và chịu trách nhiệm sản phẩm của hạng mục. Ví dụ B làm chính Audit Engine thì B quyết định cấu trúc module và chịu trách nhiệm chạy test trước khi giao. |
| **Người phối hợp (Contributor/Pair)** | làm ra một phần cụ thể có thể kiểm chứng: viết fixture, bổ sung YAML, test API, điều tra bug hoặc review logic. Không chỉ “tham gia họp”. |
| **Người kiểm tra/phê duyệt (Reviewer/Approver)** | kiểm chất lượng/độ an toàn và yêu cầu sửa nếu chưa đạt. **Code review không mặc nhiên là quyền cho phép thay đổi Google Cloud/Kubernetes**; thao tác có tác động còn cần người có thẩm quyền cho phép trước khi chạy. |

### 1.2. Đọc tài liệu theo đường ngắn nhất

**A:** đọc toàn bộ mục 2 → các điểm giao A→B/A→C ở mục 5 → mục 7–9.  
**B:** đọc mục 3 → B nhận từ A/C ở mục 5 → mục 6–9.  
**C:** đọc mục 4 → C nhận từ A/B ở mục 5 → mục 6–9.

Cả nhóm cần hiểu [Tài liệu 01](01_CIS_GKE_TongQuan_TrinhBayBang.md) trước khi quyết định một CIS control được xem là đạt hay chưa.

![Phân công trách nhiệm A B C](assets/images/06-phan-cong-a-b-c.png)

*Hình 1. Phân công trách nhiệm chính và sản phẩm của ba thành viên.*

---

## 2. THÀNH VIÊN A — CLOUD & INTEGRATION LEAD

### 2.1. A chịu trách nhiệm kết quả gì?

A đảm bảo cả nhóm **có môi trường GKE đúng, truy cập đúng, hạ tầng có thể dựng lại và an toàn để thử nghiệm**. Khi B/C hoàn thành module của mình, A phải phối hợp để nối chúng thành một luồng chạy thật, nhưng **không phải A lập trình toàn bộ Audit Engine hoặc HTML reporter**.

### 2.2. Những phần A trực tiếp thực hiện

Bảng phân rã công việc của thành viên A: mỗi hàng là một nhóm nhiệm vụ có thể kiểm chứng; nội dung trong cột bên phải là phạm vi thực hiện, không phải tên việc chung chung.

| Nhóm việc chịu trách nhiệm | Cần thực hiện cụ thể |
|---|---|
| **A1 — Chuẩn bị Google Cloud và kiểm soát chi phí** | Kiểm tra project, Billing, dịch vụ API cần bật, region/zone, quota, quyền thực thi, budget và người được phép provision/destroy. Xác định naming convention cho project, clusters, namespace và subnet; không sử dụng thông tin xác thực cá nhân/khóa dài hạn chia sẻ qua chat hoặc Git. |
| **A2 — Terraform và mạng dùng chung** | Thiết kế VPC, hai subnet hoặc phân đoạn mạng phù hợp cho Standard/Autopilot, CIDR không trùng, outputs cần dùng, network/endpoint access. Chuẩn bị GCS remote backend có versioning/IAM và state độc lập cho phần mạng chung, Standard và Autopilot. Quản lý dependency giữa các state; tránh để nhiều state cùng sở hữu một resource. Mọi plan/apply thay đổi hạ tầng đều phải được review và phê duyệt phù hợp. |
| **A3 — Tạo hai GKE clusters** | Viết cấu hình Terraform và triển khai một cluster Standard cùng một cluster Autopilot. Lựa chọn node/network cấu hình phải phù hợp quota, bảo mật và thí nghiệm cần làm; với Standard phải bảo đảm đọc được thông tin NetworkPolicy enforcement. Sau khi dựng, cung cấp cách truy cập cluster qua context riêng; cùng C smoke test ứng dụng đơn giản. |
| **A4 — Google Cloud API collector** | Viết module read-only thu thông tin cluster/mode, dataplane/network config, subnet, các trường cho những control sử dụng Cloud API. Dùng đúng Google Cloud SDK/API và trả về dữ liệu chuẩn theo **schema B định nghĩa**. Trả lỗi có phân loại nếu thiếu quyền, không thấy cluster, trường vắng hoặc gọi API thất bại; không tự sửa hạ tầng. |
| **A5 — Nền tảng CI/cloud authentication** | Cùng B xây workflow GitHub Actions, trong đó A phụ trách Terraform checks và điều kiện xác thực cloud (ví dụ WIF/OIDC khi cần chạy live audit), B phụ trách Ruff/pytest/kiểm tra Python. Workflow kiểm tra mã mặc định không có quyền apply. Nếu có job live cloud, phải giới hạn identity/permissions và cổng phê duyệt cho thao tác thay đổi. |
| **A6 — Ghép toàn bộ thành một demo end-to-end** | Chốt và cung cấp môi trường live để B kiểm tra audit engine, C triển khai lab. Đảm bảo report từ B được tạo trên đúng mode/cluster, evidence có nguồn, các bước approval/rollback không bị CI bỏ qua. Khi tất cả thử nghiệm hoàn tất, A chủ trì destroy tài nguyên cloud sau khi nhóm đã lưu evidence; kiểm tra lại Billing/resources còn sót. |

### 2.3. A phải bàn giao gì, cho ai?

| Bàn giao cho | Thông tin / sản phẩm A phải giao |
|---|---|
| **Cho B** | Thông số **không nhạy cảm** của clusters: project/region/mode, tên cluster, cách sử dụng context/identity, cách gọi collector read-only; thống nhất field contract qua `docs/contracts.md`. |
| **Cho B** | Module Google Cloud collector và tests cho các dữ liệu cloud thực sự được dùng; ví dụ output có `datapathProvider`, thông tin subnet, trường lỗi khi thiếu quyền. Không giao raw credential/kubeconfig vào repo. |
| **Cho B** | Môi trường Standard/Autopilot sẵn sàng để B chạy collector và audit live; dấu vết context/commit và cách tái tạo nếu cluster bị dọn. |
| **Cho C** | Namespace/cluster mục tiêu để deploy lab, thông tin networking/NetworkPolicy enforcement, quyền tối thiểu để triển khai và thử lưu lượng. |
| **Cho C** | Hỗ trợ đo traffic, phân tích DNS/dataplane nếu policy chặn ứng dụng, hỗ trợ cloud impact/rollback trên các thao tác có liên quan. |
| **Cho cả nhóm** | Terraform source, backend/bootstrap instructions, runbook deploy/check/destroy, trạng thái CI và bản đồ cloud architecture. A không được chỉ bàn giao đường link tới Console rồi coi như xong. |

### 2.4. Khi nào phần A được xem là hoàn thành?

Hai cluster xác minh đúng mode và usable; Terraform code/state/outputs có thể review và tái tạo; `terraform plan` không chứa thay đổi bất ngờ; kubectl context được ghi rõ khi test; Cloud collector chạy read-only với dữ liệu thật và case lỗi; CI cơ bản chạy; tài liệu cost/cleanup đủ để người khác kiểm tra. A cùng B/C chạy được ít nhất một vòng audit và re-audit trên lab.

---

## 3. THÀNH VIÊN B — PYTHON AUDIT & REPORTING LEAD

### 3.1. B chịu trách nhiệm kết quả gì?

B biến danh sách kiểm tra CIS thành **một phần mềm audit có thể chạy lại**, chứ không phải một bộ lệnh rời rạc. Phần mềm nhận dữ liệu từ collector, áp dụng rule đúng mode, xuất finding giải thích được và báo cáo before/after. B giữ sự nhất quán của schema/trạng thái và chịu trách nhiệm chất lượng mã Python.

### 3.2. Những phần B trực tiếp thực hiện

Bảng phân rã công việc của thành viên B: mỗi hàng là một nhóm nhiệm vụ có thể kiểm chứng; nội dung trong cột bên phải là phạm vi thực hiện, không phải tên việc chung chung.

| Nhóm việc chịu trách nhiệm | Cần thực hiện cụ thể |
|---|---|
| **B1 — Thiết kế giao diện Python và contract** | Chốt cách chạy CLI, các input chính, cấu trúc thư mục, schema evidence/findings, loại dữ liệu lỗi, model `PASS/FAIL/REVIEW/N/A/ERROR` và phương án cấu hình benchmark theo mode. Có fixture minh họa để A/C làm song song. Phải tách **coverage của tool** (đã implement/chưa implement/ngoài scope) khỏi **status của control** (năm trạng thái trên). |
| **B2 — Kubernetes API collector** | Thu danh sách namespace/workloads/Pod, ServiceAccount, Role/ClusterRole, RoleBinding/ClusterRoleBinding, namespace labels và NetworkPolicy phù hợp với rule. Xử lý workload do controller tạo và tên SA mặc định. Có test khi API trả dữ liệu rỗng, thiếu field, `403`, timeout; không thay thế kết luận thiếu dữ liệu bằng `FAIL`. |
| **B3 — Evidence normalizer và evaluator** | Viết quy tắc chuẩn hóa tài nguyên theo namespace/kind/name, metadata nguồn và error handling; chọn rule đúng CIS v2.0.0 theo mode. Một control ở Standard không tự động được áp dụng cho Autopilot. Khi Manual cần xác minh, cung cấp `REVIEW`, trường ghi câu hỏi cần kiểm, bằng chứng và reviewer sau khi đánh giá. |
| **B4 — Trực tiếp lập trình nhóm rule Service Account/RBAC** | - `4.1.4` — tìm **workload đang dùng** default Service Account, không flag việc Kubernetes tạo sẵn SA `default`. • `4.1.5` — đọc cấu hình token mount ở workload/Pod/ServiceAccount và **ghi rõ điều gì phải xác minh thủ công** về nhu cầu Kubernetes API. • `4.1.9` — tìm binding tùy biến tới `system:authenticated`, không kết luận sai với ba binding hệ thống mặc định được benchmark nêu. B phối hợp C để giữ CIS mapping đúng, cập nhật fixture, và thống nhất exception handling. Không cần B tự tạo mọi manifest do C phụ trách lab. |
| **B5 — Cùng C hoàn thiện rule PSS/NetworkPolicy** | C chủ trì spec và trực tiếp viết phần rule `4.2.1/4.3.1/4.3.2` theo interface B đã chốt; **B chịu trách nhiệm review/tích hợp module này vào engine**, xử lý code compatibility và thêm tests/fixtures còn thiếu. Không được để logic Standard/Autopilot bị gộp sai. Với `4.3.1`, phân biệt Standard/Autopilot theo phần Audit trong benchmark; với `4.3.2`, chỉ tạo finding CIS cho Standard. |
| **B6 — JSON/HTML reporter và before/after compare** | Reporter hiển thị nguồn CIS, kết quả theo từng resource, evidence, lỗi và kết luận Manual; hỗ trợ summary không cộng `N/A` vào PASS. Compare so trên cùng cluster/mode/control/resource/scope, chỉ kết luận cải thiện theo chứng cứ. Làm sạch log/evidence để không công khai credentials, Secret values, token hay state. |
| **B7 — Bộ test và quy trình chạy** | Thiết lập Ruff/pytest cùng A trong CI; viết unit tests và fixtures gồm happy/negative/error/Manual cases. Khi có cluster, chạy live audit và re-audit với A/C; lưu kết quả có timestamp/Git SHA/test scenario, phân biệt fixture artifact và live evidence. Viết runbook CLI/audit/report. |

### 3.3. B phải nhận gì từ A/C trước khi hoàn thiện phần mềm?

| Nguồn đầu vào | B cần nhận trước khi tích hợp và nghiệm thu |
|---|---|
| **Từ A** | các field thực sự đọc được từ Google Cloud API, cloud mode/cluster identity, đường chạy read-only, lỗi có thể xảy ra và cluster để integration tests. Nếu A không thể cung cấp một field, B không được giả dữ liệu để làm rule PASS; cần sửa contract/condition và báo `ERROR/REVIEW` phù hợp. |
| **Từ C** | CIS Matrix đã đối chiếu hai PDF, điều kiện kỳ vọng từng rule, ngoại lệ, YAML trước/sau, fixtures và câu hỏi Manual. Cũng cần traffic/admission/functional test results để B so kết luận với trạng thái thật trong lab. |

### 3.4. B phải bàn giao gì, cho ai?

| Người nhận | Sản phẩm / thông tin B bàn giao |
|---|---|
| **Cho A** | Python package/CLI có cách cài/chạy, contract cấu hình cluster/mode, test command và reporter để tích hợp live/CI. Khi A chạy công cụ phải thấy lỗi rõ ràng nếu thiếu quyền hoặc chọn sai cluster, không cần sửa source Python. |
| **Cho C** | schema finding/evidence, tests mẫu, giao diện viết rule của nhóm C, kết quả audit cho từng manifest trước/sau, cách gắn approval/rollback metadata và cách chạy re-audit. B phải cùng C kiểm tra report có phản ánh kết quả allowed/blocked traffic và application health chứ không chỉ file YAML. |
| **Cho cả nhóm** | source Python, pytest suite/CI Python job, JSON schema, HTML template, report mẫu fixture và report live, hướng dẫn run/test/compare, định nghĩa rõ năm status. |

### 3.5. Khi nào phần B được xem là hoàn thành?

Có thể chạy audit trên fixture **không cần cluster** và trên hai GKE clusters thật **khi được cấp quyền**; mỗi rule P0 theo mode có test đúng/sai/trường hợp biên; Manual không tự PASS; `N/A` không nâng tỷ lệ; API error không báo giả FAIL; JSON/HTML đọc được và không lộ secret. Cùng C chứng minh được trước/sau cho hai kịch bản remediation.

---

## 4. THÀNH VIÊN C — CIS SECURITY, LABS & QA LEAD

### 4.1. C chịu trách nhiệm kết quả gì?

C bảo đảm dự án **đang kiểm tra đúng vấn đề bảo mật và có thực nghiệm chứng minh được**. C là người giữ tính chính xác của CIS Matrix, chịu trách nhiệm chuẩn bị trạng thái trước/sau, xây kịch bản security tests, thực hiện remediation trong lab sau phê duyệt và xác nhận không làm hỏng ứng dụng.

### 4.2. Những phần C trực tiếp thực hiện

Bảng phân rã công việc của thành viên C: mỗi hàng là một nhóm nhiệm vụ có thể kiểm chứng; nội dung trong cột bên phải là phạm vi thực hiện, không phải tên việc chung chung.

| Nhóm việc chịu trách nhiệm | Cần thực hiện cụ thể |
|---|---|
| **C1 — Đối chiếu hai CIS Benchmarks v2.0.0** | Làm matrix riêng cho Standard/Autopilot: đúng ID, tiêu đề, `Level`, Automated/Manual, điều kiện áp dụng, nguồn evidence, audit/remediation/impact và các ngoại lệ. Rà kỹ các điểm dễ nhầm: `4.2.1` và `4.3.2` chỉ có trong benchmark Standard; `4.3.1` khác Level/phương thức giữa hai mode; `5.6.1` Standard khác `5.4.1` Autopilot nếu làm P1. Không lấy danh sách từ báo cáo nhóm 20 năm 2025 làm chuẩn vì phiên bản cũ. |
| **C2 — Viết spec, fixtures và trực tiếp xây rule cho PSS/NetworkPolicy** | - `4.2.1` (Standard, Manual): xác định namespace workload, kiểm tra nhãn Pod Security **`enforce`** ở mức `baseline/restricted`; thiết kế kiểm thử admission hợp lý. Không áp ID này cho Autopilot. • `4.3.1` (Standard Level 1, Autopilot Level 2, đều Manual): phối hợp A đọc dataplane/enforcement; áp rule theo logic đúng cho từng mode, không bật Calico trên Autopilot. • `4.3.2` (Standard Level 2, Automated): xác định namespace workload có default-deny bao phủ Ingress/Egress phù hợp hay không; cùng A/B xác minh cơ chế enforcement và test thực tế. C viết code kiểm tra trên **interface do B thiết kế**, bổ sung fixtures với expected result và PR để B review/tích hợp. Đây không chỉ là “ghi yêu cầu rồi để B code hết”. |
| **C3 — Tạo lab Service Account có trạng thái trước/sau** | Tạo namespace `lab-sa` (hoặc tên thống nhất), ứng dụng HTTP và hai bộ manifest. `before` mô phỏng workload dùng `default` SA; `after` dùng dedicated SA và tắt token mount **khi không cần Kubernetes API**. Không gán quyền admin để tạo lỗi. Cùng B kiểm tra `4.1.4/4.1.5`; viết health check và phương án backup/rollback. |
| **C4 — Tạo lab NetworkPolicy trên GKE Standard** | Tạo namespace `lab-network`, app/clients/Service, phương án test DNS/HTTP và luồng được phép/bị chặn. `before` chưa có default-deny; `after` có policy deny ingress+egress và allow tối thiểu. Nếu lab dùng Workload Identity Federation, phải rà thêm đường metadata/API; không tùy tiện allow-all. Cùng A xác minh `4.3.1` trước khi dùng `4.3.2` để đánh giá default-deny. |
| **C5 — Thực nghiệm Pod Security Standards** | Trên Standard, áp dụng nhãn namespace và thử tình huống workload bị admission từ chối một cách kiểm soát; phân biệt `warn/audit` với `enforce`. Không chạm vào namespace hệ thống, không đưa file có cấu hình unsafe làm “mẫu vận hành an toàn” cho môi trường khác. |
| **C6 — Chạy remediation được kiểm soát** | Chuẩn bị tác động, backup manifest/policy, kế hoạch rollback, phương pháp xác minh và yêu cầu phê duyệt. **Chỉ sau khi có approval** mới áp dụng thay đổi trên namespace lab. Sau khi sửa, kiểm tra Pod Ready, HTTP, DNS/traffic; nếu chức năng lỗi thì rollback, test lại và ghi nhận. Sau đó phối hợp B chạy re-audit, xuất Before/After thật. |
| **C7 — QA và so sánh Standard/Autopilot** | Kiểm tra kết quả report phản ánh đúng CIS Matrix; xác thực logs không giả, không bị thiếu mode; làm tài liệu ngắn về khác biệt trách nhiệm bảo mật hai chế độ. Viết runbook security labs, hướng dẫn test và khôi phục; chuẩn bị phần thuyết minh kết quả thực nghiệm. |

### 4.3. C cần nhận gì từ A/B?

| Nguồn đầu vào | C cần được cung cấp |
|---|---|
| **Từ A** | cluster/context đã xác nhận đúng, namespace quyền deploy, thông tin enforcement và môi trường mạng có thể thực hiện traffic tests. A hỗ trợ khi NetworkPolicy chặn DNS/metadata, dataplane khác mong đợi hoặc cấu hình cloud không phù hợp benchmark. |
| **Từ B** | interface viết rule, fixture/test template, JSON finding schema, audit CLI, cơ chế `REVIEW`/manual decisions và reporter compare. Nếu một policy được áp đúng mà rule báo không nhất quán, C/B cùng debug theo evidence thay vì sửa report bằng tay. |

### 4.4. C phải bàn giao gì, cho ai?

| Người nhận | Sản phẩm / thông tin C bàn giao |
|---|---|
| **Cho B** | CIS Matrix có nguồn, logic/fixture của từng rule; code `4.2.1/4.3.1/4.3.2`; YAML `before/after`; kết quả admission/traffic chức năng; manual-review questions và nhận định test. |
| **Cho A** | danh sách namespace cần deploy, yêu cầu về enforcement/permissions/networking, phương án test kết nối, rủi ro tác động và checklist điều kiện trước khi chạy live remediation. |
| **Cho cả nhóm** | manifests và scripts lab, approval/rollback template, functional/security evidence trước/sau, kết quả QA và tài liệu Standard–Autopilot. Các hình vẽ AI được để riêng, không dùng thay ảnh/log kiểm thử thật. |

### 4.5. Khi nào phần C được xem là hoàn thành?

CIS Matrix đúng theo hai PDF; 3 rule PSS/NP tích hợp với engine của B và có fixtures/tests; labs triển khai lại được; hai remediation có backup, approval, allowed/blocked/HTTP/DNS tests phù hợp và re-audit; có minh chứng điều kiện không phê duyệt → không sửa, điều kiện functional failure → rollback; report được C xác nhận khớp với thực nghiệm.

---

## 5. BÀN GIAO CHO NHAU THẾ NÀO ĐỂ KHÔNG BỊ TẮC?

**Nguyên tắc dễ nhớ:** bên tạo thành phần phải giao **đầu vào/đầu ra, cách sử dụng, bằng chứng test và giới hạn**, không chỉ nói “xong phần mình”. Có thể bàn giao phiên bản fixture trước, rồi thay bằng dữ liệu live mà không phá contract.

| Tuyến bàn giao | Sản phẩm chính | Người nhận dùng để |
|---|---|---|
| **A → B** | Cluster/mode, Google Cloud collector, hướng dẫn quyền đọc, cloud evidence | B tích hợp rule liên quan hạ tầng và chạy live audit |
| **C → B** | CIS Matrix, rule specs/fixtures, YAML & kỳ vọng PASS/FAIL/REVIEW | B thực thi/kiểm thử evaluator và đối chiếu benchmark |
| **B → A/C** | CLI, JSON schema, registry, reporter và hướng dẫn chạy | A tích hợp với GKE/CI, C QA manifests và hậu kiểm |
| **A ↔ C** | Context/permissions, dataplane/enforcement và traffic scenarios | Chạy thực nghiệm an toàn, debug DNS/network |
| **A/C → B** | Cloud + functional/admission/traffic evidence trước/sau | B xuất JSON/HTML và before/after có nguồn thật |


### 5.1. A → B: từ hạ tầng sang Python

A gửi `cluster identity + mode + Google Cloud collector output + hướng chạy read-only`. B dùng để chọn rule, đọc fields cloud và thử lỗi. Trước khi B tích hợp live, A/B cùng chạy một thao tác đọc cluster và so sánh kết quả thu được với schema dự kiến. Nếu tên field hoặc ý nghĩa khác, **chốt sửa `docs/contracts.md` trước** rồi mới merge code tích hợp.

**Ví dụ tình huống:** B cần biết `networkConfig.datapathProvider` để đánh giá `4.3.1`. A không chỉ chụp màn hình Console mà cần có collector data và cách xác minh giá trị đó từ API; B trả `ERROR/REVIEW` nếu không đọc được, không mặc định coi là Dataplane V2.

### 5.2. C → B: từ CIS/security specification sang logic Python

C gửi `CIS ID, benchmark/mode, Level, Manual/Automated, điều kiện, nguồn evidence, fixtures expected, exception và YAML lab`. B dùng để lập trình/tích hợp đúng, nhất là các rule C trực tiếp code theo interface chung. Mọi case test có outcome gây tranh luận phải quay lại đối chiếu PDF và lưu quyết định trong matrix, không chốt bằng cảm giác.

**Ví dụ tình huống:** control `4.1.5` nói token chỉ nên có khi Pod cần Kubernetes API. Nếu không có thông tin workload cần API hay không, C phải nêu câu hỏi manual; B hiển thị `REVIEW` và evidence liên quan, **không viết một if/else coi tất cả token mount là FAIL**.

### 5.3. B → A và C: từ Audit Engine sang chạy thật

B giao `CLI syntax + fixture-ready build + JSON schema + report template + test instructions`. A chạy live trên hai cluster và giải quyết lỗi kết nối/cloud; C triển khai YAML và đánh giá findings. Khi status/schema thay đổi, B thông báo và có PR thay đổi `docs/contracts.md`; A/C cần review trước khi dùng bản mới.

### 5.4. A và C → B: bằng chứng thực nghiệm để reporter nói đúng

A cung cấp dữ liệu cấu hình/mode/network thực; C cung cấp HTTP/traffic/admission results, backup, approval và trạng thái trước/sau. B gắn evidence vào report/diff. Nếu thử traffic thất bại nhưng policy YAML nhìn có vẻ đúng, **không được xuất PASS chỉ dựa vào sự tồn tại của file cấu hình**.

### 5.5. Bộ tài liệu giao tiếp chung (cả ba dùng)

Không cần quá nhiều bảng hay biểu mẫu. Cả nhóm cần duy trì tối thiểu:

- `docs/contracts.md`: mode naming, CLI inputs, collector evidence fields, error/exception contract, finding/report schema. **B** cập nhật giao diện Python; **A** xác nhận cloud fields; **C** xác nhận yêu cầu CIS/QA.
- `docs/cis-control-matrix.md`: đúng mapping hai benchmark; **C** cập nhật, **B** đối chiếu evaluator, **A** review nguồn Cloud API.
- `README.md` và runbooks: **A** phần Terraform/GKE/Cloud; **B** phần Python/tests/reports; **C** phần labs/security/rollback; cả ba cùng thử các hướng dẫn của nhau.

![Luồng bàn giao giữa A B C](assets/images/07-handoff-integration.png)

*Hình 2. Luồng bàn giao và phối hợp tích hợp giữa A, B và C.*

---

## 6. CÓ THỂ LÀM SONG SONG KHÔNG? CÓ — NHƯNG CẦN CHỐT ĐÚNG ĐIỂM GIAO

### 6.1. Ba luồng bắt đầu được cùng lúc

| Luồng song song | Có thể triển khai ngay, chưa cần chờ các luồng còn lại |
|---|---|
| **A bắt đầu với hạ tầng** | chuẩn bị cloud, repo, backend, VPC, Standard/Autopilot, thiết kế Cloud collector. Không cần chờ B lập trình audit hay C viết xong YAML lab. |
| **B bắt đầu với phần mềm offline** | chốt CLI/schema, tạo collector interface, normalizer, evaluator, JSON/HTML draft, rule `4.1.4/4.1.5/4.1.9` với fixture do tự tạo cùng C. Không cần chờ cluster thật để viết unit tests. |
| **C bắt đầu với benchmark và labs offline** | lập CIS Matrix, thiết kế manifest `before/after`, test cases, các rule PSS/NP theo interface đã chốt cùng B. Không cần chờ cluster thật để viết YAML và expected outcomes. |

**Điểm duy nhất nên thống nhất trước khi mỗi nhánh đi sâu:** benchmark/mode, tên namespace thí nghiệm, schema evidence/findings và cách gọi CLI. Nếu chưa chốt hoàn toàn thì dùng fixture v1 và ghi rõ interface tạm; tránh hai phía cùng tự đặt key khác nhau.

### 6.2. Những việc phải đợi nhau vì phụ thuộc thật

| Phụ thuộc thật | Cần có gì trước khi tiếp tục |
|---|---|
| **Live audit cần hạ tầng A** | phải có cluster/identity phù hợp thì B mới xác nhận collector bằng dữ liệu thật. |
| **Rule có ý nghĩa cần CIS Matrix C** | B không tự suy đoán Level/Manual/applicability hoặc ngoại lệ từ tên control. |
| **C viết rule chung cần contract B** | dùng interface B chốt để tích hợp; không tạo module riêng không tương thích với evaluator. |
| **NetworkPolicy test cần A và C** | A xác nhận enforcement/cấu hình mạng; C áp policy và đo traffic; B kiểm chứng audit/report. |
| **Remediation cần baseline + approval** | C không tự apply chỉ vì YAML đã sẵn; phải có kết quả baseline và quyền cho phép rõ ràng. |
| **Before/After cần cả ba** | A đảm bảo môi trường/identity, C làm thay đổi và kiểm thử ứng dụng, B chạy audit/diff/report. |

### 6.3. Khi một người bị chờ, làm gì tiếp?

Nếu chưa có cluster, B viết thêm edge-case fixtures và reporter; C hoàn thiện manifest/test/rollback documentation. Nếu rule chưa hoàn thiện, A vẫn có thể xác minh Terraform, cloud collector, context và chi phí; C vẫn có thể kiểm tra smoke/HTTP. Nếu thiếu cloud permission, **không tắt kiểm tra để giả dữ liệu live**; ghi blocker và tiếp tục phần offline.

![Ba nhánh công việc song song](assets/images/08-parallel-work.png)

*Hình 3. Các nhánh công việc song song và các điểm hội tụ của dự án.*

---

## 7. TRÁCH NHIỆM THỰC TẾ QUA HAI KỊCH BẢN DEMO

### 7.1. Service Account Hardening — mỗi người làm việc gì?

| Trách nhiệm | Việc cần thực hiện và điều kiện nghiệm thu |
|---|---|
| **B giữ đầu ra audit** | hoàn thành các rule `4.1.4/4.1.5`, fixture và báo cáo; chỉ ra bằng chứng app đang dùng `default` SA và câu hỏi Manual liên quan tới nhu cầu API. B chạy baseline và hậu kiểm, xuất diff. |
| **C giữ lab và thay đổi security** | chuẩn bị app/namespace/manifests `before/after`, phân tích tác động khi bỏ token, chuẩn bị dedicated SA, health checks và rollback. C gửi phương án cho reviewer/approver. Chỉ khi được phê duyệt C mới áp manifest `after`; sau đó kiểm tra Pod/HTTP và ghi kết quả thật. |
| **A giữ môi trường/an toàn triển khai** | xác minh cluster/context, quyền tối thiểu, giúp sao lưu/các rủi ro Cloud liên quan, hỗ trợ debug nếu rollout thất bại. A kiểm tra thay đổi có nằm trong namespace lab và không có tác động ngoài dự kiến. |
| **Chốt kết quả chung** | B đối chiếu audit `before/after`, C xác nhận ứng dụng còn chạy, A xác nhận đúng môi trường/phạm vi. Nếu bất kỳ phần nào thất bại, chưa nghiệm thu kịch bản là thành công. |

### 7.2. NetworkPolicy Hardening (Standard) — mỗi người làm việc gì?

| Trách nhiệm | Việc cần thực hiện và điều kiện nghiệm thu |
|---|---|
| **A xác nhận nền mạng** | GKE Standard thực sự dùng Dataplane V2 hoặc Calico đúng cấu hình theo `4.3.1`; chỉ rõ networking/context, hỗ trợ DNS, metadata và traffic debug. Không kích hoạt network enforcement trên cloud bừa bãi chỉ để demo. |
| **C giữ thiết kế policy/thử nghiệm** | tạo workload/client/server; đo baseline; viết policy default-deny **ingress + egress**, allow DNS/app theo nhu cầu; xin phê duyệt; backup; triển khai; đo traffic được phép/bị chặn; kiểm tra ứng dụng và khả năng rollback. |
| **B giữ đánh giá/báo cáo** | kiểm tra logic `4.3.2` do C xây theo interface chung, chạy baseline/re-audit; xuất report liên kết policy evidence và traffic evidence. Không đánh nhầm `4.3.2` thành control của Autopilot. |
| **Chốt kết quả chung** | A xác nhận enforcement, C xác nhận luồng traffic thực, B xác nhận kết luận audit/report; cả ba ghi lại ngoại lệ/hạn chế nếu hệ thống chỉ chứng minh được một phần. |

### 7.3. Khi không được duyệt hoặc phát sinh lỗi thì ai xử lý?

| Tình huống | Phối hợp xử lý và lưu chứng cứ |
|---|---|
| **Không được phê duyệt** | C dừng apply, B giữ report hiện trạng và lý do `not approved`, A xác nhận không có cloud/K8s mutation ngoài dự kiến. |
| **App/DNS/traffic sai sau sửa** | C thực hiện rollback theo phương án đã duyệt, A hỗ trợ troubleshooting, B ghi kết quả audit/functional sau rollback. Không đổi tên `FAIL` thành `PASS`. |
| **Collector báo lỗi API** | B phân tích dữ liệu/error path; A kiểm tra IAM, cluster identity, permissions; C xem rule có áp dụng đúng benchmark không. Trạng thái phù hợp là `ERROR` hoặc `REVIEW` theo bản chất, không “tự sửa” kết quả. |
| **Sai CIS ID/Level/mode** | C rà lại PDF, B sửa registry/tests, A rà cloud evidence nếu liên quan; cả nhóm giữ regression test để không tái diễn. |

---

## 8. QUY TRÌNH NHÓM: CODE, REVIEW, APPROVAL VÀ BÀN GIAO

### 8.1. Khi bắt đầu một hạng mục

Người làm chính tạo Issue ngắn gồm: **vấn đề cần giải quyết**, **đầu ra phải có**, **phụ thuộc**, **người phối hợp/reviewer**, **cách kiểm tra** và **rủi ro**. Không nhất thiết phải mở 36 Issue nhỏ theo bảng cũ; có thể gom theo sản phẩm (Terraform, collector, rule pack, labs, reporting) và chia subtask vừa đủ để theo dõi.

Nhánh Git/PR mô tả code/manifest đã thay, điều kiện CIS tương ứng, unit/live tests đã chạy, evidence, rollback nếu có. Reviewer phải là người không thực hiện chính thay đổi đó. Một PR đụng đến contract/mapping phải có người sử dụng hoặc người giữ CIS Matrix xem lại.

### 8.2. Quyền phê duyệt là một bước riêng

**Không có bước “PR merge = tự động áp hạ tầng”.** `terraform apply/destroy`, thay IAM/networking/GKE, triển khai SA/NetworkPolicy/PSS có ảnh hưởng và các thao tác tương tự phải được người được phân quyền đồng ý **trước khi thực hiện**. Hồ sơ tối thiểu ghi: đối tượng/namespace/cluster, file/commit, khác biệt cấu hình, tác động, người duyệt, cách rollback và phương pháp kiểm tra sau áp dụng. Nếu người duyệt từ chối thì chỉ báo cáo; không chạy apply.

### 8.3. Định nghĩa hoàn thành áp dụng cho tất cả

Một hạng mục **chưa hoàn thành** nếu chỉ có code nhưng chưa có cách test, chỉ có ảnh chụp nhưng không tái hiện được, hoặc có report nhưng không lần theo evidence. Đầu ra phải có code/tài liệu, test và evidence phù hợp, reviewer chấp thuận, hướng dẫn sử dụng và ghi rõ phần chưa làm/giới hạn. Nếu thay đổi cấu hình, bắt buộc có approval, backup và hậu kiểm; không được bỏ các bước đó để tiết kiệm thời gian.

### 8.4. Cách trao đổi để không cần họp liên tục

Mỗi khi bàn giao một module, gửi cho người nhận **ba thông tin**: *đã xong gì và ở đâu*, *chạy thử bằng cách nào*, *còn vướng/giới hạn gì*. Các tranh luận về CIS phải dẫn đúng benchmark/mục; tranh luận về API/schema phải cập nhật `docs/contracts.md`; tranh luận về hạ tầng phải dựa trên `terraform plan`, quyền, chi phí và tác động thực tế. Không có cam kết số ngày hay giờ làm bắt buộc trong tài liệu này.

---

## 9. DANH SÁCH NHẬN BÀN GIAO CUỐI CỦA TỪNG NGƯỜI

Bảng sau tóm tắt đầu ra theo người; các checklist phía dưới là điều kiện ký nhận chi tiết, không bỏ qua khi bàn giao.

| Thành viên | Nhóm sản phẩm cuối phải được nghiệm thu | Bên sử dụng / kiểm chứng |
|---|---|---|
| **A** | Terraform & remote state; 2 GKE clusters; Cloud collector; CI/cloud access; integration & cleanup | B nhận cluster/evidence; C nhận lab environment; cả nhóm kiểm chứng cloud |
| **B** | CLI + collector/registry/evaluator; CIS rules SA/RBAC; pytest; JSON/HTML & before/after | A dùng chạy live/CI; C dùng re-audit và QA; cả nhóm duyệt report |
| **C** | CIS Matrix; PSS/NP rules; lab YAML & 2 remediation; functional/traffic/QA evidence | B tích hợp rule/report; A hỗ trợ cluster/network; cả nhóm nghiệm thu security |

### 9.1. A — Cloud & Integration

- [ ] GCP project/region/quota/budget/permissions được kiểm tra; có người duyệt cloud operations.
- [ ] Terraform cho shared network, GKE Standard và GKE Autopilot, remote state GCS tách biệt; plan review và runbook.
- [ ] Hai cluster hoạt động, context rõ, smoke test có bằng chứng.
- [ ] Cloud collector read-only và test fields/lỗi, đã tích hợp theo schema của B.
- [ ] GitHub Actions CI/cloud auth theo quyền thích hợp; không tự apply khi chưa duyệt.
- [ ] Đã hỗ trợ B/C live integration, bảo đảm hai remediation chạy đúng lab, có cleanup và kiểm tra billing.

### 9.2. B — Python Audit & Reporting

- [ ] Contract CLI/schema, Kubernetes collector, normalizer, mode registry/evaluator thống nhất.
- [ ] Các rule SA/RBAC `4.1.4/4.1.5/4.1.9` có test/evidence; rule `4.2.1/4.3.1/4.3.2` của C đã review/tích hợp.
- [ ] Logic `Manual`, `N/A`, `ERROR`, ngoại lệ hệ thống được xử lý chính xác; không nhầm P0/P1 với CIS Level.
- [ ] Ruff/pytest chạy, fixture tests và live tests có bằng chứng.
- [ ] JSON/HTML report và compare trước/sau chạy được, không lộ token/Secret; có runbook Python.
- [ ] Kết quả hai kịch bản remediation được phản ánh đúng và có thể giải thích khi demo.

### 9.3. C — CIS Security, Labs & QA

- [ ] CIS Matrix hai benchmark v2.0.0 được đối chiếu, có tham chiếu nguồn và điều kiện áp dụng.
- [ ] Rule specs/fixtures và implementation PSS/NP `4.2.1/4.3.1/4.3.2` tích hợp với B.
- [ ] YAML lab Service Account, NetworkPolicy và PSS; `before/after`, health/admission/traffic tests rõ.
- [ ] Service Account remediation có approval, backup, functional tests, rollback plan và re-audit.
- [ ] Standard NetworkPolicy có enforcement, deny ingress/egress + allow tối thiểu, DNS/allowed/blocked tests và re-audit.
- [ ] QA report/evidence Manual/N/A/ERROR, tài liệu so Standard–Autopilot và security runbook hoàn chỉnh.

### 9.4. Việc cả nhóm phải cùng ký nhận

- [ ] Chạy end-to-end được: Terraform → cluster → lab → audit → findings → approval → remediation → functional tests → re-audit → report.
- [ ] Demo được cả trường hợp **không phê duyệt** và tình huống **rollback khi sửa gây lỗi** (có thể thông qua thử nghiệm lab an toàn).
- [ ] Không nhận vơ rằng đã kiểm tra **toàn bộ CIS v2.0.0**; mức coverage, Manual reviews và chưa triển khai được ghi rõ.
- [ ] Repository sạch thông tin nhạy cảm; hướng dẫn có thể được người khác sử dụng để tái tạo.
- [ ] Evidence thật đã sao lưu; tài nguyên cloud không còn cần thiết đã được dọn và rà soát chi phí.

---

## 10. NHỮNG CÂU HỎI NHÓM PHẢI CÙNG GIẢI THÍCH ĐƯỢC

**A phải giải thích được:** vì sao có hai cluster/mode, luồng Terraform state, cách Audit Engine xác định cluster và truy cập Google Cloud API, vì sao Dataplane V2/Calico ảnh hưởng tới NetworkPolicy, và một ví dụ status của Python.

**B phải giải thích được:** vì sao control của Autopilot không dùng nguyên registry Standard, khi nào trả REVIEW/ERROR/N/A, một case `4.1.4`/`4.1.9`, cấu trúc JSON/HTML, và vì sao compare phải đối chiếu đúng resource.

**C phải giải thích được:** một CIS control Manual cần đánh giá thế nào, vì sao PSS `enforce` khác `warn`, default-deny ingress/egress cần allow DNS, workflow rollback, và cách một fixture Python được dùng để chứng minh rule.

**Tất cả** phải biết: kịch bản nào được thực nghiệm thật; chính xác phần nào chỉ là ví dụ minh họa; ai phê duyệt; test ứng dụng nào chứng minh remediation an toàn; khi `FAIL` hoặc `REVIEW` chưa được giải quyết thì báo cáo như thế nào.

---

## 11. NGUỒN VÀ GHI CHÚ PHIÊN BẢN

Tài liệu phân công này bám theo [Tài liệu 01](01_CIS_GKE_TongQuan_TrinhBayBang.md) và hai PDF **CIS GKE Benchmark v2.0.0** / **CIS GKE Autopilot Benchmark v2.0.0** (30/06/2026). Danh sách module, đường dẫn file và sơ đồ phân công là **thiết kế đề xuất**, không phải bằng chứng đã triển khai. Báo cáo học thuật nhóm 20 năm 2025 được tham khảo như tài liệu tiền nhiệm, không thay nguồn CIS v2.0.0.

**Không chia lịch 14/21 ngày hoặc giờ công tỷ lệ cố định.** Mỗi người được nghiệm thu bằng **artifact, bài test, evidence và khả năng giải thích phần đã làm**. Nếu nhóm phân công lại, phải cập nhật đầu ra và người review trong Issue/PR; không tự bỏ bất kỳ bước approval, test hoặc rollback nào.


