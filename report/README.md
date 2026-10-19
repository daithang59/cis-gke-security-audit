# Báo cáo XeLaTeX

Thư mục này chứa mã nguồn cho Chương I và Chương II của báo cáo đồ án. Hai PDF CIS nguồn được đọc trực tiếp từ `../references/private/` nhưng không được sao chép vào đây hoặc đưa vào Git.

## Biên dịch

Yêu cầu: XeLaTeX, `latexmk` và `biber`.

```powershell
cd report
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
```

PDF đầu ra nằm tại `build/main.pdf`. Thư mục `build/` đã được loại khỏi Git.

Nếu MiKTeX tìm thấy `latexmk.exe` nhưng báo thiếu Perl, có thể chạy chuỗi tương đương sau:

```powershell
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
biber --input-directory build --output-directory build main
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
```

Bản kiểm tra ngày 19/10/2026 được biên dịch theo chuỗi trên vì bản MiKTeX cục bộ chưa có Perl. Kết quả là PDF A4 gồm 12 trang; log cuối không có citation/reference chưa xác định hoặc `overfull box`.

## Cấu trúc

- `main.tex`: điểm vào và metadata trang bìa.
- `preamble.tex`: font, bố cục, bảng, heading, header/footer và trích dẫn.
- `chapters/`: nội dung từng chương.
- `tables/`: hai bảng sáu control thuộc phạm vi đề tài; các bảng Level 1 đầy đủ được giữ riêng để tham khảo nhưng không đưa vào PDF.
- `figures/`: sơ đồ TikZ có thể bảo trì như mã nguồn.
- `references.bib`: metadata tài liệu tham khảo; không chứa nội dung PDF.

## Quy ước nguồn CIS

Mỗi recommendation được đối chiếu theo tiêu đề, `Profile Applicability`, nhãn `(Manual)`/`(Automated)` và số trang in ở footer của PDF. Trang vật lý trong trình đọc PDF lớn hơn số trang in một đơn vị do trang bìa. Danh mục kiểm chứng máy đọc được nằm tại `tables/control-inventory.csv`.

Autopilot v2.0.0 có một bất nhất nội bộ: phần Change History ghi `4.1.9` đã bị loại, nhưng mục lục, nội dung recommendation ở trang in 41 và Summary Table vẫn chứa mục này dưới Level 1/Automated. Báo cáo ưu tiên nội dung recommendation hiện hành và Summary Table, vì vậy vẫn liệt kê `4.1.9`.

Các trường `[Bổ sung ...]` trên trang bìa cần được thay bằng thông tin trường/khoa và nhóm trước khi nộp.
