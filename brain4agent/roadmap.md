# Roadmap & Active Tasks

File này chứa danh sách các tính năng, mục tiêu sắp tới và tình trạng công việc hiện tại.

## Mục tiêu hiện tại (Active)
- [ ] Chuẩn bị bài thuyết trình & demo đối chiếu các chiến lược chunking trong nhóm (REPORT_NHOM).

## Tương lai (Upcoming)
- [ ] Tích hợp mô hình nhúng thực tế (Local multilingual MiniLM hoặc OpenAI/Gemini Embedder).
- [ ] Thử nghiệm nâng cao với Markdown Header / Section Chunker cho văn bản pháp quy.

## 💡 Kho Ý Tưởng & Backlog (Idea Vault)
*Nơi lưu trữ các ý tưởng hay, kiến trúc mở rộng chưa ưu tiên làm ngay nhưng cần giữ lại để tham khảo.*
- [ ] Xây dựng crawler tự động định kỳ cập nhật chính sách từ các sàn TMĐT.
- [ ] Bổ sung metadata `effective_date` để lọc chính sách theo mốc thời gian.

## Đã hoàn thành (Done)
- [x] **Khởi tạo Bộ Nhớ Não Bộ Chuẩn (v1.0.0):** Thiết lập cấu trúc Đa Tầng brain4agent V5.2 và quy chuẩn quản trị AGENTS.md.
- [x] **Hoàn thiện Core Code Lab 7:** Triển khai `chunking.py`, `store.py`, `agent.py` và vượt qua 42/42 tests.
- [x] **Nạp dữ liệu TMĐT & Thực nghiệm Fixed-Size Chunking:** Ingest 6 tài liệu từ `D:\download\lab`, chạy `bench.py` với `chunk_size=500, overlap=50`.
- [x] **Hoàn thành Báo cáo:** Điền đầy đủ dữ liệu thực nghiệm vào `REPORT_CANHAN.md` và `REPORT_NHOM.md`.
