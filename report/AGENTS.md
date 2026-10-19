# Report authoring rules

- Biên dịch tài liệu bằng XeLaTeX; giữ toàn bộ file trung gian trong `build/`.
- Chỉ dùng hai CIS Benchmark v2.0.0 trong `../references/private/` để xác định ID, tên, Profile Applicability, Assessment Status và trang nguồn.
- Không chép dài nguyên văn nội dung CIS. Chỉ giữ tiêu đề recommendation và diễn giải ngắn bằng tiếng Việt có trích dẫn trang.
- Không sao chép hoặc di chuyển PDF CIS vào `report/`, và không đưa các PDF đó vào Git.
- Bốn bảng phân loại trong Chương I chỉ chứa recommendation Level 1. Các control Level 2 chỉ được nêu khi giải thích phạm vi dự án.
- Phân biệt yêu cầu CIS, thiết kế dự kiến và chức năng đã có bằng chứng trong repository. Không biến fixture thành kết quả audit thật.
- Thêm bảng dài bằng `longtable`; không dùng `resizebox` để ép cỡ chữ.
- Sau khi sửa nội dung, chạy `latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex` và kiểm tra warning bố cục.
