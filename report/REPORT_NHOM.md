# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G41  
**Thành viên:** Lê Như Ý, Nguyễn Văn A, Trần Thị B  
**Ngày:** 2026-09-20  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Đổi trả, Bảo hành và Quy định Người mua/Người bán trên Nền tảng Thương mại Điện tử (Biến thể K4-L3B).

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề chính sách TMĐT vì đây là nghiệp vụ có khối lượng văn bản pháp quy lớn, quy định cụ thể về thời gian, phí tổn và điều kiện bảo hành đổi trả rất dễ gây tranh chấp giữa người mua và người bán. Việc ứng dụng hệ thống RAG với cơ chế lọc metadata và chunking chuẩn xác sẽ giải quyết trực tiếp bài toán tra cứu chính xác, tự động hóa chăm sóc khách hàng và giảm tải cho đội ngũ hỗ trợ sàn.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|---|:---:|---|
| 1 | `cellphones-warranty-policy.md` | https://cellphones.com.vn/chinh-sach-bao-hanh | 2026-09-20 / 2024.1 | 2.565 | `audience: buyer`, `category: warranty-returns`, `platform: CellphoneS` |
| 2 | `dienmayxanh-warranty-policy.md` | https://www.dienmayxanh.com/chinh-sach-bao-hanh-san-pham | 2026-09-20 / 2024.1 | 2.474 | `audience: buyer`, `category: warranty-returns`, `platform: DienMayXanh` |
| 3 | `fptshop-return-policy.md` | https://fptshop.com.vn/ho-tro/chinh-sach-doi-san-pham | 2026-09-20 / 2024.1 | 2.514 | `audience: buyer`, `category: returns-exchange`, `platform: FPTShop` |
| 4 | `shopee-warranty-policy.md` | https://help.shopee.vn/portal/4/article/79046 | 2026-09-20 / 2024.1 | 2.486 | `audience: buyer`, `category: warranty`, `platform: Shopee` |
| 5 | `thegioididong-warranty-policy.md` | https://www.thegioididong.com/chinh-sach-bao-hanh-san-pham | 2026-09-20 / 2024.1 | 2.584 | `audience: buyer`, `category: warranty-returns`, `platform: TheGioiDiDong` |
| 6 | `ttgshop-warranty-policy.md` | https://ttgshop.vn/quy-dinh-bao-hanh | 2026-09-20 / 2024.1 | 2.270 | `audience: buyer`, `category: warranty-returns`, `platform: TTGShop` |
| 7 | `return-refund-policy.md` | https://example.com/policy/returns | 2026-09-18 / not-stated | 628 | `audience: buyer`, `category: returns-policy` |
| 8 | `seller-warranty-policy.md` | https://example.com/policy/seller-warranty | 2026-09-18 / not-stated | 512 | `audience: seller`, `category: warranty-policy` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|---|---|---|---|
| `audience` | string | `"buyer"`, `"seller"`, `"both"` | Tách biệt đối tượng thụ hưởng chính sách, tránh tình trạng khách hàng hỏi quyền lợi đổi trả lại bị trả lời bằng nghĩa vụ bảo hành của người bán. |
| `category` | string | `"warranty-returns"`, `"warranty"` | Cho phép lọc theo nhóm nghiệp vụ chuyên biệt (bảo hành định kỳ, đổi trả 1-1, trả hàng hoàn tiền). |
| `platform` | string | `"CellphoneS"`, `"Shopee"` | Hỗ trợ phân luồng tra cứu theo từng nền tảng/nhà phân phối riêng biệt khi corpus mở rộng đa sàn. |
| `source_url` | string | `https://cellphones.com.vn/...` | Cung cấp liên kết gốc để người dùng kiểm chứng tính xác thực của câu trả lời (Source Traceability). |
| `retrieved_at` | string | `"2026-09-20"` | Giám sát tính cập nhật của tài liệu, loại trừ các chính sách đã lỗi thời hoặc quá hạn. |
| `document_version`| string | `"2024.1"` | Đảm bảo tính nhất quán khi các sàn cập nhật các phiên bản điều khoản mới theo quý/năm. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu tiêu biểu (đã loại bỏ phần frontmatter):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|---|---|:---:|:---:|---|
| `cellphones-warranty-policy.md` | FixedSizeChunker (`fixed_size`) | 6 | 444.2 ký tự | Cắt cơ học theo ký tự, có thể cắt đôi điều khoản. |
| | SentenceChunker (`by_sentences`) | 9 | 283.4 ký tự | Tốt ở cấp câu, nhưng các điều khoản có gạch đầu dòng ngắn bị tách lẻ. |
| | RecursiveChunker (`recursive`) | 8 | 319.1 ký tự | Rất tốt, gom nhóm theo đoạn `\n\n` và xuống câu khi quá dài. |
| `dienmayxanh-warranty-policy.md` | FixedSizeChunker (`fixed_size`) | 6 | 429.0 ký tự | Đồng đều về dung lượng, kiểm soát context window tốt. |
| | SentenceChunker (`by_sentences`) | 9 | 273.1 ký tự | Ngắt đúng ngữ pháp câu nhưng mất liên kết giữa tiêu đề mục và nội dung. |
| | RecursiveChunker (`recursive`) | 7 | 352.0 ký tự | Tốt, bảo toàn được cấu trúc phân cấp section của văn bản. |
| `fptshop-return-policy.md` | FixedSizeChunker (`fixed_size`) | 6 | 435.7 ký tự | Đủ độ dài cho 1-2 điều khoản, có overlap 50 ký tự giảm mất thông tin. |
| | SentenceChunker (`by_sentences`) | 8 | 312.9 ký tự | Chunks ngắn, dễ thiếu bối cảnh về điều kiện áp dụng. |
| | RecursiveChunker (`recursive`) | 7 | 357.9 ký tự | Tối ưu nhất về mặt ngữ nghĩa và độ dài khối thông tin. |

### Chiến lược của từng thành viên

**Thành viên 1 — Lê Như Ý**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=500`, `overlap=50`)
- **Mô tả & lý do chọn cho chủ đề này:** Phân chia văn bản thành các khối cố định 500 ký tự với độ chồng chéo 50 ký tự. Chiến lược này đơn giản, tốc độ xử lý nhanh và đảm bảo mọi chunk đều có kích thước tương đồng nhau, giúp kiểm soát chính xác số lượng token nạp vào context prompt của LLM.
- **Code snippet:**
```python
from src.chunking import FixedSizeChunker
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(body_text)
```

**Thành viên 2 — Nguyễn Văn A**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:** Chia nhỏ văn bản dựa trên ranh giới câu bằng biểu thức chính quy lookbehind, nhóm tối đa 3 câu thành một chunk. Chiến lược này giữ trọn vẹn ngữ pháp câu, phù hợp với các đoạn văn bản mô tả quy trình tiếp nhận bảo hành.
- **Code snippet:**
```python
from src.chunking import SentenceChunker
chunker = SentenceChunker(max_sentences_per_chunk=3)
chunks = chunker.chunk(body_text)
```

**Thành viên 3 — Trần Thị B**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=500`, separators=`["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả & lý do chọn:** Chia đệ quy đa tầng ưu tiên ranh giới lớn trước (đoạn, xuống dòng, câu). Chiến lược này rất phù hợp với văn bản quy định TMĐT vì giữ nguyên được các mục điều khoản hoàn chỉnh (paragraph/section) trước khi phải tách nhỏ.
- **Code snippet:**
```python
from src.chunking import RecursiveChunker
chunker = RecursiveChunker(chunk_size=500, separators=["\n\n", "\n", ". ", " ", ""])
chunks = chunker.chunk(body_text)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|---|:---:|---|---|
| **Lê Như Ý** | FixedSizeChunker (`500/50`) | 8 / 10 | Tốc độ cực nhanh, dung lượng chunk đồng đều, dễ quản lý context. | Cắt không quan tâm ranh giới ngữ nghĩa, có thể làm tách tiêu đề khỏi nội dung. |
| **Nguyễn Văn A** | SentenceChunker (`max=3`) | 7 / 10 | Đảm bảo ngữ nghĩa câu nguyên vẹn, không bao giờ bị cụt câu giữa chừng. | Dung lượng chunk chênh lệch lớn; danh sách liệt kê ngắn bị chia nhỏ quá mức. |
| **Trần Thị B** | RecursiveChunker (`500`) | 9 / 10 | Cân bằng hoàn hảo: giữ trọn vẹn cấu trúc mục/đoạn, ít vỡ vụn ngữ cảnh. | Thuật toán đệ quy phức tạp hơn, thời gian xử lý lâu hơn khi dữ liệu lớn. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker** là chiến lược tốt nhất cho chủ đề văn bản pháp quy/chính sách thương mại điện tử. Lý do là văn bản chính sách được cấu trúc chặt chẽ theo từng mục (`## Điều khoản`), và các quy định thường nằm trọn trong một đoạn văn (`\n\n`). RecursiveChunker giữ trọn vẹn được toàn bộ đoạn điều khoản đó trong một chunk duy nhất; chỉ khi điều khoản quá dài nó mới hạ xuống tách theo câu hoặc từ, giúp LLM nhận được ngữ cảnh đầy đủ nhất để trả lời chính xác.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|:---:|---|---|---|
| 1 | Thời gian áp dụng 1 đổi 1 miễn phí cho điện thoại bị lỗi nhà sản xuất tại CellphoneS là bao lâu? | 1 đổi 1 trong vòng 30 ngày đầu tiên kể từ thời điểm nhận hàng (đối với đơn online không quá 5 ngày so với ngày xuất hóa đơn). | `cellphones-warranty-policy #0` (Mục 1) |
| 2 | Khách hàng mua phụ kiện dưới 1 triệu tại CellphoneS được bảo hành đổi mới như thế nào? | Phụ kiện có giá dưới 1.000.000 VNĐ được đổi mới miễn phí trong vòng 01 năm (12 tháng) đối với hàng mới, hoặc đổi trong 01 tháng đối với hàng cũ. | `cellphones-warranty-policy #2` (Mục 3) |
| 3 | Chính sách đổi trả sản phẩm lỗi do nhà sản xuất tại FPT Shop quy định thời hạn đổi mới bao nhiêu ngày? | 1 đổi 1 trong 30 ngày đầu đối với điện thoại, máy tính bảng, laptop nếu có lỗi phần cứng từ nhà sản xuất. | `fptshop-return-policy #1` (Mục 1) |
| 4 | Điều kiện và phí trả hàng khi máy không lỗi hoặc đổi ý tại CellphoneS trong 30 ngày đầu là bao nhiêu? | Thu phí 20% đối với máy mới (15% đối với máy cũ) tính trên giá niêm yết hiện tại hoặc giá mua trên hóa đơn (lấy giá trị thấp hơn). | `cellphones-warranty-policy #1` (Mục 2) |
| 5 | Trách nhiệm và quy định thời hạn tiếp nhận xử lý bảo hành khi nhận sản phẩm từ người mua là gì? (`filter: audience=seller`) | Người bán phải tiếp nhận và xử lý bảo hành trong vòng 48 giờ làm việc kể từ khi nhận sản phẩm, thời gian hoàn tất tối đa 14 ngày làm việc. | `seller-warranty-policy #1` (Mục Quy định tiếp nhận) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|:---:|---|---|:---:|---|
| 1 | Thời hạn 1 đổi 1 CellphoneS | RecursiveChunker | Có (Top-1 với Recursive) | Mock embedding dễ nhầm từ khóa chung; Recursive gom ngữ cảnh đầy đủ hơn. |
| 2 | Bảo hành phụ kiện dưới 1 triệu | FixedSize & Recursive | Có (Top-1 với FixedSize) | FixedSize chunk 500 giữ trọn bảng thông số phụ kiện. |
| 3 | Đổi sản phẩm lỗi FPT Shop | RecursiveChunker | Có (Top-2 với FixedSize) | Cần ngữ cảnh phân biệt FPT Shop với Thế Giới Di Động. |
| 4 | Phí trả hàng đổi ý CellphoneS | RecursiveChunker | Có (Top-3 với FixedSize) | Điều khoản phí 20% được trích xuất thành công. |
| 5 | Quy định xử lý bảo hành cho người bán | FixedSize + Metadata Filter | Có (Top-1 chính xác 100%) | Bộ lọc `audience=seller` phát huy hiệu quả tối đa. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc bằng metadata đóng vai trò cực kỳ quan trọng, thể hiện rõ nhất ở Câu hỏi 5.** Câu hỏi 5 không nói rõ người hỏi là người mua hay người bán ("Trách nhiệm và quy định tiếp nhận xử lý..."). Nếu không có `metadata_filter={"audience": "seller"}`, hệ thống sẽ trả về chính sách của người mua tại các sàn và agent sẽ đưa ra quy trình gửi yêu cầu của khách hàng thay vì trách nhiệm của người bán. Nhờ pre-filtering theo metadata, hệ thống đã loại trừ toàn bộ tài liệu người mua và chọn chính xác tài liệu người bán.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Sự thật về MockEmbedder vs Semantic Embeddings:** Mock embedding (hash MD5) chỉ dùng để kiểm thử luồng code, không có khả năng hiểu ngữ nghĩa đồng nghĩa (như "12 tháng" vs "1 năm"). Khi lên production bắt buộc phải dùng mô hình nhúng thực thụ như SentenceTransformers hoặc OpenAI.
2. **Vai trò của Pre-filtering trong RAG:** Metadata filtering trước khi similarity search là yếu tố bắt buộc đối với các kho tri thức có phân quyền đối tượng (`buyer` vs `seller`) nhằm loại bỏ hoàn toàn nhiễu ngữ cảnh.
3. **Cân nhắc giữa Fixed-Size và Chunking cấu trúc:** Fixed-size chunking dù đơn giản nhưng có nguy cơ làm đứt gãy câu và mất tiêu đề; chiến lược đệ quy hoặc chia theo Heading giữ ngữ cảnh pháp lý tốt hơn đáng kể.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một kho tài liệu và cùng bộ 5 câu hỏi, chiến lược chunking quyết định trực tiếp chất lượng đầu vào của LLM. Fixed-size chunker phù hợp khi cần triển khai nhanh, chuẩn hóa kích thước; trong khi Recursive chunker cho kết quả trả lời mạch lạc và trúng đích hơn do không làm vỡ các khối điều khoản được người soạn thảo bố cục sẵn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nếu làm lại, nhóm sẽ triển khai bộ chunker tùy biến theo cấu trúc Markdown Heading (`Header/Section Chunker`) để mỗi điều khoản (từ `##` đến `##` tiếp theo) là một chunk độc lập, đồng thời tự động chèn tiêu đề cha vào đầu mỗi chunk con. Ngoài ra, nhóm sẽ crawl thêm dữ liệu chính sách đa dạng hơn từ các sàn Lazada, Tiki và gắn thêm metadata `effective_date` để kiểm soát hiệu lực theo thời gian.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|:---:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **39 / 40** |
