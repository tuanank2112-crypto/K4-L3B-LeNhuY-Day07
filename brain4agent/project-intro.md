# Giới Thiệu Dự Án (Project Overview)

## 1. Mục tiêu (Goals & Objectives)
- K4-L3B Lab 07: Nền tảng dữ liệu, Embedding & Vector Store (Chủ đề chính sách thương mại điện tử).
- Cài đặt & so sánh 3 chiến lược chunking (Fixed Size, Semantic/Delimiter, Recursive/Document Structure).
- Triển khai Vector Store với tìm kiếm Cosine Similarity, metadata filtering, và xóa.
- Xây dựng Agent kết nối Knowledge Base qua RAG.

## 2. Công nghệ cốt lõi (Tech Stack)
- **Language / Runtime:** Python 3.11
- **Testing:** pytest
- **Core Libraries:** numpy, pydantic/dataclasses, dotenv
- **Embedding Backend:** MockEmbedder (mặc định) / LocalEmbedder (SentenceTransformers)
- **Data Persistence:** In-memory Vector Store / Local JSON & Markdown storage
