# Báo cáo XeLaTeX — CIS GKE Security Audit

Thư mục này chứa mã nguồn báo cáo đồ án, biên dịch bằng XeLaTeX.

## Yêu cầu

- **TeX distribution**: MiKTeX hoặc TeX Live (cần có `xelatex` và `biber`)
- **Font**: Latin Modern (Computer Modern) — đi kèm mọi bản TeX
- Không cần cài thêm font hệ thống

## Biên dịch

```powershell
cd report

# Tạo thư mục build nếu chưa có
mkdir build -ErrorAction SilentlyContinue

# Chuỗi biên dịch đầy đủ (cross-references + bibliography)
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
biber --input-directory=build --output-directory=build main
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
```

PDF đầu ra: **`build/main.pdf`** (12 trang A4, thư mục `build/` đã loại khỏi Git).

> **Lưu ý**: Nếu có `latexmk` và Perl, có thể thay bằng `latexmk -xelatex -outdir=build main.tex`.

## Cấu trúc thư mục

```
report/
├── main.tex              # File chính, metadata trang bìa
├── preamble.tex          # Font, layout, macro, placeholder figure
├── references.bib        # Tài liệu tham khảo (BibLaTeX)
├── latexmkrc             # Cấu hình latexmk (nếu dùng)
├── chapters/
│   ├── chapter01.tex     # Chương I — Giới thiệu đề tài
│   ├── chapter02.tex     # Chương II — Phương pháp thực hiện
│   ├── chapter03.tex     # Chương III — Thiết kế và kiến trúc (placeholder)
│   └── chapter04.tex     # Chương IV — Thực nghiệm và kết quả (placeholder)
├── tables/
│   ├── selected-manual.tex       # Bảng 1.1 — 3 control Manual
│   ├── selected-automated.tex    # Bảng 1.2 — 3 control Automated
│   ├── audit-outputs.tex         # Bảng 2.1 — Đầu ra Audit Engine
│   ├── control-inventory.csv     # Danh mục đối chiếu CIS đầy đủ
│   └── *.tex                     # Bảng Level 1 tham khảo (không in)
├── figures/
│   ├── manual-workflow.tex       # Hình 2.1 — TikZ
│   ├── automated-workflow.tex    # Hình 2.2 — TikZ
│   └── remote-workflow.tex       # Hình 2.3 — TikZ
└── build/                        # (gitignored) Chứa PDF đầu ra
```

## Bật Chương III–IV

Chương III (Kiến trúc) và IV (Thực nghiệm) đã có file nguồn với placeholder nhưng đang tắt.  
Để bật, bỏ comment 2 dòng trong `main.tex`:

```latex
% --- Bật chương III–IV khi nhóm bắt đầu viết nội dung chính thức ---
\include{chapters/chapter03}
\include{chapters/chapter04}
```

## Thêm hình draw.io

Báo cáo dùng macro `\placeholderfig` với `\IfFileExists`:

1. Vẽ sơ đồ bằng draw.io
2. **Export → PDF** (không chọn crop)
3. Đặt file vào `report/figures/` đúng tên:

| Tên file | Hình | Chương |
|----------|------|--------|
| `system-architecture.pdf` | Kiến trúc tổng thể | III |
| `system-workflow.pdf` | Luồng end-to-end | III |
| `audit-engine-architecture.pdf` | Chi tiết Audit Engine | III |
| `sa-hardening-before-after.pdf` | Before/after SA | IV |
| `networkpolicy-before-after.pdf` | Before/after NetworkPolicy | IV |

4. Build lại → hình tự thay placeholder, không cần sửa LaTeX.

## Sáu CIS Controls trong phạm vi

| CIS ID | Tên | Phân loại |
|--------|-----|-----------|
| 4.1.4 | Default ServiceAccount | Level 1, Automated |
| 4.1.5 | SA Token mount | Level 1, Manual |
| 4.1.9 | RBAC `system:authenticated` | Level 1, Automated |
| 4.2.1 | Pod Security Standards | Level 1, Manual |
| 4.3.1 | NetworkPolicy enforcement | Level 1/2, Manual |
| 4.3.2 | Default-deny NetworkPolicy | Level 2, Automated |

## Quy ước

- **Nguồn CIS**: Đối chiếu theo CIS GKE Benchmark v2.0.0 (Standard) và CIS GKE Autopilot Benchmark v2.0.0. PDF CIS nằm trong `../references/private/`, không đưa vào Git.
- **Trang bìa**: Thay các trường `[Bổ sung ...]` bằng thông tin trường/khoa và nhóm trước khi nộp.
- **Build artifacts**: Thư mục `build/` và file `*.pdf` đã nằm trong `.gitignore`.
