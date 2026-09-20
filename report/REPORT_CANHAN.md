# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Như Ý  
**Nhóm:** G41  
**Ngày:** 2026-09-20  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiến sát giá trị 1.0) biểu thị hai vector chỉ cùng hướng trong không gian đa chiều, phản ánh hai đoạn văn bản có sự tương đồng lớn về ngữ nghĩa và chủ đề, không bị ảnh hưởng bởi độ dài ngắn của văn bản.

**Ví dụ có độ tương tự CAO:**
- Câu A: Khách hàng được quyền đổi sản phẩm mới trong vòng 30 ngày nếu phát hiện lỗi phần cứng từ nhà sản xuất.
- Câu B: Trong một tháng đầu tiên, người mua có thể 1 đổi 1 miễn phí nếu thiết bị hỏng hóc do lỗi kỹ thuật của hãng.
- Tại sao tương đồng: Cả hai câu cùng mô tả trọn vẹn chính sách 1 đổi 1 miễn phí trong 30 ngày đối với lỗi do nhà sản xuất, dù dùng từ vựng diễn đạt khác nhau ("một tháng" vs "30 ngày", "hãng" vs "nhà sản xuất").

**Ví dụ có độ tương tự THẤP:**
- Câu A: Quy trình tiếp nhận và xử lý bảo hành điện thoại thông minh tại hệ thống bán lẻ.
- Câu B: Hướng dẫn cách nấu món phở bò truyền thống chuẩn vị thơm ngon cho gia đình.
- Tại sao khác: Hai câu thuộc hai miền ngữ nghĩa và phạm trù tri thức hoàn toàn tách biệt (quy trình dịch vụ công nghệ vs công thức ẩm thực).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid phụ thuộc lớn vào độ lớn (magnitude) của vector; văn bản dài chứa nhiều từ sẽ tạo ra vector có độ dài lớn và khoảng cách Euclid xa nhau dù chung ngữ nghĩa. Cosine similarity tự động chuẩn hóa vector về độ dài đơn vị (unit vector) và chỉ đo góc tạo bởi hai hướng, nhờ đó phản ánh chính xác sự tương đồng nội dung bất kể văn bản ngắn hay dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*  
> Bước nhảy giữa các chunk: `step = chunk_size - overlap = 500 - 50 = 450` ký tự.  
> Áp dụng công thức: `số lượng chunk = ceil((độ dài tài liệu - độ chồng chéo) / (kích thước chunk - độ chồng chéo))`  
> `số lượng chunk = ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.111...) = 23`  
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, `step = 500 - 100 = 400`, `số lượng chunk = ceil((10,000 - 100) / 400) = ceil(9,900 / 400) = ceil(24.75) = 25 chunks` (tăng thêm 2 chunks). Tăng độ chồng chéo giúp duy trì ngữ cảnh liền mạch giữa các đoạn, ngăn ngừa tình trạng một câu hoặc điều khoản quan trọng bị cắt đôi ngay ranh giới chunk khiến mô hình mất thông tin khi truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy lookbehind `re.split(r'(?<=[.!?])(?:\s+|\n+)', text.strip())` để tách chính xác ranh giới câu mà vẫn giữ lại dấu câu kết thúc của từng câu. Sau đó nhóm `max_sentences_per_chunk` câu lại với nhau bằng dấu cách và gọi `strip()`. Xử lý trường hợp văn bản rỗng bằng cách trả về ngay `[]`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Triển khai thuật toán đệ quy 2 chiều theo danh sách phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Nhánh đệ quy đi sâu sẽ hạ cấp dấu phân cách khi mảnh văn bản vượt quá `chunk_size`; nhánh gom gộp (merge) nối các mảnh liền kề sát ngưỡng `chunk_size` để chống vỡ vụn văn bản. Base case dừng khi đoạn văn bản nhỏ hơn `chunk_size` hoặc khi danh sách separator rỗng (cắt dự phòng theo độ dài cố định).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ các tài liệu dạng in-memory qua `self._store` (danh sách `dict` gồm `id`, `content`, `metadata` và `embedding`). Phương thức `search` chuẩn hóa vector truy vấn, duyệt qua các bản ghi để tính tích vô hướng (dot product) làm điểm tương đồng, sắp xếp giảm dần và trích xuất `top_k` kết quả có điểm cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` áp dụng cơ chế lọc trước (pre-filtering): lọc các bản ghi trong `self._store` khớp toàn bộ key-value của `metadata_filter` trước khi chạy similarity search, đảm bảo không bị hao hụt slot trong `top_k`. `delete_document` lọc bỏ mọi bản ghi có `metadata['doc_id'] == doc_id` hoặc `id == doc_id` và trả về `True` nếu kích thước store giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Đầu tiên truy xuất `top_k` chunk phù hợp nhất từ `self.store.search()`. Nếu không tìm thấy kết quả thì trả về thông báo lỗi rõ ràng; nếu có thì đánh số thứ tự từng đoạn `[1]`, `[2]` kèm nguồn tài liệu, đưa vào prompt yêu cầu LLM trả lời bám sát ngữ cảnh và trích dẫn số thứ tự nguồn, ngăn chặn hallucination (bịa đặt thông tin).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Day07
plugins: anyio-4.15.1
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.21s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|:---:|:---|:---|:---:|:---:|:---:|
| 1 | Chính sách bảo hành đổi mới 1 đổi 1 trong 30 ngày cho điện thoại lỗi nhà sản xuất. | Khách hàng được đổi trả sản phẩm mới trong vòng một tháng nếu phát hiện lỗi phần cứng. | cao | 0.0987 | Đúng (dương) |
| 2 | Tôi muốn hoàn tiền cho đơn hàng giao trễ. | Hệ thống hỗ trợ trả lại tiền vào tài khoản ngân hàng khi đơn hàng bị chậm trễ. | cao | 0.3198 | Đúng |
| 3 | Apple Watch được bảo hành chính hãng 12 tháng. | Bảo hành miễn phí cho đồng hồ thông minh Apple trong vòng 1 năm. | cao | -0.0872 | Sai (bất ngờ) |
| 4 | Quy trình đổi trả và hoàn tiền sản phẩm điện máy. | Công thức nấu phở bò truyền thống chuẩn vị Hà Nội. | thấp | 0.1131 | Sai lệch |
| 5 | Điện thoại này dùng rất tốt, pin trâu và màn hình đẹp. | Điện thoại này quá tệ, pin yếu và màn hình xấu. | cao | 0.2169 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là Cặp 3 ("Apple Watch 12 tháng" vs "đồng hồ Apple 1 năm") lại có điểm âm (-0.0872) trên MockEmbedder, trong khi Cặp 4 khác chủ đề lại dương (0.1131). Điều này phản ánh rõ bản chất của MockEmbedder (dựa trên băm MD5 và phép chiếu ngẫu nhiên) hoàn toàn không có khả năng học không gian ngữ nghĩa thực thụ; trong các hệ thống thực tế cần sử dụng các mô hình embedding chuyên dụng (như MiniLM hoặc OpenAI Embeddings) để các từ đồng nghĩa được ánh xạ về gần nhau trong không gian vector.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân với chiến lược **FixedSizeChunker (chunk_size=500, overlap=50)** trên kho dữ liệu thương mại điện tử 8 văn bản.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|:---:|:---:|---|
| 1 | Thời gian áp dụng 1 đổi 1 miễn phí cho điện thoại bị lỗi nhà sản xuất tại CellphoneS là bao lâu? | `ttgshop-warranty-policy #1`: Quy định số serial, tem niêm phong và tiếp nhận xử lý bảo hành. | 0.3638 | Không (nhầm sàn) | Trả lời trích từ quy định TTG Shop do mock embedding xếp hạng sai. |
| 2 | Khách hàng mua phụ kiện dưới 1 triệu tại CellphoneS được bảo hành đổi mới như thế nào? | `cellphones-warranty-policy #0`: Tiêu đề và mục 1 đổi mới miễn phí CellphoneS. | 0.1903 | Có (Top-1) | Trả lời đúng chính sách đổi mới 12 tháng cho hàng mới và 1 tháng cho hàng cũ. |
| 3 | Chính sách đổi trả sản phẩm lỗi do nhà sản xuất tại FPT Shop quy định thời hạn đổi mới bao nhiêu ngày? | `thegioididong-warranty-policy #1`: Cam kết đổi mới và thời gian xử lý cam kết 15 ngày. | 0.1982 | Có trong Top-2 (`fptshop #2`) | Agent trích xuất được điều khoản 30 ngày từ chunk FPT Shop ở vị trí Top-2. |
| 4 | Điều kiện và phí trả hàng khi máy không lỗi hoặc đổi ý tại CellphoneS trong 30 ngày đầu là bao nhiêu? | `thegioididong-warranty-policy #0`: Điều khoản đổi trả theo nhu cầu Thế Giới Di Động. | 0.3487 | Có trong Top-3 (`thegioididong #4`) | Agent trích dẫn quy định thu phí 20% trong tháng đầu tiên từ chunk liên quan. |
| 5 | Trách nhiệm và quy định thời hạn tiếp nhận xử lý bảo hành khi nhận sản phẩm từ người mua là gì? (`filter: audience=seller`) | `seller-warranty-policy #1`: Quy định tiếp nhận trong 48 giờ và tối đa 14 ngày làm việc. | 0.0981 | Có (Top-1 chính xác) | Trả lời chính xác trách nhiệm tiếp nhận trong 48h và xử lý tối đa 14 ngày cho người bán. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Nhóm nhận thấy chiến lược FixedSizeChunker rất nhạy cảm với việc chọn kích thước: nếu chunk_size quá nhỏ (300) sẽ cắt vụn một điều khoản ra 2-3 phần, làm mất liên kết giữa tiêu đề và nội dung; trong khi chiến lược chia theo Heading/Section giữ trọn vẹn được một điều khoản pháp lý trong một đơn vị truy xuất. Tuy nhiên, FixedSize kết hợp với metadata filter (`audience`) vẫn chứng minh được sức mạnh phân lập ngữ cảnh tuyệt đối ở Query 5.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|:---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 |
| **Tổng phần cá nhân** | **59 / 60** |
