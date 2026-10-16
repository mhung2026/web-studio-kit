## Kỷ luật chung
1. Trước khi làm: đọc `studio/STUDIO.md`, phiếu việc được giao (đường dẫn nằm trong lời gọi) và các file phiếu yêu cầu đọc. Không có phiếu → chỉ làm đúng yêu cầu trong lời gọi và ghi rõ giả định.
2. Chỉ ghi file trong **vùng ghi** của phiếu; phiếu không ghi thì dùng vùng mặc định của vai. Cần sửa chỗ khác → ghi vào mục "Việc ngoài vùng" của báo cáo.
3. Không nói "xong", "pass", "đã kiểm" khi không có lệnh đã chạy và output. Phần chưa chạy ghi `NOT RUN` kèm lý do.
4. Không tự nghiệm thu việc của chính mình; nghiệm thu là việc của QA và Producer.
5. Không bịa số liệu, version, API hay nguồn. Không chắc → tra tài liệu chính thức hoặc ghi rõ là giả định.
6. Thay đổi đặc tả theo cấp: **sửa lỗi** (tự sửa nếu nằm trong vùng ghi, kèm ADR ngắn), **B/D** (viết ADR trạng thái `đề xuất`, chờ duyệt), **R** (chỉ đề xuất phương án; chủ dự án quyết). Không chắc cấp → chọn cấp cao hơn. Mẫu ADR: theo mục Quy ước của `studio/STUDIO.md`; mặc định `studio/templates/adr.md`. Số ADR do Producer cấp trong phiếu.
7. Screenshot Playwright luôn truyền `filename` nằm trong vùng ghi của phiếu.
8. Không tạo secret hay khóa giả, không gọi dịch vụ tốn tiền, không đăng/gửi gì ra ngoài máy, không cài công cụ hệ thống. Chỉ cài package của dự án khi phiếu cho phép.
9. Không gọi agent khác. Cần vai khác → ghi vào báo cáo.
10. Không commit git; Producer commit.
11. Viết tiếng Việt; code, identifier, tên file giữ tiếng Anh.
12. Skill superpowers: Chỉ gọi skill có trong mục "Skill hỗ trợ" của mình; không gọi skill nào khác (kể cả `superpowers:brainstorming`, `superpowers:writing-plans`, `web-studio`). Thứ tự ưu tiên: Kỷ luật chung > phiếu việc > skill. Ngoại lệ TDD do phiếu quyết (mục "Ngoại lệ TDD"); phiếu không ghi → TDD cho phần logic, phần không unit test được (renderer, layout, config) kiểm bằng build/screenshot và ghi rõ trong báo cáo, không dừng việc. Skill bảo sửa test hay code ngoài vùng ghi → ghi vào "Việc ngoài vùng". Skill bảo hỏi "your human partner" hoặc người dùng → ghi câu hỏi vào "Vấn đề phát hiện" của báo cáo và dừng phần việc đó. Skill bảo commit → bỏ qua. Skill bảo dispatch subagent hoặc tạo worktree → không làm. Skill có trong danh sách mà chưa thấy nội dung trong ngữ cảnh → gọi tool `Skill` để nạp trước khi làm.
13. Kết thúc bằng báo cáo đúng mẫu `studio/templates/report.md`.
